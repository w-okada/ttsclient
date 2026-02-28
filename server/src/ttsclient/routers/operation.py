import asyncio
import json
import logging
import shutil
from collections.abc import Callable
from pathlib import Path
from threading import Thread

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ttsclient.const import CONFIG_FILE, MODEL_DIR, MODULE_DIR, SLOT_PARAM_FILE, UPLOAD_DIR, VOICE_CHARACTER_DIR
from ttsclient.models.module import ModuleDownloadStatus
from ttsclient.models.slot import GPTSoVITSModelImportParam, GPTSoVITSSlotInfo
from ttsclient.models.voice_character import VoiceCharacterImportParam
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.services.gpu_device_manager import GPUDeviceManager
from ttsclient.services.model_importer import get_sovits_version_from_path_fast
from ttsclient.services.module_manager import ModuleManager
from ttsclient.services.sample_manager import SampleManager
from ttsclient.services.slot_manager import SlotManager
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/operation")


@router.post("/initialize")
async def initialize():
    CONFIG_FILE.unlink(missing_ok=True)

    for dir_path in [MODEL_DIR, VOICE_CHARACTER_DIR, MODULE_DIR, UPLOAD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)

    ConfigurationManager.get_instance().reload()
    GPUDeviceManager.get_instance().reload()
    ModuleManager.get_instance().reload()
    SlotManager.get_instance().reload()
    VoiceCharacterSlotManager.get_instance().reload()
    SampleManager.get_instance().reload()

    return {"message": "initialized."}


