import logging
from pathlib import Path
import traceback
from simple_performance_timer.Timer import Timer
import librosa
import numpy as np
import torch
from ttsclient.const import LOGGER_NAME, CutMethod, ModelDir
from ttsclient.tts.configuration_manager.configuration_manager import ConfigurationManager
from ttsclient.tts.data_types.slot_manager_data_types import GPTSoVITSSlotInfo, SlotInfoMember
from ttsclient.tts.module_manager.module_manager import ModuleManager
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.embedder.embedder_manager import EmbedderManager
from ttsclient.tts.tts_manager.phone_extractor.phone_extractor_manager import PhoneExtractorManager
from ttsclient.tts.tts_manager.pipeline.pipeline import Pipeline
from ttsclient.tts.tts_manager.semantic_predictor.semantic_predictor_manager import SemanticPredictorManager
from ttsclient.tts.tts_manager.synthesizer.synthesizer_manager import SynthesizerManager
from ttsclient.tts.tts_manager.utils.get_spec import get_spepc
from ttsclient.tts.tts_manager.utils.text_cutter import cut1, cut2, cut3, cut4, cut5, merge_short_text_in_array, process_text, splits


class GPTSoVITSPipeline(Pipeline):
    def __init__(self, slot_info: SlotInfoMember):
        assert isinstance(slot_info, GPTSoVITSSlotInfo)
        self.slot_info = slot_info
        self.slot_index = self.slot_info.slot_index

        conf = ConfigurationManager.get_instance().get_tts_configuration()
        super().__init__(gpu_device_id=conf.gpu_device_id_int)
        logging.getLogger(LOGGER_NAME).info(f"construct new pipelinepitch: slot_index:{self.slot_index}, gpu_device_id:{self.gpu_device_id}")

        module_manager = ModuleManager.get_instance()
        if self.slot_info.semantic_predictor_model is None:
            logging.getLogger(LOGGER_NAME).info("use default sematic predictor")
            gpt_model = module_manager.get_module_filepath("gpt_model")
        else:
            gpt_model = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.semantic_predictor_model
            logging.getLogger(LOGGER_NAME).info(f"use custom sematic predictor {gpt_model}")
        self.t2s_model = SemanticPredictorManager.get_semantic_predictor(
            "GPTSemanticPredictor",
            gpt_model,
            self.gpu_device_id,
            self.slot_info.backend_mode == "all_onnx" or self.slot_info.backend_mode == "semantic_onnx",
        )

        if self.slot_info.synthesizer_path is None:
            sovit_model = module_manager.get_module_filepath("sovits_model")
        else:
            sovit_model = ModelDir / f"{self.slot_info.slot_index}" / self.slot_info.synthesizer_path
            logging.getLogger(LOGGER_NAME).info(f"use custom sematic predictor {sovit_model}")
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

        self.zero_wav = np.zeros(int(self.hps.data.sampling_rate * 0.3), dtype=np_dtype)

        self.cache = {}  # type:ignore
        self.force_stop_flag = False

        self.reference_cache = {}  # type:ignore

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
        # print("REF TEXT: ", prompt_text)
        phones1, bert1, norm_text1 = self.phone_extractor.get_phones_and_bert(prompt_text, prompt_language, version)

        # 参照音声の処理。
        wav16k = self._load_ref_wav(ref_wav_path, is_half, device, zero_wav)
        with torch.no_grad():
            # print(f"wav16k.device:{wav16k.device}, ssl_model.device:{ssl_model.device}, vq_model.device:{vq_model.device}")
            ssl_content = ssl_model.get_content(wav16k)

            # パフォーマンスを見るとほぼ同じ 24ms(torch) vs 22ms(onnx) (10回あたり)
            # with Timer("get latent torch"):
            #     for i in range(10):
            #         prompt = vq_model.extract_latent(ssl_content)
            # with Timer("get latent onnx"):
            #     for i in range(10):
            #         prompt2 = vq_model.get_latent(ssl_content)
            prompt = vq_model.extract_latent(ssl_content)
            # prompt2 = vq_model.get_latent(ssl_content)
            # print(f"prompt:{prompt.shape}, prompt2:{prompt2.shape}")
            # print(f"prompt1:{prompt[0, :10]}")
            # print(f"prompt2:{prompt2[0, :10]}")

        return phones1, bert1, prompt

    def _validate_target_text(self, text: str, text_language):
        text = text.strip("\n")
        # if text[0] not in splits and len(get_first(text)) < 4:
        #     text = "。" + text if text_language != "en" else "." + text
        return text

    def _generate_target_contents(self, how_to_cut: CutMethod, text: str, text_language: str, version: str):
        text = self._validate_target_text(text, text_language)
        # print("TARGET TEXT: ", text)

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
        # print("TARGET TEXT(after sentence segmentation):", text)
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
    ):
        print("START NORMAL PIPELINE!")
        ref_free: bool = False
        if_freeze: bool = False

        # 参照音声とテキストの処理
        # version = os.environ.get("version", "v2")
        version = "v2"
        with Timer("generate reference content"):
            if ref_wav_path in self.reference_cache:
                phones1, bert1, prompt = self.reference_cache[ref_wav_path]
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
                self.reference_cache[ref_wav_path] = (phones1, bert1, prompt)

        # ターゲットテキストの処理
        with Timer("generate target text"):
            texts = self._generate_target_contents(how_to_cut, text, text_language, version)

        audio_opt = []
        # ここからターゲットテキストごとの処理⇒音声化
        with Timer("generate voice"):
            for i_text, text in enumerate(texts):
                # 途中終了チェック（１）
                if self.force_stop_flag is True:
                    break
                phones2, bert2, norm_text2 = self.phone_extractor.get_phones_and_bert(text, text_language, version)
                # print("実際に入力された目標テキスト（文ごと）", text)
                # print("フロントエンド処理後のテキスト（文ごと）:", norm_text2)

                if not ref_free:
                    bert = torch.cat([bert1, bert2], 1)
                    all_phoneme_ids = torch.LongTensor(phones1 + phones2).to(self.device).unsqueeze(0)
                else:
                    bert = bert2
                    all_phoneme_ids = torch.LongTensor(phones2).to(self.device).unsqueeze(0)

                bert = bert.to(self.device).unsqueeze(0)
                all_phoneme_len = torch.tensor([all_phoneme_ids.shape[-1]]).to(self.device)
                # ここまでで、テキスト部分の準備完了。（phonemeとbert）　⇒ではなかった。

                # 途中終了チェック（２）
                if self.force_stop_flag is True:
                    break

                # ここからターゲットテキストのsematicを抽出
                if i_text in self.cache and if_freeze is True:
                    pred_semantic = self.cache[i_text]
                else:
                    with torch.no_grad():
                        # print("start t2s_model.model.infer_panel...")
                        pred_semantic = self.t2s_model.predict(
                            all_phoneme_ids,
                            all_phoneme_len,
                            None if ref_free else prompt,
                            bert,
                            # prompt_phone_len=ph_offset,
                            top_k=top_k,
                            top_p=top_p,
                            temperature=temperature,
                        )
                        # print("startt2s_model.model.infer_panel...done")
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
                    # パフォーマンスを見るとtorchのほうが早い 62ms(torch) vs 265ms(onnx) (10回あたり)
                    # with Timer("get soec torch"):
                    #     for i in range(10):
                    #         refers = [get_spepc(self.hps, ref_wav_path).to(self.torch_dtype).to(self.device)]

                    # with Timer("get soec onnx"):
                    #     for i in range(10):
                    #         refers2 = [torch.Tensor(self.vq_model.get_spec(ref_wav_path)).to(self.torch_dtype).to(self.device)]

                    refers = [get_spepc(self.hps, ref_wav_path).to(self.torch_dtype).to(self.device)]
                    # refers2 = [torch.Tensor(self.vq_model.get_spec(ref_wav_path)).to(self.torch_dtype).to(self.device)]
                    # print(f"refers:{refers[0].shape}, refers2:{refers2[0].shape}")
                    # print(f"refers:{refers[0][0, :10]}")
                    # print(f"refers2:{refers2[0][0, :10]}")

                phones2 = torch.LongTensor(phones2).to(self.device).unsqueeze(0)

                audio = self.vq_model.decode(
                    pred_semantic,
                    phones2,
                    refers,
                    speed=speed,
                    ref_wav_path=ref_wav_path,
                )

                max_audio = np.abs(audio).max()  # 简单防止16bit爆音
                if max_audio > 1:
                    audio /= max_audio
                audio_opt.append(audio)
                audio_opt.append(self.zero_wav)

        # yield hps.data.sampling_rate, (np.concatenate(audio_opt, 0) * 32768).astype(np.int16)
        return self.hps.data.sampling_rate, (np.concatenate(audio_opt, 0) * 32768).astype(np.int16)
