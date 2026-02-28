from fastapi import APIRouter

router = APIRouter()


@router.get("/api/hello")
async def hello():
    return {
        "message": "Hello World! TTSClient gives a cute voice to you!",
        "credit": "w-okada",
        "repository": "https://github.com/w-okada/voice-changer",
    }
