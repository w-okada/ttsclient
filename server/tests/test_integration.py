"""統合検証テスト: 初期化 → 各マネージャー操作 → エンドツーエンドフロー"""

import wave as wave_mod
from pathlib import Path


def _create_dummy_wav(path: Path, duration_sec: float = 3.0, sample_rate: int = 16000) -> None:
    """テスト用のダミー WAV ファイルを作成する。"""
    n_samples = int(sample_rate * duration_sec)
    with wave_mod.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_samples)


def _create_dummy_sovits(path: Path) -> None:
    """v2 ヘッダーを持つダミー SoVITS モデルファイルを作成する。"""
    path.write_bytes(b"01" + b"\x00" * 100)


# ============================================================
# 初期化
# ============================================================


class TestInitialize:
    def test_creates_directories(self, client, work_dir):
        resp = client.post("/api/operation/initialize")
        assert resp.status_code == 200
        assert resp.json() == {"message": "initialized."}

        assert (work_dir / "models").is_dir()
        assert (work_dir / "voice_characters").is_dir()
        assert (work_dir / "modules").is_dir()
        assert (work_dir / "upload_dir").is_dir()

    def test_creates_default_config(self, client, work_dir):
        client.post("/api/operation/initialize")
        assert (work_dir / "settings" / "tts_conf.json").exists()

    def test_idempotent(self, client):
        resp1 = client.post("/api/operation/initialize")
        resp2 = client.post("/api/operation/initialize")
        assert resp1.status_code == 200
        assert resp2.status_code == 200


# ============================================================
# ConfigurationManager
# ============================================================


class TestConfiguration:
    def test_get_default(self, client):
        client.post("/api/operation/initialize")
        resp = client.get("/api/configuration-manager/configuration")
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_slot_index"] == -1
        assert data["current_vc_index"] == -1
        assert data["gpu_device_id_int"] == -1

    def test_put_and_persist(self, client):
        client.post("/api/operation/initialize")
        new_config = {
            "current_slot_index": 3,
            "current_vc_index": 5,
            "gpu_device_id_int": 0,
            "transcribe_audio": False,
            "transcriber_model_size": "base",
            "transcriber_device": "cpu",
            "transcriber_compute_type": "float32",
        }
        resp = client.put("/api/configuration-manager/configuration", json=new_config)
        assert resp.status_code == 200
        assert resp.json()["current_slot_index"] == 3
        assert resp.json()["current_vc_index"] == 5
        assert resp.json()["transcribe_audio"] is False

        # reload して永続化を確認
        resp2 = client.get("/api/configuration-manager/configuration", params={"reload": True})
        assert resp2.json()["current_slot_index"] == 3
        assert resp2.json()["current_vc_index"] == 5


# ============================================================
# GPUDeviceManager
# ============================================================


class TestGPUDevices:
    def test_cpu_always_present(self, client):
        client.post("/api/operation/initialize")
        resp = client.get("/api/gpu-device-manager/devices")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["name"] == "cpu"
        assert data[0]["device_id_int"] == -1


# ============================================================
# ModuleManager
# ============================================================


