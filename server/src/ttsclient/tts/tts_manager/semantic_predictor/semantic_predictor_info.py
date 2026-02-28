from pathlib import Path
from pydantic import BaseModel

from ttsclient.const import SemanticPredictorType


class SemanticPredictorInfo(BaseModel):
    semantic_predictor_type: SemanticPredictorType
    path: Path
    hz: int
    max_sec: int
