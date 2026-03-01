# T2S Dynamic Batching 設計

## 1. 背景・動機

### プロファイル結果

CUDA Graph + PE 事前計算 + weight_norm 除去を適用した最新計測結果:

| ステップ | 時間 (ms) | 割合 |
| --- | --- | --- |
| phone_extraction | 2.0 | 1.4% |
| **semantic_prediction (T2S)** | **105.1** | **75.4%** |
| spectrogram | 3.7 | 2.7% |
| sv_embedding | 8.7 | 6.2% |
| decode (SoVITS) | 14.0 | 10.0% |
| その他 | ~6 | 4.3% |
| **合計** | **~139** | |

T2S の自己回帰デコードがパイプライン全体の **75%** を占めている。

### なぜ T2S だけバッチ化するか

T2S と SoVITS は GPU 上のボトルネック特性が根本的に異なる:

| 特性 | T2S (semantic_prediction) | SoVITS (decode) |
| --- | --- | --- |
| 処理方式 | 自己回帰 (token-by-token) | 単一 forward pass |
| ボトルネック | メモリ帯域律速 | 演算律速 |
| 1ステップの行列サイズ | 小さい (`[1, 1, 512]`) | 大きい (flow + dec 全体) |
| GPU SM 利用率 | 低い（カーネル起動が支配的） | 高い |
| バッチ化効果 | **高い** — 帯域が余っている | 低い — SM が既に飽和 |
| 所要時間 | 105ms (75%) | 14ms (10%) |

T2S はメモリ帯域律速の小行列演算を数百回繰り返すため、バッチ化で複数リクエストをまとめると帯域を有効活用できる（LLM 推論と同じ原理）。SoVITS は既に演算律速でバッチ化の恩恵が小さく、14ms と軽いためシーケンシャル実行で十分。

## 2. 現在のアーキテクチャ

### 呼び出しフロー

```
POST /api/tts-manager/operation/generateVoice  (async def, 実質ブロッキング)
  └─ TTSManager.run(param)                       [シングルトン, 同期]
       ├─ check_and_load_model()
       ├─ check_and_load_voice_character_setting()
       └─ pipeline.run()                          [GPTSoVITSPipeline]
            ├─ _generate_ref_contents()            [初回のみ、以降キャッシュ]
            │   ├─ phone_extractor.get_phones_and_bert()  [CPU]
            │   ├─ ssl_model.get_content(wav16k)          [GPU]
            │   └─ vq_model.extract_latent(ssl_content)   [GPU]
            │
            └─ for text_chunk in texts:            [テキストチャンクループ]
                 ├─ phone_extractor.get_phones_and_bert()  [CPU, 2ms]
                 ├─ t2s_model.predict()                    [GPU, 105ms]
                 │   └─ infer_panel()
                 │        ├─ infer_panel_cuda_graph()      [高速パス]
                 │        └─ infer_panel_naive()            [フォールバック]
                 ├─ get_spepc()                            [GPU, 3.7ms]
                 ├─ sv_model.compute_embedding()           [GPU, 8.7ms]
                 └─ vq_model.decode()                      [GPU, 14ms]
```

**現在の制約**:
- `generate_voice` は `async def` だが、`TTSManager.run()` が同期ブロッキングのため、複数リクエストが来てもイベントループを占有する
- すべて batch_size=1 前提。リクエスト間バッチングの仕組みがない
- `TTSManager` はシングルトンで状態を共有しているが、排他制御がない

### T2S の入出力形状

```python
# 入力
all_phoneme_ids: [1, phoneme_len]        # phoneme_len ≈ 30-200
all_phoneme_len: [1]
prompt:          [1, prompt_len]          # prompt_len ≈ 100-300 (参照音声の semantic tokens)
bert:            [1, 1024, phoneme_len]   # BERT 埋め込み

# 中間（自己回帰ループ毎ステップ）
xy_pos:     [1, 1, hidden_dim]           # hidden_dim = 512
k_cache[i]: [1, seq_len, hidden_dim]     # 12 レイヤー分、seq_len は毎ステップ +1
v_cache[i]: [1, seq_len, hidden_dim]
logits:     [1, vocab_size]              # vocab_size = 1025

# 出力
pred_semantic: [1, 1, generated_len]     # generated_len ≈ 50-500
```