class TestModules:
    def test_all_modules_not_downloaded(self, client):
        client.post("/api/operation/initialize")
        resp = client.get("/api/module-manager/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        for mod in data:
            assert mod["downloaded"] is False


# ============================================================
# SlotManager
# ============================================================


class TestSlots:
    def test_initial_slots_empty(self, client):
        client.post("/api/operation/initialize")
        resp = client.get("/api/slot-manager/slots")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 20
        assert all(s["tts_type"] is None for s in data)

    def test_import_get_update_move_delete(self, client, work_dir):
        client.post("/api/operation/initialize")
        upload_dir = work_dir / "upload_dir"

        # ダミーモデル配置
        (upload_dir / "gpt.ckpt").write_bytes(b"dummy gpt model")
        _create_dummy_sovits(upload_dir / "sovits.pth")

        # POST: インポート
        resp = client.post(
            "/api/slot-manager/slots",
            content=GPT_SOVITS_IMPORT_JSON.format(slot=0, name="テストモデル", gpt="gpt.ckpt", sovits="sovits.pth"),
        )
        assert resp.status_code == 200

        # GET: 確認
        resp = client.get("/api/slot-manager/slots/0")
        data = resp.json()
        assert data["tts_type"] == "GPT-SoVITS"
        assert data["name"] == "テストモデル"
        assert data["version"] == "v2"
        assert data["model_version"] == "v2"

        # PUT: 更新
        data["name"] = "更新モデル"
        resp = client.put("/api/slot-manager/slots/0", content=_json_dumps(data))
        assert resp.status_code == 200

        resp = client.get("/api/slot-manager/slots/0")
        assert resp.json()["name"] == "更新モデル"

        # MOVE: 0 → 5
        resp = client.post("/api/slot-manager/slots/operation/move_model", json={"src": 0, "dst": 5})
        assert resp.status_code == 200

        assert client.get("/api/slot-manager/slots/5").json()["name"] == "更新モデル"
        assert client.get("/api/slot-manager/slots/0").json()["tts_type"] is None

        # DELETE
        resp = client.delete("/api/slot-manager/slots/5")
        assert resp.status_code == 200
        assert client.get("/api/slot-manager/slots/5").json()["tts_type"] is None


# ============================================================
# VoiceCharacterSlotManager
# ============================================================


class TestVoiceCharacter:
    def test_crud(self, client):
        client.post("/api/operation/initialize")

        # POST
        resp = client.post(
            "/api/voice-character-slot-manager/slots",
            json={"tts_type": "VoiceCharacter", "name": "テストキャラ", "slot_index": 0},
        )
        assert resp.status_code == 200

        # GET
        data = client.get("/api/voice-character-slot-manager/slots/0").json()
        assert data["tts_type"] == "VoiceCharacter"
        assert data["name"] == "テストキャラ"
        assert data["reference_voices"] == []

        # PUT
        data["name"] = "更新キャラ"
        data["description"] = "テスト説明"
        resp = client.put("/api/voice-character-slot-manager/slots/0", json=data)
        assert resp.status_code == 200
        assert client.get("/api/voice-character-slot-manager/slots/0").json()["name"] == "更新キャラ"

        # MOVE: 0 → 3
        resp = client.post(
            "/api/voice-character-slot-manager/slots/operation/move_model",
            json={"src": 0, "dst": 3},
        )
        assert resp.status_code == 200
        assert client.get("/api/voice-character-slot-manager/slots/3").json()["name"] == "更新キャラ"
        assert client.get("/api/voice-character-slot-manager/slots/0").json()["tts_type"] is None

        # DELETE
        resp = client.delete("/api/voice-character-slot-manager/slots/3")
        assert resp.status_code == 200
        assert client.get("/api/voice-character-slot-manager/slots/3").json()["tts_type"] is None

    def test_reference_voice(self, client, work_dir):
        client.post("/api/operation/initialize")
        client.post(
            "/api/voice-character-slot-manager/slots",
            json={"tts_type": "VoiceCharacter", "name": "テストキャラ", "slot_index": 0},
        )

        # ダミー WAV 配置
        upload_dir = work_dir / "upload_dir"
        _create_dummy_wav(upload_dir / "test.wav")

        # ADD voice
        resp = client.post(
            "/api/voice-character-slot-manager/slots/0/voices",
            json={"voice_type": "reference", "wav_file": "test.wav", "text": "テストテキスト", "slot_index": 0},
        )
        assert resp.status_code == 200

        data = client.get("/api/voice-character-slot-manager/slots/0").json()
        assert len(data["reference_voices"]) == 1
        assert data["reference_voices"][0]["text"] == "テストテキスト"

        # UPDATE voice
        voice = data["reference_voices"][0]
        voice["text"] = "更新テキスト"
        resp = client.put("/api/voice-character-slot-manager/slots/0/voices/0", json=voice)
        assert resp.status_code == 200

        data = client.get("/api/voice-character-slot-manager/slots/0").json()
        assert data["reference_voices"][0]["text"] == "更新テキスト"

        # DELETE voice
        resp = client.delete("/api/voice-character-slot-manager/slots/0/voices/0")
        assert resp.status_code == 200

        data = client.get("/api/voice-character-slot-manager/slots/0").json()
        assert data["reference_voices"] == []

    def test_user_dict_record(self, client, work_dir):
        client.post("/api/operation/initialize")
        client.post(
            "/api/voice-character-slot-manager/slots",
            json={"tts_type": "VoiceCharacter", "name": "テストキャラ", "slot_index": 0},
        )

        resp = client.post(
            "/api/voice-character-slot-manager/slots/0/voices/operation/add_user_dict_record",
            json={
                "string": "テスト",
                "pos": "名詞",
                "pos_group1": "一般",
                "pos_group2": "*",
                "pos_group3": "*",
                "ctype": "*",
                "cform": "*",
                "orig": "テスト",
                "read": "テスト",
                "pron": "テスト",
                "acc": 0,
                "mora_size": 3,
                "chain_rule": "*",
                "chain_flag": 0,
            },
        )
        assert resp.status_code == 200

        csv_file = work_dir / "voice_characters" / "0" / "user_dict.csv"
        assert csv_file.exists()
        assert "テスト" in csv_file.read_text(encoding="utf-8")


# ============================================================
# SampleManager
# ============================================================


class TestSamples:
    def test_get_samples(self, client):
        client.post("/api/operation/initialize")
        resp = client.get("/api/sample-manager/samples")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        ids = {s["id"] for s in data}
        assert "Zundamon_official_v2" in ids
        assert "VC_Zundamon_official" in ids


# ============================================================
# エンドツーエンド
# ============================================================


class TestEndToEnd:
    def test_full_flow(self, client, work_dir):
        """初期化 → モジュール確認 → モデルインポート → キャラ登録 → 参照音声追加 → 設定変更"""
        # 1. 初期化
        resp = client.post("/api/operation/initialize")
        assert resp.status_code == 200

        # 2. モジュール確認
        modules = client.get("/api/module-manager/modules").json()
        assert len(modules) > 0

        # 3. GPU デバイス確認
        devices = client.get("/api/gpu-device-manager/devices").json()
        assert devices[0]["name"] == "cpu"

        # 4. モデルインポート
        upload_dir = work_dir / "upload_dir"
        (upload_dir / "gpt.ckpt").write_bytes(b"gpt model data")
        _create_dummy_sovits(upload_dir / "sovits.pth")

        resp = client.post(
            "/api/slot-manager/slots",
            content=GPT_SOVITS_IMPORT_JSON.format(slot=0, name="E2E モデル", gpt="gpt.ckpt", sovits="sovits.pth"),
        )
        assert resp.status_code == 200

        slot = client.get("/api/slot-manager/slots/0").json()
        assert slot["tts_type"] == "GPT-SoVITS"

        # 5. ボイスキャラクター登録
        resp = client.post(
            "/api/voice-character-slot-manager/slots",
            json={"tts_type": "VoiceCharacter", "name": "E2E キャラ", "slot_index": 0},
        )
        assert resp.status_code == 200

        # 6. 参照音声追加
        _create_dummy_wav(upload_dir / "ref.wav")

        resp = client.post(
            "/api/voice-character-slot-manager/slots/0/voices",
            json={"voice_type": "reference", "wav_file": "ref.wav", "text": "こんにちは"},
        )
        assert resp.status_code == 200

        vc = client.get("/api/voice-character-slot-manager/slots/0").json()
        assert len(vc["reference_voices"]) == 1

        # 7. 設定変更
        resp = client.put(
            "/api/configuration-manager/configuration",
            json={
                "current_slot_index": 0,
                "current_vc_index": 0,
                "gpu_device_id_int": -1,
                "transcribe_audio": False,
                "transcriber_model_size": "small",
                "transcriber_device": "cpu",
                "transcriber_compute_type": "int8",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["current_slot_index"] == 0
        assert resp.json()["current_vc_index"] == 0

        # 8. サンプル一覧確認
        samples = client.get("/api/sample-manager/samples").json()
        assert len(samples) == 2

        # 9. 最終状態検証
        slots = client.get("/api/slot-manager/slots").json()
        used_slots = [s for s in slots if s["tts_type"] is not None]
        assert len(used_slots) == 1

        vcs = client.get("/api/voice-character-slot-manager/slots").json()
        used_vcs = [v for v in vcs if v["tts_type"] is not None]
        assert len(used_vcs) == 1
        assert len(used_vcs[0]["reference_voices"]) == 1

        config = client.get("/api/configuration-manager/configuration").json()
        assert config["current_slot_index"] == 0
        assert config["current_vc_index"] == 0


# ============================================================
# ヘルパー
# ============================================================

# slot ルーターは Depends(_detect_model) で Request.body() を直接読むため、
# json= ではなく content= で送る必要がある
GPT_SOVITS_IMPORT_JSON = (
    '{{"tts_type":"GPT-SoVITS","name":"{name}","slot_index":{slot},'
    '"semantic_predictor_model_path":"{gpt}","synthesizer_model_path":"{sovits}"}}'
)


def _json_dumps(data: dict) -> str:
    import json

    return json.dumps(data, ensure_ascii=False)
