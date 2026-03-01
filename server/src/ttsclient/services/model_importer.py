import hashlib
import logging
import os
import shutil
from pathlib import Path

from ttsclient.const import SLOT_PARAM_FILE
from ttsclient.models.slot import (
    GPTSoVITSModelImportParam,
    GPTSoVITSSlotInfo,
    ModelImportParamMember,
    ReservedForSampleModelImportParam,
    ReservedForSampleSlotInfo,
    SlotInfoMember,
)

logger = logging.getLogger(__name__)

_HEAD_TO_VERSION: dict[bytes, list] = {
    b"00": ["v1", "v1", False],
    b"01": ["v2", "v2", False],
    b"02": ["v2", "v3", False],
    b"03": ["v2", "v3", True],
    b"04": ["v2", "v4", True],
    b"05": ["v2", "v2Pro", False],
    b"06": ["v2", "v2ProPlus", False],
}

_HASH_PRETRAINED: dict[str, list] = {
    "dc3c97e17592963677a4a1681f30c653": ["v2", "v2", False],
    "6642b37f3dbb1f76882b69937c95a5f3": ["v2", "v2", False],
    "43797be674a37c1c83ee81081941ed0f": ["v2", "v3", False],
    "4f26b9476d0c5033e04162c486074374": ["v2", "v4", False],
    "c7e9fce2223f3db685cdfa1e6368728a": ["v2", "v2Pro", False],
    "66b313e39455b57ab1b0bc0b239c9d0a": ["v2", "v2ProPlus", False],
}


def _get_hash_from_file(path: Path) -> str:
    with open(path, "rb") as f:
        data = f.read(8192)
    return hashlib.md5(data).hexdigest()


def get_sovits_version_from_path_fast(sovits_path: Path) -> tuple[str, str, bool]:
    """SoVITS モデルファイルからバージョン情報を高速検出する。"""
    # 1. pretrained ハッシュで判定
    file_hash = _get_hash_from_file(sovits_path)
    if file_hash in _HASH_PRETRAINED:
        return tuple(_HASH_PRETRAINED[file_hash])  # type: ignore[return-value]

    # 2. ヘッダーバイトで判定
    with open(sovits_path, "rb") as f:
        head = f.read(2)
    if head != b"PK" and head in _HEAD_TO_VERSION:
        return tuple(_HEAD_TO_VERSION[head])  # type: ignore[return-value]

    # 3. ファイルサイズでの判定は廃止（旧形式のモデルは未サポート）
    raise NotImplementedError(
        f"モデルバージョンを検出できません (hash={file_hash}, head={head!r})。"
        "v2Pro/v2ProPlus 以外のモデルはサポートされていません。"
    )


def import_model(model_dir: Path, param: ModelImportParamMember, remove_src: bool = False) -> None:
    """モデルファイルをスロットディレクトリに配置し params.json を書き込む。"""
    assert param.slot_index is not None
    slot_dir = model_dir / str(param.slot_index)
    slot_dir.mkdir(parents=True, exist_ok=True)

    try:
        slot_info: SlotInfoMember
        if param.tts_type == "RESERVED_FOR_SAMPLE":
            assert isinstance(param, ReservedForSampleModelImportParam)
            slot_info = ReservedForSampleSlotInfo(
                slot_index=param.slot_index,
                progress=param.progress,
            )
        elif param.tts_type == "GPT-SoVITS":
            assert isinstance(param, GPTSoVITSModelImportParam)
            assert param.synthesizer_model_path is not None

            version, model_version, _if_lora = get_sovits_version_from_path_fast(param.synthesizer_model_path)
            logger.info("モデルバージョン検出: version=%s, model_version=%s", version, model_version)

            for src in [param.icon_file, param.semantic_predictor_model_path, param.synthesizer_model_path]:
                if src is not None:
                    dst = slot_dir / src.name
                    if len(str(src)) > 80 or len(str(dst)) > 80:
                        raise RuntimeError(f"ファイル名が長すぎます: {src} -> {dst}")
                    shutil.copy(src, dst)
                    if remove_src:
                        src.unlink()

            slot_info = GPTSoVITSSlotInfo(
                version=version,
                model_version=model_version,
                slot_index=param.slot_index,
                name=param.name,
                terms_of_use_url=param.terms_of_use_url,
                icon_file=Path(param.icon_file.name) if param.icon_file is not None else None,
                semantic_predictor_model_path=Path(param.semantic_predictor_model_path.name) if param.semantic_predictor_model_path is not None else None,
                synthesizer_model_path=Path(param.synthesizer_model_path.name) if param.synthesizer_model_path is not None else None,
            )
        else:
            raise RuntimeError(f"不明な tts_type: {param.tts_type}")
    except Exception:
        shutil.rmtree(slot_dir, ignore_errors=True)
        raise

    config_file = slot_dir / SLOT_PARAM_FILE
    config_file.write_text(slot_info.model_dump_json(indent=4), encoding="utf-8")
