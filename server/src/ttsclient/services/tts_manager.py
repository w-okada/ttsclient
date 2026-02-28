import numpy as np

from ttsclient.models.tts import (
    GenerateVoiceParam,
    GetJpTextToUserDictRecordsParam,
    GetPhonesParam,
    OpenJTalkUserDictRecord,
)


class TTSManager:
    _instance: "TTSManager | None" = None

    @classmethod
    def get_instance(cls) -> "TTSManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run(self, param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
        # TODO: 音声合成エンジン呼び出し
        sample_rate = 32000
        audio_data = np.zeros(sample_rate, dtype=np.int16)
        return sample_rate, audio_data

    def get_phones(self, param: GetPhonesParam) -> tuple[list[int], list[str]]:
        # TODO: 音素解析
        return [], []

    def jp_text_to_user_dict_records(self, param: GetJpTextToUserDictRecordsParam) -> list[OpenJTalkUserDictRecord]:
        # TODO: 日本語テキスト → ユーザー辞書レコード変換
        return []