### CUDA Graph の制約

T2S CUDA Graph (`T2SCudaGraphDecode`):
- **batch_size=1 専用**: `bsz != 1` で RuntimeError
- **固定形状バッファ**: バケットシステム `[384, 512, 640, 768, 1024, 1536, 2048]` で max_seq_len を管理
- **KV Cache を静的バッファにコピー**: prompt 処理後に `setup_from_prompt()` で転送
- **CUDA 同期禁止**: `multinomial_sample_one_no_sync()` (Gumbel-max trick) で回避
- **RNG 分離**: private `torch.Generator` で CUDA Graph のデフォルト generator 競合を回避
- **バケット変更時にグラフ再キャプチャ**: バッファサイズが変わると `_capture_graph()` を再実行

SoVITS CUDA Graph (`SoVITSCudaGraphDecode`):
- batch_size=1 専用
- 2D バケット `(y_len, text_len)` で LRU キャッシュ (最大4グラフ)
- private generator でノイズ再生成

## 3. 提案アーキテクチャ

### 全体設計

```
FastAPI (async)
  │
  │  await run_in_executor(preprocess)        ← CPU バウンド
  ▼
┌──────────────────────────────┐
│  Preprocess (per request)    │
│  ├─ text splitting           │
│  ├─ phone/BERT extraction    │
│  ├─ reference audio cache    │
│  └─ spectrogram / SV emb     │
└──────────┬───────────────────┘
           │ T2SRequest (phoneme_ids, bert, prompt, params)
           ▼
┌──────────────────────────────────────────┐
│  T2SBatchScheduler                       │
│  ├─ request_queue: asyncio.Queue         │
│  ├─ _scheduler_loop() (asyncio.Task)     │
│  │   ├─ _collect_batch()                 │
│  │   │   ├─ max_wait: 50ms              │
│  │   │   └─ max_batch_size: 4-8         │
│  │   └─ _run_batch()                     │
│  │       ├─ batch=1 → CUDA Graph path    │
│  │       └─ batch>1 → Naive batch path   │
│  └─ result: asyncio.Future per request   │
└──────────┬───────────────────────────────┘
           │ pred_semantic per request
           ▼
┌──────────────────────────────┐
│  Postprocess (per request)   │
│  └─ vq_model.decode()        │  ← GPU Lock で直列化
└──────────────────────────────┘
```

### asyncio 統合

```python
# routers/tts.py
@router.post("/generateVoice")
async def generate_voice(param: GenerateVoiceParam):
    tts = TTSManager.get_instance()

    # 1. Preprocess (CPU) — イベントループをブロックしない
    chunks = await asyncio.get_event_loop().run_in_executor(
        None, tts.preprocess, param
    )

    # 2. T2S — バッチスケジューラ経由
    for chunk in chunks:
        chunk.pred_semantic = await tts.scheduler.submit(chunk.t2s_request)

    # 3. Postprocess (GPU) — Lock で直列化
    async with tts.gpu_lock:
        result = await asyncio.get_event_loop().run_in_executor(
            None, tts.postprocess, chunks
        )

    return StreamingResponse(result, ...)
```

## 4. T2S バッチ推論の実装方針

### 4.1 `infer_panel_batched()` メソッド

`Text2SemanticDecoder` に新たに追加するバッチ推論メソッド。既存の `infer_panel_naive()` をベースに、可変長入力のバッチ処理に対応する。

