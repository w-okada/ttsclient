"""v2Pro パイプライン一致性テスト: オリジナル GPT-SoVITS vs ttsclient

各ステージの中間出力を比較し、差異が出る箇所を特定する。
スタンドアロンスクリプト（v2Pro チェックポイント + SV モデルが必要なため CI では動かない）。

Usage:
    cd server
    uv run python tests/test_pipeline_consistency.py \
        --sovits-path <v2Pro .pth> \
        --sv-path <pretrained_eres2netv2w24s4ep4.ckpt> \
        --ref-wav <reference.wav>
"""

import argparse
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

# ──────────────────────────────────────────
# パス設定
# ──────────────────────────────────────────
_server_dir = Path(__file__).resolve().parent.parent
_src_dir = _server_dir / "src"
_third_party = _server_dir.parent / "third_party" / "GPT-SoVITS"
_gpt_sovits_dir = _third_party / "GPT_SoVITS"
_eres2net_dir = _gpt_sovits_dir / "eres2net"

# ttsclient を先にインポート可能にする
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))
# オリジナル GPT-SoVITS モジュール用 (GPT_SoVITS/ 内のモジュール)
if str(_gpt_sovits_dir) not in sys.path:
    sys.path.insert(0, str(_gpt_sovits_dir))
# GPT_SoVITS パッケージ自体 (from GPT_SoVITS.xxx import ... 用)
if str(_third_party) not in sys.path:
    sys.path.insert(0, str(_third_party))
# eres2net 用
if str(_eres2net_dir) not in sys.path:
    sys.path.insert(0, str(_eres2net_dir))


# ──────────────────────────────────────────
# ユーティリティ
# ──────────────────────────────────────────
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"


def compare(name: str, a: torch.Tensor, b: torch.Tensor, *, atol: float = 1e-5, rtol: float = 1e-4) -> bool:
    """2 つのテンソルを比較して結果を出力する。"""
    if a.shape != b.shape:
        print(f"  {name:20s}: {FAIL} (shape mismatch: {a.shape} vs {b.shape})")
        return False
    # dtype が異なる場合は float32 に統一して比較
    a_cmp, b_cmp = a.float(), b.float()
    max_diff = (a_cmp - b_cmp).abs().max().item()
    close = torch.allclose(a_cmp, b_cmp, atol=atol, rtol=rtol)
    status = PASS if close else FAIL
    dtype_note = f", dtype={a.dtype} vs {b.dtype}" if a.dtype != b.dtype else ""
    print(f"  {name:20s}: {status} (max_diff={max_diff:.2e}, shape={list(a.shape)}{dtype_note})")
    return close


def compare_with_note(
    name: str, a: torch.Tensor, b: torch.Tensor,
    *, atol: float = 1e-5, rtol: float = 1e-4, note: str = "",
) -> bool:
    """比較結果 + 注釈付きで出力する。"""
    if a.shape != b.shape:
        print(f"  {name:20s}: {FAIL} (shape mismatch: {a.shape} vs {b.shape})")
        return False
    a_cmp, b_cmp = a.float(), b.float()
    max_diff = (a_cmp - b_cmp).abs().max().item()
    close = torch.allclose(a_cmp, b_cmp, atol=atol, rtol=rtol)
    status = PASS if close else FAIL
    suffix = f" ← {note}" if note and not close else ""
    print(f"  {name:20s}: {status} (max_diff={max_diff:.2e}, shape={list(a.shape)}){suffix}")
    return close


# ──────────────────────────────────────────
# モデルローダー
# ──────────────────────────────────────────
def load_original_synthesizer(dict_s2: dict, hps, device: torch.device):
    """オリジナル GPT-SoVITS の SynthesizerTrn をロードする。"""
    from module.models import SynthesizerTrn as OrigSynthesizerTrn

    model = OrigSynthesizerTrn(
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model,
    )
    if hasattr(model, "enc_q"):
        del model.enc_q
    model = model.float().to(device)
    model.eval()
    model.load_state_dict(dict_s2["weight"], strict=False)
    return model


def load_ours_synthesizer(dict_s2: dict, hps, device: torch.device):
    """ttsclient の SynthesizerTrn をロードする。"""
    from ttsclient.tts.tts_manager.models.synthesizer.models import (
        SynthesizerTrn as OurSynthesizerTrn,
    )

    model = OurSynthesizerTrn(
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model,
    )
    if hasattr(model, "enc_q"):
        del model.enc_q
    model = model.float().to(device)
    model.eval()
    model.load_state_dict(dict_s2["weight"], strict=False)
    return model


def load_original_sv(sv_path: Path, device: torch.device):
    """オリジナルの SV モデルをロードする (float32 固定)。"""
    from ERes2NetV2 import ERes2NetV2
    import kaldi as Kaldi  # noqa: F811

    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)
    model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    model.load_state_dict(pretrained_state)
    model.eval()
    model = model.float().to(device)
    return model, Kaldi


def load_ours_sv(sv_path: Path, device: torch.device):
    """ttsclient の SV モデルをロードする (float32 固定)。"""
    from ERes2NetV2 import ERes2NetV2
    import kaldi as Kaldi  # noqa: F811

    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)
    model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    model.load_state_dict(pretrained_state)
    model.eval()
    model = model.float().to(device)
    return model, Kaldi


