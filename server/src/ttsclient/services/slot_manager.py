import logging
import shutil
from pathlib import Path

from ttsclient.const import MAX_SLOT_INDEX, MODEL_DIR, SLOT_PARAM_FILE
from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.slot import (
    GPTSoVITSSlotInfo,
    ModelImportParamMember,
    ReservedForSampleModelImportParam,
    ReservedForSampleSlotInfo,
    SlotInfo,
    SlotInfoMember,
)
from ttsclient.services.model_importer import import_model

logger = logging.getLogger(__name__)


def _load_slot_info(model_dir: Path, slot_index: int) -> SlotInfoMember:
    """単一スロットの params.json を読み込む。"""
    json_file = model_dir / str(slot_index) / SLOT_PARAM_FILE
    if not json_file.exists():
        return SlotInfo(tts_type=None, slot_index=slot_index)

    try:
        json_text = json_file.read_text(encoding="utf-8")
        base = SlotInfo.model_validate_json(json_text)
        if base.tts_type == "RESERVED_FOR_SAMPLE":
            return ReservedForSampleSlotInfo.model_validate_json(json_text)
        elif base.tts_type == "GPT-SoVITS":
            return GPTSoVITSSlotInfo.model_validate_json(json_text)
        return base
    except Exception:
        logger.error("スロット %d の読み込みに失敗", slot_index, exc_info=True)
        return SlotInfo(tts_type="BROKEN", slot_index=slot_index)


def _reload_slot_infos(model_dir: Path) -> list[SlotInfoMember]:
    """全スロットを走査して読み込む。"""
    return [_load_slot_info(model_dir, i) for i in range(MAX_SLOT_INDEX)]


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
        self._slots = _reload_slot_infos(MODEL_DIR)
        logger.info("スロット情報を読み込みました: %d 件", len(self._slots))
        return self._slots

    def get_slot_infos(self) -> list[SlotInfoMember]:
        return self._slots

    def get_slot_info(self, index: int) -> SlotInfoMember | None:
        for slot in self._slots:
            if slot.slot_index == index:
                return slot
        return None

    def get_blank_slot_index(self) -> int:
        """空きスロットのインデックスを返す。見つからなければ RuntimeError。"""
        self.reload()
        used = {s.slot_index for s in self._slots if s.tts_type is not None}
        for i in range(MAX_SLOT_INDEX):
            if i not in used:
                return i
        raise RuntimeError("空きスロットがありません")

    def set_new_slot(self, param: ModelImportParamMember, *, remove_src: bool = False) -> None:
        if param.slot_index is None:
            param.slot_index = self.get_blank_slot_index()

        existing = self.get_slot_info(param.slot_index)
        assert existing is not None and existing.tts_type is None, f"スロット {param.slot_index} は既に使用中です"

        logger.info("新規スロット設定: %s", param)
        import_model(MODEL_DIR, param, remove_src)
        self.reload()

    def update_slot_info(self, slot_info: SlotInfoMember) -> None:
        existing = self.get_slot_info(slot_info.slot_index)
        assert existing is not None and existing.tts_type is not None, f"スロット {slot_info.slot_index} は存在しません"

        slot_dir = MODEL_DIR / str(slot_info.slot_index)
        slot_dir.mkdir(parents=True, exist_ok=True)
        config_file = slot_dir / SLOT_PARAM_FILE
        config_file.write_text(slot_info.model_dump_json(indent=4), encoding="utf-8")

        idx = next(i for i, s in enumerate(self._slots) if s.slot_index == slot_info.slot_index)
        self._slots[idx] = slot_info

    def delete_slot(self, slot_index: int) -> None:
        slot_dir = MODEL_DIR / str(slot_index)
        if slot_dir.exists():
            shutil.rmtree(slot_dir)
        self.reload()

    def move_model_slot(self, param: MoveModelParam) -> None:
        assert param.dst < MAX_SLOT_INDEX, f"dst {param.dst} が MAX_SLOT_INDEX {MAX_SLOT_INDEX} を超えています"

        dst_slot = self.get_slot_info(param.dst)
        assert dst_slot is not None and dst_slot.tts_type is None, f"移動先スロット {param.dst} は既に使用中です"
        src_slot = self.get_slot_info(param.src)
        assert src_slot is not None and src_slot.tts_type is not None, f"移動元スロット {param.src} は存在しません"

        src_path = MODEL_DIR / str(param.src)
        dst_path = MODEL_DIR / str(param.dst)
        if src_path.exists():
            shutil.move(src_path, dst_path)

        src_slot.slot_index = param.dst
        config_file = dst_path / SLOT_PARAM_FILE
        config_file.write_text(src_slot.model_dump_json(indent=4), encoding="utf-8")
        self.reload()

    def set_icon_file(self, index: int, param: SetIconParam) -> None:
        slot_info = self.get_slot_info(index)
        assert slot_info is not None and slot_info.tts_type is not None, f"スロット {index} は存在しません"

        icon_dst = MODEL_DIR / str(index) / param.icon_file.name
        logger.info("アイコン移動: %s -> %s", param.icon_file, icon_dst)
        shutil.move(param.icon_file, icon_dst)

        slot_info.icon_file = Path(icon_dst.name)
        self.update_slot_info(slot_info)

    def reserve_slot_for_sample(self, slot_index: int, progress: float = 0.0) -> None:
        """サンプルダウンロード用にスロットを予約する。"""
        existing = self.get_slot_info(slot_index)
        assert existing is not None and existing.tts_type is None, f"スロット {slot_index} は既に使用中です"

        param = ReservedForSampleModelImportParam(
            tts_type="RESERVED_FOR_SAMPLE",
            name="RESERVED_FOR_SAMPLE",
            slot_index=slot_index,
            progress=progress,
        )
        import_model(MODEL_DIR, param)
        self.reload()

    def release_slot_from_reserved_for_sample(self, slot_index: int) -> None:
        """サンプル用に予約していたスロットを解放する。"""
        self.delete_slot(slot_index)

    def generate_onnx(self, index: int) -> None:
        raise NotImplementedError("ONNX 生成は未実装です")
