# v2 サーバーサイド API 実装プラン

## 概要

v1 (master) のサーバーサイド API を v2 ブランチで再構築する。
依存関係の順に段階的に実装し、各ステップで動作確認を行う。

- 代替URL (`/api_xxx` 形式)、YMM4互換API、Socket.IO は対象外
- サービス層はスタブ（モック）で仮実装し、API の型定義とルーティングを先に確定する

---

## ステップ1: 基盤 — const.py + 共通モデル + app.py 更新

**目的**: 全ステップで共通利用する型・定数・共通モデルを定義し、app.py に CORS とルーター登録の骨組みを作る

**ファイル**:
- [x] `server/src/ttsclient/const.py` — 型エイリアス・定数
- [x] `server/src/ttsclient/models/__init__.py` — re-export
- [x] `server/src/ttsclient/models/common.py` — SetIconParam, MoveModelParam
- [x] `server/src/ttsclient/app.py` — CORS 設定、ルーター登録の骨組み

**検証**: `uv run fastapi dev` で起動できること、`/health` が引き続き動くこと

---

## ステップ2: Hello + Proxy + FileUploader (基盤API)

**目的**: 依存のない最もシンプルな API 群を実装

**ファイル**:
- [x] `server/src/ttsclient/routers/hello.py` — `GET /api/hello`
- [x] `server/src/ttsclient/routers/proxy.py` — `GET /get_proxy`
- [x] `server/src/ttsclient/routers/uploader.py` — `/api/uploader/*`
- [x] `server/src/ttsclient/utils/__init__.py`
- [x] `server/src/ttsclient/utils/file_uploader.py` — EasyFileUploader
- [x] `server/src/ttsclient/routers/__init__.py` — 更新

**検証**: Swagger UI で各エンドポイントの型が表示されること

---

## ステップ3: Configuration + GPU Device + Module (設定・デバイス管理)

**目的**: 設定取得/更新、GPU情報、モジュール一覧の API を実装

**ファイル**:
- [x] `server/src/ttsclient/models/tts_configuration.py` — TTSConfiguration
- [x] `server/src/ttsclient/models/gpu_device.py` — GPUInfo
- [x] `server/src/ttsclient/models/module.py` — ModuleInfo, ModuleStatus, ModuleDownloadStatus
- [x] `server/src/ttsclient/routers/configuration.py` — GET/PUT
- [x] `server/src/ttsclient/routers/gpu_device.py` — GET
- [x] `server/src/ttsclient/routers/module.py` — GET
- [x] `server/src/ttsclient/services/__init__.py` — 更新
- [x] `server/src/ttsclient/services/configuration_manager.py` — スタブ
- [x] `server/src/ttsclient/services/gpu_device_manager.py` — スタブ
- [x] `server/src/ttsclient/services/module_manager.py` — スタブ

**検証**: Swagger UI で GET/PUT リクエストが正しいスキーマで表示されること

---

## ステップ4: Slot Manager (モデルスロット管理)

**目的**: GPT-SoVITS モデルの CRUD + 操作系 API を実装

**ファイル**:
- [x] `server/src/ttsclient/models/slot.py` — SlotInfo, GPTSoVITSSlotInfo, ModelImportParam 等
- [x] `server/src/ttsclient/routers/slot.py` — 全8エンドポイント
- [x] `server/src/ttsclient/services/slot_manager.py` — スタブ

**エンドポイント**:
- `GET /api/slot-manager/slots` — 全スロット取得
- `GET /api/slot-manager/slots/{index}` — スロット取得
- `POST /api/slot-manager/slots` — モデルインポート
- `PUT /api/slot-manager/slots/{index}` — スロット更新
- `DELETE /api/slot-manager/slots/{index}` — スロット削除
- `POST /api/slot-manager/slots/operation/move_model` — モデル移動
- `POST /api/slot-manager/slots/{index}/operation/set_icon_file` — アイコン設定
- `POST /api/slot-manager/slots/{index}/operation/generate_onnx` — ONNX 生成

**検証**: Swagger UI で全エンドポイントが表示されること

---

## ステップ5: Voice Character Manager (ボイスキャラクター管理)

**目的**: ボイスキャラクターの CRUD + 参照音声管理 API を実装

**ファイル**:
- [x] `server/src/ttsclient/models/voice_character.py` — VoiceCharacter, ReferenceVoice, EmotionType 等
- [x] `server/src/ttsclient/routers/voice_character.py` — 全15エンドポイント
- [x] `server/src/ttsclient/services/voice_character_slot_manager.py` — スタブ

