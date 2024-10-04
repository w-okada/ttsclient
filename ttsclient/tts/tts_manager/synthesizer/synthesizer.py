from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import torch

from ttsclient.tts.tts_manager.synthesizer.synthesizer_info import SynthesizerInfo


class Synthesizer(ABC):
    @abstractmethod
    def get_info(self) -> SynthesizerInfo:
        pass

    @abstractmethod
    def get_hps(self):
        pass

    @abstractmethod
    def extract_latent(self, ssl_content: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def decode(
        self,
        pred_semantic: torch.Tensor,
        phones2: torch.Tensor,
        refers: list[torch.Tensor],
        speed: float,
        ref_wav_path: str | None = None,
    ) -> np.ndarray:
        pass

    @classmethod
    @abstractmethod
    def generate_onnx(cls, model_path: Path) -> None:
        pass
