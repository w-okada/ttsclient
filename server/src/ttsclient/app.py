from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ttsclient.const import APP_NAME, VERSION

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


# ルーター登録 (各ステップで追加していく)
# from ttsclient.routers import hello, proxy, uploader
# from ttsclient.routers import configuration, gpu_device, module
# from ttsclient.routers import slot
# from ttsclient.routers import voice_character
# from ttsclient.routers import tts, sample
# from ttsclient.routers import operation
