import logging
from fastapi import APIRouter

from ttsclient.const import LOGGER_NAME
from ttsclient.server.validation_error_logging_route import ValidationErrorLoggingRoute
from ttsclient.tts.configuration_manager.configuration_manager import ConfigurationManager
from ttsclient.tts.data_types.data_types import TTSConfiguration


class RestAPIConfigurationManager:
    def __init__(self):
        self.router = APIRouter()
        self.router.route_class = ValidationErrorLoggingRoute
        self.router.add_api_route("/api/configuration-manager/configuration", self.get_configuration, methods=["GET"])
        self.router.add_api_route("/api/configuration-manager/configuration", self.put_configuration, methods=["PUT"])

        self.router.add_api_route("/api_configuration-manager_configuration", self.get_configuration, methods=["GET"])
        self.router.add_api_route("/api_configuration-manager_configuration", self.put_configuration, methods=["PUT"])
        # self.router.add_api_route("/api/configuration-manager/configuration", self.post_configuration, methods=["POST"])

    def get_configuration(self, reload: bool = False):
        configuration_manager = ConfigurationManager.get_instance()
        if reload:
            configuration_manager.reload()
        return configuration_manager.get_tts_configuration()

    def put_configuration(self, configuration: TTSConfiguration):
        """
        注意: VoiceChangerConfigurationには初期値が設定されているので、フィールドが欠けていても初期値で補われてエラーが出ない。
        　　　フィールドの型が異なる場合はエラーが出る。
        """
        configuration_manager = ConfigurationManager.get_instance()
        logging.getLogger(LOGGER_NAME).info(f"Configuration updated: {configuration}")
        configuration_manager.set_tts_configuration(configuration)
        pass
