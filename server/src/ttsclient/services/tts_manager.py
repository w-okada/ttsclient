import numpy as np

from ttsclient.models.tts import (
    GenerateVoiceParam,
    GetJpTextToUserDictRecordsParam,
    GetPhonesParam,
    OpenJTalkUserDictRecord,
)


class TTSManager:
    """TTS 推論マネージャー。

    以下のメソッドは PipelineManager / pyopenjtalk 等の推論エンジンに依存するため、
    現時点ではスタブとして実装している。推論エンジン統合時に実装する。

    - run(): PipelineManager 経由で音声合成を実行
    - get_phones(): PipelineManager + pyopenjtalk で音素列を取得
    - jp_text_to_user_dict_records(): pyopenjtalk でテキストを解析しユーザー辞書レコードを生成
    """

    _instance: "TTSManager | None" = None

    @classmethod
    def get_instance(cls) -> "TTSManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run(self, param: GenerateVoiceParam) -> tuple[int, np.ndarray]:
        """音声合成を実行する。(スタブ: PipelineManager 依存)"""
        raise NotImplementedError("PipelineManager 統合後に実装")

    def get_phones(self, param: GetPhonesParam) -> tuple[list[int], list[str]]:
        """テキストから音素列を取得する。(スタブ: PipelineManager + pyopenjtalk 依存)"""
        raise NotImplementedError("PipelineManager + pyopenjtalk 統合後に実装")

    def jp_text_to_user_dict_records(self, param: GetJpTextToUserDictRecordsParam) -> list[OpenJTalkUserDictRecord]:
        """日本語テキストからユーザー辞書レコードを生成する。(スタブ: pyopenjtalk 依存)"""
        raise NotImplementedError("pyopenjtalk 統合後に実装")
