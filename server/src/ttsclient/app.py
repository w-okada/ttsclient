from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
