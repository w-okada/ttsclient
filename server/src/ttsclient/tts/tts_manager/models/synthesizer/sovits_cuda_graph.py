"""SoVITS decode パイプラインの CUDA Graph ラッパー

ge（参照音声エンコード）計算は動的なので Graph 外に置き、
ステップ 2-8（quantizer → enc_p → flow → dec）を Graph 化する。

動的次元は codes_len(m) と text_len(n) の 2 つ。
2D バケットキャッシュ方式で対応する。
"""

import math
from collections import OrderedDict

import torch
import torch.nn.functional as F

# y_len = codes_len * 2 のバケット
_Y_BUCKETS = [64, 128, 256, 512, 768, 1024]
# text_len のバケット
_TEXT_BUCKETS = [64, 128, 256]
# VRAM 節約のためキャッシュするグラフ数を制限
MAX_CACHED_GRAPHS = 4


def _get_bucket(value, buckets):
    for b in buckets:
        if value <= b:
            return b
    return None  # バケット外


class SoVITSCudaGraphDecode:
    """SoVITS decode パイプラインの CUDA Graph ラッパー

    2D バケット (y_len, text_len) ごとにグラフをキャッシュし、
    LRU で古いものを破棄する。
    """

    def __init__(self, model):
        self.model = model
        self._device = next(model.parameters()).device
        self._dtype = next(model.parameters()).dtype
        # (y_bucket, text_bucket) -> _GraphEntry, LRU 順
        self._cache = OrderedDict()
        # Generator の upsample factor を計算
        self._upsample_factor = math.prod(model.dec.ups[i].stride[0]
                                          for i in range(model.dec.num_upsamples))

    def decode(self, codes, text, ge):
        codes_len = codes.size(2)
        text_len = text.size(-1)
        y_len = codes_len * 2  # semantic_frame_rate == "25hz"

        y_bucket = _get_bucket(y_len, _Y_BUCKETS)
        text_bucket = _get_bucket(text_len, _TEXT_BUCKETS)

        # バケット外はフォールバック
        if y_bucket is None or text_bucket is None:
            return self.model._decode_pipeline(codes, text, ge)

        key = (y_bucket, text_bucket)

        # LRU: 使用されたエントリを末尾に移動
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            # 新規エントリ作成
            if len(self._cache) >= MAX_CACHED_GRAPHS:
                # 最も古いエントリを削除
                self._cache.popitem(last=False)
            self._cache[key] = _GraphEntry(
                self.model, y_bucket, text_bucket,
                self._device, self._dtype,
            )

        entry = self._cache[key]
        return entry.run(codes, text, ge, codes_len, text_len,
                         self._upsample_factor)


class _GraphEntry:
    """1 つの (y_bucket, text_bucket) に対応する CUDA Graph エントリ"""

    def __init__(self, model, y_bucket, text_bucket, device, dtype):
        self.model = model
        self.y_bucket = y_bucket
        self.text_bucket = text_bucket
        self._device = device
        self._dtype = dtype
        self._graph = None

        # ノイズ用 private generator（デフォルト CUDA RNG を汚染しない）
        self._noise_gen = torch.Generator(device=device)
        self._noise_gen.manual_seed(torch.randint(2**62, (1,)).item())

        self._allocate_buffers()
        self._capture_graph()

    def _allocate_buffers(self):
        device, dtype = self._device, self._dtype
        y_bucket = self.y_bucket
        text_bucket = self.text_bucket

        # codes: [1, 1, codes_len] — codes_len = y_bucket // 2
        codes_bucket = y_bucket // 2
        self.static_codes = torch.zeros(1, 1, codes_bucket, dtype=torch.long, device=device)
        self.static_text = torch.zeros(1, text_bucket, dtype=torch.long, device=device)
        # ge: [1, gin_channels, 1]
        gin_channels = self.model.gin_channels
        self.static_ge = torch.zeros(1, gin_channels, 1, dtype=dtype, device=device)
        # lengths (GPU tensors — 値を変更可能、shape は固定)
        self.static_y_lengths = torch.zeros(1, dtype=torch.long, device=device)
        self.static_text_lengths = torch.zeros(1, dtype=torch.long, device=device)
        # マスク: sequence_mask の GPU→CPU 同期を回避するための静的バッファ
        self.static_y_mask = torch.ones(1, 1, y_bucket, dtype=dtype, device=device)
        self.static_text_mask = torch.ones(1, 1, text_bucket, dtype=dtype, device=device)
        # noise: randn_like の代替
        inter_channels = self.model.inter_channels
        self.static_noise = torch.randn(1, inter_channels, y_bucket, dtype=dtype, device=device)
        # output: dec の出力バッファ
        self.static_output = None  # capture 時に確定

    def _decode_fn(self):
        """capture される計算（quantizer → enc_p → flow → dec）"""
        quantized = self.model.quantizer.decode(self.static_codes)
        if self.model.semantic_frame_rate == "25hz":
            quantized = F.interpolate(quantized, size=self.y_bucket, mode="nearest")

        ge_for_enc_p = self.model.ge_to512(
            self.static_ge.transpose(2, 1)
        ).transpose(2, 1)

        x, m_p, logs_p, y_mask = self.model.enc_p(
            quantized, self.static_y_lengths, self.static_text,
            self.static_text_lengths, ge_for_enc_p,
            y_mask=self.static_y_mask, text_mask=self.static_text_mask,
        )

        z_p = m_p + self.static_noise * torch.exp(logs_p) * 0.5

        z = self.model.flow(z_p, y_mask, g=self.static_ge, reverse=True)

        o = self.model.dec((z * y_mask)[:, :, :], g=self.static_ge)
        # output を保存（clone せず参照を保持）
        self.static_output = o

    def _capture_graph(self):
        """warmup 3 回 → capture"""
        # warmup 用に lengths をバケットサイズに設定
        self.static_y_lengths.fill_(self.y_bucket)
        self.static_text_lengths.fill_(self.text_bucket)
        # マスクをバケットサイズで全1に初期化
        self.static_y_mask.fill_(1.0)
        self.static_text_mask.fill_(1.0)

        side_stream = torch.cuda.Stream(device=self._device)
        side_stream.wait_stream(torch.cuda.current_stream(self._device))
        with torch.no_grad():
            with torch.cuda.stream(side_stream):
                for _ in range(3):
                    self._decode_fn()
            torch.cuda.current_stream(self._device).wait_stream(side_stream)

            self._graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(self._graph):
                self._decode_fn()

    def run(self, codes, text, ge, codes_len, text_len, upsample_factor):
        """copy → noise.normal_() → replay → trim → clone"""
        # 実データを static バッファにコピー（パディング領域はゼロ）
        self.static_codes.zero_()
        self.static_codes[:, :, :codes_len].copy_(codes)

        self.static_text.zero_()
        self.static_text[:, :text_len].copy_(text)

        self.static_ge.copy_(ge)

        y_len = codes_len * 2
        self.static_y_lengths.fill_(y_len)
        self.static_text_lengths.fill_(text_len)

        # マスクを実データの長さに合わせて更新（パディング領域はゼロ）
        self.static_y_mask.zero_()
        self.static_y_mask[:, :, :y_len] = 1.0

        self.static_text_mask.zero_()
        self.static_text_mask[:, :, :text_len] = 1.0

        # 毎回新しいノイズを注入（private generator でデフォルト RNG を汚さない）
        self.static_noise.normal_(generator=self._noise_gen)

        # Graph replay
        self._graph.replay()

        # 有効領域のみトリミングして返す
        actual_audio_len = y_len * upsample_factor
        return self.static_output[:, :, :actual_audio_len].clone()
