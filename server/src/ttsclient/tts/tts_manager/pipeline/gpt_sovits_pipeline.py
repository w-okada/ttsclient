import logging
from pathlib import Path
import traceback
from simple_performance_timer.Timer import Timer
import librosa
import numpy as np
import torch

from ttsclient.gpt_sovits_utils import cut1, cut2, cut3, cut4, cut5, get_spepc, merge_short_text_in_array, process_text, splits
from ttsclient.const import LOGGER_NAME, CutMethod, ModelDir
from ttsclient.services.configuration_manager import ConfigurationManager
from ttsclient.models.slot import GPTSoVITSSlotInfo, SlotInfoMember
from ttsclient.services.module_manager import ModuleManager
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.embedder.embedder_manager import EmbedderManager
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_manager import PhoneExtractorManager
from ttsclient.tts.tts_manager.pipeline.pipeline import Pipeline
from ttsclient.tts.tts_manager.semantic_predictor.semantic_predictor_manager import SemanticPredictorManager
from ttsclient.tts.tts_manager.sv.sv_model import SVModel
from ttsclient.tts.tts_manager.synthesizer.synthesizer_manager import SynthesizerManager


class GPTSoVITSPipeline(Pipeline):
    def __init__(self, slot_info: SlotInfoMember):
        assert isinstance(slot_info, GPTSoVITSSlotInfo)

        self.slot_info = slot_info
        self.slot_index = self.slot_info.slot_index

        conf = ConfigurationManager.get_instance().get_tts_configuration()
        super().__init__(gpu_device_id=conf.gpu_device_id_int)
        logging.getLogger(LOGGER_NAME).info(f"construct new pipelinepitch: slot_index:{self.slot_index}, gpu_device_id:{self.gpu_device_id}")

        module_manager = ModuleManager.get_instance()
        if self.slot_info.semantic_predictor_model_path is None:
            logging.getLogger(LOGGER_NAME).info("use default sematic predictor")
            gpt_model = module_manager.get_module_filepath("gpt_model")
        else:
            gpt_model = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.semantic_predictor_model_path
            logging.getLogger(LOGGER_NAME).info(f"use custom sematic predictor {gpt_model}")
        self.t2s_model = SemanticPredictorManager.get_semantic_predictor(
            "GPTSemanticPredictor",
            gpt_model,
            self.gpu_device_id,
            self.slot_info.backend_mode == "all_onnx" or self.slot_info.backend_mode == "semantic_onnx",
        )

        if self.slot_info.synthesizer_model_path is None:
            if self.slot_info.model_version == "v2Pro":
                sovit_model = module_manager.get_module_filepath("sovits_model_v2pro")
            elif self.slot_info.model_version == "v2ProPlus":
                sovit_model = module_manager.get_module_filepath("sovits_model_v2proplus")
            else:
                sovit_model = module_manager.get_module_filepath("sovits_model")
        else:
            sovit_model = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.synthesizer_model_path
            logging.getLogger(LOGGER_NAME).info(f"use custom synthesizer {sovit_model}")
        self.vq_model = SynthesizerManager.get_synthesizer(
            "SovitsSynthesizer",
            sovit_model,
            self.gpu_device_id,
            self.slot_info.backend_mode == "all_onnx" or self.slot_info.backend_mode == "synthesizer_onnx",
        )
        self.hps = self.vq_model.get_hps()

        cnhubert_base_path = ModuleManager.get_instance().get_module_filepath("chinese-hubert-base_bin")
        self.ssl_model = EmbedderManager.get_embedder("cnhubert", cnhubert_base_path.parent, self.gpu_device_id)

        bert_path = ModuleManager.get_instance().get_module_filepath("chinese-roberta-wwm-ext-large_bin").parent
        self.phone_extractor = PhoneExtractorManager.get_phone_extractor("BertPhoneExtractor", bert_path, self.gpu_device_id)

        self.device = DeviceManager.get_instance().get_pytorch_device(self.gpu_device_id)
        self.is_half = DeviceManager.get_instance().half_precision_available(self.gpu_device_id)
        np_dtype = np.int16
        self.torch_dtype = torch.float16 if self.is_half is True else torch.float32

        # SV モデル（v2Pro 系のみ）
        if self.vq_model.is_v2pro:
            sv_model_path = ModuleManager.get_instance().get_module_filepath("pretrained_eres2netv2w24s4ep4")
            self.sv_model = SVModel(sv_model_path, self.gpu_device_id)
            logging.getLogger(LOGGER_NAME).info("SV model loaded for v2Pro")
        else:
            self.sv_model = None

        self.zero_wav = np.zeros(int(self.hps.data.sampling_rate * 0.3), dtype=np_dtype)

        self.cache = {}  # type:ignore
        self.force_stop_flag = False

        self.reference_cache = {}  # type:ignore

    def get_phones(self, text: str, language: str):
        version = "v2"  # model_versionとversionの扱いが異なる。影響範囲を見極め切れていないのでとりあえずここはv2で固定。
        phones, bert, norm_text, _phone_symbols = self.phone_extractor.get_phones_and_bert(text, language, version, is_reference_voice=True)
        return phones, bert, norm_text, _phone_symbols

    def _validate_ref_text(self, prompt_text: str, prompt_language):
        prompt_text = prompt_text.strip("\n")
        if prompt_text[-1] not in splits:
            prompt_text += "。" if prompt_language != "en" else "."
        return prompt_text

    def _load_ref_wav(self, ref_wav_path: Path, is_half: bool, device: torch.device, zero_wav: np.ndarray):
        wav16k, sr = librosa.load(ref_wav_path, sr=16000)
        if wav16k.shape[0] > 160000 or wav16k.shape[0] < 48000:
            print("Reference audio is outside the 3-10 second range, please choose another one!")
            raise OSError("Reference audio is outside the 3-10 second range, please choose another one!")
        wav16k_torch = torch.from_numpy(wav16k)
        zero_wav_torch = torch.from_numpy(zero_wav)
        if is_half is True:
            wav16k_torch = wav16k_torch.half().to(device)
            zero_wav_torch = zero_wav_torch.half().to(device)
        else:
            wav16k_torch = wav16k_torch.to(device)
            zero_wav_torch = zero_wav_torch.to(device)
        wav16k_torch = torch.cat([wav16k_torch, zero_wav_torch])
        return wav16k_torch

    def _generate_ref_contents(
        self,
        ssl_model,
        vq_model,
        prompt_text: str,
        prompt_language: str,
        ref_wav_path: Path,
        is_half: bool,
        device: torch.device,
        zero_wav: np.ndarray,
        version: str,
    ):
        # 参照音声とテキストの処理
        # 参照テキストの処理。
        prompt_text = self._validate_ref_text(prompt_text, prompt_language)
        phones1, bert1, norm_text1, _phone_symbols_1 = self.phone_extractor.get_phones_and_bert(prompt_text, prompt_language, version, is_reference_voice=True)

        # 参照音声の処理。
        wav16k = self._load_ref_wav(ref_wav_path, is_half, device, zero_wav)
        with torch.no_grad():
            ssl_content = ssl_model.get_content(wav16k)
            prompt = vq_model.extract_latent(ssl_content)

        return phones1, bert1, prompt

    def _validate_target_text(self, text: str, text_language):
        text = text.strip("\n")
        return text

    def _generate_target_contents(self, how_to_cut: CutMethod, text: str, text_language: str, version: str):
        text = self._validate_target_text(text, text_language)

        if how_to_cut == "Slice once every 4 sentences":
            text = cut1(text)
        elif how_to_cut == "Slice per 50 characters":
            text = cut2(text)
        elif how_to_cut == "Slice by Chinese punct":
            text = cut3(text)
        elif how_to_cut == "Slice by English punct":
            text = cut4(text)
        elif how_to_cut == "Slice by every punct":
            text = cut5(text)
        while "\n\n" in text:
            text = text.replace("\n\n", "\n")
        texts = text.split("\n")
        texts = process_text(texts)
        texts = merge_short_text_in_array(texts, 5)

        new_texts = []
        for text in texts:
            # 解决输入目标文本的空行导致报错的问题
            if len(text.strip()) == 0:
                continue
            if text[-1] not in splits:
                text += "。" if text_language != "en" else "."
            new_texts.append(text)
        return new_texts

    def force_stop(self):
        self.force_stop_flag = True

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
        # v3追加オプション
        sample_steps: int = 8,
        phone_symbols: list[str] | None = None,
    ):
        print("RUN NORMAL PIPELINE!")
        ref_free: bool = False
        if_freeze: bool = False

        # 参照音声とテキストの処理
        version = "v2"  # model_versionとversionの扱いが異なる。影響範囲を見極め切れていないのでとりあえずここはv2で固定。
        with Timer("generate reference content", False):
            key = f"{prompt_language}_{prompt_text}_{ref_wav_path}"
            if key in self.reference_cache:
                phones1, bert1, prompt = self.reference_cache[key]
            elif ref_free is False:
                phones1, bert1, prompt = self._generate_ref_contents(
                    self.ssl_model,
                    self.vq_model,
                    prompt_text,
                    prompt_language,
                    Path(ref_wav_path),
                    self.is_half,
                    self.device,
                    self.zero_wav,
                    version,
                )
                self.reference_cache[key] = (phones1, bert1, prompt)

        # ターゲットテキストの処理
        with Timer("generate target text", False):
            texts = self._generate_target_contents(how_to_cut, text, text_language, version)

        audio_opt = []
        # ここからターゲットテキストごとの処理⇒音声化
        with Timer("generate voice", False):
            for i_text, text in enumerate(texts):
                # 途中終了チェック（１）
                if self.force_stop_flag is True:
                    break
                phones2, bert2, norm_text2, _phone_symbols_2 = self.phone_extractor.get_phones_and_bert(text, text_language, version, is_reference_voice=False)
                if phone_symbols is not None:
                    # only not for zh (bertはゼロ配列で返る)
                    phones2, bert2 = self.phone_extractor.phone_symbols_to_sequence_and_bert(phone_symbols, version)

                if not ref_free:
                    bert = torch.cat([bert1, bert2], 1)
                    all_phoneme_ids = torch.LongTensor(phones1 + phones2).to(self.device).unsqueeze(0)
                else:
                    bert = bert2
                    all_phoneme_ids = torch.LongTensor(phones2).to(self.device).unsqueeze(0)

                bert = bert.to(self.device).unsqueeze(0)
                all_phoneme_len = torch.tensor([all_phoneme_ids.shape[-1]]).to(self.device)

                # 途中終了チェック（２）
                if self.force_stop_flag is True:
                    break

                # ここからターゲットテキストのsematicを抽出
                if i_text in self.cache and if_freeze is True:
                    pred_semantic = self.cache[i_text]
                else:
                    with torch.no_grad():
                        pred_semantic = self.t2s_model.predict(
                            all_phoneme_ids,
                            all_phoneme_len,
                            None if ref_free else prompt,
                            bert,
                            top_k=top_k,
                            top_p=top_p,
                            temperature=temperature,
                        )
                        self.cache[i_text] = pred_semantic
                refers = []

                # 途中終了チェック（３）
                if self.force_stop_flag is True:
                    break

                if inp_refs:
                    for path_str in inp_refs:
                        try:
                            path = Path(path_str)
                            refer = get_spepc(self.hps, path.name).to(self.torch_dtype).to(self.device)
                            refers.append(refer)
                        except:
                            traceback.print_exc()
                if len(refers) == 0:
                    refers = [get_spepc(self.hps, ref_wav_path).to(self.torch_dtype).to(self.device)]

                # sv_emb の計算（v2Pro のみ）
                sv_emb = None
                if self.sv_model is not None:
                    sv_emb = []
                    ref_paths = [Path(p) for p in inp_refs] if inp_refs else [Path(ref_wav_path)]
                    for rp in ref_paths:
                        wav_16k, _ = librosa.load(str(rp), sr=16000)
                        wav_16k_torch = torch.from_numpy(wav_16k).to(self.device)
                        sv_emb.append(self.sv_model.compute_embedding(wav_16k_torch))

                phones2 = torch.LongTensor(phones2).to(self.device).unsqueeze(0)

                audio = self.vq_model.decode(
                    pred_semantic,
                    phones2,
                    refers,
                    speed=speed,
                    sv_emb=sv_emb,
                    ref_wav_path=ref_wav_path,
                )

                max_audio = np.abs(audio).max()  # 简单防止16bit爆音
                if max_audio > 1:
                    audio /= max_audio
                audio_opt.append(audio)
                audio_opt.append(self.zero_wav)

        return self.hps.data.sampling_rate, (np.concatenate(audio_opt, 0) * 32768).astype(np.int16)
