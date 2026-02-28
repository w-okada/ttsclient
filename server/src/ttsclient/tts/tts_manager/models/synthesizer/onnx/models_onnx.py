from typing import Optional
import torch
import torch.nn as nn
from torch.nn import Conv1d, ConvTranspose1d
from torch.nn import functional as F
from torch.nn.utils import weight_norm, remove_weight_norm

from ttsclient.tts.tts_manager.models.synthesizer import modules
from ttsclient.tts.tts_manager.models.synthesizer.quantize import ResidualVectorQuantizer
from ttsclient.tts.tts_manager.utils.dict_to_attr_recursive import DictToAttrRecursive
from ttsclient.tts.tts_manager.models.synthesizer.onnx import attentions_onnx
from ttsclient.tts.tts_manager.text import symbols as symbols_v1
from ttsclient.tts.tts_manager.text import symbols2 as symbols_v2
from ttsclient.tts.tts_manager.models.synthesizer.commons import init_weights


class TextEncoder(nn.Module):
    def __init__(
        self,
        out_channels,
        hidden_channels,
        filter_channels,
        n_heads,
        n_layers,
        kernel_size,
        p_dropout,
        latent_channels=192,
        version="v2",
    ):
        super().__init__()
        self.out_channels = out_channels
        self.hidden_channels = hidden_channels
        self.filter_channels = filter_channels
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.kernel_size = kernel_size
        self.p_dropout = p_dropout
        self.latent_channels = latent_channels
        self.version = version

        self.ssl_proj = nn.Conv1d(768, hidden_channels, 1)

        self.encoder_ssl = attentions_onnx.Encoder(
            hidden_channels,
            filter_channels,
            n_heads,
            n_layers // 2,
            kernel_size,
            p_dropout,
        )

        self.encoder_text = attentions_onnx.Encoder(hidden_channels, filter_channels, n_heads, n_layers, kernel_size, p_dropout)

        if self.version == "v1":
            symbols = symbols_v1.symbols
        else:
            symbols = symbols_v2.symbols
        self.text_embedding = nn.Embedding(len(symbols), hidden_channels)

        self.mrte = attentions_onnx.MRTE()

        self.encoder2 = attentions_onnx.Encoder(
            hidden_channels,
            filter_channels,
            n_heads,
            n_layers // 2,
            kernel_size,
            p_dropout,
        )

        self.proj = nn.Conv1d(hidden_channels, out_channels * 2, 1)

    def forward(self, y, text, ge):
        y_mask = torch.ones_like(y[:1, :1, :])

        y = self.ssl_proj(y * y_mask) * y_mask
        y = self.encoder_ssl(y * y_mask, y_mask)

        text_mask = torch.ones_like(text).to(y.dtype).unsqueeze(0)

        text = self.text_embedding(text).transpose(1, 2)
        text = self.encoder_text(text * text_mask, text_mask)
        y = self.mrte(y, y_mask, text, text_mask, ge)

        y = self.encoder2(y * y_mask, y_mask)

        stats = self.proj(y) * y_mask
        m, logs = torch.split(stats, self.out_channels, dim=1)
        return y, m, logs, y_mask

    # def extract_latent(self, x):
    #     x = self.ssl_proj(x)
    #     quantized, codes, commit_loss, quantized_list = self.quantizer(x)
    #     return codes.transpose(0, 1)

    # def decode_latent(self, codes, y_mask, refer, refer_mask, ge):
    #     quantized = self.quantizer.decode(codes)

    #     y = self.vq_proj(quantized) * y_mask
    #     y = self.encoder_ssl(y * y_mask, y_mask)

    #     y = self.mrte(y, y_mask, refer, refer_mask, ge)

    #     y = self.encoder2(y * y_mask, y_mask)

    #     stats = self.proj(y) * y_mask
    #     m, logs = torch.split(stats, self.out_channels, dim=1)
    #     return y, m, logs, y_mask, quantized


