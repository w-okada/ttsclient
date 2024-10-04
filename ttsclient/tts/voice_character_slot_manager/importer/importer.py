import logging
from pathlib import Path
import shutil
from typing import cast

from ttsclient.const import LOGGER_NAME, VOICE_CHARACTER_SLOT_PARAM_FILE
from ttsclient.tts.data_types.slot_manager_data_types import VoiceCharacter, VoiceCharacterImportParam


def import_voice_character(vc_dir: Path, voice_character_import_param: VoiceCharacterImportParam, remove_src: bool = False):
    slot_dir = vc_dir / f"{voice_character_import_param.slot_index}"
    slot_dir.mkdir(parents=True, exist_ok=True)
    try:
        if voice_character_import_param.tts_type == "GPT-SoVITS":
            for src in cast(list[Path | None], [voice_character_import_param.icon_file, voice_character_import_param.zip_file]):
                if src is not None:
                    dst = slot_dir / src.name
                    if len(str(src)) > 80 or len(str(dst)) > 80:
                        raise RuntimeError(f"filename is too long: {src} -> {dst}")
                    logging.getLogger(LOGGER_NAME).debug(f"copy {src} to {dst}")
                    shutil.copy(src, dst)
                    if remove_src is True:
                        src.unlink()

            assert voice_character_import_param.slot_index is not None

            if voice_character_import_param.zip_file is not None:
                # unzip
                zipfile = str(slot_dir / voice_character_import_param.zip_file.name)
                shutil.unpack_archive(str(zipfile), str(slot_dir))
                voice_character_import_param.zip_file.unlink
                # paramはすでにあるので、読み込む。
                slot_info = VoiceCharacter.model_validate_json(open(slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE, encoding="utf-8").read())
                slot_info.slot_index = voice_character_import_param.slot_index
            else:
                # generate config file
                slot_info = VoiceCharacter(
                    tts_type=voice_character_import_param.tts_type,
                    slot_index=voice_character_import_param.slot_index,
                    name=voice_character_import_param.name,
                    icon_file=Path(voice_character_import_param.icon_file.name) if voice_character_import_param.icon_file is not None else None,
                )
                slot_info.terms_of_use_url = voice_character_import_param.terms_of_use_url

        else:
            logging.getLogger(LOGGER_NAME).error(f"Unknown tts type: {voice_character_import_param.tts_type}")
            raise RuntimeError(f"Unknown tts type: {voice_character_import_param.tts_type}")
    except RuntimeError as e:
        shutil.rmtree(slot_dir)
        raise e

    config_file = slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(slot_info.model_dump_json(indent=4))
