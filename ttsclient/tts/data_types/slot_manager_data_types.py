from pathlib import Path
from pydantic import BaseModel

from ttsclient.const import BackendMode, BasicVoiceType, LanguageType, TTSType


class ModelImportParam(BaseModel):
    tts_type: TTSType
    name: str
    terms_of_use_url: str = ""
    slot_index: int | None = None
    icon_file: Path | None = None


class GPTSoVITSModelImportParam(ModelImportParam):
    semantic_predictor_model: Path | None = None
    synthesizer_path: Path | None = None


ModelImportParamMember = ModelImportParam | GPTSoVITSModelImportParam


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
    enable_faster: bool | None = False
    semantic_predictor_model: Path | None = None
    synthesizer_path: Path | None = None
    top_k: int = 20
    top_p: float = 1
    temperature: float = 1
    if_freeze: bool = False

    backend_mode: BackendMode = "all_torch"
    onnx_vq_model_path: Path | None = None
    onnx_spec_path: Path | None = None
    onnx_latent_path: Path | None = None
    onnx_encoder_path: Path | None = None
    onnx_fsdec_path: Path | None = None
    onnx_ssdec_path: Path | None = None

    batch_size: int = 1  # only for faster
    batch_threshold: float = 0.75  # only for faster
    split_bucket: bool = True  # only for faster
    return_fragment: bool = False  # only for faster
    fragment_interval: float = 0.3  # only for faster
    seed: int = -1  # only for faster
    parallel_infer: bool = True  # only for faster
    repetition_penalty: float = 1.35  # only for faster


SlotInfoMember = SlotInfo | GPTSoVITSSlotInfo


class ReferenceVoiceImportParam(BaseModel):
    voice_type: BasicVoiceType | str
    wav_file: Path
    slot_index: int | None = None
    icon_file: Path | None = None
    text: str | None = None


class ReferenceVoice(BaseModel):
    voice_type: BasicVoiceType | str
    slot_index: int = -1
    wav_file: Path
    text: str
    language: LanguageType
    icon_file: Path | None = None


class VoiceCharacterImportParam(BaseModel):
    tts_type: TTSType
    name: str
    terms_of_use_url: str = ""
    slot_index: int | None = None
    icon_file: Path | None = None
    zip_file: Path | None = None


class VoiceCharacter(BaseModel):
    tts_type: TTSType | None = None
    slot_index: int = -1
    name: str = ""
    description: str = ""
    credit: str = ""
    terms_of_use_url: str = ""
    icon_file: Path | None = None
    reference_voices: list[ReferenceVoice] = []


class MoveModelParam(BaseModel):
    src: int
    dst: int


class MoveReferenceVoiceParam(BaseModel):
    src: int
    dst: int


class SetIconParam(BaseModel):
    icon_file: Path
