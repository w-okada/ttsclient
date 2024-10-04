from abc import ABC, abstractmethod
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_info import PhoneExtractorInfo


class PhoneExtractor(ABC):
    @abstractmethod
    def get_info(self) -> PhoneExtractorInfo:
        pass

    @abstractmethod
    def get_phones_and_bert(self, text, language, version):
        pass
