import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from ttsclient.const import UPLOAD_DIR
from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.slot import (
    GPTSoVITSModelImportParam,
    GPTSoVITSSlotInfo,
    ModelImportParam,
    ModelImportParamMember,
    SlotInfo,
    SlotInfoMember,
)
from ttsclient.services.slot_manager import SlotManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/slot-manager")


async def _detect_model(request: Request) -> ModelImportParamMember:
    body = await request.body()
    base = ModelImportParam.model_validate_json(body)
    match base.tts_type:
        case "GPT-SoVITS":
            return GPTSoVITSModelImportParam.model_validate_json(body)
        case _:
            raise HTTPException(status_code=400, detail=f"unknown tts_type: {base.tts_type}")


async def _detect_slot_info(request: Request) -> SlotInfoMember:
    body = await request.body()
    base = SlotInfo.model_validate_json(body)
    match base.tts_type:
        case "GPT-SoVITS":
            return GPTSoVITSSlotInfo.model_validate_json(body)
        case _:
            raise HTTPException(status_code=400, detail=f"unknown tts_type: {base.tts_type}")


@router.get("/slots")
async def get_slots(reload: bool = False):
    manager = SlotManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_slot_infos()


@router.get("/slots/{index}")
async def get_slot(index: int, reload: bool = False):
    manager = SlotManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_slot_info(index)


@router.post("/slots")
async def post_slot(import_param: ModelImportParamMember = Depends(_detect_model)):
    manager = SlotManager.get_instance()
    if isinstance(import_param, GPTSoVITSModelImportParam):
        if import_param.semantic_predictor_model_path is not None:
            import_param.semantic_predictor_model_path = UPLOAD_DIR / import_param.semantic_predictor_model_path
        if import_param.synthesizer_model_path is not None:
            import_param.synthesizer_model_path = UPLOAD_DIR / import_param.synthesizer_model_path
    manager.set_new_slot(import_param, remove_src=True)
    return {"message": "ok"}


@router.put("/slots/{index}")
async def put_slot(index: int, slot_info: SlotInfoMember = Depends(_detect_slot_info)):
    manager = SlotManager.get_instance()
    manager.update_slot_info(slot_info)
    return {"message": "ok"}


@router.delete("/slots/{index}")
async def delete_slot(index: int):
    manager = SlotManager.get_instance()
    manager.delete_slot(index)
    return {"message": "ok"}


@router.post("/slots/operation/move_model")
async def move_model(param: MoveModelParam):
    manager = SlotManager.get_instance()
    manager.move_model_slot(param)
    return {"message": "ok"}


@router.post("/slots/{index}/operation/set_icon_file")
async def set_icon_file(index: int, param: SetIconParam):
    param.icon_file = UPLOAD_DIR / param.icon_file.name
    manager = SlotManager.get_instance()
    manager.set_icon_file(index, param)
    return {"message": "ok"}


@router.post("/slots/{index}/operation/generate_onnx")
async def generate_onnx(index: int):
    manager = SlotManager.get_instance()
    manager.generate_onnx(index)
    return {"message": "ok"}
