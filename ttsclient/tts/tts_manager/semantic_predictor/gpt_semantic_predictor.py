from pathlib import Path

import numpy as np
import torch
import onnxruntime
from tqdm import tqdm
from ttsclient.tts.tts_manager.models.ar.onnx.t2s_model_onnx import T2SModel
from ttsclient.tts.tts_manager.models.ar.t2s_lightning_module import Text2SemanticLightningModule
from ttsclient.tts.tts_manager.semantic_predictor.semantic_predictor_info import SemanticPredictorInfo
from ttsclient.tts.tts_manager.semantic_predictor.smantic_predictor import SemanticPredictor
from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager


class GPTSemanticPredictor(SemanticPredictor):
    info: SemanticPredictorInfo
    t2s_model: Text2SemanticLightningModule

    def __init__(self, model_path: Path, device_id: int, use_onnx: bool):
        print("load new semantic_predictor: GPTSemanticPredictor")

        self.device = DeviceManager.get_instance().get_pytorch_device(device_id)
        self.is_half = DeviceManager.get_instance().half_precision_available(device_id)
        self.model_path = model_path

        onnx_encoder_stem = self.model_path.stem + "_encoder"
        self.onnx_encoder_path = self.model_path.with_name(onnx_encoder_stem).with_suffix(".onnx")
        onnx_fsdec_stem = self.model_path.stem + "_fsdec"
        self.onnx_fsdec_path = self.model_path.with_name(onnx_fsdec_stem).with_suffix(".onnx")
        onnx_ssdec_stem = self.model_path.stem + "_ssdec"
        self.onnx_ssdec_path = self.model_path.with_name(onnx_ssdec_stem).with_suffix(".onnx")

        self.use_onnx = use_onnx

        dict_s1 = torch.load(model_path, map_location="cpu")
        config = dict_s1["config"]

        if self.use_onnx is False:
            self.t2s_model = Text2SemanticLightningModule(config, output_dir="****", is_train=False)

            max_sec = config["data"]["max_sec"]

            self.t2s_model.load_state_dict(dict_s1["weight"])
            if self.is_half is True:
                self.t2s_model = self.t2s_model.half()
                # self.t2s_model.model = self.t2s_model.model.half()
            self.t2s_model = self.t2s_model.to(self.device)
            # self.t2s_model.model = self.t2s_model.model.to(self.device)

            self.t2s_model.eval()

            self.info = SemanticPredictorInfo(
                semantic_predictor_type="GPTSemanticPredictor",
                path=model_path,
                hz=50,
                max_sec=max_sec,
            )

        else:

            # #####################
            # ONNX
            # #####################
            self.eos = config["model"]["EOS"]

            (
                onnx_providers,
                onnx_provider_options,
            ) = DeviceManager.get_instance().get_onnx_execution_provider(device_id=device_id)

            self.candidate_onnx_providers = onnx_providers
            self.candidate_onnx_provider_options = onnx_provider_options

            # print("self.candidate_onnx_providers", self.candidate_onnx_providers)
            # print("self.candidate_onnx_provider_options", self.candidate_onnx_provider_options)

            so = onnxruntime.SessionOptions()
            so.log_severity_level = 3

            if self.onnx_encoder_path.exists() is True:
                self.onnx_session_encoder = onnxruntime.InferenceSession(str(self.onnx_encoder_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
                self.onnx_session_fsdec = onnxruntime.InferenceSession(str(self.onnx_fsdec_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
                self.onnx_session_ssdec = onnxruntime.InferenceSession(str(self.onnx_ssdec_path), sess_options=so, providers=onnx_providers, provider_options=onnx_provider_options)
            else:
                self.onnx_session_encoder = None
                self.onnx_session_fsdec = None
                self.onnx_session_ssdec = None

    def get_info(self) -> SemanticPredictorInfo:
        return self.info

    def predict(
        self,
        all_phoneme_ids: torch.Tensor,
        all_phoneme_len: torch.Tensor,
        prompt: torch.Tensor | None,
        bert: torch.Tensor,
        top_k: int,
        top_p: float,
        temperature: float,
    ) -> torch.Tensor:

        if self.use_onnx is True and self.onnx_session_encoder is not None:
            pred_semantic = torch.Tensor(self.predict_onnx(all_phoneme_ids, all_phoneme_len, prompt, bert, top_k, top_p, temperature)).to(torch.int64)

        else:
            pred_semantic, idx = self.t2s_model.model.infer_panel(
                all_phoneme_ids,
                all_phoneme_len,
                prompt,  # 参照なしの場合　None を入れる。
                bert,
                top_k=top_k,
                top_p=top_p,
                temperature=temperature,
                early_stop_num=self.info.hz * self.info.max_sec,
            )
            pred_semantic = pred_semantic[:, -idx:].unsqueeze(0)

        return pred_semantic

    def predict_onnx(
        self,
        all_phoneme_ids: torch.Tensor,
        all_phoneme_len: torch.Tensor,
        prompt: torch.Tensor | None,
        bert: torch.Tensor,
        top_k: int,
        top_p: float,
        temperature: float,
    ):
        print("semantice predictor run with onnx")
        # early_stop_num = self.t2s_model.early_stop_num
        early_stop_num = 100

        (x,) = self.onnx_session_encoder.run(
            ["x"],
            {
                "all_phoneme_ids": all_phoneme_ids.cpu().numpy(),
                "bert": bert.cpu().numpy(),
            },
        )

        assert prompt is not None
        prefix_len = prompt.shape[1]

        (y, k, v, y_emb, x_example) = self.onnx_session_fsdec.run(
            ["y", "k", "v", "y_emb", "x_example"],
            {
                "x": x,
                "prompts": prompt.cpu().numpy(),
            },
        )

        stop = False
        for idx in tqdm(range(1500)):
            # [1, N] [N_layer, N, 1, 512] [N_layer, N, 1, 512] [1, N, 512] [1] [1, N, 512] [1, N]
            (y, k, v, y_emb, logits, samples) = self.onnx_session_ssdec.run(
                ["y", "k", "v", "y_emb", "logits", "samples"],
                {
                    "iy": y,
                    "ik": k,
                    "iv": v,
                    "iy_emb": y_emb,
                    "ix_example": x_example,
                },
            )

            # logits_torch = torch.Tensor(logits)
            # print(f"logits_torch1: {logits_torch.shape}")
            # print(f"logits_torch2: {logits_torch}")

            if early_stop_num != -1 and (y.shape[1] - prefix_len) > early_stop_num:
                stop = True
            # if torch.argmax(torch.Tensor(logits), dim=-1)[0] == self.t2s_model.model.EOS or samples[0, 0] == self.t2s_model.model.EOS:
            if torch.argmax(torch.Tensor(logits), dim=-1)[0] == self.eos or samples[0, 0] == self.eos:

                stop = True
            if stop:
                break
        y[0, -1] = 0
        sliced_y = y[:, -idx:]
        unsqueezed_y = np.expand_dims(sliced_y, axis=0)
        return unsqueezed_y
        # return y[:, -idx:].unsqueeze(0)

    # #####################################
    # ONNXエクスポート用
    # #####################################
    @classmethod
    def generate_onnx(cls, model_path: Path):
        t2s_model = T2SModel(str(model_path))

        onnx_encoder_stem = model_path.stem + "_encoder"
        onnx_encoder_path = model_path.with_name(onnx_encoder_stem).with_suffix(".onnx")
        onnx_fsdec_stem = model_path.stem + "_fsdec"
        onnx_fsdec_path = model_path.with_name(onnx_fsdec_stem).with_suffix(".onnx")
        onnx_ssdec_stem = model_path.stem + "_ssdec"
        onnx_ssdec_path = model_path.with_name(onnx_ssdec_stem).with_suffix(".onnx")

        all_phoneme_ids = torch.ones((1, 98), dtype=torch.long)
        prompt = torch.ones((1, 236), dtype=torch.long)
        bert = torch.ones((1, 1024, 98), dtype=torch.float32)

        t2s_model.export(
            all_phoneme_ids,
            bert,
            prompt,
            onnx_encoder_path,
            onnx_fsdec_path,
            onnx_ssdec_path,
        )

        return (onnx_encoder_path, onnx_fsdec_path, onnx_ssdec_path)
