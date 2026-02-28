from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.slot import ModelImportParamMember, SlotInfoMember


class SlotManager:
    _instance: "SlotManager | None" = None

    def __init__(self) -> None:
        self._slots: list[SlotInfoMember] = []

    @classmethod
    def get_instance(cls) -> "SlotManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[SlotInfoMember]:
        # TODO: MODEL_DIR からスロット情報を読み込み
        self._slots = []
        return self._slots

    def get_slot_infos(self) -> list[SlotInfoMember]:
        return self._slots

    def get_slot_info(self, index: int) -> SlotInfoMember | None:
        for slot in self._slots:
            if slot.slot_index == index:
                return slot
        return None

    def set_new_slot(self, import_param: ModelImportParamMember, *, remove_src: bool = False) -> None:
        # TODO: モデルファイルの配置とスロット登録
        pass

    def update_slot_info(self, slot_info: SlotInfoMember) -> None:
        # TODO: スロット情報の更新・保存
        pass

    def delete_slot(self, slot_index: int) -> None:
        # TODO: スロット削除
        pass

    def move_model_slot(self, param: MoveModelParam) -> None:
        # TODO: スロット移動
        pass

    def set_icon_file(self, index: int, param: SetIconParam) -> None:
        # TODO: アイコンファイル設定
        pass

    def generate_onnx(self, index: int) -> None:
        # TODO: ONNX モデル生成
        pass
