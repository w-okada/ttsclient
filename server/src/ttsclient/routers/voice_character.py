from fastapi import APIRouter, Response

from ttsclient.const import UPLOAD_DIR
from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.tts import OpenJTalkUserDictRecord
from ttsclient.models.voice_character import (
    ReferenceVoice,
    ReferenceVoiceImportParam,
    VoiceCharacter,
    VoiceCharacterImportParam,
)
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

router = APIRouter(prefix="/api/voice-character-slot-manager")


# --- キャラクター CRUD ---


@router.get("/slots", response_model=list[VoiceCharacter])
async def get_slots(reload: bool = False):
    manager = VoiceCharacterSlotManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_slot_infos()


@router.get("/slots/{index}", response_model=VoiceCharacter | None)
async def get_slot(index: int, reload: bool = False):
    manager = VoiceCharacterSlotManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_slot_info(index)


@router.post("/slots")
async def post_slot(import_param: VoiceCharacterImportParam):
    manager = VoiceCharacterSlotManager.get_instance()
    if import_param.zip_file is not None:
        import_param.zip_file = UPLOAD_DIR / import_param.zip_file
    manager.set_new_slot(import_param, remove_src=True)
    return {"message": "ok"}


@router.put("/slots/{index}")
async def put_slot(index: int, slot_info: VoiceCharacter):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.update_slot_info(slot_info)
    return {"message": "ok"}


@router.delete("/slots/{index}")
async def delete_slot(index: int):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.delete_slot(index)
    return {"message": "ok"}


@router.post("/slots/operation/move_model")
async def move_model(param: MoveModelParam):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.move_model_slot(param)
    return {"message": "ok"}


@router.post("/slots/{index}/operation/set_icon_file")
async def set_icon_file(index: int, param: SetIconParam):
    param.icon_file = UPLOAD_DIR / param.icon_file.name
    manager = VoiceCharacterSlotManager.get_instance()
    manager.set_icon_file(index, param)
    return {"message": "ok"}


# --- 参照音声管理 ---


@router.post("/slots/{index}/voices")
async def post_voice(index: int, param: ReferenceVoiceImportParam):
    manager = VoiceCharacterSlotManager.get_instance()
    param.wav_file = UPLOAD_DIR / param.wav_file.name
    if param.icon_file is not None:
        param.icon_file = UPLOAD_DIR / param.icon_file.name
    manager.add_voice_audio(index, param, remove_src=True)
    return {"message": "ok"}


@router.put("/slots/{index}/voices/{voice_index}")
async def put_voice(index: int, voice_index: int, voice: ReferenceVoice):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.update_voice_audio(index, voice_index, voice)
    return {"message": "ok"}


@router.delete("/slots/{index}/voices/{voice_index}")
async def delete_voice(index: int, voice_index: int):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.delete_voice_audio(index, voice_index)
    return {"message": "ok"}


@router.post("/slots/{index}/voices/operation/move_voice")
async def move_voice(index: int, param: MoveModelParam):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.move_voice_audio(index, param)
    return {"message": "ok"}


@router.post("/slots/{index}/voices/operation/zip_and_download")
async def zip_and_download(index: int):
    manager = VoiceCharacterSlotManager.get_instance()
    _name, buffer = manager.zip_and_download(index)
    file_content = buffer.read()
    headers = {"Content-Disposition": "attachment; filename=vc.zip"}
    return Response(content=file_content, media_type="application/zip", headers=headers)


@router.post("/slots/{index}/voices/{voice_index}/operation/set_icon_file")
async def set_voice_icon_file(index: int, voice_index: int, param: SetIconParam):
    param.icon_file = UPLOAD_DIR / param.icon_file.name
    manager = VoiceCharacterSlotManager.get_instance()
    manager.set_voice_icon_file(index, voice_index, param)
    return {"message": "ok"}


@router.post("/slots/{index}/voices/operation/add_user_dict_record")
async def add_user_dict_record(index: int, param: OpenJTalkUserDictRecord):
    manager = VoiceCharacterSlotManager.get_instance()
    manager.add_user_dict_record(index, param)
    return {"message": "ok"}
