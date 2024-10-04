from abc import ABC, abstractmethod

import torch

from ttsclient.tts.tts_manager.embedder.embedder_info import EmbedderInfo


class Embedder(ABC):
    @abstractmethod
    def get_info(self) -> EmbedderInfo:
        pass

    @abstractmethod
    def get_content(self, wav16k: torch.Tensor) -> torch.Tensor:
        pass
