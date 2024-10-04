import os

from ttsclient.const import ConfigFile
from ttsclient.tts.data_types.data_types import TTSConfiguration


class ConfigurationManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.reload()

    def reload(self):
        if os.path.exists(ConfigFile):
            self.voice_changer_configuration = TTSConfiguration.model_validate_json(open(ConfigFile, encoding="utf-8").read())
        else:
            self.voice_changer_configuration = TTSConfiguration()
            self.save_tts_configuration()

    def get_tts_configuration(self) -> TTSConfiguration:
        return self.voice_changer_configuration

    def set_tts_configuration(self, conf: TTSConfiguration):
        self.voice_changer_configuration = conf
        self.save_tts_configuration()

    def save_tts_configuration(self):
        open(ConfigFile, "w", encoding="utf-8").write(self.voice_changer_configuration.model_dump_json(indent=4))
