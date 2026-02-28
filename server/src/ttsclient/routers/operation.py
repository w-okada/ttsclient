import asyncio
import json
import shutil
from collections.abc import Callable
from threading import Thread

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ttsclient.const import CONFIG_FILE, MODEL_DIR, MODULE_DIR, UPLOAD_DIR, VOICE_CHARACTER_DIR
from ttsclient.models.module import ModuleDownloadStatus
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.services.gpu_device_manager import GPUDeviceManager
from ttsclient.services.module_manager import ModuleManager
from ttsclient.services.sample_manager import SampleManager
from ttsclient.services.slot_manager import SlotManager
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

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