async def _sse_download(
    download_fn: Callable[[Callable[[list[ModuleDownloadStatus]], None]], None],
) -> StreamingResponse:
    queue: asyncio.Queue[list[ModuleDownloadStatus] | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def on_progress(statuses: list[ModuleDownloadStatus]) -> None:
        asyncio.run_coroutine_threadsafe(queue.put(statuses), loop)

    def run() -> None:
        try:
            download_fn(on_progress)
        finally:
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    async def event_stream():
        thread = Thread(target=run)
        thread.start()
        try:
            while True:
                statuses = await queue.get()
                if statuses is None:
                    yield "event: done\ndata: {}\n\n"
                    break
                data = json.dumps([s.model_dump() for s in statuses], ensure_ascii=False)
                yield f"event: progress\ndata: {data}\n\n"
        finally:
            thread.join(timeout=5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/download-modules")
async def download_modules():
    manager = ModuleManager.get_instance()
    manager.reload()
    return await _sse_download(manager.download_initial_modules)


@router.get("/download-models")
async def download_models():
    manager = ModuleManager.get_instance()
    return await _sse_download(manager.download_initial_models)


# =============================================================
# 初期モデル登録
# =============================================================


def _setup_pretrained_slot(
    mod_mgr: ModuleManager,
    slot_mgr: SlotManager,
    *,
    name: str,
    gpt_module_id: str,
    sovits_module_id: str,
    icon_module_id: str,
) -> None:
    """Pretrained モデルをシンボリックリンクでスロットに配置する。"""
    gpt_path = mod_mgr.get_module_filepath(gpt_module_id)
    sovits_path = mod_mgr.get_module_filepath(sovits_module_id)
    icon_path = mod_mgr.get_module_filepath(icon_module_id)

    if gpt_path is None or not gpt_path.exists():
        raise FileNotFoundError(f"GPT モデル未ダウンロード: {gpt_module_id}")
    if sovits_path is None or not sovits_path.exists():
        raise FileNotFoundError(f"SoVITS モデル未ダウンロード: {sovits_module_id}")
    if icon_path is None or not icon_path.exists():
        raise FileNotFoundError(f"アイコン未ダウンロード: {icon_module_id}")

    slot_index = slot_mgr.get_blank_slot_index()
    slot_dir = MODEL_DIR / str(slot_index)
    slot_dir.mkdir(parents=True, exist_ok=True)

    # モデルファイルはシンボリックリンク（数百 MB のコピー回避）
    (slot_dir / gpt_path.name).symlink_to(gpt_path.resolve())
    (slot_dir / sovits_path.name).symlink_to(sovits_path.resolve())

    # アイコンはコピー（小さいファイル）
    shutil.copy(icon_path, slot_dir / icon_path.name)

    version, model_version, if_lora_v3 = get_sovits_version_from_path_fast(sovits_path)
    slot_info = GPTSoVITSSlotInfo(
        slot_index=slot_index,
        name=name,
        version=version,
        model_version=model_version,
        if_lora_v3=if_lora_v3,
        semantic_predictor_model_path=Path(gpt_path.name),
        synthesizer_model_path=Path(sovits_path.name),
        icon_file=Path(icon_path.name),
    )
    (slot_dir / SLOT_PARAM_FILE).write_text(slot_info.model_dump_json(indent=4), encoding="utf-8")
    slot_mgr.reload()


def _setup_jvnv_finetuned(slot_mgr: SlotManager) -> None:
    """JVNV fine-tuned モデルをスロットに登録する。"""
    semantic_path = UPLOAD_DIR / "jvnv_f1-e15.ckpt"
    synthesizer_path = UPLOAD_DIR / "jvnv_f1_e8_s480.pth"
    icon_path = UPLOAD_DIR / "F1_finetune.png"

    for path, label in [(semantic_path, "semantic"), (synthesizer_path, "synthesizer"), (icon_path, "icon")]:
        if not path.exists():
            raise FileNotFoundError(f"JVNV fine-tuned {label} 未ダウンロード: {path}")

    slot_mgr.set_new_slot(
        GPTSoVITSModelImportParam(
            name="JVNV-F1 Fine-tuned",
            semantic_predictor_model_path=semantic_path,
            synthesizer_model_path=synthesizer_path,
            icon_file=icon_path,
        ),
        remove_src=True,
    )


def _setup_initial_models() -> dict:
    """ダウンロード済みの初期モデルをスロット/ボイスキャラクターとして登録する。"""
    mod_mgr = ModuleManager.get_instance()
    slot_mgr = SlotManager.get_instance()
    vc_mgr = VoiceCharacterSlotManager.get_instance()

    results: dict[str, list[str]] = {"model_slots": [], "voice_characters": [], "errors": []}

    # Pretrained v3
    try:
        _setup_pretrained_slot(
            mod_mgr,
            slot_mgr,
            name="GPT-SoVITS Pretrained v3",
            gpt_module_id="gpt_model_v3",
            sovits_module_id="sovits_model_v3",
            icon_module_id="GPT-SoVITS_icon_v3",
        )
        results["model_slots"].append("Pretrained v3")
    except Exception as e:
        logger.error("Pretrained v3 スロット作成失敗: %s", e, exc_info=True)
        results["errors"].append(f"Pretrained v3: {e}")

    # Pretrained v4 (GPT は v3 と共有)
    try:
        _setup_pretrained_slot(
            mod_mgr,
            slot_mgr,
            name="GPT-SoVITS Pretrained v4",
            gpt_module_id="gpt_model_v3",
            sovits_module_id="sovits_model_v4",
            icon_module_id="GPT-SoVITS_icon_v4",
        )
        results["model_slots"].append("Pretrained v4")
    except Exception as e:
        logger.error("Pretrained v4 スロット作成失敗: %s", e, exc_info=True)
        results["errors"].append(f"Pretrained v4: {e}")

    # JVNV fine-tuned
    try:
        _setup_jvnv_finetuned(slot_mgr)
        results["model_slots"].append("JVNV-F1 Fine-tuned")
    except Exception as e:
        logger.error("JVNV fine-tuned スロット作成失敗: %s", e, exc_info=True)
        results["errors"].append(f"JVNV fine-tuned: {e}")

    # JVNV ボイスパック
    for zip_name in ["JVNV_F1.zip", "JVNV_F2.zip", "JVNV_M1.zip", "JVNV_M2.zip"]:
        try:
            zip_path = UPLOAD_DIR / zip_name
            if not zip_path.exists():
                logger.warning("ボイスパック未ダウンロード: %s", zip_name)
                continue
            vc_mgr.set_new_slot(
                VoiceCharacterImportParam(
                    tts_type="VoiceCharacter",
                    name="",
                    zip_file=zip_path,
                ),
                remove_src=True,
            )
            results["voice_characters"].append(zip_name)
        except Exception as e:
            logger.error("ボイスパック登録失敗 %s: %s", zip_name, e, exc_info=True)
            results["errors"].append(f"{zip_name}: {e}")

    return results


@router.post("/setup-initial-models")
async def setup_initial_models():
    results = _setup_initial_models()
    return {"message": f"model_slots={results['model_slots']}, voice_characters={results['voice_characters']}, errors={results['errors']}"}