class Generator(torch.nn.Module):
    def __init__(
        self,
        initial_channel,
        resblock,
        resblock_kernel_sizes,
        resblock_dilation_sizes,
        upsample_rates,
        upsample_initial_channel,
        upsample_kernel_sizes,
        gin_channels=0,
    ):
        super(Generator, self).__init__()
        self.num_kernels = len(resblock_kernel_sizes)
        self.num_upsamples = len(upsample_rates)
        self.conv_pre = Conv1d(initial_channel, upsample_initial_channel, 7, 1, padding=3)
        resblock = modules.ResBlock1 if resblock == "1" else modules.ResBlock2

        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(upsample_rates, upsample_kernel_sizes)):
            self.ups.append(
                weight_norm(
                    ConvTranspose1d(
                        upsample_initial_channel // (2**i),
                        upsample_initial_channel // (2 ** (i + 1)),
                        k,
                        u,
                        padding=(k - u) // 2,
                    )
                )
            )

        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = upsample_initial_channel // (2 ** (i + 1))
            for j, (k, d) in enumerate(zip(resblock_kernel_sizes, resblock_dilation_sizes)):
                self.resblocks.append(resblock(ch, k, d))

        self.conv_post = Conv1d(ch, 1, 7, 1, padding=3, bias=False)
        self.ups.apply(init_weights)

        if gin_channels != 0:
            self.cond = nn.Conv1d(gin_channels, upsample_initial_channel, 1)

    def forward(self, x, g: Optional[torch.Tensor] = None):
        x = self.conv_pre(x)
        if g is not None:
            x = x + self.cond(g)

        for i in range(self.num_upsamples):
            x = F.leaky_relu(x, modules.LRELU_SLOPE)
            x = self.ups[i](x)
            xs = None
            for j in range(self.num_kernels):
                if xs is None:
                    xs = self.resblocks[i * self.num_kernels + j](x)
                else:
                    xs += self.resblocks[i * self.num_kernels + j](x)
            x = xs / self.num_kernels
        x = F.leaky_relu(x)
        x = self.conv_post(x)
        x = torch.tanh(x)

        return x

    def remove_weight_norm(self):
        print("Removing weight norm...")
        for l in self.ups:  # noqa
            remove_weight_norm(l)
        for l in self.resblocks:  # noqa
            l.remove_weight_norm()


# class PosteriorEncoder(nn.Module):
#     def __init__(
#         self,
#         in_channels,
#         out_channels,
#         hidden_channels,
#         kernel_size,
#         dilation_rate,
#         n_layers,
#         gin_channels=0,
#     ):
#         super().__init__()
#         self.in_channels = in_channels
#         self.out_channels = out_channels
#         self.hidden_channels = hidden_channels
#         self.kernel_size = kernel_size
#         self.dilation_rate = dilation_rate
#         self.n_layers = n_layers
#         self.gin_channels = gin_channels

#         self.pre = nn.Conv1d(in_channels, hidden_channels, 1)
#         self.enc = modules.WN(
#             hidden_channels,
#             kernel_size,
#             dilation_rate,
#             n_layers,
#             gin_channels=gin_channels,
#         )
#         self.proj = nn.Conv1d(hidden_channels, out_channels * 2, 1)

#     def forward(self, x, x_lengths, g=None):
#         if g is not None:
#             g = g.detach()
#         x_mask = torch.unsqueeze(sequence_mask(x_lengths, x.size(2)), 1).to(x.dtype)
#         x = self.pre(x) * x_mask
#         x = self.enc(x, x_mask, g=g)
#         stats = self.proj(x) * x_mask
#         m, logs = torch.split(stats, self.out_channels, dim=1)
#         z = (m + torch.randn_like(m) * torch.exp(logs)) * x_mask
#         return z, m, logs, x_mask


class ResidualCouplingBlock(nn.Module):
    def __init__(
        self,
        channels,
        hidden_channels,
        kernel_size,
        dilation_rate,
        n_layers,
        n_flows=4,
        gin_channels=0,
    ):
        super().__init__()
        self.channels = channels
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        self.dilation_rate = dilation_rate
        self.n_layers = n_layers
        self.n_flows = n_flows
        self.gin_channels = gin_channels

        self.flows = nn.ModuleList()
        for i in range(n_flows):
            self.flows.append(
                modules.ResidualCouplingLayer(
                    channels,
                    hidden_channels,
                    kernel_size,
                    dilation_rate,
                    n_layers,
                    gin_channels=gin_channels,
                    mean_only=True,
                )
            )
            self.flows.append(modules.Flip())

    def forward(self, x, x_mask, g=None, reverse=False):
        if not reverse:
            for flow in self.flows:
                x, _ = flow(x, x_mask, g=g, reverse=reverse)
        else:
            for flow in reversed(self.flows):
                x = flow(x, x_mask, g=g, reverse=reverse)
        return x


