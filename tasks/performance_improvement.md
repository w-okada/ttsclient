# Performance Improvement Log

## Phase 2: CUDA Graph (T2S decode)

### 概要

T2S デコードループのカーネル起動オーバーヘッドを CUDA Graph で削減する最適化。

### 実装ファイル

- `server/src/ttsclient/tts/tts_manager/models/ar/t2s_cuda_graph.py` (新規)
- `server/src/ttsclient/tts/tts_manager/models/ar/t2s_model.py` (修正)

### 仕組み

#### 問題: カーネル起動オーバーヘッド

T2S デコードは最大 1500 回のイテレーションで、各ステップごとに 12 層の Transformer ブロック + 最終線形射影の CUDA カーネルを個別に起動する。Python レベルのカーネル起動コスト（1ステップあたり ~100+ カーネル × ~5-10us）が累積する。

#### 解決: CUDA Graph

デコードステップの全カーネル起動を1回キャプチャし、`graph.replay()` で再実行する。これにより Python → CUDA ドライバの往復がステップあたり1回に削減される。

#### 静的 KV キャッシュ

CUDA Graph はテンソル形状が静的でなければならない。既存の JIT パスは `torch.cat()` で KV キャッシュを毎ステップ伸長するため形状が動的。これを固定サイズの静的バッファ `[1, H, max_seq_len, D]` に置き換え、`index_copy_()` で書き込み、アテンションマスクで未使用位置を遮蔽する。

### 動的バケットによる max_seq_len 最適化

#### 問題: 固定 2048 での性能劣化

初期実装では `max_seq_len=2048` で静的バッファを確保していた。実際のシーケンス長が ~270 の場合、SDPA は毎ステップ 2048 位置すべてに対してアテンション計算を行う。大部分はマスクで -inf に設定されているが、GPU は全位置のメモリ読み込み・dot product・softmax を実行してしまう。これにより CUDA Graph パスが JIT パスより**遅く**なっていた。

| | Naive (JIT) | CUDA Graph (2048固定) |
|---|---|---|
| decode速度 | ~460 it/s | ~350 it/s |
| decode時間 (64 steps) | ~130ms | ~185ms |

#### 解決: バケット方式

`prompt_len + 300`（デコードバッファ）を計算し、最も近いバケットサイズに切り上げる：

```
バケット: [384, 512, 640, 768, 1024, 1536, 2048]
デコードバッファ: 300 トークン（ほとんどのデコードはこの範囲内で完了）
```

例: prompt_len=207 → 207 + 300 = 507 → バケット **512**

バケットが変わった場合のみバッファを再確保して CUDA Graph を再キャプチャする。同じ参照音声を使う限り prompt_len は一定なので、再キャプチャはほぼ発生しない。

デコードがバケットを超えた場合は `RuntimeError` が発生し、`infer_panel()` の try/except で naive パスにフォールバックする。

### ベンチマーク結果

テスト条件: 「追加使用量を有効にしてください。」（prompt_len=207, decode ~60-65 steps）

| | Naive (JIT) | CUDA Graph (2048固定) | CUDA Graph (バケット512) |
|---|---|---|---|
| decode速度 | ~460 it/s | ~350 it/s | ~620 it/s |
| decode時間 | ~128ms | ~185ms | ~99ms |
| ステップあたり | ~2.1ms | ~2.8ms | ~1.6ms |
| 対 Naive 比 | baseline | 1.33x 遅い | **1.3x 速い** |

### アーキテクチャ

```
infer_panel()
├─ x.is_cuda → try infer_panel_cuda_graph()
│  ├─ idx=0: process_prompt() [JIT] → setup_from_prompt()
│  │  └─ バケット計算 → バッファ確保 → graph キャプチャ → KV コピー
│  └─ idx=1+: embedding+PE [graph外] → graph.replay() → sample [graph外]
└─ fallback → infer_panel_naive() [JIT]
```

### Graph 外に残す処理（毎ステップ実行）

| 処理 | 理由 |
|------|------|
| `ar_audio_embedding(y[:, -1:])` | 入力トークンが毎ステップ変わる |
| PE lookup | 位置インデックスが変わる |
| `sample(logits, y, ...)` | `y` が動的に伸長（repetition penalty） |
| EOS 判定 `.item()` | CPU 同期が必要 |

### メモリ使用量

バケット 512 の場合:
- KV キャッシュ: 12層 x 2(K+V) x `[1, 8, 512, 64]` x 2B (fp16) = **12 MB**
- Graph 自体: ~10-30 MB
- 合計: **~25-45 MB** 追加（2048 固定時の ~60-80 MB から削減）
