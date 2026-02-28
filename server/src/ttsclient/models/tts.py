from pydantic import BaseModel

from ttsclient.const import CutMethod, LanguageType


class GenerateVoiceParam(BaseModel):
    voice_character_slot_index: int
    reference_voice_slot_index: int
    text: str
    language: LanguageType
    speed: float
    cutMethod: CutMethod
    sample_steps: int | None = None
    phone_symbols: list[str] | None = None


class OpenJTalkUserDictRecord(BaseModel):
    string: str
    pos: str
    pos_group1: str
    pos_group2: str
    pos_group3: str
    ctype: str
    cform: str
    orig: str
    read: str
    pron: str
    acc: int
    mora_size: int
    chain_rule: str
    chain_flag: int


class GetJpTextToUserDictRecordsParam(BaseModel):
    text: str
    voice_character_slot_index: int


class GetPhonesParam(BaseModel):
    text: str
    language: LanguageType
    voice_character_slot_index: int
    user_dict_records: list[OpenJTalkUserDictRecord] | None


class GetPhonesResponse(BaseModel):
    phones: list[int]
    phone_symbols: list[str]
