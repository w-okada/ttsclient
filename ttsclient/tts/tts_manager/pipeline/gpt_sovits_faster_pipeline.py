import logging
import random

import numpy as np
from ttsclient.const import LOGGER_NAME, CutMethod, CutMethods, CutMethodsForFaster, ModelDir
from ttsclient.tts.configuration_manager.configuration_manager import ConfigurationManager
from ttsclient.tts.data_types.slot_manager_data_types import GPTSoVITSSlotInfo, SlotInfoMember
from ttsclient.tts.module_manager.module_manager import ModuleManager
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.pipeline.gpt_sovits_faster_pipeline_modules.TTS import TTS, TTS_Config
from ttsclient.tts.tts_manager.pipeline.pipeline import Pipeline


class GPTSoVITSFasterPipeline(Pipeline):
    def __init__(self, slot_info: SlotInfoMember):
        assert isinstance(slot_info, GPTSoVITSSlotInfo)
        self.slot_info = slot_info
        self.slot_index = self.slot_info.slot_index

        conf = ConfigurationManager.get_instance().get_tts_configuration()
        super().__init__(gpu_device_id=conf.gpu_device_id_int)
        logging.getLogger(LOGGER_NAME).info(f"construct new pipelinepitch: slot_index:{self.slot_index}, gpu_device_id:{self.gpu_device_id}")

        module_manager = ModuleManager.get_instance()
        tts_config = TTS_Config()

        if self.slot_info.semantic_predictor_model is None:
            tts_config.t2s_weights_path = module_manager.get_module_filepath("gpt_model")
            logging.getLogger(LOGGER_NAME).info("use default sematic predictor")
        else:
            tts_config.t2s_weights_path = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.semantic_predictor_model
            logging.getLogger(LOGGER_NAME).info(f"use custom sematic predictor {tts_config.t2s_weights_path}")

        if self.slot_info.synthesizer_path is None:
            tts_config.vits_weights_path = module_manager.get_module_filepath("sovits_model")
            logging.getLogger(LOGGER_NAME).info("use default sematic predictor")
        else:
            tts_config.vits_weights_path = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.synthesizer_path
            logging.getLogger(LOGGER_NAME).info(f"use custom sematic predictor {tts_config.vits_weights_path}")

        tts_config.cnhuhbert_base_path = ModuleManager.get_instance().get_module_filepath("chinese-hubert-base_bin").parent
        tts_config.bert_base_path = ModuleManager.get_instance().get_module_filepath("chinese-roberta-wwm-ext-large_bin").parent

        tts_config.device = DeviceManager.get_instance().get_pytorch_device(self.gpu_device_id)
        tts_config.is_half = DeviceManager.get_instance().half_precision_available(self.gpu_device_id)

        self.tts_pipeline = TTS(tts_config)

        self.zero_wav = np.zeros(int(tts_config.sampling_rate * 0.3), dtype=np.int16)

    def force_stop(self):
        self.tts_pipeline.stop()

    def run(
        self,
        ref_wav_path: str,
        prompt_text: str,
        prompt_language: str,
        text: str,
        text_language: str,
        how_to_cut: CutMethod = "No slice",
        top_k: int = 20,
        top_p: float = 1,
        temperature: float = 1,
        speed: float = 1,
        inp_refs: list[str] = [],
        # ここからfasterの追加オプション
        batch_size: int = 1,
        batch_threshold: float = 0.75,
        split_bucket: bool = True,
        return_fragment: bool = False,
        fragment_interval: float = 0.3,
        seed: int = -1,
        parallel_infer: bool = True,
        repetition_penalty: float = 1.35,
    ):
        print("START FAST PIPELINE!")

        cut_method_index = 0
        for index in range(len(CutMethods)):
            if CutMethods[index] == how_to_cut:
                cut_method_index = index
                break
        cut_method_for_faster = CutMethodsForFaster[cut_method_index]
        print(f"translate cut_method {how_to_cut} -> {cut_method_for_faster}")

        # seed = -1 if keep_random else seed
        # actual_seed = seed if seed not in [-1, "", None] else random.randrange(1 << 32)
        actual_seed = seed if seed != -1 else random.randrange(1 << 32)
        inputs = {
            "text": text,
            "text_lang": text_language,
            "ref_audio_path": ref_wav_path,
            "aux_ref_audio_paths": inp_refs,
            "prompt_text": prompt_text,
            "prompt_lang": prompt_language,
            "top_k": top_k,
            "top_p": top_p,
            "temperature": temperature,
            # "text_split_method": how_to_cut,
            "text_split_method": cut_method_for_faster,
            "batch_size": batch_size,  # int(batch_size)
            "batch_threshold": batch_threshold,
            "split_bucket": split_bucket,
            "return_fragment": return_fragment,
            "speed_factor": speed,
            "fragment_interval": fragment_interval,
            "seed": actual_seed,
            "parallel_infer": parallel_infer,
            "repetition_penalty": repetition_penalty,
        }

        audio_opt = []
        sample_rate = 32000
        for item in self.tts_pipeline.run(inputs):
            sample_rate = item[0]
            audio = item[1]
            audio_opt.append(audio)
            audio_opt.append(self.zero_wav)

        result = np.concatenate(audio_opt, 0)

        return sample_rate, result
