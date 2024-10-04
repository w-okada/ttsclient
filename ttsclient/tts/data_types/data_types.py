from pathlib import Path
from pydantic import BaseModel


class TTSConfiguration(BaseModel):
    current_slot_index: int = -1
    gpu_device_id_int: int = -1


class GPUInfo(BaseModel):
    name: str = ""
    device_id: str = ""
    adapter_ram: int = 0
    device_id_int: int = 0
    cuda_compute_version_major: int = -1
    cuda_compute_version_minor: int = -1


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
