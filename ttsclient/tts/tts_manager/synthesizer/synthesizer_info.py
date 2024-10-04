from pathlib import Path
from pydantic import BaseModel

from ttsclient.const import SynthesizerType


class SynthesizerInfo(BaseModel):
    synthesizer_type: SynthesizerType
    path: Path
    # hps: DictToAttrRecursive