class SynthesizerTrn(nn.Module):
    """
    Synthesizer for Training
    """

    def __init__(
        self,
        spec_channels,
        segment_size,
        inter_channels,
        hidden_channels,
        filter_channels,
        n_heads,
        n_layers,
        kernel_size,
        p_dropout,
        resblock,
        resblock_kernel_sizes,
        resblock_dilation_sizes,
        upsample_rates,
        upsample_initial_channel,
        upsample_kernel_sizes,
        n_speakers=0,
        gin_channels=0,
        use_sdp=True,
        semantic_frame_rate=None,
        freeze_quantizer=None,
        version="v2",
        **kwargs
    ):
        super().__init__()
        self.spec_channels = spec_channels
        self.inter_channels = inter_channels
        self.hidden_channels = hidden_channels
        self.filter_channels = filter_channels
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.kernel_size = kernel_size
        self.p_dropout = p_dropout
        self.resblock = resblock
        self.resblock_kernel_sizes = resblock_kernel_sizes
        self.resblock_dilation_sizes = resblock_dilation_sizes
        self.upsample_rates = upsample_rates
        self.upsample_initial_channel = upsample_initial_channel
        self.upsample_kernel_sizes = upsample_kernel_sizes
        self.segment_size = segment_size
        self.n_speakers = n_speakers
        self.gin_channels = gin_channels
        self.version = version

        self.use_sdp = use_sdp
        self.enc_p = TextEncoder(
            inter_channels,
            hidden_channels,
            filter_channels,
            n_heads,
            n_layers,
            kernel_size,
            p_dropout,
            version=version,
        )
        self.dec = Generator(
            inter_channels,
            resblock,
            resblock_kernel_sizes,
            resblock_dilation_sizes,
            upsample_rates,
            upsample_initial_channel,
            upsample_kernel_sizes,
            gin_channels=gin_channels,
        )
        # self.enc_q = PosteriorEncoder(
        #     spec_channels,
        #     inter_channels,
        #     hidden_channels,
        #     5,
        #     1,
        #     16,
        #     gin_channels=gin_channels,
        # )
        self.flow = ResidualCouplingBlock(inter_channels, hidden_channels, 5, 1, 4, gin_channels=gin_channels)

        # self.version=os.environ.get("version","v1")
        if self.version == "v1":
            self.ref_enc = modules.MelStyleEncoder(spec_channels, style_vector_dim=gin_channels)
        else:
            self.ref_enc = modules.MelStyleEncoder(704, style_vector_dim=gin_channels)

        ssl_dim = 768
        self.ssl_dim = ssl_dim
        assert semantic_frame_rate in ["25hz", "50hz"]
        self.semantic_frame_rate = semantic_frame_rate
        if semantic_frame_rate == "25hz":
            self.ssl_proj = nn.Conv1d(ssl_dim, ssl_dim, 2, stride=2)
        else:
            self.ssl_proj = nn.Conv1d(ssl_dim, ssl_dim, 1, stride=1)

        self.quantizer = ResidualVectorQuantizer(dimension=ssl_dim, n_q=1, bins=1024)
        if freeze_quantizer:
            self.ssl_proj.requires_grad_(False)
            self.quantizer.requires_grad_(False)
            # self.enc_p.text_embedding.requires_grad_(False)
            # self.enc_p.encoder_text.requires_grad_(False)
            # self.enc_p.mrte.requires_grad_(False)

    def forward(self, codes, text, refer):
        refer_mask = torch.ones_like(refer[:1, :1, :])
        if self.version == "v1":
            ge = self.ref_enc(refer * refer_mask, refer_mask)
        else:
            ge = self.ref_enc(refer[:, :704] * refer_mask, refer_mask)

        quantized = self.quantizer.decode(codes)
        if self.semantic_frame_rate == "25hz":
            dquantized = torch.cat([quantized, quantized]).permute(1, 2, 0)
            quantized = dquantized.contiguous().view(1, self.ssl_dim, -1)

        x, m_p, logs_p, y_mask = self.enc_p(quantized, text, ge)

        z_p = m_p + torch.randn_like(m_p) * torch.exp(logs_p)

        z = self.flow(z_p, y_mask, g=ge, reverse=True)

        o = self.dec((z * y_mask)[:, :, :], g=ge)
        return o

    # def extract_latent(self, x):
    #     ssl = self.ssl_proj(x)
    #     quantized, codes, commit_loss, quantized_list = self.quantizer(ssl)
    #     return codes.transpose(0, 1)


