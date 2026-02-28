import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

# GPT-SoVITS サブモジュールのパスを追加（推論エンジンが依存）
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(_PROJECT_ROOT / "third_party" / "GPT-SoVITS" / "GPT_SoVITS"))
sys.path.append(str(_PROJECT_ROOT / "third_party" / "GPT-SoVITS"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ttsclient.const import APP_NAME, VERSION
from ttsclient.routers import (
    configuration,
    gpu_device,
    hello,
    module,
    operation,
    proxy,
    sample,
    slot,
    tts,
    uploader,
    voice_character,
)
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.services.gpu_device_manager import GPUDeviceManager
from ttsclient.services.module_manager import ModuleManager
from ttsclient.services.sample_manager import SampleManager
from ttsclient.services.slot_manager import SlotManager
from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    ConfigurationManager.get_instance().reload()
    GPUDeviceManager.get_instance().reload()
    ModuleManager.get_instance().reload()
    SlotManager.get_instance().reload()
    VoiceCharacterSlotManager.get_instance().reload()
    SampleManager.get_instance().reload()
    yield


app = FastAPI(title=APP_NAME, version=VERSION, lifespan=lifespan)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# ルーター登録
app.include_router(hello.router)
app.include_router(proxy.router)
app.include_router(uploader.router)
app.include_router(configuration.router)
app.include_router(gpu_device.router)
app.include_router(module.router)

app.include_router(slot.router)

app.include_router(voice_character.router)

app.include_router(tts.router)
app.include_router(sample.router)
app.include_router(operation.router)

# web/dist/ が存在する場合のみ静的ファイルを配信
_WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"
if _WEB_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_WEB_DIST, html=True), name="static")
