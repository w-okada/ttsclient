import logging
import os
from pathlib import Path
import shutil
from ttsclient.const import LOGGER_NAME, MAX_SLOT_INDEX, SLOT_PARAM_FILE, ModelDir
from ttsclient.tts.data_types.slot_manager_data_types import GPTSoVITSSlotInfo, ModelImportParamMember, MoveModelParam, SetIconParam, SlotInfo, SlotInfoMember
from ttsclient.tts.slot_manager.model_importer.model_importer import import_model
from ttsclient.tts.tts_manager.semantic_predictor.gpt_semantic_predictor import GPTSemanticPredictor
from ttsclient.tts.tts_manager.synthesizer.sovits_synthesizer import SovitsSynthesizer


def load_slot_info(model_dir: Path, slot_index: int) -> SlotInfoMember:
    slot_dir = model_dir / str(slot_index)
    json_file = slot_dir / SLOT_PARAM_FILE
    if not os.path.exists(json_file):
        # return None
        blank = SlotInfo()
        blank.tts_type = None
        blank.slot_index = slot_index
        return blank

    try:
        tmp_slot_info = SlotInfo.model_validate_json(open(json_file, encoding="utf-8").read())
        logging.getLogger(LOGGER_NAME).debug(tmp_slot_info)
        if tmp_slot_info.tts_type == "GPT-SoVITS":
            slot_info: SlotInfoMember = GPTSoVITSSlotInfo.model_validate_json(open(json_file, encoding="utf-8").read())

        return slot_info
    except Exception as e:
        logging.getLogger(LOGGER_NAME).error(f"Error in loading slot info: {e}")
        broken = SlotInfo()
        broken.tts_type = "BROKEN"
        broken.slot_index = slot_index
        return broken


def reload_slot_infos(model_dir: Path) -> list[SlotInfoMember]:
    slot_infos = []
    for i in range(MAX_SLOT_INDEX):
        slot_info = load_slot_info(model_dir, i)
        slot_infos.append(slot_info)

    return slot_infos


class SlotManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.reload()

    def reload(self, use_log=True) -> list[SlotInfoMember]:
        logging.getLogger(LOGGER_NAME).debug("Reloading Slot info")
        self.slot_infos = reload_slot_infos(ModelDir)
        return self.slot_infos

    def get_slot_infos(self) -> list[SlotInfoMember]:
        return self.slot_infos

    def get_slot_info(self, index: int):
        slot_info_array = [slot_info for slot_info in self.get_slot_infos() if slot_info.slot_index == index]
        if len(slot_info_array) == 0:
            raise RuntimeError(f"slot_index:{index} is not found.")
        return slot_info_array[0]

    def get_blank_slot_index(self) -> int:
        self.reload(use_log=False)
        exist_slot_index = {slot_info.slot_index for slot_info in self.slot_infos if slot_info.tts_type is not None}
        next_index = next((i for i in range(MAX_SLOT_INDEX) if i not in exist_slot_index), -1)
        if next_index == -1:
            raise RuntimeError("No blank slot index")
        return next_index

    def set_new_slot(self, model_import_param: ModelImportParamMember, remove_src: bool = False):
        if model_import_param.slot_index is None:
            model_import_param.slot_index = self.get_blank_slot_index()

        assert self.get_slot_info(model_import_param.slot_index).tts_type is None, f"slot_index:{model_import_param.slot_index} is already exists."

        logging.getLogger(LOGGER_NAME).info(f"set new slot: {model_import_param}")
        import_model(ModelDir, model_import_param, remove_src)
        self.reload()

    def delete_slot(self, slot_index: int):
        slot_dir = ModelDir / str(slot_index)
        if os.path.exists(slot_dir):
            shutil.rmtree(slot_dir)
        self.reload(use_log=False)

    def update_slot_info(self, slot_info: SlotInfoMember):
        org_slot_info = self.get_slot_info(slot_info.slot_index)
        logging.getLogger(LOGGER_NAME).debug(f"updating slot info: org => {org_slot_info}")
        assert org_slot_info.tts_type is not None, f"src:{slot_info.slot_index} is not exist."
        logging.getLogger(LOGGER_NAME).debug(f"updating slot info: new => {slot_info}")
        slot_dir = ModelDir / f"{slot_info.slot_index}"
        slot_dir.mkdir(parents=True, exist_ok=True)
        config_file = slot_dir / SLOT_PARAM_FILE

        with open(config_file, "w", encoding="utf-8") as f:
            f.write(slot_info.model_dump_json(indent=4))

        index_in_slot_info = [i for i, s in enumerate(self.get_slot_infos()) if s.slot_index == org_slot_info.slot_index]
        assert len(index_in_slot_info) == 1
        self.slot_infos[index_in_slot_info[0]] = slot_info

    def set_icon_file(self, index: int, param: SetIconParam):
        icon_dst_path = ModelDir / f"{index}" / param.icon_file.name
        logging.getLogger(LOGGER_NAME).info(f"set new icon, moving from up folder {param.icon_file} -> {icon_dst_path}")
        shutil.move(param.icon_file, icon_dst_path)
        slot_info = self.get_slot_info(index)
        assert slot_info is not None, f"slot_index:{index} is not exists."
        slot_info.icon_file = Path(icon_dst_path.name)
        logging.getLogger(LOGGER_NAME).info(f"set new icon, new slot info {slot_info}")
        self.update_slot_info(slot_info)

    def move_model_slot(self, param: MoveModelParam):
        assert param.dst <= MAX_SLOT_INDEX, f"dst:{param.dst} is over MAX_SLOT_INDEX:{MAX_SLOT_INDEX}"
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot src: {self.get_slot_info(param.src)}")
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot src: {self.get_slot_info(param.src).voice_changer_type}")
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot src: {self.get_slot_info(param.src).voice_changer_type is not None}")
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot dst: {self.get_slot_info(param.dst)}")
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot dst: {self.get_slot_info(param.dst).voice_changer_type}")
        # logging.getLogger(LOGGER_NAME).info(f"move_model_slot dst: {self.get_slot_info(param.dst).voice_changer_type is None}")

        assert self.get_slot_info(param.dst).tts_type is None, f"dst:{param.dst} is already exists."
        assert self.get_slot_info(param.src).tts_type is not None, f"src:{param.src} is not exist."

        slot_info = self.get_slot_info(param.src)
        slot_info.slot_index = param.dst

        src_path = ModelDir / str(param.src)
        dst_path = ModelDir / str(param.dst)
        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)

        # self._validate_slot_index(param.dst)

        slot_dir = ModelDir / f"{param.dst}"
        config_file = slot_dir / SLOT_PARAM_FILE
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(slot_info.model_dump_json(indent=4))
        self.reload(use_log=False)

    def generate_onnx(self, index: int):
        slot_info = self.get_slot_info(index)
        if slot_info.tts_type == "GPT-SoVITS":
            print(f"generating sysnthesizer onnx: slot:{slot_info.slot_index}")
            assert isinstance(slot_info, GPTSoVITSSlotInfo)
            assert slot_info.synthesizer_path is not None
            synthesizer_path = ModelDir / f"{slot_info.slot_index}" / slot_info.synthesizer_path
            (onnx_vq_model_path, onnx_spec_path, onnx_latent_path) = SovitsSynthesizer.generate_onnx(synthesizer_path)
            print(f"onnx_vq_model_path: {onnx_vq_model_path}")
            print(f"onnx_spec_path: {onnx_spec_path}")
            print(f"onnx_latent_path: {onnx_latent_path}")

            assert slot_info.semantic_predictor_model is not None
            semantic_predictor_model = ModelDir / f"{slot_info.slot_index}" / slot_info.semantic_predictor_model
            (onnx_encoder_path, onnx_fsdec_path, onnx_ssdec_path) = GPTSemanticPredictor.generate_onnx(semantic_predictor_model)
            print(f"onnx_encoder_path: {onnx_encoder_path}")
            print(f"onnx_fsdec_path: {onnx_fsdec_path}")
            print(f"onnx_ssdec_path: {onnx_ssdec_path}")

            slot_info.onnx_vq_model_path = onnx_vq_model_path.name
            slot_info.onnx_spec_path = onnx_spec_path.name
            slot_info.onnx_latent_path = onnx_latent_path.name
            slot_info.onnx_encoder_path = onnx_encoder_path.name
            slot_info.onnx_fsdec_path = onnx_fsdec_path.name
            slot_info.onnx_ssdec_path = onnx_ssdec_path.name

            self.update_slot_info(slot_info)
