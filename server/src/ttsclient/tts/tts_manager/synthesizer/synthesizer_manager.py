from pathlib import Path
from ttsclient.const import SynthesizerType
from ttsclient.tts.tts_manager.synthesizer.sovits_synthesizer import SovitsSynthesizer
from ttsclient.tts.tts_manager.synthesizer.sovits_synthesizer_v3 import SovitsSynthesizerV3
from ttsclient.tts.tts_manager.synthesizer.synthesizer import Synthesizer


class SynthesizerManager:
    current_synthesizer: Synthesizer | None = None

    @classmethod
    def get_synthesizer(
        cls,
        synthesizer_type: SynthesizerType,
        model_path: Path,
        device_id: int,
        use_onnx: bool,
    ) -> Synthesizer:
        try:
            cls.current_synthesizer = cls.load_synthesizer(synthesizer_type, model_path, device_id, use_onnx)
        except Exception as e:
            raise e

        assert cls.current_synthesizer is not None
        return cls.current_synthesizer

    @classmethod
    def load_synthesizer(
        cls,
        synthesizer_type: SynthesizerType,
        model_path: Path,
        device_id: int,
        use_onnx: bool,
    ):
        if synthesizer_type == "SovitsSynthesizer":
            synthesizer = SovitsSynthesizer(model_path, device_id, use_onnx)
            return synthesizer
        elif synthesizer_type == "SovitsSynthesizerV3":
            synthesizer = SovitsSynthesizerV3(model_path, False, device_id, use_onnx, version="v3")
            return synthesizer
        elif synthesizer_type == "SovitsSynthesizerV3Lora":
            synthesizer = SovitsSynthesizerV3(model_path, True, device_id, use_onnx, version="v3")
            return synthesizer
        elif synthesizer_type == "SovitsSynthesizerV4":
            synthesizer = SovitsSynthesizerV3(model_path, False, device_id, use_onnx, version="v4")
            return synthesizer
        elif synthesizer_type == "SovitsSynthesizerV4Lora":
            synthesizer = SovitsSynthesizerV3(model_path, True, device_id, use_onnx, version="v4")
            return synthesizer
        else:
            raise ValueError(f"Unsupported synthesizer type: {synthesizer_type}")
