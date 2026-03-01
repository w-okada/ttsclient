# DM-002: パイプライン一致性テスト (オリジナル GPT-SoVITS vs ttsclient)

## ステータス

検証完了 — 全精度モードで完全一致を確認

## コンテキスト

ttsclient は GPT-SoVITS v2Pro の推論パイプラインを独自に再構築している。
オリジナルと ttsclient で同一のモデル重みを使い、同一入力に対して同一出力が得られることを保証する必要がある。

テストファイル: `server/tests/test_pipeline_consistency.py`

## パイプライン構成

GPT-SoVITS の TTS 推論は以下の 6 段階で構成される:

```
参照音声 + 参照テキスト + ターゲットテキスト
    │
    ├─ (1) Phone 抽出 + BERT (参照テキスト)
    ├─ (2) SSL (CNHubert) → extract_latent (参照音声 → prompt semantic tokens)
    ├─ (3) Phone 抽出 + BERT (ターゲットテキスト)
    ├─ (4) T2S (GPT) semantic prediction
    ├─ (5) Spectrogram + SV embedding (参照音声)
    └─ (6) SoVITS decode → 音声出力
```

## テスト一覧

### Test 1–6: コンポーネント単体・パイプライン部分テスト

| Test | 対象 | 内容 |
|------|------|------|
| 1 | SV embedding (float32) | オリジナル / ttsclient の SV 計算方式が同一結果を返すか |
| 2 | SV embedding (half) | half precision 時の SV 一致性 (GPU のみ) |
| 3 | SynthesizerTrn.decode 段階比較 | decode 内部の 7 段階 (ref_enc → quantizer → enc_p → sampling → flow → dec) を個別比較 |
| 4 | SynthesizerTrn.decode E2E | decode() 一括呼び出しの最終出力比較 |
| 5 | extract_latent | VQ quantizer の latent code 抽出の一致性 |
| 6 | パイプライン (実音声) | 実際の参照音声から spectrogram → SV → decode まで (ダミー semantic) |

### Test 7: 真の E2E パイプライン一致性

パイプライン全 6 段階を個別に実行し、各段階の中間出力を比較する。

#### Stage A: Phone+BERT (参照テキスト)

- **オリジナル**: `TextPreprocessor.get_phones_and_bert()`
- **ttsclient**: `BertPhoneExtractor.get_phones_and_bert()` の流れを再現
- **比較対象**: `phones` (list[int]), `bert` (tensor)

#### Stage B: SSL → extract_latent (参照音声)

- CNHubert で参照音声から SSL content を抽出
- SoVITS の `extract_latent()` で semantic token (prompt) を取得
- **比較対象**: `prompt_semantic` の値と形状
  - オリジナル: `codes[0, 0].expand(B, -1)` → `(1, seq_len)`
  - ttsclient: `codes[0, 0].unsqueeze(0)` → `(1, seq_len)`
  - B=1 では同一結果

#### Stage C: Phone+BERT (ターゲットテキスト)

- Stage A と同様の比較

#### Stage D: T2S semantic prediction

- 同一 seed (`_set_seed(42)` — random/np/torch/cuda 全リセット + TF32 無効化) で 2 回実行
- `t2s_model.infer_panel()` の出力が seed リセットで完全一致することを確認
- Phone 差異がある場合は、オリジナル / ttsclient それぞれの phones で T2S を実行し差異を分離

#### Stage E: Spectrogram + SV embedding

- `spectrogram_torch()` でオリジナル / ttsclient の spectrogram を比較
- SV embedding は float32 固定で計算 (本番と同一)

#### Stage F: SoVITS decode

- 全ステージの出力を集約して `vq_model.decode()` を呼び出し
- オリジナル SynthesizerTrn vs ttsclient SynthesizerTrn の最終音声出力を比較

## 事前調査で発見した差異ポイントと結論

| 箇所 | オリジナル | ttsclient | 影響 |
|------|-----------|-----------|------|
| prompt 形状 | `codes[0, 0].expand(B, -1)` | `codes[0, 0].unsqueeze(0)` | B=1 で同一 → **影響なし** |
| BERT 非中国語 dtype | `torch.float32` 固定 | `self.dtype` (half 可) | 値はゼロテンソルのため **影響なし** |
| LangSegmenter 連結 | 連続する同種言語セグメントを結合 | 結合せず個別処理 | 日本語単一テストでは **影響なし** (混在時は要検証) |
| infer_panel 選択 | `run()` 内で `infer_panel_batch_infer` に差し替え | デフォルト `infer_panel` | B=1 では同一結果 → **影響なし** |
| seed 設定 | `set_seed()` (random/np/torch/cuda + TF32) | 同等の `_set_seed()` | **影響なし** |

## 実行方法

### 必要なモデルファイル

