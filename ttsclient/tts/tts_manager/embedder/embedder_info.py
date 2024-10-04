from pathlib import Path
from pydantic import BaseModel

from ttsclient.const import EmbedderType


class EmbedderInfo(BaseModel):
    embedder_type: EmbedderType
    path: Path
