from pathlib import Path

from pydantic import BaseModel

from ttsclient.const import DownloadState


class ModuleInfo(BaseModel):
    id: str
    display_name: str
    url: str
    save_to: Path
    hash: str


class ModuleStatus(BaseModel):
    info: ModuleInfo
    downloaded: bool
    valid: bool


class ModuleDownloadStatus(BaseModel):
    id: str
    status: DownloadState
    progress: float
    error_message: str | None = None
