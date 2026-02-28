from ttsclient.models.tts_configuration import TTSConfiguration


class ConfigurationManager:
    _instance: "ConfigurationManager | None" = None

    def __init__(self) -> None:
        self._configuration = TTSConfiguration()

    @classmethod
    def get_instance(cls) -> "ConfigurationManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> None:
        # TODO: CONFIG_FILE から読み込み
        pass

    def get_tts_configuration(self) -> TTSConfiguration:
        return self._configuration

    def set_tts_configuration(self, configuration: TTSConfiguration) -> None:
        self._configuration = configuration
        # TODO: CONFIG_FILE に保存
