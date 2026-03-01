from ttsclient.tts.tts_manager.pipeline.pipeline import Pipeline
from ttsclient.tts.tts_manager.pipeline.gpt_sovits_pipeline import GPTSoVITSPipeline
from ttsclient.models.slot import GPTSoVITSSlotInfo, SlotInfo


class PipelineManager:

    @classmethod
    def get_pipeline(cls, slot_info: SlotInfo) -> Pipeline:
        if slot_info.tts_type != "GPT-SoVITS":
            raise RuntimeError(f"Unknown tts type: {slot_info.tts_type}")
        assert isinstance(slot_info, GPTSoVITSSlotInfo)
        if slot_info.model_version in ("v2Pro", "v2ProPlus"):
            return GPTSoVITSPipeline(slot_info)
        raise NotImplementedError(f"Unsupported model version: {slot_info.model_version}")
