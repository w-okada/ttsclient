from pathlib import Path
from pydantic import BaseModel

from ttsclient.const import PhoneExtractorType


class PhoneExtractorInfo(BaseModel):
    phone_extractor_type: PhoneExtractorType
    path: Path
