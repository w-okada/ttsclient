from pathlib import Path

from ttsclient.const import PhoneExtractorType
from ttsclient.tts.tts_manager.phone_extractor.bert_phone_extractor import BertPhoneExtractor
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor import PhoneExtractor


class PhoneExtractorManager:
    current_phone_extractor: PhoneExtractor | None = None

    @classmethod
    def get_phone_extractor(
        cls,
        phone_extractor_type: PhoneExtractorType,
        model_path: Path,
        device_id: int,
    ) -> PhoneExtractor:
        try:
            cls.current_phone_extractor = cls.load_phone_extractor(phone_extractor_type, model_path, device_id)
        except Exception as e:
            raise RuntimeError(e)

        assert cls.current_phone_extractor is not None
        return cls.current_phone_extractor

    @classmethod
    def load_phone_extractor(
        cls,
        phone_extractor_type: PhoneExtractorType,
        model_path: Path,
        device_id: int,
    ):
        if phone_extractor_type == "BertPhoneExtractor":
            phone_extractor = BertPhoneExtractor(model_path, device_id)
            return phone_extractor
        else:
            raise ValueError(f"Unsupported phone extractor type: {phone_extractor_type}")
