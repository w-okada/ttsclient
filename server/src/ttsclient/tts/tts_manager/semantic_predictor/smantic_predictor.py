from abc import ABC, abstractmethod
from pathlib import Path

import torch

from ttsclient.tts.tts_manager.semantic_predictor.semantic_predictor_info import SemanticPredictorInfo


class SemanticPredictor(ABC):
    @abstractmethod
    def get_info(self) -> SemanticPredictorInfo:
        pass

    @abstractmethod
    def predict(
        self,
        all_phoneme_ids: torch.Tensor,
        all_phoneme_len: torch.Tensor,
        prompt: torch.Tensor | None,
        bert: torch.Tensor,
        top_k: int,
        top_p: float,
        temperature: float,
    ) -> torch.Tensor:
        pass

    @classmethod
    @abstractmethod
    def generate_onnx(cls, model_path: Path) -> None:
        pass
