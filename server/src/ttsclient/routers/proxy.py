from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ttsclient.const import MODEL_DIR, VOICE_CHARACTER_DIR

router = APIRouter(prefix="/api/proxy")


@router.get("/get")
async def get_proxy(path: str):
    if path.startswith("/"):
        path = path[1:]

    if path.startswith("models"):
        file_path = MODEL_DIR / Path(path).relative_to("models")
    elif path.startswith("voice_characters"):
        file_path = VOICE_CHARACTER_DIR / Path(path).relative_to("voice_characters")
    else:
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if file_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory, not a file")

    return FileResponse(file_path)
