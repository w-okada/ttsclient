from pathlib import Path

import torch
from feature_extractor import cnhubert
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.embedder.embedder import Embedder
from ttsclient.tts.tts_manager.embedder.embedder_info import EmbedderInfo


class CNHubertEmbedder(Embedder):
    def __init__(self, model_path: Path, device_id: int):
        self.device = DeviceManager.get_instance().get_pytorch_device(device_id)
        self.is_half = DeviceManager.get_instance().half_precision_available(device_id)

        cnhubert.cnhubert_base_path = model_path
        self.ssl_model = cnhubert.get_model()
        if self.is_half is True:
            self.ssl_model = self.ssl_model.half().to(self.device)
        else:
            self.ssl_model = self.ssl_model.to(self.device)

        self.info = EmbedderInfo(
            embedder_type="cnhubert",
            path=model_path,
        )

    def get_info(self) -> EmbedderInfo:
        return self.info

    def get_content(self, wav16k: torch.Tensor) -> torch.Tensor:
        ssl_content = self.ssl_model.model(wav16k.unsqueeze(0))["last_hidden_state"].transpose(1, 2)
        return ssl_content
