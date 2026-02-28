import io

from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.tts import OpenJTalkUserDictRecord
from ttsclient.models.voice_character import (
    ReferenceVoice,
    ReferenceVoiceImportParam,
    VoiceCharacter,
    VoiceCharacterImportParam,
)


class VoiceCharacterSlotManager:
    _instance: "VoiceCharacterSlotManager | None" = None

    def __init__(self) -> None:
        self._slots: list[VoiceCharacter] = []

    @classmethod
    def get_instance(cls) -> "VoiceCharacterSlotManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[VoiceCharacter]:
        # TODO: VOICE_CHARACTER_DIR からスロット情報を読み込み
        self._slots = []
        return self._slots

    def get_slot_infos(self) -> list[VoiceCharacter]:
        return self._slots

    def get_slot_info(self, index: int) -> VoiceCharacter | None:
        for slot in self._slots:
            if slot.slot_index == index:
                return slot
        return None

    def set_new_slot(self, import_param: VoiceCharacterImportParam, *, remove_src: bool = False) -> None:
        # TODO: キャラクター登録
        pass

    def update_slot_info(self, slot_info: VoiceCharacter) -> None:
        # TODO: キャラクター情報の更新・保存
        pass

    def delete_slot(self, index: int) -> None:
        # TODO: キャラクター削除
        pass

    def move_model_slot(self, param: MoveModelParam) -> None:
        # TODO: キャラクター移動
        pass

    def set_icon_file(self, index: int, param: SetIconParam) -> None:
        # TODO: アイコンファイル設定
        pass

    # --- 参照音声管理 ---

    def add_voice_audio(self, index: int, param: ReferenceVoiceImportParam, *, remove_src: bool = False) -> None:
        # TODO: 参照音声追加
        pass

    def update_voice_audio(self, index: int, voice_index: int, voice: ReferenceVoice) -> None:
        # TODO: 参照音声更新
        pass

    def delete_voice_audio(self, index: int, voice_index: int) -> None:
        # TODO: 参照音声削除
        pass

    def move_voice_audio(self, index: int, param: MoveModelParam) -> None:
        # TODO: 参照音声移動
        pass

    def set_voice_icon_file(self, index: int, voice_index: int, param: SetIconParam) -> None:
        # TODO: 参照音声アイコン設定
        pass

    def add_user_dict_record(self, index: int, param: OpenJTalkUserDictRecord) -> None:
        # TODO: ユーザー辞書レコード追加
        pass

    def zip_and_download(self, index: int) -> tuple[str, io.BytesIO]:
        # TODO: ZIP 化ダウンロード
        buffer = io.BytesIO()
        return "voice_character", buffer
