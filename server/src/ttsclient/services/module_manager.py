import hashlib
import logging
import math
from collections.abc import Callable
from pathlib import Path
from threading import Thread

import requests

from ttsclient.const import MODULE_DIR, UPLOAD_DIR
from ttsclient.models.module import ModuleDownloadStatus, ModuleInfo, ModuleStatus

logger = logging.getLogger(__name__)

REGISTERED_MODULES: list[ModuleInfo] = [
    # --- Core models (v2) ---
    ModuleInfo(
        id="gpt_model",
        display_name="gpt_model",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt",
        save_to=MODULE_DIR / "s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt",
        hash="732f94e63b148066e24c7f9d2637f3374083e637635f07fbdb695dee20ddbe1f",
    ),
    # --- Core models (v2Pro) --- (GPT は v2 と共通)
    ModuleInfo(
        id="sovits_model_v2pro",
        display_name="sovits_model_v2pro",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/v2Pro/s2Gv2Pro.pth",
        save_to=MODULE_DIR / "v2Pro/s2Gv2Pro.pth",
        hash="0f8ead815234365edf045c6d86370ed6e4f440e8195be77ff0ea72684ad406a5",
    ),
    # --- Core models (v2ProPlus) --- (GPT は v2 と共通)
    ModuleInfo(
        id="sovits_model_v2proplus",
        display_name="sovits_model_v2proplus",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/v2Pro/s2Gv2ProPlus.pth",
        save_to=MODULE_DIR / "v2Pro/s2Gv2ProPlus.pth",
        hash="d42a22bbbf65fb2bbdd45ad6a66841156977db45c7aabe0a6992ff378d9c7d3b",
    ),
    # --- Speaker Verification (v2Pro 系で使用) ---
    ModuleInfo(
        id="pretrained_eres2netv2w24s4ep4",
        display_name="pretrained_eres2netv2w24s4ep4",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/sv/pretrained_eres2netv2w24s4ep4.ckpt",
        save_to=MODULE_DIR / "sv/pretrained_eres2netv2w24s4ep4.ckpt",
        hash="4f5a0bf73c61eb41b174e1bb54e7ee3c83233892be8e0af1f187024e8e581a35",
    ),
    # --- chinese-roberta-wwm-ext-large ---
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_bin",
        display_name="chinese-roberta-wwm-ext-large_bin",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin",
        save_to=MODULE_DIR / "chinese-roberta-wwm-ext-large/pytorch_model.bin",
        hash="e53a693acc59ace251d143d068096ae0d7b79e4b1b503fa84c9dcf576448c1d8",
    ),
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_config",
        display_name="chinese-roberta-wwm-ext-large_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/config.json",
        save_to=MODULE_DIR / "chinese-roberta-wwm-ext-large/config.json",
        hash="3d57de2fd7e80d0e5c8ff194f0bbb6baa10df7e43fc262a0cc71298a78b0a3e5",
    ),
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_tokenizer",
        display_name="chinese-roberta-wwm-ext-large_tokenizer",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/tokenizer.json",
        save_to=MODULE_DIR / "chinese-roberta-wwm-ext-large/tokenizer.json",
        hash="173796956820ea27bd14f76bf28162607ff4254807e2948253eb5b46f5bb643b",
    ),
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_G2PWModel_1.1.zip",
        display_name="G2PWModel_1.1.zip",
        url="https://www.modelscope.cn/models/kamiorinn/g2pw/resolve/master/G2PWModel_1.1.zip",
        save_to=Path("GPT_SoVITS/text/G2PWModel_1.1.zip"),
        hash="b116f6930a7ee55eef6576a8d8e14bf40c1106583439e8ae924b901512379c64",
    ),
    # --- chinese-hubert-base ---
    ModuleInfo(
        id="chinese-hubert-base_bin",
        display_name="chinese-hubert-base_bin",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/pytorch_model.bin",
        save_to=MODULE_DIR / "chinese-hubert-base/pytorch_model.bin",
        hash="24164f129c66499d1346e2aa55f183250c223161ec2770c0da3d3b08cf432d3c",
    ),
    ModuleInfo(
        id="chinese-hubert-base_config",
        display_name="chinese-hubert-base_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/config.json",
        save_to=MODULE_DIR / "chinese-hubert-base/config.json",
        hash="c3e5060a1277e0f078cc6be9da4528a605dba6ece93018981fe2c820e5c7b103",
    ),
    ModuleInfo(
        id="chinese-hubert-base_preprocessor_config",
        display_name="chinese-hubert-base_preprocessor_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/preprocessor_config.json",
        save_to=MODULE_DIR / "chinese-hubert-base/preprocessor_config.json",
        hash="dcd684124d06722947939d41ea6ae58dbf10968c60a11a29f23ddc602c64a29b",
    ),
    # --- Initial models (pretrained icons) ---
    ModuleInfo(
        id="GPT-SoVITS_icon_v2pro",
        display_name="GPT-SoVITS_icon_v2pro",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/pretrained/gpt_sovits_pretrain_v2pro.png",
        save_to=UPLOAD_DIR / "gpt_sovits_pretrain_v2pro.png",
        hash="23eb8b7237fbb2359050ef3583cf0ab21e849596631605c6c9c0be9a7744d737",
    ),
    ModuleInfo(
        id="GPT-SoVITS_icon_v2proplus",
        display_name="GPT-SoVITS_icon_v2proplus",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/pretrained/gpt_sovits_pretrain_v2proplus.png",
        save_to=UPLOAD_DIR / "gpt_sovits_pretrain_v2proplus.png",
        hash="0decba46dd1df2283740e5051437c93e8a61ce11db8833361220f466c04456b0",
    ),
    # --- Initial models (JVNV fine-tuned) ---
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_semantice",
        display_name="GPT-SoVITS_FT_JVNV_semantice",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/jvnv_f1-e15.ckpt",
        save_to=UPLOAD_DIR / "jvnv_f1-e15.ckpt",
        hash="d47a7070039a3327b760f27122b9ccc9d3bbd5a59b72ec1b5ed9c1ae75194b6b",
    ),
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_synthesizer",
        display_name="GPT-SoVITS_FT_JVNV_synthesizer",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/jvnv_f1_e8_s480.pth",
        save_to=UPLOAD_DIR / "jvnv_f1_e8_s480.pth",
        hash="2ea6105d2dab14a0df28dc4d79077cf06ea41e28ff72cf47914fe78751ffe910",
    ),
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_icon",
        display_name="GPT-SoVITS_FT_JVNV_icon",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/F1_finetune.png",
        save_to=UPLOAD_DIR / "F1_finetune.png",
        hash="beeb7e30660f5b06246aa1fb92ef0185883d11ca5e53a5ecef48f3824d1fdb50",
    ),
    # --- Initial models (JVNV voice packs) ---
    ModuleInfo(
        id="JVNV_F1_VOICE",
        display_name="JVNV_F1_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_F1.zip",
        save_to=UPLOAD_DIR / "JVNV_F1.zip",
        hash="78715260c07a8e9dabc31f60e10ee0e7044155ecfca9a4bbb52d15fda3438077",
    ),
    ModuleInfo(
        id="JVNV_F2_VOICE",
        display_name="JVNV_F2_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_F2.zip",
        save_to=UPLOAD_DIR / "JVNV_F2.zip",
        hash="387e03c86e16607f8085da1ddf5857486244cbe19aff2dc03c7e5f67b2dc1221",
    ),
    ModuleInfo(
        id="JVNV_M1_VOICE",
        display_name="JVNV_M1_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_M1.zip",
        save_to=UPLOAD_DIR / "JVNV_M1.zip",
        hash="eddeb129a5318257e4290ebd2622b53143dd5eae6d9c10fed76daa69917fbd9a",
    ),
    ModuleInfo(
        id="JVNV_M2_VOICE",
        display_name="JVNV_M2_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_M2.zip",
        save_to=UPLOAD_DIR / "JVNV_M2.zip",
        hash="4bb68a46498dc80bfd425b4d4bd0397e23b65fd124db6516339d86704ed87620",
    ),
]