```python
def infer_panel_batched(
    self,
    batch_phoneme_ids: list[torch.LongTensor],    # list of [1, phoneme_len_i]
    batch_phoneme_lens: list[torch.LongTensor],   # list of [1]
    batch_prompts: list[torch.LongTensor],         # list of [1, prompt_len_i]
    batch_bert: list[torch.LongTensor],            # list of [1, 1024, phoneme_len_i]
    top_k, top_p, temperature, repetition_penalty,
    batch_early_stop_nums: list[int],
) -> list[tuple[torch.Tensor, int]]:
    ...
```

### 4.2 パディング戦略

バッチ内でテキスト長・プロンプト長が異なるため、最大長にパディングする:

```python
B = len(batch)
device = batch_phoneme_ids[0].device

# テキスト (phoneme + BERT) のパディング
max_phoneme_len = max(x.shape[1] for x in batch_phoneme_ids)
padded_phoneme_ids = torch.zeros(B, max_phoneme_len, dtype=torch.long, device=device)
padded_bert = torch.zeros(B, 1024, max_phoneme_len, dtype=batch_bert[0].dtype, device=device)

# プロンプト (reference semantic tokens) のパディング
max_prompt_len = max(p.shape[1] for p in batch_prompts)
padded_prompts = torch.zeros(B, max_prompt_len, dtype=torch.long, device=device)

for i in range(B):
    plen = batch_phoneme_ids[i].shape[1]
    padded_phoneme_ids[i, :plen] = batch_phoneme_ids[i][0]
    padded_bert[i, :, :plen] = batch_bert[i][0]
    prlen = batch_prompts[i].shape[1]
    padded_prompts[i, :prlen] = batch_prompts[i][0]
```

### 4.3 Attention Mask

`T2SBlock.process_prompt()` は既に `padding_mask` に対応している (t2s_model.py:88-141)。パディングされた位置にはマスクを適用し、attention 計算から除外する。

```python
# padding_mask: [B, max_seq_len, 1]  — True = パディング位置
phoneme_mask = torch.arange(max_phoneme_len, device=device).unsqueeze(0) >= actual_phoneme_lens.unsqueeze(1)
prompt_mask = torch.arange(max_prompt_len, device=device).unsqueeze(0) >= actual_prompt_lens.unsqueeze(1)
padding_mask = torch.cat([phoneme_mask, prompt_mask], dim=1).unsqueeze(-1)  # [B, total_len, 1]
```

**注意**: `process_prompt_flash()` は `padding_mask` 未対応（batch_size=1 前提で最適化されている）。バッチ推論では `process_prompt()` を使用する。

### 4.4 EOS 処理

バッチ内の各サンプルが異なるタイミングで EOS に到達する。`active_mask` で追跡:

```python
active_mask = torch.ones(B, dtype=torch.bool, device=device)  # True = まだ生成中
generated_tokens = [[] for _ in range(B)]

for idx in range(1500):
    # ... decode step ...
    logits = self.ar_predict_layer(xy_dec[:, -1])  # [B, vocab_size]
    samples = batched_sample(logits, ...)           # [B, 1]

    for i in range(B):
        if not active_mask[i]:
            continue
        if samples[i, 0].item() == self.EOS or torch.argmax(logits[i]).item() == self.EOS:
            active_mask[i] = False
        else:
            generated_tokens[i].append(samples[i, 0])

    if not active_mask.any():
        break

    # EOS に達したサンプルもバッチ内に残す（KV Cache 形状の一貫性のため）
    # batch_size 4-8 なら無駄は許容範囲
```

### 4.5 KV Cache 管理

バッチ推論では CUDA Graph を使わず、Naive パス (`process_prompt` + `decode_next_token`) を使用する。KV Cache は JIT 関数内で `torch.cat` で動的に伸長する。

```python
# prompt 処理
xy_dec, k_cache, v_cache = self.t2s_transformer.process_prompt(
    xy_pos, attn_mask, padding_mask   # padding_mask 付きで呼び出し
)
# k_cache: List[12] of [B, seq_len, hidden_dim]
# v_cache: List[12] of [B, seq_len, hidden_dim]

# デコードステップ
for idx in range(1, 1500):
    xy_dec, k_cache, v_cache = self.t2s_transformer.decode_next_token(
        xy_pos, k_cache, v_cache
    )
    # k_cache[i] は毎ステップ cat で +1 伸長
```

