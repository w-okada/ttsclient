from fastapi import APIRouter

from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute
from ttsclient.tts.module_manager.module_manager import ModuleManager


class RestAPIModuleManager:
    def __init__(self):
        self.router = APIRouter()
        self.router.route_class = ValidationErrorLoggingRoute
        self.router.add_api_route("/api/module-manager/modules", self.get_modules, methods=["GET"])

        self.router.add_api_route("/api_module-manager_modules", self.get_modules, methods=["GET"])

    def get_modules(self, reload: bool = False):
        moduele_manager = ModuleManager.get_instance()
        if reload:
            moduele_manager.reload()
        return moduele_manager.get_modules()
