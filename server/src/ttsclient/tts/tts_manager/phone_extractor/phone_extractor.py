from abc import ABC, abstractmethod
from pathlib import Path
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_info import PhoneExtractorInfo


class PhoneExtractor(ABC):
    @abstractmethod
    def get_info(self) -> PhoneExtractorInfo:
        pass

    @abstractmethod
    def phone_symbols_to_sequence_and_bert(self, cleaned_text, version):
        pass

    @abstractmethod
    def get_phones_and_bert(self, text, language, version, is_reference_voice: bool = True):
        pass
