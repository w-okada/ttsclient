import logging
from pathlib import Path

import numpy as np
import torch
import onnxruntime
import onnx
from onnxsim import simplify
import json

from ttsclient.const import LOGGER_NAME
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager
from ttsclient.tts.tts_manager.models.synthesizer.models import SynthesizerTrn
from ttsclient.tts.tts_manager.models.synthesizer.onnx.models_onnx import Spectrogram, SynthesizerTrnLatent, SynthesizerTrn as SynthesizerTrnOnnx
from ttsclient.tts.tts_manager.synthesizer.synthesizer import Synthesizer
from ttsclient.tts.tts_manager.synthesizer.synthesizer_info import SynthesizerInfo
from ttsclient.tts.tts_manager.utils.dict_to_attr_recursive import DictToAttrRecursive

from simple_performance_timer.Timer import Timer

# from ttsclient.tts.tts_manager.utils.load_audio import load_audio


class SovitsSynthesizer(Synthesizer):
    def __init__(self, model_path: Path, device_id: int, use_onnx: bool, del_enc: bool = True):
        print("load new syntehtizer: SovitsSynthesizer")
        self.device = DeviceManager.get_instance().get_pytorch_device(device_id)
        self.is_half = DeviceManager.get_instance().half_precision_available(device_id)
        self.model_path = model_path
        onnx_vq_model_stem = self.model_path.stem + "_vq_model"
        self.onnx_vq_model_path = self.model_path.with_name(onnx_vq_model_stem).with_suffix(".onnx")
        onnx_spec_stem = self.model_path.stem + "_spec"
        self.onnx_spec_path = self.model_path.with_name(onnx_spec_stem).with_suffix(".onnx")
        onnx_latent_stem = self.model_path.stem + "_latent"
        self.onnx_latent_path = self.model_path.with_name(onnx_latent_stem).with_suffix(".onnx")
        self.use_onnx = use_onnx

        dict_s2 = torch.load(model_path, map_location="cpu")
        self.hps = DictToAttrRecursive(dict_s2["config"])
        if self.use_onnx is False:
            self.hps.model.semantic_frame_rate = "25hz"
            if dict_s2["weight"]["enc_p.text_embedding.weight"].shape[0] == 322:
                self.hps.model.version = "v1"
            else:
                self.hps.model.version = "v2"
            # print("sovits version:", hps.model.version)

            self.vq_model = SynthesizerTrn(
                self.hps.data.filter_length // 2 + 1,
                self.hps.train.segment_size // self.hps.data.hop_length,
                n_speakers=self.hps.data.n_speakers,
                **self.hps.model,
            )
            if del_enc is True:
                del self.vq_model.enc_q
            if self.is_half is True:
                self.vq_model = self.vq_model.half().to(self.device)
            else:
                self.vq_model = self.vq_model.to(self.device)
            self.vq_model.eval()
            self.vq_model.load_state_dict(dict_s2["weight"], strict=False)

            self.info = SynthesizerInfo(
                synthesizer_type="SovitsSynthesizer",
                path=model_path,
            )
        else:
            # #####################
            # ONNX
            # #####################
            (
                onnx_providers,
                onnx_provider_options,
            ) = DeviceManager.get_instance().get_onnx_execution_provider(device_id=device_id)

            self.candidate_onnx_providers = onnx_providers
            self.candidate_onnx_provider_options = onnx_provider_options

            so = onnxruntime.SessionOptions()
            so.log_severity_level = 3

            if self.onnx_vq_model_path.exists() is True:
                self.onnx_session_vq_model = onnxruntime.InferenceSession(str(self.onnx_vq_model_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
                # self.onnx_session_spec = onnxruntime.InferenceSession(str(self.onnx_spec_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
                self.onnx_session_latent = onnxruntime.InferenceSession(str(self.onnx_latent_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
            else:
                self.onnx_session_vq_model = None
                # self.onnx_session_spec = None
                self.onnx_session_latent = None

    def get_info(self) -> SynthesizerInfo:
        return self.info

    def get_hps(self):
        return self.hps

    def extract_latent(self, ssl_content: torch.Tensor) -> torch.Tensor:
        if self.use_onnx is False or self.onnx_session_latent is None:
            codes = self.vq_model.extract_latent(ssl_content)
            prompt_semantic = codes[0, 0]
            prompt = prompt_semantic.unsqueeze(0).to(self.device)
        else:
            prompt = self.get_latent(ssl_content)

        return prompt

    def decode(
        self,
        pred_semantic: torch.Tensor,  # torch.Size([1, 1, m])
        phones2: torch.Tensor,  # torch.Size([1, n])
        refers: list[torch.Tensor],  # list[([1, 1025, x)]
        speed: float,
        ref_wav_path: str | None = None,
    ) -> np.ndarray:
        if self.use_onnx is False or self.onnx_session_vq_model is None:
            with Timer("sovits_synthesizer.decode torch "):

                audio = (
                    self.vq_model.decode(
                        pred_semantic,
                        phones2,
                        refers,
                        speed,
                    )
                    .detach()
                    .cpu()
                    .numpy()[0, 0]
                )
            # print(f"audio.shape: {refers[0].shape}, pred_semantic.shape: {pred_semantic.shape}, phones2.shape: {phones2.shape}")
        else:

            with Timer("sovits_synthesizer.decode onnx2"):
                audio = self.onnx_session_vq_model.run(
                    ["audio"],
                    {
                        "pred_semantic": pred_semantic.cpu().numpy(),
                        "text_seq": phones2.cpu().numpy(),
                        "ref_spec": refers[0].cpu().numpy(),
                    },
                )
                audio = audio[0][0, 0]

        # audio = np.concatenate([audio, unit[0][0, 0]], axis=0)

        # self.generate_onnx()

        return audio

    # def get_spec(self, filename: Path):

    #     audio = load_audio(filename, int(self.hps.data.sampling_rate))
    #     audio = torch.FloatTensor(audio)
    #     maxx = audio.abs().max()
    #     if maxx > 1:
    #         audio /= min(2, maxx)
    #     audio_norm = audio
    #     audio_norm = audio_norm.unsqueeze(0)

    #     res = self.onnx_session_spec.run(
    #         ["spec"],
    #         {
    #             "y": audio_norm.cpu().numpy(),
    #         },
    #     )
    #     return res[0]

    def get_latent(self, ssl_content):
        res = self.onnx_session_latent.run(
            ["prompt"],
            {
                "ssl_content": ssl_content.cpu().numpy(),
            },
        )
        return torch.LongTensor(res[0][0])

    # #####################################
    # ONNXエクスポート用
    # #####################################
    @classmethod
    def generate_onnx(cls, model_path: Path):
        dict_s2 = torch.load(model_path, map_location="cpu")

        if dict_s2["weight"]["enc_p.text_embedding.weight"].shape[0] == 322:
            model_version = "v1"
        else:
            model_version = "v2"

        if model_version == "v1":
            logging.getLogger(LOGGER_NAME).warn("sovits version: v1, not support to export onnx")
            raise RuntimeError("sovits version: v1, not support to export onnx")

        onnx_vq_model_stem = model_path.stem + "_vq_model"
        onnx_vq_model_path = model_path.with_name(onnx_vq_model_stem).with_suffix(".onnx")
        onnx_spec_stem = model_path.stem + "_spec"
        onnx_spec_path = model_path.with_name(onnx_spec_stem).with_suffix(".onnx")
        onnx_latent_stem = model_path.stem + "_latent"
        onnx_latent_path = model_path.with_name(onnx_latent_stem).with_suffix(".onnx")

        cls.generate_onnx_sovits(dict_s2, onnx_vq_model_path)
        cls.generate_onnx_spec(dict_s2, onnx_spec_path)
        cls.generate_onnx_latent(dict_s2, onnx_latent_path)
        return (onnx_vq_model_path, onnx_spec_path, onnx_latent_path)

    @classmethod
    def generate_onnx_sovits(cls, dict_s2, onnx_path: Path):
        hps = DictToAttrRecursive(dict_s2["config"])
        vq_model_onnx = SynthesizerTrnOnnx(
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model,
        )
        vq_model_onnx = vq_model_onnx.cpu()
        vq_model_onnx.eval()
        vq_model_onnx.load_state_dict(dict_s2["weight"], strict=False)

        pred_semantic = torch.ones((1, 1, 66), dtype=torch.long)
        text_seq = torch.ones((1, 40), dtype=torch.long)
        ref_spec = torch.ones((1, 1025, 392), dtype=torch.float32)

        torch.onnx.export(
            vq_model_onnx,
            (pred_semantic, text_seq, ref_spec),
            onnx_path,
            input_names=["pred_semantic", "text_seq", "ref_spec"],
            output_names=["audio"],
            dynamic_axes={
                "pred_semantic": {2: "pred_length"},
                "text_seq": {1: "text_length"},
                "ref_spec": {2: "audio_length"},
            },
            opset_version=17,
            verbose=False,
        )

        model_onnx2 = onnx.load(onnx_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_path))

    @classmethod
    def generate_onnx_spec(cls, dict_s2, onnx_path: Path):
        hps = DictToAttrRecursive(dict_s2["config"])
        spec = Spectrogram(hps)
        audio = torch.ones((1, 32000), dtype=torch.float32)
        torch.onnx.export(
            spec,
            (audio,),
            onnx_path,
            input_names=["y"],
            output_names=["spec"],
            dynamic_axes={
                "y": {1: "audio_length"},
            },
            opset_version=17,
            verbose=False,
        )

        model_onnx2 = onnx.load(onnx_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_path))

    @classmethod
    def generate_onnx_latent(cls, dict_s2, onnx_path: Path):
        hps = DictToAttrRecursive(dict_s2["config"])
        synthesizer_latent = SynthesizerTrnLatent(
            hps.data.filter_length // 2 + 1,
            hps.train.segment_size // hps.data.hop_length,
            n_speakers=hps.data.n_speakers,
            **hps.model,
        )
        synthesizer_latent = synthesizer_latent.cpu()
        synthesizer_latent.eval()
        synthesizer_latent.load_state_dict(dict_s2["weight"], strict=False)

        ssl_content = torch.ones((1, 768, 32), dtype=torch.float32)

        torch.onnx.export(
            synthesizer_latent,
            (ssl_content),
            onnx_path,
            input_names=["ssl_content"],
            output_names=["prompt"],
            dynamic_axes={
                "ssl_content": {2: "content_length"},
            },
            opset_version=17,
            verbose=False,
        )

        model_onnx2 = onnx.load(onnx_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_path))
