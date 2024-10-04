from pydantic import BaseModel

from ttsclient.const import CutMethod, LanguageType


class GenerateVoiceParam(BaseModel):
    voice_character_slot_index: int
    reference_voice_slot_index: int
    text: str
    language: LanguageType
    speed: float
    cutMethod: CutMethod
