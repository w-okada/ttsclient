from fastapi import APIRouter

from ttsclient.models.module import ModuleStatus
from ttsclient.services.module_manager import ModuleManager

router = APIRouter(prefix="/api/module-manager")


@router.get("/modules", response_model=list[ModuleStatus])
async def get_modules(reload: bool = False):
    manager = ModuleManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_modules()