**エンドポイント**:
- `GET /api/voice-character-slot-manager/slots` — 全キャラクター取得
- `GET /api/voice-character-slot-manager/slots/{index}` — キャラクター取得
- `POST /api/voice-character-slot-manager/slots` — キャラクターインポート
- `PUT /api/voice-character-slot-manager/slots/{index}` — キャラクター更新
- `DELETE /api/voice-character-slot-manager/slots/{index}` — キャラクター削除
- `POST /api/voice-character-slot-manager/slots/operation/move_model` — 移動
- `POST /api/voice-character-slot-manager/slots/{index}/operation/set_icon_file` — アイコン設定
- `POST /api/voice-character-slot-manager/slots/{index}/voices` — 参照音声追加
- `PUT /api/voice-character-slot-manager/slots/{index}/voices/{voice_index}` — 参照音声更新
- `DELETE /api/voice-character-slot-manager/slots/{index}/voices/{voice_index}` — 参照音声削除
- `POST /api/voice-character-slot-manager/slots/{index}/voices/operation/move_voice` — 参照音声移動
- `POST /api/voice-character-slot-manager/slots/{index}/voices/operation/zip_and_download` — ZIP 化 DL
- `POST /api/voice-character-slot-manager/slots/{index}/voices/{voice_index}/operation/set_icon_file` — 参照音声アイコン
- `POST /api/voice-character-slot-manager/slots/{index}/voices/operation/add_user_dict_record` — 辞書追加

**検証**: Swagger UI で全エンドポイントが表示されること

---

## ステップ6: TTS Manager + Sample Manager (音声合成・サンプル)

**目的**: 音声生成・音素取得・サンプル管理 API を実装

**ファイル**:
- [x] `server/src/ttsclient/models/tts.py` — GenerateVoiceParam, GetPhonesParam/Response, OpenJTalkUserDictRecord
- [x] `server/src/ttsclient/models/sample.py` — SampleInfo, GPTSoVITSSampleInfo, SampleDownloadParam
- [x] `server/src/ttsclient/routers/tts.py` — 3エンドポイント
- [x] `server/src/ttsclient/routers/sample.py` — 2エンドポイント
- [x] `server/src/ttsclient/services/tts_manager.py` — スタブ
- [x] `server/src/ttsclient/services/sample_manager.py` — スタブ

**エンドポイント (TTS)**:
- `POST /api/tts-manager/operation/generateVoice` — 音声生成 → WAV ストリーム
- `POST /api/tts-manager/operation/getPhones` — 音素取得
- `POST /api/tts-manager/operation/getJpTextToUserDictRecords` — 日本語辞書レコード

**エンドポイント (Sample)**:
- `GET /api/sample-manager/samples` — サンプル一覧
- `POST /api/sample-manager/samples/operation/download` — サンプル DL

**検証**: Swagger UI で全エンドポイントが表示されること

---

## ステップ7: Operation (初期化) + 最終検証

**目的**: システム初期化エンドポイントと全体の動作確認

**ファイル**:
- [ ] `server/src/ttsclient/routers/operation.py` — `POST /api/operation/initialize`
- [ ] `server/src/ttsclient/app.py` — 全ルーター登録の最終確認

**検証**:
- `uv run fastapi dev` で起動
- `/docs` (Swagger UI) で全エンドポイントの型定義が正しいこと
- `/api/hello` でヘルスチェック
- 各 CRUD エンドポイントに Swagger UI からリクエスト送信

---

## ファイル構成 (最終形)

```
server/src/ttsclient/
├── app.py
├── const.py
├── models/
│   ├── __init__.py
│   ├── common.py
│   ├── tts_configuration.py
│   ├── gpu_device.py
│   ├── module.py
│   ├── slot.py
│   ├── voice_character.py
│   ├── tts.py
│   └── sample.py
├── routers/
│   ├── __init__.py
│   ├── hello.py
│   ├── configuration.py
│   ├── gpu_device.py
│   ├── module.py
│   ├── slot.py
│   ├── voice_character.py
│   ├── tts.py
│   ├── sample.py
│   ├── uploader.py
│   ├── operation.py
│   └── proxy.py
├── services/
│   ├── __init__.py
│   ├── configuration_manager.py
│   ├── gpu_device_manager.py
│   ├── module_manager.py
│   ├── slot_manager.py
│   ├── voice_character_slot_manager.py
│   ├── tts_manager.py
│   └── sample_manager.py
└── utils/
    ├── __init__.py
    └── file_uploader.py
```