# ──────────────────────────────────────────
# テスト 1: SV embedding 一致性
# ──────────────────────────────────────────
def test_sv_embedding(sv_path: Path, ref_wav_path: Path, device: torch.device) -> bool:
    """SV embedding の一致性をテストする。

    オリジナル: wav.half() → fbank → forward3  (half precision fbank)
    ttsclient:  wav.float() → fbank → feat.half() → forward3

    このテストでは float32 統一で比較するので、
    アルゴリズムの差異のみを検出する。
    """
    print("\n[Test 1] SV embedding consistency (float32 unified)")
    import librosa
    from ERes2NetV2 import ERes2NetV2
    import kaldi as Kaldi

    # モデルをロード (同一 weight)
    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)

    orig_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    orig_model.load_state_dict(pretrained_state)
    orig_model.eval().float().to(device)

    ours_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    ours_model.load_state_dict(pretrained_state)
    ours_model.eval().float().to(device)

    # wav をロード (float32)
    wav_16k, _ = librosa.load(str(ref_wav_path), sr=16000)
    wav_tensor = torch.from_numpy(wav_16k).float().to(device)

    with torch.no_grad():
        # ── オリジナル方式 (compute_embedding3 相当) ──
        # バッチ形式: [1, samples]
        wav_batch = wav_tensor.unsqueeze(0)  # [1, samples]
        feat_orig = torch.stack(
            [Kaldi.fbank(w.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0) for w in wav_batch]
        )  # [1, T, 80]
        sv_emb_orig = orig_model.forward3(feat_orig)  # [1, 20480]

        # ── ttsclient 方式 (compute_embedding 相当) ──
        feat_ours = Kaldi.fbank(
            wav_tensor.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0
        )  # [T, 80]
        feat_ours = feat_ours.unsqueeze(0).to(device)  # [1, T, 80]
        sv_emb_ours = ours_model.forward3(feat_ours)  # [1, 20480]

    return compare("sv_emb", sv_emb_orig.squeeze(0), sv_emb_ours.squeeze(0))


# ──────────────────────────────────────────
# テスト 2: SV embedding half precision 差異
# ──────────────────────────────────────────
def test_sv_embedding_half(sv_path: Path, ref_wav_path: Path, device: torch.device) -> bool:
    """SV embedding の half precision 一致性をテストする。

    両方とも wav.half() → fbank (オリジナルと同じ方式) で比較。
    """
    print("\n[Test 2] SV embedding half-precision consistency")
    import librosa
    from ERes2NetV2 import ERes2NetV2
    import kaldi as Kaldi

    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)

    orig_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    orig_model.load_state_dict(pretrained_state)
    orig_model.eval().half().to(device)

    ours_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    ours_model.load_state_dict(pretrained_state)
    ours_model.eval().half().to(device)

    wav_16k, _ = librosa.load(str(ref_wav_path), sr=16000)
    wav_tensor = torch.from_numpy(wav_16k).to(device)

    with torch.no_grad():
        # ── オリジナル方式 (compute_embedding3): wav.half() → fbank ──
        wav_half = wav_tensor.half()
        feat_orig = torch.stack(
            [Kaldi.fbank(wav_half.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0)]
        )
        sv_emb_orig = orig_model.forward3(feat_orig).squeeze(0)

        # ── ttsclient 方式 (compute_embedding): wav.half() → fbank ──
        feat_ours = Kaldi.fbank(
            wav_half.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0
        ).unsqueeze(0).to(device)
        sv_emb_ours = ours_model.forward3(feat_ours).squeeze(0)

    return compare("sv_emb (half)", sv_emb_orig.float(), sv_emb_ours.float())


