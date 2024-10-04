from pathlib import Path

from ttsclient.const import EmbedderType
from ttsclient.tts.tts_manager.embedder.cnhubert_embedder import CNHubertEmbedder
from ttsclient.tts.tts_manager.embedder.embedder import Embedder


class EmbedderManager:
    current_embedder: Embedder | None = None

    @classmethod
    def get_embedder(
        cls,
        embedder_type: EmbedderType,
        model_path: Path,
        device_id: int,
    ) -> Embedder:
        try:
            cls.current_embedder = cls.load_embedder(embedder_type, model_path, device_id)
        except Exception as e:
            raise RuntimeError(e)

        assert cls.current_embedder is not None
        return cls.current_embedder

    @classmethod
    def load_embedder(
        cls,
        embedder_type: EmbedderType,
        model_path: Path,
        device_id: int,
    ):
        if embedder_type == "cnhubert":
            embedder = CNHubertEmbedder(model_path, device_id)
            return embedder
        else:
            raise ValueError(f"Unsupported embedder type: {embedder_type}")