REQUIRED_MODULES = [
    "gpt_model",
    "sovits_model_v2pro",
    "sovits_model_v2proplus",
    "pretrained_eres2netv2w24s4ep4",
    "chinese-roberta-wwm-ext-large_bin",
    "chinese-roberta-wwm-ext-large_config",
    "chinese-roberta-wwm-ext-large_tokenizer",
    "chinese-hubert-base_bin",
    "chinese-hubert-base_config",
    "chinese-hubert-base_preprocessor_config",
]

INITIAL_MODELS = [
    "GPT-SoVITS_icon_v2pro",
    "GPT-SoVITS_icon_v2proplus",
    "GPT-SoVITS_FT_JVNV_semantice",
    "GPT-SoVITS_FT_JVNV_synthesizer",
    "GPT-SoVITS_FT_JVNV_icon",
    "JVNV_F1_VOICE",
    "JVNV_F2_VOICE",
    "JVNV_M1_VOICE",
    "JVNV_M2_VOICE",
]

_CHUNK_SIZE = 1024 * 1024  # 1MB


class ModuleManager:
    _instance: "ModuleManager | None" = None

    def __init__(self) -> None:
        self._modules: list[ModuleStatus] = []
        self._threads: dict[str, Thread | None] = {}

    @classmethod
    def get_instance(cls) -> "ModuleManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[ModuleStatus]:
        self._modules = []
        for module_info in REGISTERED_MODULES:
            downloaded = False
            valid = False
            if module_info.save_to.exists():
                downloaded = True
                valid = self._check_hash(module_info.id)
            self._modules.append(ModuleStatus(info=module_info, downloaded=downloaded, valid=valid))
        logger.info("モジュール状態を検出: %d 件", len(self._modules))
        return self._modules

    def get_modules(self) -> list[ModuleStatus]:
        return self._modules

    def get_module_filepath(self, module_id: str) -> Path | None:
        target = self._find_module_info(module_id)
        return target.save_to if target else None

    def download(self, module_id: str, callback: Callable[[ModuleDownloadStatus], None]) -> None:
        target = self._find_module_info(module_id)
        if target is None:
            logger.error("モジュールが見つかりません: %s", module_id)
            callback(ModuleDownloadStatus(id=module_id, status="error", progress=1.0, error_message=f"module not found {module_id}"))
            return

        self._cleanup_finished_threads()

        if module_id in self._threads:
            logger.error("既にダウンロード中: %s", module_id)
            callback(ModuleDownloadStatus(id=module_id, status="error", progress=1.0, error_message=f"module is already downloading {module_id}"))
            return

        self._threads[module_id] = None
        logger.info("ダウンロード開始: %s", module_id)
        t = Thread(target=self._download, args=(target, callback))
        t.start()
        self._threads[module_id] = t

    def download_initial_modules(self, callback: Callable[[list[ModuleDownloadStatus]], None]) -> None:
        self._download_module_list(REQUIRED_MODULES, callback)

    def download_initial_models(self, callback: Callable[[list[ModuleDownloadStatus]], None]) -> None:
        self._download_module_list(INITIAL_MODELS, callback)

    def _download_module_list(self, module_ids: list[str], callback: Callable[[list[ModuleDownloadStatus]], None]) -> None:
        targets = [m for m in self._modules if m.info.id in module_ids and not m.valid]
        status_dict = {m.info.id: ModuleDownloadStatus(id=m.info.id, status="processing", progress=0.0) for m in targets}

        def on_progress(status: ModuleDownloadStatus) -> None:
            status_dict[status.id] = status
            callback(list(status_dict.values()))

        for m in targets:
            self.download(m.info.id, on_progress)

        for t in self._threads.values():
            if t is not None:
                t.join()

    def _download(self, target: ModuleInfo, callback: Callable[[ModuleDownloadStatus], None]) -> None:
        target.save_to.parent.mkdir(parents=True, exist_ok=True)
        try:
            resp = requests.get(target.url, stream=True, allow_redirects=True, timeout=30)
            resp.raise_for_status()
            content_length = int(resp.headers.get("content-length", 1024 * 1024 * 1024))
            chunk_num = math.ceil(content_length / _CHUNK_SIZE)

            with open(target.save_to, "wb") as f:
                for i, chunk in enumerate(resp.iter_content(chunk_size=_CHUNK_SIZE)):
                    f.write(chunk)
                    callback(ModuleDownloadStatus(id=target.id, status="processing", progress=min(1.0, round((i + 1) / chunk_num, 2))))

            callback(ModuleDownloadStatus(id=target.id, status="validating", progress=1.0))

            if self._check_hash(target.id):
                logger.info("ダウンロード完了: %s", target.id)
                callback(ModuleDownloadStatus(id=target.id, status="done", progress=1.0))
            else:
                raise ValueError(f"ハッシュ不一致: {target.id}")
        except Exception as e:
            logger.error("ダウンロードエラー: %s, %s", target.id, e)
            callback(ModuleDownloadStatus(id=target.id, status="error", progress=1.0, error_message=str(e)))

    def _check_hash(self, module_id: str) -> bool:
        target = self._find_module_info(module_id)
        if target is None:
            return False
        try:
            sha256 = hashlib.sha256()
            with open(target.save_to, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest() == target.hash
        except OSError:
            return False

    def _find_module_info(self, module_id: str) -> ModuleInfo | None:
        for m in REGISTERED_MODULES:
            if m.id == module_id:
                return m
        return None

    def _cleanup_finished_threads(self) -> None:
        for tid, t in list(self._threads.items()):
            if t is not None and not t.is_alive():
                t.join()
                del self._threads[tid]
