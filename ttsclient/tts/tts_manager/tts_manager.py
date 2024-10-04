from ttsclient.const import VoiceCharacterDir
from ttsclient.tts.configuration_manager.configuration_manager import (
    ConfigurationManager,
)
from ttsclient.tts.data_types.tts_manager_data_types import GenerateVoiceParam
from ttsclient.tts.slot_manager.slot_manager import SlotManager
from ttsclient.tts.tts_manager.pipeline.pipline_manager import PipelineManager
from ttsclient.tts.voice_character_slot_manager.voice_character_slot_manager import (
    VoiceCharacterSlotManager,
)


class TTSManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.loaded_model_slot_id = -1
        self.pipeline = None
        self.backend_mode = None
        pass

    def load_model(self, slot_id: int):
        self.loaded_model_slot_id = slot_id
        slot_manager = SlotManager.get_instance()
        slot_info = slot_manager.get_slot_info(slot_id)
        self.pipeline = PipelineManager.get_pipeline(slot_info)
        self.use_faster = slot_info.enable_faster
        self.backend_mode = slot_info.backend_mode

    def stop_tts(self):
        if self.pipeline is not None:
            self.pipeline.force_stop()

    def check_and_load_model(self):
        conf = ConfigurationManager.get_instance().get_tts_configuration()
        slot_info = SlotManager.get_instance().get_slot_info(conf.current_slot_index)

        # Check
        exec_load = False
        if self.pipeline is None:
            exec_load = True
        elif self.loaded_model_slot_id != conf.current_slot_index:
            exec_load = True
        elif self.pipeline.gpu_device_id != conf.gpu_device_id_int:
            exec_load = True
        elif slot_info.enable_faster != self.use_faster:
            exec_load = True
        elif self.backend_mode != slot_info.backend_mode:
            exec_load = True
        print("self.backend_mode != slot_info.backend_mode:", self.backend_mode, slot_info.backend_mode)
        # Load
        if exec_load is True:
            self.load_model(conf.current_slot_index)

    def run(self, generarte_voice_param: GenerateVoiceParam):
        conf = ConfigurationManager.get_instance().get_tts_configuration()

        slot_manager = SlotManager.get_instance()
        slot_info = slot_manager.get_slot_info(conf.current_slot_index)
        self.check_and_load_model()

        assert self.pipeline is not None, "Model is not loaded"

        voice_character_slot_manager = VoiceCharacterSlotManager.get_instance()
        voice_character = voice_character_slot_manager.get_slot_info(generarte_voice_param.voice_character_slot_index)
        reference_voices = [v for v in voice_character.reference_voices if v.slot_index == generarte_voice_param.reference_voice_slot_index]
        assert len(reference_voices) == 1, f"reference voice not found. voice_character_slot_index:{generarte_voice_param.voice_character_slot_index}, reference_voice_slot_index:{generarte_voice_param.reference_voice_slot_index}"
        reference_voice = reference_voices[0]

        slot_dir = VoiceCharacterDir / f"{generarte_voice_param.voice_character_slot_index}"

        ref_wav_path = slot_dir / f"{reference_voice.wav_file}"
        synthesis_result = self.pipeline.run(
            ref_wav_path=str(ref_wav_path),
            prompt_text=reference_voice.text,
            prompt_language=reference_voice.language,
            text=generarte_voice_param.text,
            text_language=generarte_voice_param.language,
            how_to_cut=generarte_voice_param.cutMethod,
            speed=generarte_voice_param.speed,
            # slot_infoからの入力
            top_k=slot_info.top_k,
            top_p=slot_info.top_p,
            temperature=slot_info.temperature,
            # faster用の入力
            batch_size=slot_info.batch_size,
            batch_threshold=slot_info.batch_threshold,
            split_bucket=slot_info.split_bucket,
            return_fragment=slot_info.return_fragment,
            fragment_interval=slot_info.fragment_interval,
            seed=slot_info.seed,
            parallel_infer=slot_info.parallel_infer,
            repetition_penalty=slot_info.repetition_penalty,
        )
        last_sampling_rate, last_audio_data = synthesis_result

        return last_sampling_rate, last_audio_data