class SynthesizerTrnLatent(SynthesizerTrn):
    def forward(self, x):
        ssl = self.ssl_proj(x)
        quantized, codes, commit_loss, quantized_list = self.quantizer(ssl)
        return codes.transpose(0, 1)


def spectrogram_torch(y, n_fft, sampling_rate, hop_size, win_size, center=False):
    hann_window = torch.hann_window(win_size).to(dtype=y.dtype, device=y.device)
    y = torch.nn.functional.pad(
        y.unsqueeze(1),
        (int((n_fft - hop_size) / 2), int((n_fft - hop_size) / 2)),
        mode="reflect",
    )
    y = y.squeeze(1)
    spec = torch.stft(
        y,
        n_fft,
        hop_length=hop_size,
        win_length=win_size,
        window=hann_window,
        center=center,
        pad_mode="reflect",
        normalized=False,
        onesided=True,
        return_complex=False,
    )
    spec = torch.sqrt(spec.pow(2).sum(-1) + 1e-6)
    return spec


class VitsModel(nn.Module):
    def __init__(self, vits_path):
        super().__init__()
        dict_s2 = torch.load(vits_path, map_location="cpu")
        self.hps = dict_s2["config"]
        if dict_s2["weight"]["enc_p.text_embedding.weight"].shape[0] == 322:
            self.hps["model"]["version"] = "v1"
        else:
            self.hps["model"]["version"] = "v2"

        self.hps = DictToAttrRecursive(self.hps)
        self.hps.model.semantic_frame_rate = "25hz"
        self.vq_model = SynthesizerTrn(
            self.hps.data.filter_length // 2 + 1,
            self.hps.train.segment_size // self.hps.data.hop_length,
            n_speakers=self.hps.data.n_speakers,
            **self.hps.model,
        )
        self.vq_model.eval()
        self.vq_model.load_state_dict(dict_s2["weight"], strict=False)

    def forward(self, text_seq, pred_semantic, ref_audio):
        refer = spectrogram_torch(
            ref_audio,
            self.hps.data.filter_length,
            self.hps.data.sampling_rate,
            self.hps.data.hop_length,
            self.hps.data.win_length,
            center=False,
        )
        return self.vq_model(pred_semantic, text_seq, refer)[0, 0]


class Spectrogram(nn.Module):
    def __init__(self, hps):
        super().__init__()
        self.n_fft = hps.data.filter_length
        self.sampling_rate = hps.data.sampling_rate
        self.hop_size = hps.data.hop_length
        self.win_size = hps.data.win_length
        self.center = False

    def forward(self, y):
        hann_window = torch.hann_window(self.win_size).to(dtype=y.dtype, device=y.device)
        y = torch.nn.functional.pad(
            y.unsqueeze(1),
            (int((self.n_fft - self.hop_size) / 2), int((self.n_fft - self.hop_size) / 2)),
            mode="reflect",
        )
        y = y.squeeze(1)
        spec = torch.stft(
            y,
            self.n_fft,
            hop_length=self.hop_size,
            win_length=self.win_size,
            window=hann_window,
            center=self.center,
            pad_mode="reflect",
            normalized=False,
            onesided=True,
            return_complex=False,
        )
        spec = torch.sqrt(spec.pow(2).sum(-1) + 1e-6)
        return spec
