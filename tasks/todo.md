# v2 サービス層 段階的実装プラン

## 概要

API 層（ルーター・モデル・型定義、30パス/38メソッド）は完成済み。サービス層は全てスタブ（TODO）。
v1 のビジネスロジックを移植しつつ、推論エンジン系（PipelineManager, pyopenjtalk 等）はスタブのまま残す。

## スタブのまま残す範囲

- `SlotManager.generate_onnx()` — torch/onnx + 推論エンジン依存
- `TTSManager.run()` — PipelineManager 依存
- `TTSManager.get_phones()` — PipelineManager + pyopenjtalk 依存
- `TTSManager.jp_text_to_user_dict_records()` — pyopenjtalk 依存

---

## ステップ 1: ConfigurationManager (~35行)

- [x] `services/configuration_manager.py` — reload / set / _save 実装

---

## ステップ 2: GPUDeviceManager (~100行)

- [x] `services/gpu_device_manager.py`
  - [x] `reload()`: CPU エントリ先頭追加 + CUDA 検出（torch オプショナル）
  - [x] `is_cuda_available()`: try import torch
  - [x] `_reload_cuda_info()`: torch.cuda で GPU 情報取得
  - [x] `_reload_gpu_info_win()`: Windows WMI（ImportError 時スキップ）

---

## ステップ 3: ModuleManager (~300行)

- [x] `services/module_manager.py`
  - [x] `REGISTERED_MODULES` 定数: v1 の全モジュール定義移植 (25件)
  - [x] `reload()`: 存在確認 + SHA256 ハッシュ検証
  - [x] `_check_hash()`: SHA256 計算・照合
  - [x] `download()`: バックグラウンドスレッドで HTTP DL + 進捗コールバック
  - [x] `_download()`: requests.get(stream=True) チャンクDL
  - [x] `get_module_filepath()`: モジュール保存先パス
- [x] `pyproject.toml`: requests>=2.31 追加

---

## ステップ 4: SlotManager + model_importer (~320行)

- [x] `services/model_importer.py` (新規)
  - [x] `import_model()`: スロットDir作成、ファイルコピー/移動、SlotInfo生成、params.json書き込み
  - [x] `get_sovits_version_from_path_fast()`: ヘッダー/ハッシュ/サイズでバージョン検出 (v2Pro/v2ProPlus対応)
- [x] `services/slot_manager.py`
  - [x] `_load_slot_info()` / `_reload_slot_infos()`: params.json 読み込み
  - [x] `reload()`, `get_blank_slot_index()`
  - [x] `set_new_slot()`, `update_slot_info()`, `delete_slot()`
  - [x] `move_model_slot()`, `set_icon_file()`
  - [x] `reserve_slot_for_sample()` / `release_slot_from_reserved_for_sample()`
  - [x] `generate_onnx()`: raise NotImplementedError

---

## ステップ 5: VoiceCharacterSlotManager + vc_importer (~410行)

- [x] `services/voice_character_importer.py` (新規)
  - [x] `import_voice_character()`: Dir作成、ZIP展開 or 新規作成、params.json書き込み
- [x] `services/voice_character_slot_manager.py`
  - [x] CRUD: reload, set_new_slot, update_slot_info, delete_slot, move, set_icon
  - [x] 参照音声: add_voice_audio, update, delete, move, set_voice_icon_file
  - [x] `add_user_dict_record()`: CSV ファイル追記
  - [x] `zip_and_download()`: ZIP 化 → BytesIO
  - [x] `reserve_slot_for_sample()` / `release_slot_from_reserved_for_sample()`
- [x] librosa, soundfile, faster-whisper はオプショナル import（pyproject.toml 変更不要）

---

## ステップ 6: SampleManager (~150行)

- [x] `services/sample_manager.py`
  - [x] `REGISTERED_SAMPLES` 定数: v1 のサンプルリスト移植 (2件)
  - [x] `reload()`: サンプルリスト設定
  - [x] `download()`: スロット予約 → HTTP DL → インポート (GPT-SoVITS / VoiceCharacter 両対応)

---

## ステップ 7: TTSManager (スタブ整理のみ)

- [x] `services/tts_manager.py` — コメント整理のみ

---

## ステップ 8: 統合検証

- [x] `POST /api/operation/initialize` で全ディレクトリ初期化 + 全マネージャー reload
- [x] エンドツーエンド: 初期化 → モジュール確認 → モデルインポート → キャラ登録 → 参照音声追加 → 設定変更

---

# v2 残タスク

## 推論エンジン統合（GPT-SoVITS 本体との結合が必要）

- [x] `TTSManager.run()` — 音声生成（PipelineManager 依存）→ v1 コード移植完了
- [x] `TTSManager.get_phones()` — 音素抽出（PipelineManager + pyopenjtalk 依存）→ v1 コード移植完了
- [x] `TTSManager.jp_text_to_user_dict_records()` — ユーザー辞書生成（pyopenjtalk 依存）→ v1 コード移植完了
- [ ] `SlotManager.generate_onnx()` — ONNX 生成（PyTorch/ONNX 依存）
- [ ] v2 パイプライン対応 — ONNX / Faster / v2 Pipeline は後日
- [x] v3/v4 パイプライン — PipelineManager 統合完了（import テスト OK）

## 未実装機能

- [ ] 参照音声の録音 — UI/API/バックエンド 全て未実装
- [ ] 自動テキスト化 (Whisper) — 設定UIはあるが faster-whisper 統合なし

## 改善

- [ ] エラーハンドリングの標準化
- [ ] テスト基盤整備（ユニットテスト / E2E）