### 4.6 CUDA Graph との使い分け

```
batch_size == 1 → 既存の infer_panel_cuda_graph() — 最速、レイテンシ劣化なし
batch_size >  1 → infer_panel_batched() (Naive パス) — スループット優先
```

単一リクエスト時に CUDA Graph パスを維持することで、**単一リクエストのレイテンシは一切劣化しない**。

### 4.7 sample() のバッチ対応

既存の `sample()` / `logits_to_probs()` は batch 次元を持つテンソルを受け付ける構造になっている（`dim=1` で操作）。ただし `repetition_penalty` の `previous_tokens` 処理で各サンプルごとの生成履歴を渡す必要がある:

```python
# previous_tokens をバッチ内で最大長にパディング
max_gen_len = max(len(g) for g in generated_tokens)
prev_tokens = torch.zeros(B, max_gen_len, dtype=torch.long, device=device)
for i in range(B):
    if generated_tokens[i]:
        prev_tokens[i, :len(generated_tokens[i])] = torch.stack(generated_tokens[i])
```

## 5. Pipeline の分割

現在の `GPTSoVITSPipeline.run()` を 3 フェーズに分割する:

### Phase 構成

```python
class GPTSoVITSPipeline:
    def preprocess(self, param) -> list[T2SChunk]:
        """CPU バウンド: テキスト分割 + phoneme/BERT + 参照音声処理"""
        # 1. _generate_ref_contents() — キャッシュ付き
        # 2. _generate_target_contents() — テキスト分割
        # 3. per chunk: phone_extractor.get_phones_and_bert()
        # 4. per chunk: bert concat, phoneme_ids 構築
        # 5. spectrogram + sv_emb 計算
        return chunks

    # T2S は scheduler 経由で実行（pipeline 外）

    def postprocess(self, chunks: list[T2SChunk]) -> tuple[int, np.ndarray]:
        """GPU バウンド: SoVITS decode + 音声結合"""
        audio_opt = []
        for chunk in chunks:
            audio = self.vq_model.decode(
                chunk.pred_semantic, chunk.phones2,
                chunk.refers, speed=chunk.speed,
                sv_emb=chunk.sv_emb,
            )
            audio_opt.append(audio)
        return self.hps.data.sampling_rate, concat_audio(audio_opt)
```

### T2SChunk データクラス

```python
@dataclass
class T2SChunk:
    # Preprocess の出力 / T2S の入力
    all_phoneme_ids: torch.LongTensor   # [1, phoneme_len]
    all_phoneme_len: torch.LongTensor   # [1]
    prompt: torch.LongTensor            # [1, prompt_len]
    bert: torch.Tensor                  # [1, 1024, phoneme_len]
    top_k: int
    top_p: float
    temperature: float
    repetition_penalty: float
    early_stop_num: int

    # T2S の出力 / Postprocess の入力
    pred_semantic: torch.Tensor | None = None  # [1, 1, m]

    # Postprocess 用
    phones2: torch.LongTensor | None = None
    refers: list[torch.Tensor] | None = None
    speed: float = 1.0
    sv_emb: list[torch.Tensor] | None = None
```

## 6. スレッドセーフティ

### ロック戦略

```python
class TTSManager:
    def __init__(self):
        self._model_lock = asyncio.Lock()     # モデルロード/設定変更の排他制御
        self._gpu_lock = asyncio.Lock()        # SoVITS decode の GPU 排他制御
        self.scheduler: T2SBatchScheduler      # T2S はスケジューラが内部で排他管理
```

