import torch
import torch.nn.functional as F

# prompt_len + decode が収まるバケットサイズ
_BUCKETS = [384, 512, 640, 768, 1024, 1536, 2048]
# ほとんどのデコードは 300 トークン以内で完了する
_DECODE_BUFFER = 300


def _get_bucket(needed):
    for b in _BUCKETS:
        if needed <= b:
            return b
    return _BUCKETS[-1]


class T2SCudaGraphDecode:
    """T2S デコードステップの CUDA Graph ラッパー

    静的バッファに KV キャッシュを保持し、デコードステップ全体を
    CUDA Graph としてキャプチャ・再実行することで、カーネル起動
    オーバーヘッドを削減する。batch_size=1 専用。

    max_seq_len を prompt_len + DECODE_BUFFER のバケットに合わせて
    動的に確保し、無駄なアテンション計算を抑制する。
    """

    def __init__(self, model):
        self.model = model
        self.num_layers = model.num_layers
        self.num_heads = model.num_head
        self.hidden_dim = model.model_dim
        self.head_dim = self.hidden_dim // self.num_heads

        self._device = next(model.parameters()).device
        self._dtype = next(model.parameters()).dtype

        # 初期状態ではバッファ未確保
        self.max_seq_len = 0
        self._graph = None

    def _allocate_buffers(self, max_seq_len):
        """静的バッファを（再）確保し、既存の graph を無効化する"""
        device, dtype = self._device, self._dtype
        self.max_seq_len = max_seq_len

        self.static_x = torch.zeros(1, 1, self.hidden_dim, device=device, dtype=dtype)
        self.static_logits = torch.zeros(1, self.model.vocab_size, device=device, dtype=dtype)

        self.k_caches = [
            torch.zeros(1, self.num_heads, max_seq_len, self.head_dim, device=device, dtype=dtype)
            for _ in range(self.num_layers)
        ]
        self.v_caches = [
            torch.zeros(1, self.num_heads, max_seq_len, self.head_dim, device=device, dtype=dtype)
            for _ in range(self.num_layers)
        ]

        self.attn_mask = torch.full(
            (1, 1, 1, max_seq_len),
            torch.finfo(dtype).min,
            device=device,
            dtype=dtype,
        )
        self.cache_pos = torch.zeros(1, dtype=torch.long, device=device)

        # バッファが変わったので graph を無効化
        self._graph = None

    def setup_from_prompt(self, k_caches, v_caches):
        """prompt 処理後の KV キャッシュを静的バッファに転送

        Args:
            k_caches: List[Tensor] — 各レイヤー [1, seq_len, hidden_dim]
            v_caches: List[Tensor] — 各レイヤー [1, seq_len, hidden_dim]
        """
        seq_len = k_caches[0].shape[1]
        needed = _get_bucket(seq_len + _DECODE_BUFFER)

        # バケットが変わった場合のみバッファを再確保
        if needed != self.max_seq_len:
            self._allocate_buffers(needed)

        # Graph キャプチャ（バッファ再確保後 or 初回）
        if self._graph is None:
            self._capture_graph()

        # マスクをリセットし、prompt 位置を unmask
        self.attn_mask.fill_(torch.finfo(self.attn_mask.dtype).min)
        self.attn_mask[0, 0, 0, :seq_len] = 0.0

        # prompt の KV を静的バッファにコピー
        for i in range(self.num_layers):
            k = k_caches[i].view(1, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
            v = v_caches[i].view(1, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
            self.k_caches[i][:, :, :seq_len, :].copy_(k)
            self.v_caches[i][:, :, :seq_len, :].copy_(v)

    def _decode_fn(self):
        """CUDA Graph にキャプチャされるデコード計算"""
        x = self.static_x  # [1, 1, hidden_dim]

        for i in range(self.num_layers):
            layer = self.model.h.layers[i]

            # QKV projection
            qkv = F.linear(x, layer.self_attn.in_proj_weight, layer.self_attn.in_proj_bias)
            q, k, v = qkv.chunk(3, dim=-1)

            # Multi-head reshape: [1, H, 1, D]
            q = q.view(1, 1, self.num_heads, self.head_dim).transpose(1, 2)
            k = k.view(1, 1, self.num_heads, self.head_dim).transpose(1, 2)
            v = v.view(1, 1, self.num_heads, self.head_dim).transpose(1, 2)

            # Static cache write (GPU tensor index for CUDA Graph compatibility)
            self.k_caches[i].index_copy_(2, self.cache_pos, k)
            self.v_caches[i].index_copy_(2, self.cache_pos, v)

            # Full-length SDPA with mask
            attn = F.scaled_dot_product_attention(
                q, self.k_caches[i], self.v_caches[i], attn_mask=self.attn_mask
            )

            # Output projection + Post-norm (residual -> LN -> MLP -> LN)
            attn = attn.transpose(1, 2).reshape(1, 1, self.hidden_dim)
            attn = F.linear(attn, layer.self_attn.out_proj.weight, layer.self_attn.out_proj.bias)
            x = x + attn
            x = F.layer_norm(x, [self.hidden_dim], layer.norm1.weight, layer.norm1.bias, layer.norm1.eps)
            mlp_out = F.relu(F.linear(x, layer.linear1.weight, layer.linear1.bias))
            mlp_out = F.linear(mlp_out, layer.linear2.weight, layer.linear2.bias)
            x = x + mlp_out
            x = F.layer_norm(x, [self.hidden_dim], layer.norm2.weight, layer.norm2.bias, layer.norm2.eps)

        # Final projection (bias=False)
        self.static_logits.copy_(F.linear(x[:, -1], self.model.ar_predict_layer.weight))

    def _capture_graph(self):
        """サイドストリームでウォームアップし、CUDA Graph をキャプチャ"""
        side_stream = torch.cuda.Stream()
        with torch.no_grad():
            with torch.cuda.stream(side_stream):
                for _ in range(3):
                    self._decode_fn()
            torch.cuda.current_stream().wait_stream(side_stream)

            self._graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self._graph):
                self._decode_fn()

    def decode(self, x_input, pos):
        """1ステップのデコードを実行

        Args:
            x_input: [1, 1, hidden_dim] — トークン埋め込み + PE
            pos: int — KV キャッシュの書き込み位置

        Returns:
            logits: [1, vocab_size] — clone済み（sample の in-place 対策）
        """
        if pos >= self.max_seq_len:
            raise RuntimeError(f"Position {pos} exceeds max_seq_len {self.max_seq_len}")

        # Unmask new position
        self.attn_mask[0, 0, 0, pos] = 0.0
        # Update write position
        self.cache_pos.fill_(pos)
        # Copy input to static buffer
        self.static_x.copy_(x_input)
        # Replay captured graph
        self._graph.replay()
        # Return cloned logits (sample() does in-place scatter)
        return self.static_logits.clone()
