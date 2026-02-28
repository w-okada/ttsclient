import shutil

from fastapi import APIRouter

from ttsclient.const import CONFIG_FILE, MODEL_DIR, MODULE_DIR, UPLOAD_DIR, VOICE_CHARACTER_DIR
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.services.gpu_device_manager import GPUDeviceManager
from ttsclient.services.module_manager import ModuleManager
from ttsclient.services.sample_manager import SampleManager
from ttsclient.services.slot_manager import SlotManager
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

router = APIRouter(prefix="/api/operation")


@router.post("/initialize")
async def initialize():
    CONFIG_FILE.unlink(missing_ok=True)

    for dir_path in [MODEL_DIR, VOICE_CHARACTER_DIR, MODULE_DIR, UPLOAD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)

    ConfigurationManager.get_instance().reload()
    GPUDeviceManager.get_instance().reload()
    ModuleManager.get_instance().reload()
    SlotManager.get_instance().reload()
    VoiceCharacterSlotManager.get_instance().reload()
    SampleManager.get_instance().reload()

    return {"message": "initialized."}