| 引数 | 説明 | パス例 |
|------|------|--------|
| `--sovits-path` | v2Pro SoVITS チェックポイント | `modules/v2Pro/s2Gv2Pro.pth` |
| `--sv-path` | SV モデル | `modules/sv/pretrained_eres2netv2w24s4ep4.ckpt` |
| `--t2s-path` | T2S (GPT) モデル | `modules/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt` |
| `--bert-path` | BERT モデルディレクトリ | `modules/chinese-roberta-wwm-ext-large` |
| `--cnhubert-path` | CNHubert モデルディレクトリ | `modules/chinese-hubert-base` |
| `--ref-wav` | 参照音声 | `voice_characters/0/029be6ca-f505-452f-8780-00be39e1b7e9.wav` |

### コマンド

```bash
cd server

# CPU float32 (Test 1-7)
uv run python tests/test_pipeline_consistency.py \
    --sovits-path modules/v2Pro/s2Gv2Pro.pth \
    --sv-path modules/sv/pretrained_eres2netv2w24s4ep4.ckpt \
    --t2s-path "modules/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt" \
    --bert-path modules/chinese-roberta-wwm-ext-large \
    --cnhubert-path modules/chinese-hubert-base \
    --ref-wav voice_characters/0/029be6ca-f505-452f-8780-00be39e1b7e9.wav \
    --ref-text "こんにちは。" \
    --target-text "今日はいい天気ですね。" \
    --text-lang ja \
    --device cpu

# GPU float32
# --device cuda:0 に変更

# GPU half precision (float16)
# --device cuda:0 --half を指定
```

### オプション引数

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `--ref-text` | `"こんにちは。"` | 参照テキスト |
| `--target-text` | `"今日はいい天気ですね。"` | ターゲットテキスト |
| `--text-lang` | `ja` | テキスト言語 |
| `--device` | `cpu` | デバイス (`cpu` / `cuda:0`) |
| `--half` | (なし) | half precision で実行 |

`--t2s-path`, `--bert-path`, `--cnhubert-path` を省略すると Test 1–6 のみ実行される。

## テスト結果

### CPU float32

```
Stage A: phones (ref)    PASS (identical)
         bert (ref)      PASS (max_diff=0.00e+00)
Stage B: prompt_semantic PASS (identical)
Stage C: phones (tgt)    PASS (identical)
         bert (tgt)      PASS (max_diff=0.00e+00)
Stage D: pred_semantic   PASS (identical)
Stage E: spectrogram     PASS (max_diff=0.00e+00)
Stage F: final_audio     PASS (max_diff=0.00e+00)
```

### GPU float32

```
Stage A: phones (ref)    PASS (identical)
         bert (ref)      PASS (max_diff=0.00e+00)
Stage B: prompt_semantic PASS (identical)
Stage C: phones (tgt)    PASS (identical)
         bert (tgt)      PASS (max_diff=0.00e+00)
Stage D: pred_semantic   PASS (identical)
Stage E: spectrogram     PASS (max_diff=0.00e+00)
Stage F: final_audio     PASS (max_diff=3.73e-08)
```

Stage F の微小な差異 (3.73e-08) は GPU 浮動小数点演算の非決定性によるもので許容範囲内。

### GPU half precision (float16)

```
Stage A: phones (ref)    PASS (identical)
         bert (ref)      PASS (max_diff=0.00e+00, dtype=float32 vs float16)
Stage B: prompt_semantic PASS (identical)
Stage C: phones (tgt)    PASS (identical)
         bert (tgt)      PASS (max_diff=0.00e+00, dtype=float32 vs float16)
Stage D: pred_semantic   PASS (identical)
Stage E: spectrogram     PASS (max_diff=0.00e+00)
Stage F: final_audio     PASS (max_diff=0.00e+00)
```

bert の dtype 差異 (float32 vs float16) は、オリジナルが非中国語で `torch.float32` 固定のゼロテンソルを返すのに対し、ttsclient が `self.dtype` (float16) で返すため。値はすべてゼロなので実質的な差異はない。

## 実装上の注意点

### TTS_infer_pack のインポート回避

`TTS_infer_pack/__init__.py` が `TTS.py` を import し、`ffmpeg` 依存を引き込む。
テストでは `text_segmentation_method` のみを個別ロードし、ダミーパッケージを `sys.modules` に登録することで回避している。

### SV モデルの精度

SV モデルは本番同様 float32 固定で計算し、結果を decode 時に dtype にキャストしている。

### 未検証の領域

- **日本語+英語混在テキスト**: LangSegmenter の連続セグメント結合ロジックに差異がある。日本語単一テキストでは発生しないが、混在テキストで phones 差異が生じる可能性がある。
- **中国語テキスト**: BERT feature が非ゼロになるため、dtype 差異が実質的な影響を持つ可能性がある。
- **バッチサイズ B>1**: prompt 形状や infer_panel の差異が顕在化する可能性がある (ttsclient は B=1 固定のため現状は問題なし)。
