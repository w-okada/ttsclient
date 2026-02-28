from fastapi import APIRouter

from ttsclient.models.gpu_device import GPUInfo
from ttsclient.services.gpu_device_manager import GPUDeviceManager

router = APIRouter(prefix="/api/gpu-device-manager")


@router.get("/devices", response_model=list[GPUInfo])
async def get_devices(reload: bool = False):
    manager = GPUDeviceManager.get_instance()
    if reload:
        manager.reload()
    return manager.get_gpu_info()
