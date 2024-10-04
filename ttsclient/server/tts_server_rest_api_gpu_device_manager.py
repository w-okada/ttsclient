from fastapi import APIRouter

from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute
from ttsclient.tts.gpu_device_manager.gpu_device_manager import GPUDeviceManager


class RestAPIGPUDeviceManager:
    def __init__(self):
        self.router = APIRouter()
        self.router.route_class = ValidationErrorLoggingRoute
        self.router.add_api_route("/api/gpu-device-manager/devices", self.get_devices, methods=["GET"])

        self.router.add_api_route("/api_gpu-device-manager_devices", self.get_devices, methods=["GET"])

    def get_devices(self, reload: bool = False):
        gpu_device_manager = GPUDeviceManager.get_instance()
        if reload:
            gpu_device_manager.reload()

        if gpu_device_manager.is_cuda_available() is False:
            return gpu_device_manager.get_gpu_info()
        else:
            return gpu_device_manager.get_cuda_info()
