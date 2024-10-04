import logging
from pathlib import Path
import shutil
from typing import cast

from ttsclient.const import LOGGER_NAME, SLOT_PARAM_FILE
from ttsclient.tts.data_types.slot_manager_data_types import GPTSoVITSModelImportParam, GPTSoVITSSlotInfo, ModelImportParamMember


def import_model(model_dir: Path, model_importer_param: ModelImportParamMember, remove_src: bool = False):
    slot_dir = model_dir / f"{model_importer_param.slot_index}"
    slot_dir.mkdir(parents=True, exist_ok=True)
    try:
        if model_importer_param.tts_type == "GPT-SoVITS":
            assert isinstance(model_importer_param, GPTSoVITSModelImportParam)
            for src in cast(list[Path | None], [model_importer_param.icon_file, model_importer_param.semantic_predictor_model, model_importer_param.synthesizer_path]):
                if src is not None:
                    dst = slot_dir / src.name
                    if len(str(src)) > 80 or len(str(dst)) > 80:
                        raise RuntimeError(f"filename is too long: {src} -> {dst}")
                    logging.getLogger(LOGGER_NAME).debug(f"copy {src} to {dst}")
                    shutil.copy(src, dst)
                    if remove_src is True:
                        src.unlink()

            # generate config file
            assert model_importer_param.slot_index is not None
            slot_info = GPTSoVITSSlotInfo(
                slot_index=model_importer_param.slot_index,
                name=model_importer_param.name,
                icon_file=Path(model_importer_param.icon_file.name) if model_importer_param.icon_file is not None else None,
                semantic_predictor_model=Path(model_importer_param.semantic_predictor_model.name) if model_importer_param.semantic_predictor_model is not None else None,
                synthesizer_path=Path(model_importer_param.synthesizer_path.name) if model_importer_param.synthesizer_path is not None else None,
                # icon_file=Path(slot_dir / model_importer_param.icon_file.name) if model_importer_param.icon_file is not None else None,
                # semantic_predictor_model=Path(slot_dir / model_importer_param.semantic_predictor_model.name) if model_importer_param.semantic_predictor_model is not None else None,
                # synthesizer_path=Path(slot_dir / model_importer_param.synthesizer_path.name) if model_importer_param.synthesizer_path is not None else None,
            )
            slot_info.terms_of_use_url = model_importer_param.terms_of_use_url

        else:
            logging.getLogger(LOGGER_NAME).error(f"Unknown tts type: {model_importer_param.tts_type}")
            raise RuntimeError(f"Unknown tts type: {model_importer_param.tts_type}")
    except RuntimeError as e:
        shutil.rmtree(slot_dir)
        raise e

    config_file = slot_dir / SLOT_PARAM_FILE
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(slot_info.model_dump_json(indent=4))
