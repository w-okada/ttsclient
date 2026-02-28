from pathlib import Path

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

app = FastAPI(title=APP_NAME, version=VERSION)

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