| リソース | ロック | 理由 |
| --- | --- | --- |
| モデルロード/切替 | `_model_lock` | `check_and_load_model()` と推論の競合防止 |
| T2S 推論 | スケジューラ内部 | 単一 GPU ワーカーが直列に batch 実行 |
| SoVITS decode | `_gpu_lock` | GPU 上の SoVITS モデルを直列実行 |
| reference_cache | ロック不要 | 同一キーへの書き込みは冪等（同じ結果） |
| semantic_cache | チャンク単位 | freeze モード時、チャンク ID ベースのキャッシュ |

### モデル切替時の挙動

モデル切替 (`check_and_load_model`) が発生した場合:

1. `_model_lock` を取得
2. スケジューラのキューに残っているリクエストを drain（Future に例外を設定）
3. 新しいモデルをロード
4. スケジューラに新しい T2S モデルの参照を設定
5. `_model_lock` を解放

## 7. 段階的実装計画

### Phase 1: asyncio.Lock による直列化

**目的**: 安全な async/await パターンの確立。スループット改善はなし。

**変更ファイル**:
- `routers/tts.py` — `run_in_executor` でイベントループをブロックしない
- `tts_manager.py` — `asyncio.Lock` の追加

```python
# routers/tts.py
@router.post("/generateVoice")
async def generate_voice(param: GenerateVoiceParam):
    tts = TTSManager.get_instance()
    async with tts._model_lock:
        sample_rate, audio_data = await asyncio.get_event_loop().run_in_executor(
            None, tts.run, param
        )
    ...
```

**検証**:
- 複数同時リクエストでクラッシュしないこと
- 単一リクエストのレイテンシが劣化しないこと

### Phase 2: T2S バッチ推論メソッドの実装

**目的**: `infer_panel_batched()` の追加とユニットテスト。スケジューラはまだ導入しない。

**変更ファイル**:
- `models/ar/t2s_model.py` — `infer_panel_batched()` 追加
- `models/ar/utils.py` — 必要に応じて `sample()` のバッチ対応

**検証**:
- batch_size=1 で `infer_panel_naive` と同一出力（deterministic seed）
- batch_size=2,4 で正常に動作し、各サンプルが独立した EOS タイミングで終了
- padding_mask が正しく機能すること

### Phase 3: バッチスケジューラの統合

**目的**: エンドツーエンドの Dynamic Batching を実現。

**新規ファイル**:
- `t2s_batch_scheduler.py` — `T2SBatchScheduler` クラス

**変更ファイル**:
- `tts_manager.py` — スケジューラの初期化と統合
- `pipeline/gpt_sovits_pipeline.py` — `preprocess()` / `postprocess()` の分離
- `routers/tts.py` — async フローの変更
- `app.py` — スケジューラの lifecycle 管理

**T2SBatchScheduler の設計**:

```python
class T2SBatchScheduler:
    def __init__(self, t2s_model, max_batch_size=4, max_wait_ms=50):
        self._queue: asyncio.Queue[T2SRequest] = asyncio.Queue()
        self._t2s_model = t2s_model
        self._max_batch_size = max_batch_size
        self._max_wait_ms = max_wait_ms
        self._task: asyncio.Task | None = None

    async def start(self):
        self._task = asyncio.create_task(self._scheduler_loop())

    async def stop(self):
        self._task.cancel()

    async def submit(self, request: T2SRequest) -> torch.Tensor:
        future = asyncio.get_event_loop().create_future()
        await self._queue.put((request, future))
        return await future

    async def _scheduler_loop(self):
        while True:
            batch = await self._collect_batch()
            await asyncio.get_event_loop().run_in_executor(
                None, self._run_batch, batch
            )

    async def _collect_batch(self) -> list[tuple[T2SRequest, asyncio.Future]]:
        # 最初のリクエストは無制限に待つ
        first = await self._queue.get()
        batch = [first]

        # 追加リクエストを max_wait_ms まで収集
        deadline = asyncio.get_event_loop().time() + self._max_wait_ms / 1000
        while len(batch) < self._max_batch_size:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                break
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=remaining)
                batch.append(item)
            except asyncio.TimeoutError:
                break

        return batch

    def _run_batch(self, batch):
        requests, futures = zip(*batch)
        with torch.no_grad():
            if len(requests) == 1:
                # 単一リクエスト → CUDA Graph パスを維持
                result = self._t2s_model.infer_panel(...)
                futures[0].set_result(result)
            else:
                # バッチ推論
                results = self._t2s_model.infer_panel_batched(...)
                for future, result in zip(futures, results):
                    future.set_result(result)
```