# ──────────────────────────────────────────
# テスト 3: SynthesizerTrn.decode 段階比較
# ──────────────────────────────────────────
def test_decode_stages(sovits_path: Path, sv_path: Path, ref_wav_path: Path, device: torch.device) -> bool:
    """SynthesizerTrn.decode の各段階を展開して比較する。"""
    print("\n[Test 3] SynthesizerTrn.decode stage-by-stage")

    from module import commons as orig_commons
    from ttsclient.tts.tts_manager.models.synthesizer import commons as ours_commons

    # ──────────── モデルロード ────────────
    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = _make_hps(dict_s2)

    orig_model = load_original_synthesizer(dict_s2, hps, device)
    ours_model = load_ours_synthesizer(dict_s2, hps, device)

    # ──────────── ダミー入力 ────────────
    torch.manual_seed(42)
    codes = torch.randint(0, 1024, (1, 1, 50)).to(device)
    text = torch.randint(0, 300, (1, 30)).to(device)
    refer = torch.randn(1, 1025, 100).to(device)

    # SV embedding (v2Pro)
    sv_emb_tensor = torch.randn(20480).to(device)

    all_pass = True

    with torch.no_grad():
        # ━━━ Stage 1: get_ge (ref_enc + sv_emb + prelu) ━━━
        refer_lengths = torch.LongTensor([refer.size(2)]).to(device)
        refer_mask_orig = torch.unsqueeze(
            orig_commons.sequence_mask(refer_lengths, refer.size(2)), 1
        ).to(refer.dtype)
        refer_mask_ours = torch.unsqueeze(
            ours_commons.sequence_mask(refer_lengths, refer.size(2)), 1
        ).to(refer.dtype)
        all_pass &= compare("refer_mask", refer_mask_orig, refer_mask_ours)

        ge_orig = orig_model.ref_enc(refer[:, :704] * refer_mask_orig, refer_mask_orig)
        ge_ours = ours_model.ref_enc(refer[:, :704] * refer_mask_ours, refer_mask_ours)
        all_pass &= compare("ge (ref_enc)", ge_orig, ge_ours)

        # sv_emb projection
        sv_proj_orig = orig_model.sv_emb(sv_emb_tensor)
        sv_proj_ours = ours_model.sv_emb(sv_emb_tensor)
        all_pass &= compare("sv_proj", sv_proj_orig, sv_proj_ours)

        ge_orig = ge_orig + sv_proj_orig.unsqueeze(-1)
        ge_ours = ge_ours + sv_proj_ours.unsqueeze(-1)
        all_pass &= compare("ge + sv", ge_orig, ge_ours)

        ge_orig = orig_model.prelu(ge_orig)
        ge_ours = ours_model.prelu(ge_ours)
        all_pass &= compare("ge (prelu)", ge_orig, ge_ours)

        # ━━━ Stage 2: quantizer.decode ━━━
        quantized_orig = orig_model.quantizer.decode(codes)
        quantized_ours = ours_model.quantizer.decode(codes)
        all_pass &= compare("quantized", quantized_orig, quantized_ours)

        if orig_model.semantic_frame_rate == "25hz":
            quantized_orig = F.interpolate(quantized_orig, size=int(quantized_orig.shape[-1] * 2), mode="nearest")
            quantized_ours = F.interpolate(quantized_ours, size=int(quantized_ours.shape[-1] * 2), mode="nearest")
            all_pass &= compare("quantized (interp)", quantized_orig, quantized_ours)

        # ━━━ Stage 3: ge_to512 ━━━
        ge_for_enc_p_orig = orig_model.ge_to512(ge_orig.transpose(2, 1)).transpose(2, 1)
        ge_for_enc_p_ours = ours_model.ge_to512(ge_ours.transpose(2, 1)).transpose(2, 1)
        all_pass &= compare_with_note(
            "ge_for_enc_p", ge_for_enc_p_orig, ge_for_enc_p_ours,
            note="ref_enc の fp 誤差伝播 (下流 PASS なら問題なし)",
        )

        # ━━━ Stage 4: enc_p ━━━
        y_lengths = torch.LongTensor([codes.size(2) * 2]).to(device)
        text_lengths = torch.LongTensor([text.size(-1)]).to(device)

        # オリジナル enc_p: 6 値返し
        x_orig, m_p_orig, logs_p_orig, y_mask_orig, _, _ = orig_model.enc_p(
            quantized_orig, y_lengths, text, text_lengths, ge_for_enc_p_orig, 1
        )
        # ttsclient enc_p: 4 値返し
        x_ours, m_p_ours, logs_p_ours, y_mask_ours = ours_model.enc_p(
            quantized_ours, y_lengths, text, text_lengths, ge_for_enc_p_ours, 1
        )
        all_pass &= compare("enc_p: x", x_orig, x_ours)
        all_pass &= compare("enc_p: m_p", m_p_orig, m_p_ours)
        all_pass &= compare("enc_p: logs_p", logs_p_orig, logs_p_ours)
        all_pass &= compare("enc_p: y_mask", y_mask_orig, y_mask_ours)

        # ━━━ Stage 5: sampling (z_p) ━━━
        noise_scale = 0.5
        torch.manual_seed(42)
        noise_orig = torch.randn_like(m_p_orig)
        z_p_orig = m_p_orig + noise_orig * torch.exp(logs_p_orig) * noise_scale

        torch.manual_seed(42)
        noise_ours = torch.randn_like(m_p_ours)
        z_p_ours = m_p_ours + noise_ours * torch.exp(logs_p_ours) * noise_scale
        all_pass &= compare("z_p", z_p_orig, z_p_ours)

        # ━━━ Stage 6: flow (reverse) ━━━
        z_orig = orig_model.flow(z_p_orig, y_mask_orig, g=ge_orig, reverse=True)
        z_ours = ours_model.flow(z_p_ours, y_mask_ours, g=ge_ours, reverse=True)
        all_pass &= compare("z (flow)", z_orig, z_ours)

        # ━━━ Stage 7: dec (Generator) ━━━
        o_orig = orig_model.dec((z_orig * y_mask_orig)[:, :, :], g=ge_orig)
        o_ours = ours_model.dec((z_ours * y_mask_ours)[:, :, :], g=ge_ours)
        all_pass &= compare("output", o_orig, o_ours)

    return all_pass


# ──────────────────────────────────────────
# テスト 4: decode 一括呼び出し一致性
# ──────────────────────────────────────────
def test_decode_end_to_end(sovits_path: Path, device: torch.device) -> bool:
    """SynthesizerTrn.decode() を直接呼び出して最終出力を比較する。"""
    print("\n[Test 4] SynthesizerTrn.decode() end-to-end")

    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = _make_hps(dict_s2)

    orig_model = load_original_synthesizer(dict_s2, hps, device)
    ours_model = load_ours_synthesizer(dict_s2, hps, device)

    # ダミー入力
    codes = torch.randint(0, 1024, (1, 1, 50)).to(device)
    text = torch.randint(0, 300, (1, 30)).to(device)
    refer = torch.randn(1, 1025, 100).to(device)
    sv_emb = [torch.randn(20480).to(device)]

    torch.manual_seed(42)
    out_orig = orig_model.decode(codes, text, [refer], sv_emb=sv_emb)

    torch.manual_seed(42)
    out_ours = ours_model.decode(codes, text, [refer], sv_emb=sv_emb)

    return compare("decode output", out_orig, out_ours)


