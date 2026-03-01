from pathlib import Path

import torch

from ttsclient.tts.tts_manager.sv.eres2net.ERes2NetV2 import ERes2NetV2
from ttsclient.tts.tts_manager.sv.eres2net import kaldi as Kaldi

from ttsclient.tts.tts_manager.device_manager.device_manager import DeviceManager


class SVModel:
    def __init__(self, model_path: Path, device_id: int):
        device = DeviceManager.get_instance().get_pytorch_device(device_id)
        is_half = DeviceManager.get_instance().half_precision_available(device_id)

        pretrained_state = torch.load(model_path, map_location="cpu", weights_only=False)
        embedding_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
        embedding_model.load_state_dict(pretrained_state)
        embedding_model.eval()

        if is_half:
            self.embedding_model = embedding_model.half().to(device)
        else:
            self.embedding_model = embedding_model.to(device)

        self.is_half = is_half
        self.device = device

    @torch.no_grad()
    def compute_embedding(self, wav_16k: torch.Tensor) -> torch.Tensor:
        """Compute speaker verification embedding from 16kHz waveform.

        Args:
            wav_16k: 1D tensor of audio samples at 16kHz.

        Returns:
            sv_emb: 1D tensor of shape [20480].
        """
        if self.is_half:
            wav_16k = wav_16k.half()

        feat = Kaldi.fbank(
            wav_16k.unsqueeze(0),
            num_mel_bins=80,
            sample_frequency=16000,
            dither=0,
        )
        # feat: [T, 80] -> [1, T, 80]
        feat = feat.unsqueeze(0).to(self.device)

        sv_emb = self.embedding_model.forward3(feat)
        return sv_emb.squeeze(0)  # [20480]
