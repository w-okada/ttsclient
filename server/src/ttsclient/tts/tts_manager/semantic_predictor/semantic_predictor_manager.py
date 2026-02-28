from pathlib import Path
from ttsclient.const import SemanticPredictorType
from ttsclient.tts.tts_manager.semantic_predictor.gpt_semantic_predictor import GPTSemanticPredictor
from ttsclient.tts.tts_manager.semantic_predictor.smantic_predictor import SemanticPredictor


class SemanticPredictorManager:
    current_semantic_predictor: SemanticPredictor | None = None

    @classmethod
    def get_semantic_predictor(
        cls,
        semantic_predictor_type: SemanticPredictorType,
        model_path: Path,
        device_id: int,
        use_onnx: bool,
    ) -> SemanticPredictor:
        try:
            cls.current_semantic_predictor = cls.load_semantic_predictor(semantic_predictor_type, model_path, device_id, use_onnx)
        except Exception as e:
            raise RuntimeError(e)

        assert cls.current_semantic_predictor is not None
        return cls.current_semantic_predictor

    @classmethod
    def load_semantic_predictor(
        cls,
        semantic_predictor_type: SemanticPredictorType,
        model_path: Path,
        device_id: int,
        use_onnx: bool,
    ):
        if semantic_predictor_type == "GPTSemanticPredictor":
            semantic_predictor = GPTSemanticPredictor(model_path, device_id, use_onnx)
            return semantic_predictor
        else:
            raise ValueError(f"Unsupported semantic predictor type: {semantic_predictor_type}")
