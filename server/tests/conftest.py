import pytest


@pytest.fixture()
def work_dir(tmp_path, monkeypatch):
    """cwd を tmp_path に変更し、const.py の相対パスが一時ディレクトリを参照するようにする。"""
    monkeypatch.chdir(tmp_path)

    from ttsclient.services.configuration_manager import ConfigurationManager
    from ttsclient.services.gpu_device_manager import GPUDeviceManager
    from ttsclient.services.module_manager import ModuleManager
    from ttsclient.services.sample_manager import SampleManager
    from ttsclient.services.slot_manager import SlotManager
    from ttsclient.services.tts_manager import TTSManager
    from ttsclient.services.tts_queue import TTSQueue
    from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

    ConfigurationManager._instance = None
    GPUDeviceManager._instance = None
    ModuleManager._instance = None
    SlotManager._instance = None
    VoiceCharacterSlotManager._instance = None
    SampleManager._instance = None
    TTSManager._instance = None
    TTSQueue._instance = None

    yield tmp_path

    ConfigurationManager._instance = None
    GPUDeviceManager._instance = None
    ModuleManager._instance = None
    SlotManager._instance = None
    VoiceCharacterSlotManager._instance = None
    SampleManager._instance = None
    TTSManager._instance = None
    TTSQueue._instance = None


@pytest.fixture()
def client(work_dir):
    from fastapi.testclient import TestClient

    from ttsclient.app import app

    return TestClient(app)