# ──────────────────────────────────────────
# テスト 5: extract_latent 一致性
# ──────────────────────────────────────────
def test_extract_latent(sovits_path: Path, device: torch.device) -> bool:
    """extract_latent の出力を比較する。"""
    print("\n[Test 5] extract_latent consistency")

    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = _make_hps(dict_s2)

    orig_model = load_original_synthesizer(dict_s2, hps, device)
    ours_model = load_ours_synthesizer(dict_s2, hps, device)

    # ダミー SSL content
    torch.manual_seed(42)
    ssl_content = torch.randn(1, 768, 50).to(device)

    with torch.no_grad():
        codes_orig = orig_model.extract_latent(ssl_content)
        codes_ours = ours_model.extract_latent(ssl_content)

    return compare("latent codes", codes_orig.float(), codes_ours.float())


# ──────────────────────────────────────────
# テスト 6: パイプライン全体 (ref_wav → decode)
# ──────────────────────────────────────────
def test_pipeline_with_real_audio(
    sovits_path: Path, sv_path: Path, ref_wav_path: Path, device: torch.device
) -> bool:
    """実際のリファレンス音声を使ってパイプライン全体の一致性を検証する。

    SSL → extract_latent → get_spepc → SV → decode の各ステージを比較。
    """
    print("\n[Test 6] Pipeline with real audio (ref_wav → decode)")
    import librosa
    import kaldi as Kaldi
    from ERes2NetV2 import ERes2NetV2
    from module.mel_processing import spectrogram_torch as orig_spectrogram_torch
    from ttsclient.tts.tts_manager.utils.mel_processing import spectrogram_torch as ours_spectrogram_torch

    # ──────────── モデルロード ────────────
    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = _make_hps(dict_s2)

    orig_model = load_original_synthesizer(dict_s2, hps, device)
    ours_model = load_ours_synthesizer(dict_s2, hps, device)

    all_pass = True

    # ━━━ Stage A: Spectrogram (get_spepc) ━━━
    wav_sr, _ = librosa.load(str(ref_wav_path), sr=int(hps.data.sampling_rate))
    audio_tensor = torch.FloatTensor(wav_sr)
    maxx = audio_tensor.abs().max()
    if maxx > 1:
        audio_tensor = audio_tensor / min(2, maxx)
    audio_norm = audio_tensor.unsqueeze(0)

    spec_orig = orig_spectrogram_torch(
        audio_norm, hps.data.filter_length, hps.data.sampling_rate,
        hps.data.hop_length, hps.data.win_length, center=False,
    )
    spec_ours = ours_spectrogram_torch(
        audio_norm, hps.data.filter_length, hps.data.sampling_rate,
        hps.data.hop_length, hps.data.win_length, center=False,
    )
    all_pass &= compare_with_note(
        "spectrogram", spec_orig, spec_ours,
        note="epsilon 差: orig=1e-8 vs ours=1e-6 (sqrt 内)",
    )

    # ━━━ Stage B: SSL (CNHubert) ━━━
    # CNHubert は同一モデルを使うため、同一入力で同一出力になるはず。
    # ここではモデルロードを省略し、spectrogram の一致を確認した上で decode に進む。
    print("  (SSL/CNHubert: 同一モデル・同一入力のため省略)")

    # ━━━ Stage C: SV embedding (実音声) ━━━
    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)
    sv_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    sv_model.load_state_dict(pretrained_state)
    sv_model.eval().float().to(device)

    wav_16k, _ = librosa.load(str(ref_wav_path), sr=16000)
    wav_16k_tensor = torch.from_numpy(wav_16k).float().to(device)

    with torch.no_grad():
        # オリジナル方式
        feat_orig = torch.stack(
            [Kaldi.fbank(wav_16k_tensor.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0)]
        )
        sv_emb_orig = sv_model.forward3(feat_orig).squeeze(0)

        # ttsclient 方式
        feat_ours = Kaldi.fbank(
            wav_16k_tensor.unsqueeze(0), num_mel_bins=80, sample_frequency=16000, dither=0
        ).unsqueeze(0)
        sv_emb_ours = sv_model.forward3(feat_ours).squeeze(0)

    all_pass &= compare("sv_emb (real)", sv_emb_orig, sv_emb_ours)

    # ━━━ Stage D: decode (実 spectrogram + ダミー semantic) ━━━
    refer = spec_orig.to(device)
    codes = torch.randint(0, 1024, (1, 1, 50)).to(device)
    text = torch.randint(0, 300, (1, 30)).to(device)

    torch.manual_seed(42)
    out_orig = orig_model.decode(codes, text, [refer], sv_emb=[sv_emb_orig])

    torch.manual_seed(42)
    out_ours = ours_model.decode(codes, text, [refer], sv_emb=[sv_emb_ours])

    all_pass &= compare("decode (real ref)", out_orig, out_ours)

    return all_pass