**検証**:
- 単一リクエスト: CUDA Graph パスが使われ、レイテンシ劣化なし
- 4 同時リクエスト: バッチ化が発生し、スループットが改善
- モデル切替時にキュー内リクエストが適切にエラー返却される

## 8. パフォーマンス見積もり

### 単一リクエスト

Phase 3 導入後も batch_size=1 は CUDA Graph パスを使うため、レイテンシは **変化なし** (~139ms)。

### 4 同時リクエストのスループット

**現状 (Phase 1: Lock 直列化)**:
```
Request 1: |== T2S 105ms ==|== SoVITS 14ms ==|
Request 2:                                     |== T2S 105ms ==|== SoVITS 14ms ==|
Request 3:                                                                        |== ...
Request 4:                                                                                 |== ...
合計: 4 × ~139ms ≈ 556ms
```

**Phase 3 (Dynamic Batching)**:
```
T2S batch(4): |========= ~130ms =========|
SoVITS seq:                                |= 14ms =|= 14ms =|= 14ms =|= 14ms =|
合計: ~130ms + 56ms ≈ 186ms
```

| シナリオ | 合計時間 | スループット | 対 Lock 比 |
| --- | --- | --- | --- |
| Lock 直列 (4req) | ~556ms | 7.2 req/s | 1.0x |
| Dynamic Batch (4req) | ~186ms | 21.5 req/s | **~3.0x** |

**T2S バッチ推論の時間見積もり根拠**: メモリ帯域律速の自己回帰デコードでは、batch_size を 1→4 にしても SDPA の実行時間はほぼ線形に増加しない（帯域に余裕がある）。prompt 処理は batch_size に対してやや線形的だが、全体の ~20% 程度。概算で batch=4 の T2S は単一の ~1.2-1.3 倍 (105 × 1.25 ≈ 130ms)。

### 待機時間のオーバーヘッド

`max_wait_ms=50ms` の設定で、単一リクエストが来た場合:
- キューが空 → 即座に処理（待機なし）
- 最初の 1 件が来てから 50ms 以内に追加が来なければ batch=1 として処理

つまり単一リクエスト時の追加レイテンシは **0ms**（キューが空ならば待たずに即実行）。

## 9. リスクと対策

| リスク | 影響 | 対策 |
| --- | --- | --- |
| パディングが attention 品質に影響 | 生成品質の劣化 | `padding_mask` で確実にマスク。`process_prompt()` は既に対応済み |
| batch=4 で VRAM 不足 | OOM クラッシュ | `max_batch_size` を設定で調整可能に。KV Cache は `[B, seq, dim]` でバッチ分増加 |
| EOS 後の無駄な計算 | スループット低下 | batch_size 4-8 なら影響軽微。将来的に dynamic slot refilling で改善可能 |
| バッチ待機による単一リクエストのレイテンシ増加 | 体感悪化 | batch=1 は CUDA Graph パスに直接ルーティング、待機スキップ |
| モデル切替中のリクエスト | リクエスト失敗 | `_model_lock` でブロック。キュー内リクエストは drain して例外返却 |
| `process_prompt_flash()` がバッチ未対応 | バッチ推論で使えない | バッチ推論は `process_prompt()` (padding_mask 対応済み) を使用。性能差は prompt 処理のみで全体への影響は小さい |
| JIT と Python ループの相互作用 | デバッグ困難 | Phase 2 で十分なユニットテストを書いてからスケジューラを統合 |
| `repetition_penalty` のバッチ処理 | 各サンプル独立の履歴が必要 | `previous_tokens` をサンプルごとにパディングして batch 処理 |
