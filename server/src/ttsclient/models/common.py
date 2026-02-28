from pathlib import Path

from pydantic import BaseModel


class MoveModelParam(BaseModel):
    src: int
    dst: int


class SetIconParam(BaseModel):
    icon_file: Path
