from pydantic import BaseModel

from ttsclient.const import TranscriberComputeType, TranscriberDevice, TranscriberModelSize


class TTSConfiguration(BaseModel):
    current_slot_index: int = -1
    gpu_device_id_int: int = -1
    transcribe_audio: bool = True
    transcriber_model_size: TranscriberModelSize = "small"
    transcriber_device: TranscriberDevice = "cpu"
    transcriber_compute_type: TranscriberComputeType = "int8"
