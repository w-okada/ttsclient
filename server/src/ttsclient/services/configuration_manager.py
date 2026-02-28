import logging

from ttsclient.const import CONFIG_FILE, SETTINGS_DIR
from ttsclient.models.tts_configuration import TTSConfiguration

logger = logging.getLogger(__name__)


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
        if CONFIG_FILE.exists():
            json_text = CONFIG_FILE.read_text(encoding="utf-8")
            self._configuration = TTSConfiguration.model_validate_json(json_text)
            logger.info("設定ファイルを読み込みました: %s", CONFIG_FILE)
        else:
            self._configuration = TTSConfiguration()
            self._save()
            logger.info("デフォルト設定を作成しました: %s", CONFIG_FILE)

    def get_tts_configuration(self) -> TTSConfiguration:
        return self._configuration

    def set_tts_configuration(self, configuration: TTSConfiguration) -> None:
        self._configuration = configuration
        self._save()

    def _save(self) -> None:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(self._configuration.model_dump_json(indent=4), encoding="utf-8")
