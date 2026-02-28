from pathlib import Path

from pydantic import BaseModel

from ttsclient.const import BackendMode, GPTSoVITSModelVersion, GPTSoVITSVersion, TTSType

# --- インポートパラメータ ---


class ModelImportParam(BaseModel):
    tts_type: TTSType
    name: str
    terms_of_use_url: str = ""
    slot_index: int | None = None
    icon_file: Path | None = None


class GPTSoVITSModelImportParam(ModelImportParam):
    tts_type: TTSType = "GPT-SoVITS"
    semantic_predictor_model_path: Path | None = None
    synthesizer_model_path: Path | None = None


class ReservedForSampleModelImportParam(ModelImportParam):
    tts_type: TTSType = "RESERVED_FOR_SAMPLE"
    progress: float


ModelImportParamMember = ModelImportParam | GPTSoVITSModelImportParam | ReservedForSampleModelImportParam


# --- スロット情報 ---


class SlotInfo(BaseModel):
    tts_type: TTSType | None = None
    slot_index: int = -1
    name: str = ""
    description: str = ""
    credit: str = ""
    terms_of_use_url: str = ""
    icon_file: Path | None = None


class GPTSoVITSSlotInfo(SlotInfo):
    tts_type: TTSType = "GPT-SoVITS"
    version: GPTSoVITSVersion = "v2"
    model_version: GPTSoVITSModelVersion = "v2"
    if_lora_v3: bool = False
    enable_faster: bool | None = False
    semantic_predictor_model_path: Path | None = None
    synthesizer_model_path: Path | None = None

    # ハイパーパラメータ
    top_k: int = 20
    top_p: float = 1
    temperature: float = 1
    if_freeze: bool = False

    # ONNX バックエンドモード
    backend_mode: BackendMode = "all_torch"
    onnx_vq_model_path: Path | None = None
    onnx_spec_path: Path | None = None
    onnx_latent_path: Path | None = None
    onnx_encoder_path: Path | None = None
    onnx_fsdec_path: Path | None = None
    onnx_ssdec_path: Path | None = None

    # Faster モード専用パラメータ
    batch_size: int = 1
    batch_threshold: float = 0.75
    split_bucket: bool = True
    return_fragment: bool = False
    fragment_interval: float = 0.3
    seed: int = -1
    parallel_infer: bool = True
    repetition_penalty: float = 1.35


class ReservedForSampleSlotInfo(SlotInfo):
    tts_type: TTSType = "RESERVED_FOR_SAMPLE"
    progress: float


SlotInfoMember = SlotInfo | GPTSoVITSSlotInfo | ReservedForSampleSlotInfo
