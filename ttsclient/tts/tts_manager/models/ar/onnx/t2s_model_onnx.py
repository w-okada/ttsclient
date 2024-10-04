import onnx
import torch
import torch.nn as nn
from onnxsim import simplify
import json

from ttsclient.tts.tts_manager.models.ar.onnx.t2s_lightning_module_onnx import Text2SemanticLightningModule


class T2SEncoder(nn.Module):
    def __init__(self, t2s):
        super().__init__()
        self.encoder = t2s.onnx_encoder

    # def forward(self, ref_seq, text_seq, ref_bert, text_bert):
    #     bert = torch.cat([ref_bert.transpose(0, 1), text_bert.transpose(0, 1)], 1)
    #     all_phoneme_ids = torch.cat([ref_seq, text_seq], 1)
    #     bert = bert.unsqueeze(0)
    #     return self.encoder(all_phoneme_ids, bert)

    def forward(self, all_phoneme_ids, bert):
        return self.encoder(all_phoneme_ids, bert)


class T2SModel(nn.Module):
    def __init__(self, t2s_path):
        super().__init__()
        dict_s1 = torch.load(t2s_path, map_location="cpu")
        self.config = dict_s1["config"]
        self.t2s_model = Text2SemanticLightningModule(self.config, "ojbk", is_train=False)
        self.t2s_model.load_state_dict(dict_s1["weight"])
        self.t2s_model.eval()
        self.hz = 50
        self.max_sec = self.config["data"]["max_sec"]
        self.t2s_model.model.top_k = torch.LongTensor([self.config["inference"]["top_k"]])
        self.t2s_model.model.early_stop_num = torch.LongTensor([self.hz * self.max_sec])
        self.t2s_model = self.t2s_model.model
        self.t2s_model.init_onnx()
        self.onnx_encoder = T2SEncoder(self.t2s_model)
        self.first_stage_decoder = self.t2s_model.first_stage_decoder
        self.stage_decoder = self.t2s_model.stage_decoder
        # self.t2s_model = torch.jit.script(self.t2s_model)

    def forward(self, ref_seq, text_seq, ref_bert, text_bert, prompts):
        early_stop_num = self.t2s_model.early_stop_num

        # [1,N] [1,N] [N, 1024] [N, 1024] [1, 768, N]
        x = self.onnx_encoder(ref_seq, text_seq, ref_bert, text_bert)

        prefix_len = prompts.shape[1]

        # [1,N,512] [1,N]
        y, k, v, y_emb, x_example = self.first_stage_decoder(x, prompts)

        stop = False
        for idx in range(1, 1500):
            # [1, N] [N_layer, N, 1, 512] [N_layer, N, 1, 512] [1, N, 512] [1] [1, N, 512] [1, N]
            enco = self.stage_decoder(y, k, v, y_emb, x_example)
            y, k, v, y_emb, logits, samples = enco
            if early_stop_num != -1 and (y.shape[1] - prefix_len) > early_stop_num:
                stop = True
            if torch.argmax(logits, dim=-1)[0] == self.t2s_model.EOS or samples[0, 0] == self.t2s_model.EOS:
                stop = True
            if stop:
                break
        y[0, -1] = 0

        return y[:, -idx:].unsqueeze(0)

    def export(
        self,
        all_phoneme_ids,
        bert,
        prompt,
        # ref_seq,
        # text_seq,
        # ref_bert,
        # text_bert,
        # prompts,
        onnx_encoder_path,
        onnx_fsdec_path,
        onnx_ssdec_path,
        dynamo=False,
    ):
        # self.onnx_encoder = torch.jit.script(self.onnx_encoder)
        # if dynamo:
        #     export_options = torch.onnx.ExportOptions(dynamic_shapes=True)
        #     onnx_encoder_export_output = torch.onnx.dynamo_export(
        #         self.onnx_encoder,
        #         (ref_seq, text_seq, ref_bert, text_bert),
        #         export_options=export_options,
        #     )
        #     onnx_encoder_export_output.save(f"onnx/{project_name}/{project_name}_t2s_encoder.onnx")
        #     return

        torch.onnx.export(
            self.onnx_encoder,
            (all_phoneme_ids, bert),
            onnx_encoder_path,
            input_names=["all_phoneme_ids", "bert"],
            output_names=["x"],
            dynamic_axes={
                "all_phoneme_ids": {1: "text_length"},
                "bert": {2: "content_length"},
            },
            opset_version=16,
        )

        model_onnx2 = onnx.load(onnx_encoder_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_encoder_path))

        x = self.onnx_encoder(all_phoneme_ids, bert)

        torch.onnx.export(
            self.first_stage_decoder,
            (x, prompt),
            onnx_fsdec_path,
            input_names=["x", "prompts"],
            output_names=["y", "k", "v", "y_emb", "x_example"],
            dynamic_axes={
                "x": {1: "x_length"},
                "prompts": {1: "prompts_length"},
            },
            verbose=False,
            opset_version=16,
        )

        model_onnx2 = onnx.load(onnx_fsdec_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_fsdec_path))

        y, k, v, y_emb, x_example = self.first_stage_decoder(x, prompt)

        torch.onnx.export(
            self.stage_decoder,
            (y, k, v, y_emb, x_example),
            onnx_ssdec_path,
            input_names=["iy", "ik", "iv", "iy_emb", "ix_example"],
            output_names=["y", "k", "v", "y_emb", "logits", "samples"],
            dynamic_axes={
                "iy": {1: "iy_length"},
                "ik": {1: "ik_length"},
                "iv": {1: "iv_length"},
                "iy_emb": {1: "iy_emb_length"},
                "ix_example": {1: "ix_example_length"},
            },
            verbose=False,
            opset_version=16,
        )

        model_onnx2 = onnx.load(onnx_ssdec_path)
        model_simp, check = simplify(model_onnx2)
        meta = model_simp.metadata_props.add()
        meta.key = "metadata"

        metadata = {
            "application": "TTS_CLIENT",
            "model-version": "1.0",
        }
        meta.value = json.dumps(metadata)
        onnx.save(model_simp, str(onnx_ssdec_path))
