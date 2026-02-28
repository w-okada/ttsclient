from pydantic import BaseModel, ConfigDict

from ttsclient.const import DownloadState, TTSType


class SampleDownloadParam(BaseModel):
    slot_index: int
    sample_id: str


class SampleDownloadStatus(BaseModel):
    id: str
    status: DownloadState
    progress: float
    error_message: str | None = None


class SampleInfo(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    tts_type: TTSType
    lang: str
    tag: list[str]
    name: str
    terms_of_use_url: str
    icon_url: str | None
    credit: str
    description: str


class GPTSoVITSSampleInfo(SampleInfo):
    semantic_predictor_model_url: str | None = None
    synthesizer_model_url: str | None = None
    version: str
    model_version: str
    lora_v3: bool


class VoiceCharacterSampleInfo(SampleInfo):
    zip_url: str


SampleInfoMember = SampleInfo | GPTSoVITSSampleInfo | VoiceCharacterSampleInfo