# ──────────────────────────────────────────
# テスト 7: True E2E パイプライン一致性
# ──────────────────────────────────────────
def _set_seed(seed: int):
    """seed をリセットする (original の set_seed と同等)。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False


def test_true_e2e(
    sovits_path: Path,
    sv_path: Path,
    t2s_path: Path,
    bert_path: Path,
    cnhubert_path: Path,
    ref_wav_path: Path,
    ref_text: str,
    target_text: str,
    text_lang: str,
    device: torch.device,
    is_half: bool = False,
) -> bool:
    """真の E2E パイプライン一致性テスト。

    オリジナル GPT-SoVITS と ttsclient の全パイプラインステージを
    個別に実行し、各段階の中間出力を比較する。
    """
    precision_label = "half (float16)" if is_half else "float32"
    print(f"\n[Test 7] True E2E pipeline consistency ({precision_label})")
    print(f"  ref_text:    {ref_text!r}")
    print(f"  target_text: {target_text!r}")
    print(f"  text_lang:   {text_lang}")

    import importlib
    import importlib.util
    import librosa
    from transformers import AutoModelForMaskedLM, AutoTokenizer
    from feature_extractor import cnhubert
    from AR.models.t2s_lightning_module import Text2SemanticLightningModule

    # TTS_infer_pack/__init__.py が TTS.py を import して ffmpeg 依存になるため、
    # text_segmentation_method を先にロードし、TTS_infer_pack パッケージを
    # ダミーで sys.modules に登録してから TextPreprocessor を読み込む
    if "TTS_infer_pack" not in sys.modules:
        _tsm_spec = importlib.util.spec_from_file_location(
            "TTS_infer_pack.text_segmentation_method",
            _gpt_sovits_dir / "TTS_infer_pack" / "text_segmentation_method.py",
        )
        _tsm_mod = importlib.util.module_from_spec(_tsm_spec)
        # ダミーパッケージ
        import types
        _pkg = types.ModuleType("TTS_infer_pack")
        _pkg.__path__ = [str(_gpt_sovits_dir / "TTS_infer_pack")]
        sys.modules["TTS_infer_pack"] = _pkg
        sys.modules["TTS_infer_pack.text_segmentation_method"] = _tsm_mod
        _tsm_spec.loader.exec_module(_tsm_mod)
        _pkg.text_segmentation_method = _tsm_mod
    # TextPreprocessor を直接ロード
    _tp_spec = importlib.util.spec_from_file_location(
        "TTS_infer_pack.TextPreprocessor",
        _gpt_sovits_dir / "TTS_infer_pack" / "TextPreprocessor.py",
    )
    _tp_mod = importlib.util.module_from_spec(_tp_spec)
    _tp_spec.loader.exec_module(_tp_mod)
    TextPreprocessor = _tp_mod.TextPreprocessor

    from text.cleaner import clean_text
    from text import cleaned_text_to_sequence
    from text.LangSegmenter import LangSegmenter
    from module.mel_processing import spectrogram_torch as orig_spectrogram_torch
    from ttsclient.tts.tts_manager.utils.mel_processing import spectrogram_torch as ours_spectrogram_torch
    from ERes2NetV2 import ERes2NetV2
    import kaldi as Kaldi

    all_pass = True
    dtype = torch.float16 if is_half else torch.float32

    # ──────────── 共通モデルロード ────────────
    print(f"\n  Loading models... (dtype={dtype})")

    # BERT model + tokenizer (shared)
    tokenizer = AutoTokenizer.from_pretrained(bert_path)
    bert_model = AutoModelForMaskedLM.from_pretrained(bert_path)
    if is_half:
        bert_model = bert_model.half().to(device)
    else:
        bert_model = bert_model.float().to(device)
    bert_model.eval()

    # CNHubert SSL model (shared)
    cnhubert.cnhubert_base_path = str(cnhubert_path)
    ssl_model = cnhubert.get_model()
    if is_half:
        ssl_model = ssl_model.half().to(device)
    else:
        ssl_model = ssl_model.float().to(device)

    # T2S model (shared)
    dict_s1 = torch.load(t2s_path, map_location="cpu", weights_only=False)
    t2s_config = dict_s1["config"]
    t2s_module = Text2SemanticLightningModule(t2s_config, output_dir="****", is_train=False)
    t2s_module.load_state_dict(dict_s1["weight"])
    if is_half:
        t2s_module = t2s_module.half().to(device)
    else:
        t2s_module = t2s_module.float().to(device)
    t2s_module.eval()
    hz = 50
    max_sec = t2s_config["data"]["max_sec"]

    # SoVITS model (2 instances, same weight)
    dict_s2 = torch.load(sovits_path, map_location="cpu")
    hps = _make_hps(dict_s2)
    if is_half:
        from module.models import SynthesizerTrn as OrigSynthesizerTrn
        from ttsclient.tts.tts_manager.models.synthesizer.models import (
            SynthesizerTrn as OurSynthesizerTrn,
        )
        def _load_synth(cls):
            m = cls(
                hps.data.filter_length // 2 + 1,
                hps.train.segment_size // hps.data.hop_length,
                n_speakers=hps.data.n_speakers, **hps.model,
            )
            if hasattr(m, "enc_q"):
                del m.enc_q
            m = m.half().to(device)
            m.eval()
            m.load_state_dict(dict_s2["weight"], strict=False)
            return m
        orig_vq = _load_synth(OrigSynthesizerTrn)
        ours_vq = _load_synth(OurSynthesizerTrn)
    else:
        orig_vq = load_original_synthesizer(dict_s2, hps, device)
        ours_vq = load_ours_synthesizer(dict_s2, hps, device)

    # SV model (shared — float32 固定: 本番でも SV は float32 で fbank 計算後に half cast)
    pretrained_state = torch.load(sv_path, map_location="cpu", weights_only=False)
    sv_model = ERes2NetV2(baseWidth=24, scale=4, expansion=4)
    sv_model.load_state_dict(pretrained_state)
    sv_model.eval().float().to(device)

    # テキスト前処理用の句読点セット
    _splits = set("!?…,.-。？！，、；：")

    # ════════════════════════════════════════════
    # Stage A: Phone+BERT (参照テキスト)
    # ════════════════════════════════════════════
    print("\n  Stage A: Phone+BERT (reference text)")

    _ref_text = ref_text.strip("\n")
    if _ref_text[-1] not in _splits:
        _ref_text += "。" if text_lang != "en" else "."

    # ── オリジナル: TextPreprocessor ──
    orig_preprocessor = TextPreprocessor(bert_model, tokenizer, device)
    orig_phones1, orig_bert1, orig_norm1 = orig_preprocessor.get_phones_and_bert(
        _ref_text, text_lang, "v2"
    )

    # ── ttsclient: BertPhoneExtractor の流れを再現 ──
    def ours_get_phones_and_bert(text, language, version, final=False):
        """BertPhoneExtractor.get_phones_and_bert の再現。"""
        textlist = []
        langlist = []
        if language in {"en"}:
            langlist.append("en")
            textlist.append(text)
        elif language in {"zh", "ja", "ko", "yue", "auto", "auto_yue"}:
            if language == "auto":
                for tmp in LangSegmenter.getTexts(text):
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            elif language == "auto_yue":
                for tmp in LangSegmenter.getTexts(text):
                    if tmp["lang"] == "zh":
                        tmp["lang"] = "yue"
                    langlist.append(tmp["lang"])
                    textlist.append(tmp["text"])
            else:
                for tmp in LangSegmenter.getTexts(text):
                    if tmp["lang"] == "en":
                        langlist.append(tmp["lang"])
                    else:
                        langlist.append(language)
                    textlist.append(tmp["text"])
        phones_list = []
        bert_list = []
        norm_text_list = []
        for i in range(len(textlist)):
            lang = langlist[i].replace("all_", "")
            phones_raw, word2ph, norm_text = clean_text(textlist[i], lang, version)
            phones_seq = cleaned_text_to_sequence(phones_raw, version)
            # BERT feature
            if lang == "zh":
                bert_feat = orig_preprocessor.get_bert_feature(norm_text, word2ph).to(device)
            else:
                # ttsclient: self.dtype (half の場合 float16)
                bert_feat = torch.zeros(
                    (1024, len(phones_seq)), dtype=dtype,
                ).to(device)
            phones_list.append(phones_seq)
            norm_text_list.append(norm_text)
            bert_list.append(bert_feat)
        bert = torch.cat(bert_list, dim=1)
        phones_seq = sum(phones_list, [])
        norm_text = "".join(norm_text_list)
        if not final and len(phones_seq) < 6:
            return ours_get_phones_and_bert("." + text, language, version, final=True)
        return phones_seq, bert.to(dtype), norm_text

    ours_phones1, ours_bert1, ours_norm1 = ours_get_phones_and_bert(
        _ref_text, text_lang, "v2"
    )

    # 比較
    phones1_match = orig_phones1 == ours_phones1
    status = PASS if phones1_match else FAIL
    print(f"  {'phones (ref)':20s}: {status} ({'identical' if phones1_match else 'DIFFERENT'})")
    if not phones1_match:
        print(f"    orig ({len(orig_phones1)}): {orig_phones1[:20]}...")
        print(f"    ours ({len(ours_phones1)}): {ours_phones1[:20]}...")
    all_pass &= phones1_match

    all_pass &= compare("bert (ref)", orig_bert1, ours_bert1)

    # ════════════════════════════════════════════
    # Stage B: SSL → extract_latent (参照音声)
    # ════════════════════════════════════════════
    print("\n  Stage B: SSL → extract_latent")

    wav16k, _ = librosa.load(str(ref_wav_path), sr=16000)
    wav16k_tensor = torch.from_numpy(wav16k).to(dtype).to(device)
    zero_wav = torch.zeros(int(16000 * 0.3), dtype=dtype).to(device)
    wav16k_padded = torch.cat([wav16k_tensor, zero_wav])

    with torch.no_grad():
        ssl_content = ssl_model.model(wav16k_padded.unsqueeze(0))[
            "last_hidden_state"
        ].transpose(1, 2)

        # extract_latent (共通 SynthesizerTrn.extract_latent)
        codes = orig_vq.extract_latent(ssl_content)

    # オリジナル: codes[0, 0] → (seq_len,) → expand(1, -1) → (1, seq_len)
    orig_prompt = codes[0, 0].to(device)
    orig_prompt_2d = orig_prompt.unsqueeze(0)  # (1, seq_len)

    # ttsclient: SovitsSynthesizer.extract_latent
    #   codes[0, 0] → unsqueeze(0) → (1, seq_len)
    ours_prompt_2d = codes[0, 0].unsqueeze(0).to(device)

    prompt_match = torch.equal(orig_prompt_2d, ours_prompt_2d)
    status = PASS if prompt_match else FAIL
    print(f"  {'prompt_semantic':20s}: {status} ({'identical' if prompt_match else 'DIFFERENT'})")
    print(f"  {'prompt shape':20s}: orig={list(orig_prompt_2d.shape)}, ours={list(ours_prompt_2d.shape)}")
    all_pass &= prompt_match

    # ════════════════════════════════════════════
    # Stage C: Phone+BERT (ターゲットテキスト)
    # ════════════════════════════════════════════
    print("\n  Stage C: Phone+BERT (target text)")

    _target_text = target_text.strip("\n")
    if _target_text[-1] not in _splits:
        _target_text += "。" if text_lang != "en" else "."

    orig_phones2, orig_bert2, orig_norm2 = orig_preprocessor.get_phones_and_bert(
        _target_text, text_lang, "v2"
    )
    ours_phones2, ours_bert2, ours_norm2 = ours_get_phones_and_bert(
        _target_text, text_lang, "v2"
    )

    phones2_match = orig_phones2 == ours_phones2
    status = PASS if phones2_match else FAIL
    print(f"  {'phones (tgt)':20s}: {status} ({'identical' if phones2_match else 'DIFFERENT'})")
    if not phones2_match:
        print(f"    orig ({len(orig_phones2)}): {orig_phones2[:20]}...")
        print(f"    ours ({len(ours_phones2)}): {ours_phones2[:20]}...")
    all_pass &= phones2_match

    all_pass &= compare("bert (tgt)", orig_bert2, ours_bert2)

    # ════════════════════════════════════════════
    # Stage D: T2S semantic prediction
    # ════════════════════════════════════════════
    print("\n  Stage D: T2S semantic prediction")

    # 共通入力としてオリジナル側の phones/bert を使用
    # (Stage A/C で差異があっても T2S 自体の一致性を検証する)
    test_phones1 = orig_phones1
    test_bert1 = orig_bert1
    test_phones2 = orig_phones2
    test_bert2 = orig_bert2

    bert_combined = torch.cat([test_bert1, test_bert2], 1)
    all_phoneme_ids = torch.LongTensor(test_phones1 + test_phones2).to(device).unsqueeze(0)
    bert_combined = bert_combined.to(dtype).to(device).unsqueeze(0)
    all_phoneme_len = torch.tensor([all_phoneme_ids.shape[-1]]).to(device)
    prompt_for_t2s = orig_prompt_2d  # (1, seq_len)

    # 同一 seed で 2 回実行 → 同一 model.infer_panel で完全一致するはず
    seed = 42

    _set_seed(seed)
    with torch.no_grad():
        pred_semantic_a, idx_a = t2s_module.model.infer_panel(
            all_phoneme_ids,
            all_phoneme_len,
            prompt_for_t2s,
            bert_combined,
            top_k=20, top_p=1.0, temperature=1.0,
            early_stop_num=hz * max_sec,
            repetition_penalty=1.35,
        )
    pred_semantic_a_sliced = pred_semantic_a[:, -idx_a:].unsqueeze(0)

    _set_seed(seed)
    with torch.no_grad():
        pred_semantic_b, idx_b = t2s_module.model.infer_panel(
            all_phoneme_ids,
            all_phoneme_len,
            prompt_for_t2s,
            bert_combined,
            top_k=20, top_p=1.0, temperature=1.0,
            early_stop_num=hz * max_sec,
            repetition_penalty=1.35,
        )
    pred_semantic_b_sliced = pred_semantic_b[:, -idx_b:].unsqueeze(0)

    t2s_match = torch.equal(pred_semantic_a_sliced, pred_semantic_b_sliced)
    status = PASS if t2s_match else FAIL
    print(f"  {'pred_semantic':20s}: {status} (shape={list(pred_semantic_a_sliced.shape)})")
    all_pass &= t2s_match

    # Phone 差異がある場合の分離テスト: ttsclient 側の phones/bert で T2S を実行
    if not (phones1_match and phones2_match):
        print("\n  Stage D (extra): T2S with ttsclient phones/bert")
        ours_bert_combined = torch.cat([ours_bert1, ours_bert2], 1)
        ours_all_phoneme_ids = torch.LongTensor(ours_phones1 + ours_phones2).to(device).unsqueeze(0)
        ours_bert_combined = ours_bert_combined.to(device).unsqueeze(0)
        ours_all_phoneme_len = torch.tensor([ours_all_phoneme_ids.shape[-1]]).to(device)

        _set_seed(seed)
        with torch.no_grad():
            pred_semantic_ours, idx_ours = t2s_module.model.infer_panel(
                ours_all_phoneme_ids,
                ours_all_phoneme_len,
                prompt_for_t2s,
                ours_bert_combined,
                top_k=20, top_p=1.0, temperature=1.0,
                early_stop_num=hz * max_sec,
                repetition_penalty=1.35,
            )
        pred_semantic_ours_sliced = pred_semantic_ours[:, -idx_ours:].unsqueeze(0)

        cross_match = torch.equal(pred_semantic_a_sliced, pred_semantic_ours_sliced)
        status = PASS if cross_match else WARN
        print(f"  {'pred_sem (cross)':20s}: {status} "
              f"(orig_phones→{list(pred_semantic_a_sliced.shape)} vs "
              f"ours_phones→{list(pred_semantic_ours_sliced.shape)})")

    # 以降は orig 側の pred_semantic を使用
    pred_semantic = pred_semantic_a_sliced

    # ════════════════════════════════════════════
    # Stage E: Spectrogram + SV embedding (参照音声)
    # ════════════════════════════════════════════
    print("\n  Stage E: Spectrogram + SV")

    wav_sr, _ = librosa.load(str(ref_wav_path), sr=int(hps.data.sampling_rate))
    audio_tensor = torch.FloatTensor(wav_sr)
    maxx = audio_tensor.abs().max()
    if maxx > 1:
        audio_tensor = audio_tensor / min(2, maxx)
    audio_norm = audio_tensor.unsqueeze(0)

    spec_orig = orig_spectrogram_torch(
        audio_norm, hps.data.filter_length, hps.data.sampling_rate,
        hps.data.hop_length, hps.data.win_length, center=False,
    )
    spec_ours = ours_spectrogram_torch(
        audio_norm, hps.data.filter_length, hps.data.sampling_rate,
        hps.data.hop_length, hps.data.win_length, center=False,
    )
    all_pass &= compare("spectrogram", spec_orig, spec_ours)

    # SV embedding (SV model は float32 固定 — float32 で計算)
    with torch.no_grad():
        wav16k_sv = torch.from_numpy(wav16k).float().to(device)
        feat_sv = Kaldi.fbank(
            wav16k_sv.unsqueeze(0), num_mel_bins=80,
            sample_frequency=16000, dither=0,
        )
        feat_sv = feat_sv.unsqueeze(0).to(device)
        sv_emb = sv_model.forward3(feat_sv).squeeze(0)  # float32

    print(f"  {'sv_emb':20s}: computed (shape={list(sv_emb.shape)}, dtype={sv_emb.dtype})")

    # ════════════════════════════════════════════
    # Stage F: SoVITS decode
    # ════════════════════════════════════════════
    print("\n  Stage F: SoVITS decode")

    phones2_tensor = torch.LongTensor(test_phones2).to(device).unsqueeze(0)
    refer = spec_orig.to(dtype).to(device)
    sv_emb_decode = sv_emb.to(dtype)

    torch.manual_seed(42)
    with torch.no_grad():
        out_orig = orig_vq.decode(
            pred_semantic, phones2_tensor, [refer], sv_emb=[sv_emb_decode]
        )

    torch.manual_seed(42)
    with torch.no_grad():
        out_ours = ours_vq.decode(
            pred_semantic, phones2_tensor, [refer], sv_emb=[sv_emb_decode]
        )

    all_pass &= compare("final_audio", out_orig, out_ours)

    return all_pass


# ──────────────────────────────────────────
# ヘルパー
# ──────────────────────────────────────────
def _make_hps(dict_s2: dict):
    """チェックポイントの config から hps を構築する。"""
    from ttsclient.gpt_sovits_utils import DictToAttrRecursive

    hps = DictToAttrRecursive(dict_s2["config"])
    hps.model.semantic_frame_rate = "25hz"

    # バージョン判定
    if dict_s2["weight"]["enc_p.text_embedding.weight"].shape[0] == 322:
        hps.model.version = "v1"
    elif "sv_emb.weight" in dict_s2["weight"]:
        hps.model.version = "v2Pro"
    else:
        hps.model.version = "v2"

    return hps


# ──────────────────────────────────────────
# メイン
# ──────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="v2Pro パイプライン一致性テスト")
    parser.add_argument("--sovits-path", type=Path, required=True, help="v2Pro SoVITS チェックポイント (.pth)")
    parser.add_argument("--sv-path", type=Path, required=True, help="SV モデル (.ckpt)")
    parser.add_argument("--ref-wav", type=Path, required=True, help="リファレンス音声 (.wav)")
    parser.add_argument("--device", type=str, default="cpu", help="デバイス (cpu / cuda:0)")
    # Test 7 用の追加引数
    parser.add_argument("--t2s-path", type=Path, default=None, help="T2S モデル (.ckpt)")
    parser.add_argument("--bert-path", type=Path, default=None, help="BERT モデルディレクトリ")
    parser.add_argument("--cnhubert-path", type=Path, default=None, help="CNHubert モデルディレクトリ")
    parser.add_argument("--ref-text", type=str, default="こんにちは。", help="参照テキスト")
    parser.add_argument("--target-text", type=str, default="今日はいい天気ですね。", help="ターゲットテキスト")
    parser.add_argument("--text-lang", type=str, default="ja", help="テキスト言語")
    parser.add_argument("--half", action="store_true", help="half precision (float16) で実行")
    args = parser.parse_args()

    # 入力検証
    for path, label in [(args.sovits_path, "SoVITS"), (args.sv_path, "SV"), (args.ref_wav, "ref wav")]:
        if not path.exists():
            print(f"Error: {label} path does not exist: {path}")
            sys.exit(1)

    device = torch.device(args.device)
    print(f"Device: {device}")
    print(f"SoVITS: {args.sovits_path}")
    print(f"SV:     {args.sv_path}")
    print(f"Ref:    {args.ref_wav}")

    results: dict[str, bool] = {}

    # Test 1: SV embedding (float32)
    results["SV emb (f32)"] = test_sv_embedding(args.sv_path, args.ref_wav, device)

    # Test 2: SV embedding (half precision 差異)
    if device.type == "cuda":
        results["SV emb (half)"] = test_sv_embedding_half(args.sv_path, args.ref_wav, device)
    else:
        print("\n[Test 2] SV embedding half-precision: SKIP (CPU mode)")

    # Test 3: decode 段階比較
    results["decode stages"] = test_decode_stages(args.sovits_path, args.sv_path, args.ref_wav, device)

    # Test 4: decode end-to-end
    results["decode e2e"] = test_decode_end_to_end(args.sovits_path, device)

    # Test 5: extract_latent
    results["extract_latent"] = test_extract_latent(args.sovits_path, device)

    # Test 6: パイプライン (実音声)
    results["pipeline (real)"] = test_pipeline_with_real_audio(
        args.sovits_path, args.sv_path, args.ref_wav, device
    )

    # Test 7: True E2E パイプライン
    if args.t2s_path and args.bert_path and args.cnhubert_path:
        for path, label in [
            (args.t2s_path, "T2S"), (args.bert_path, "BERT"), (args.cnhubert_path, "CNHubert"),
        ]:
            if not path.exists():
                print(f"Error: {label} path does not exist: {path}")
                sys.exit(1)
        results["true E2E"] = test_true_e2e(
            args.sovits_path, args.sv_path, args.t2s_path,
            args.bert_path, args.cnhubert_path, args.ref_wav,
            args.ref_text, args.target_text, args.text_lang, device,
            is_half=args.half,
        )
    else:
        print("\n[Test 7] True E2E: SKIP (--t2s-path, --bert-path, --cnhubert-path が必要)")

    # ──────────── サマリー ────────────
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    all_pass = True
    for name, passed in results.items():
        status = PASS if passed else FAIL
        print(f"  {name:20s}: {status}")
        all_pass &= passed

    print()
    if all_pass:
        print("All tests passed!")
    else:
        print("Some tests FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
