from pathlib import Path

from pydantic import BaseModel

from ttsclient.const import LanguageType, TTSType


class ReferenceVoiceImportParam(BaseModel):
    voice_type: str
    wav_file: Path
    slot_index: int | None = None
    icon_file: Path | None = None
    text: str | None = None


class ReferenceVoice(BaseModel):
    voice_type: str
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


class EmotionType(BaseModel):
    name: str
    color: str


class VoiceCharacter(BaseModel):
    tts_type: TTSType | None = None
    slot_index: int = -1
    name: str = ""
    description: str = ""
    credit: str = ""
    terms_of_use_url: str = ""
    icon_file: Path | None = None
    reference_voices: list[ReferenceVoice] = []
    emotion_types: list[EmotionType] = []
    progress: float = 0
