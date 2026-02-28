import logging
import shutil
from pathlib import Path

from ttsclient.const import VOICE_CHARACTER_SLOT_PARAM_FILE
from ttsclient.models.voice_character import VoiceCharacter, VoiceCharacterImportParam

logger = logging.getLogger(__name__)


def import_voice_character(vc_dir: Path, param: VoiceCharacterImportParam, remove_src: bool = False) -> None:
    """ボイスキャラクターをスロットディレクトリにインポートする。"""
    assert param.slot_index is not None
    slot_dir = vc_dir / str(param.slot_index)
    slot_dir.mkdir(parents=True, exist_ok=True)

    try:
        if param.tts_type not in ("GPT-SoVITS", "VoiceCharacter"):
            raise RuntimeError(f"不明な tts_type: {param.tts_type}")

        for src in [param.icon_file, param.zip_file]:
            if src is not None:
                dst = slot_dir / src.name
                if len(str(src)) > 80 or len(str(dst)) > 80:
                    raise RuntimeError(f"ファイル名が長すぎます: {src} -> {dst}")
                shutil.copy(src, dst)
                if remove_src:
                    src.unlink()

        if param.zip_file is not None:
            # ZIP 展開 → 既存の params.json を読み込み
            zip_path = slot_dir / param.zip_file.name
            shutil.unpack_archive(str(zip_path), str(slot_dir))
            zip_path.unlink()
            slot_info = VoiceCharacter.model_validate_json(
                (slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE).read_text(encoding="utf-8")
            )
            slot_info.slot_index = param.slot_index
        else:
            # 新規作成
            slot_info = VoiceCharacter(
                tts_type=param.tts_type,
                slot_index=param.slot_index,
                name=param.name,
                terms_of_use_url=param.terms_of_use_url,
                icon_file=Path(param.icon_file.name) if param.icon_file is not None else None,
            )
    except Exception:
        shutil.rmtree(slot_dir, ignore_errors=True)
        raise

    config_file = slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE
    config_file.write_text(slot_info.model_dump_json(indent=4), encoding="utf-8")
