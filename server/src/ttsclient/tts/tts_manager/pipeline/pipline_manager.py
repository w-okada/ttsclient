from ttsclient.tts.tts_manager.pipeline.pipeline import Pipeline
from ttsclient.tts.tts_manager.pipeline.gpt_sovits_v3_pipeline import GPTSoVITSV3Pipeline
from ttsclient.tts.tts_manager.pipeline.gpt_sovits_v4_pipeline import GPTSoVITSV4Pipeline
from ttsclient.models.slot import GPTSoVITSSlotInfo, SlotInfo


class PipelineManager:

    @classmethod
    def get_pipeline(cls, slot_info: SlotInfo) -> Pipeline:
        if slot_info.tts_type != "GPT-SoVITS":
            raise RuntimeError(f"Unknown tts type: {slot_info.tts_type}")
        assert isinstance(slot_info, GPTSoVITSSlotInfo)
        if slot_info.model_version in ("v3", "v4"):
            if slot_info.model_version == "v3":
                return GPTSoVITSV3Pipeline(slot_info)
            return GPTSoVITSV4Pipeline(slot_info)
        raise RuntimeError(f"Unsupported model version: {slot_info.model_version}")
