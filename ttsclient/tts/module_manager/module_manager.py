import logging
from pathlib import Path
from typing import Callable
import math
import requests
import hashlib
from threading import Thread


from ...const import LOGGER_NAME, UPLOAD_DIR, ModuleDir
from ..data_types.data_types import ModuleInfo, ModuleStatus
from ..data_types.module_manager_data_types import ModuleDownloadStatus


REGISTERD_MODULES: list[ModuleInfo] = [
    ModuleInfo(
        id="gpt_model",
        display_name="gpt_model",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt",
        save_to=ModuleDir / Path("s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt"),
        hash="732f94e63b148066e24c7f9d2637f3374083e637635f07fbdb695dee20ddbe1f",
    ),
    ModuleInfo(
        id="sovits_model",
        display_name="sovits_model",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/gsv-v2final-pretrained/s2G2333k.pth",
        save_to=ModuleDir / Path("s2G2333k.pth"),
        hash="924fdccaa3c574bf139c25c9759aa1ed3b3f99e19a7c529ee996c2bc17663695",
    ),
    # // chinese-roberta-wwm-ext-large // #
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_bin",
        display_name="chinese-roberta-wwm-ext-large_bin",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin",
        # url="https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/pytorch_model.bin",
        save_to=ModuleDir / Path("chinese-roberta-wwm-ext-large/pytorch_model.bin"),
        hash="e53a693acc59ace251d143d068096ae0d7b79e4b1b503fa84c9dcf576448c1d8",
    ),
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_config",
        display_name="chinese-roberta-wwm-ext-large_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/config.json",
        # url="https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/resolve/main/config.json",
        save_to=ModuleDir / Path("chinese-roberta-wwm-ext-large/config.json"),
        hash="3d57de2fd7e80d0e5c8ff194f0bbb6baa10df7e43fc262a0cc71298a78b0a3e5",
    ),
    ModuleInfo(
        id="chinese-roberta-wwm-ext-large_tokenizer",
        display_name="chinese-roberta-wwm-ext-large_tokenizer",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/tokenizer.json",
        # url="https://huggingface.co/hfl/chinese-roberta-wwm-ext-large/blob/main/tokenizer.json",
        save_to=ModuleDir / Path("chinese-roberta-wwm-ext-large/tokenizer.json"),
        hash="173796956820ea27bd14f76bf28162607ff4254807e2948253eb5b46f5bb643b",
    ),
    # // chinese-hubert-base // #
    ModuleInfo(
        id="chinese-hubert-base_bin",
        display_name="chinese-hubert-base_bin",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/pytorch_model.bin",
        save_to=ModuleDir / Path("chinese-hubert-base/pytorch_model.bin"),
        hash="24164f129c66499d1346e2aa55f183250c223161ec2770c0da3d3b08cf432d3c",
    ),
    ModuleInfo(
        id="chinese-hubert-base_config",
        display_name="chinese-hubert-base_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/config.json",
        save_to=ModuleDir / Path("chinese-hubert-base/config.json"),
        hash="c3e5060a1277e0f078cc6be9da4528a605dba6ece93018981fe2c820e5c7b103",
    ),
    ModuleInfo(
        id="chinese-hubert-base_preprocessor_config",
        display_name="chinese-hubert-base_preprocessor_config",
        url="https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/preprocessor_config.json",
        save_to=ModuleDir / Path("chinese-hubert-base/preprocessor_config.json"),
        hash="dcd684124d06722947939d41ea6ae58dbf10968c60a11a29f23ddc602c64a29b",
    ),
    # ---------------------- #
    # Intial Models
    # ---------------------- #
    ModuleInfo(
        id="GPT-SoVITS_icon",
        display_name="GPT-SoVITS_icon",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/pretrained/pretrained.png",
        save_to=UPLOAD_DIR / Path("pretrained.png"),
        hash="af664eb8a206e62313b0b9a5880c73d4d266ec61f2ebde5753ee4a391371bee0",
    ),
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_semantice",
        display_name="PT-SoVITS_FT_JVNV_semantice",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/jvnv_f1-e15.ckpt",
        save_to=UPLOAD_DIR / Path("jvnv_f1-e15.ckpt"),
        hash="2ea6105d2dab14a0df28dc4d79077cf06ea41e28ff72cf47914fe78751ffe910",
    ),
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_synthesizer",
        display_name="GPT-SoVITS_FT_JVNV_synthesize",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/jvnv_f1_e8_s480.pth",
        save_to=UPLOAD_DIR / Path("jvnv_f1_e8_s480.pth"),
        hash="d47a7070039a3327b760f27122b9ccc9d3bbd5a59b72ec1b5ed9c1ae75194b6b",
    ),
    ModuleInfo(
        id="GPT-SoVITS_FT_JVNV_icon",
        display_name="GPT-SoVITS_FT_JVNV_icon",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/fine-tune-by-JVNV-F1/F1_finetune.png",
        save_to=UPLOAD_DIR / Path("F1_finetune.png"),
        hash="beeb7e30660f5b06246aa1fb92ef0185883d11ca5e53a5ecef48f3824d1fdb50",
    ),
    ModuleInfo(
        id="JVNV_F1_VOICE",
        display_name="JVNV_F1_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_F1.zip",
        save_to=UPLOAD_DIR / Path("JVNV_F1.zip"),
        hash="78715260c07a8e9dabc31f60e10ee0e7044155ecfca9a4bbb52d15fda3438077",
    ),
    ModuleInfo(
        id="JVNV_F2_VOICE",
        display_name="JVNV_F2_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_F2.zip",
        save_to=UPLOAD_DIR / Path("JVNV_F2.zip"),
        hash="387e03c86e16607f8085da1ddf5857486244cbe19aff2dc03c7e5f67b2dc1221",
    ),
    ModuleInfo(
        id="JVNV_M1_VOICE",
        display_name="JVNV_M1_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_M1.zip",
        save_to=UPLOAD_DIR / Path("JVNV_M1.zip"),
        hash="eddeb129a5318257e4290ebd2622b53143dd5eae6d9c10fed76daa69917fbd9a",
    ),
    ModuleInfo(
        id="JVNV_M2_VOICE",
        display_name="JVNV_M2_VOICE",
        url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/jvnv-voices/JVNV_M2.zip",
        save_to=UPLOAD_DIR / Path("JVNV_M2.zip"),
        hash="4bb68a46498dc80bfd425b4d4bd0397e23b65fd124db6516339d86704ed87620",
    ),
]
REQUIRED_MODULES = [
    "gpt_model",
    "sovits_model",
    "chinese-roberta-wwm-ext-large_bin",
    "chinese-roberta-wwm-ext-large_config",
    "chinese-roberta-wwm-ext-large_tokenizer",
    "chinese-hubert-base_bin",
    "chinese-hubert-base_config",
    "chinese-hubert-base_preprocessor_config",
]
INITIAL_MODELS = [
    "GPT-SoVITS_icon",
    "GPT-SoVITS_FT_JVNV_semantice",
    "GPT-SoVITS_FT_JVNV_synthesizer",
    "GPT-SoVITS_FT_JVNV_icon",
    "JVNV_F1_VOICE",
    "JVNV_F2_VOICE",
    "JVNV_M1_VOICE",
    "JVNV_M2_VOICE",
]


class ModuleManager:
    _instance = None
    module_status_list: list[ModuleStatus] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:

            cls._instance = cls()
            return cls._instance

        return cls._instance

    def __init__(self):
        self.module_status_list = []
        self.threads = {}
        self.reload()
        logging.getLogger(LOGGER_NAME).info(f"Initial module status: {self.module_status_list}")

    def reload(self):
        self.module_status_list = []
        for module_info in REGISTERD_MODULES:
            module_status = ModuleStatus(info=module_info, downloaded=False, valid=False)
            logging.getLogger(LOGGER_NAME).info(f"{module_info.id} : downloaded:{module_status.downloaded}, valid:{module_status.valid}")
            if module_info.save_to.exists():
                module_status.downloaded = True
                if self._check_hash(module_info.id):
                    module_status.valid = True
            self.module_status_list.append(module_status)

    def get_modules(self) -> list[ModuleStatus]:
        return self.module_status_list

    def _download(self, target_module: ModuleInfo, callback: Callable[[ModuleDownloadStatus], None]):
        # print(params)
        # (target_module, callback) = params
        target_module.save_to.parent.mkdir(parents=True, exist_ok=True)

        req = requests.get(target_module.url, stream=True, allow_redirects=True)
        content_length_header = req.headers.get("content-length")
        content_length = int(content_length_header) if content_length_header is not None else 1024 * 1024 * 1024
        chunk_size = 1024 * 1024
        chunk_num = math.ceil(content_length / chunk_size)
        with open(target_module.save_to, "wb") as f:
            for i, chunk in enumerate(req.iter_content(chunk_size=chunk_size)):
                f.write(chunk)
                callback(
                    ModuleDownloadStatus(
                        id=target_module.id,
                        status="processing",
                        progress=min(1.0, round((i + 1) / chunk_num, 2)),
                    )
                )

        callback(
            ModuleDownloadStatus(
                id=target_module.id,
                status="validating",
                progress=min(1.0, round((i + 1) / chunk_num, 2)),
            )
        )
        try:
            self._check_hash(target_module.id)
            logging.getLogger(LOGGER_NAME).info(f"Downloading completed: {target_module.id}")
            callback(
                ModuleDownloadStatus(
                    id=target_module.id,
                    status="done",
                    progress=1.0,
                )
            )
        except Exception as e:
            logging.getLogger(LOGGER_NAME).error(f"Downloading error: {target_module.id}, {e}")
            callback(
                ModuleDownloadStatus(
                    id=target_module.id,
                    status="error",
                    progress=1.0,
                    error_message=str(e),
                )
            )

    def _get_target_module(self, id: str):
        target_module = None
        for module in REGISTERD_MODULES:
            if module.id == id:
                target_module = module
                break
        return target_module

    def download(
        self,
        id: str,
        callback: Callable[[ModuleDownloadStatus], None],
    ):
        logging.getLogger(LOGGER_NAME).info(f"Downloading module: {id}")
        # check module exists
        target_module = self._get_target_module(id)
        if target_module is None:
            logging.getLogger(LOGGER_NAME).error(f"No such module: {id}")
            callback(
                ModuleDownloadStatus(
                    id=id,
                    status="error",
                    progress=1.0,
                    error_message=f"module not found {id}",
                )
            )
            return

        # release finished thread
        for exist_trehad_id, exist_thread in list(self.threads.items()):
            if exist_thread is None or exist_thread.is_alive():
                pass  # active thread
            else:
                # thread finished
                exist_thread.join()
                self.threads.pop(exist_trehad_id)

        # check already downloading
        if id in self.threads:
            logging.getLogger(LOGGER_NAME).error(f"Already downloading: {id}")
            callback(
                ModuleDownloadStatus(
                    id=id,
                    status="error",
                    progress=1.0,
                    error_message=f"module is already downloading {id}",
                )
            )
            return

        # start download
        self.threads[id] = None  # dummy, to avoid multiple download
        logging.getLogger(LOGGER_NAME).info(f"Start downloading: {id}")
        t = Thread(
            target=self._download,
            args=(
                target_module,
                callback,
            ),
        )
        t.start()
        self.threads[id] = t

    def _check_hash(self, id: str):
        target_module = self._get_target_module(id)
        if target_module is None:
            # raise VCClientError(ERROR_CODE_MODULE_NOT_FOUND, f"Module {id} not found")
            raise RuntimeError(f"Module {id} not found")

        with open(target_module.save_to, "rb") as f:
            data = f.read()
            hash = hashlib.sha256(data).hexdigest()
            if hash != target_module.hash:
                logging.getLogger(LOGGER_NAME).error(f"hash is not valid: valid:{target_module.hash}, incoming:{hash}")
                return False
            else:
                return True

    def get_module_filepath(self, id: str):
        target_module = self._get_target_module(id)
        if target_module is None:
            return None
        return target_module.save_to

    def download_initial_modules(self, callback: Callable[[list[ModuleDownloadStatus]], None]):
        modules = [x for x in self.get_modules() if x.info.id in REQUIRED_MODULES and x.valid is False]

        logging.getLogger(LOGGER_NAME).info("---- TEST MODULES ---- start")
        test_modules = [x for x in self.get_modules() if x.info.id in REQUIRED_MODULES]
        for i in test_modules:
            logging.getLogger(LOGGER_NAME).info(f"Module:{i.info.id} -> Download:{i.downloaded}, Status:{i.valid}")
        logging.getLogger(LOGGER_NAME).info("---- TEST MODULES ---- end")

        # x.info.idをキーにした辞書配列でstatusを管理。
        status_dict = {x.info.id: ModuleDownloadStatus(id=x.info.id, status="processing", progress=0.0) for x in modules}

        # status_dictをdownloadのコールバックで更新する
        def download_callback(status: ModuleDownloadStatus):
            status_dict[status.id] = status
            callback(list(status_dict.values()))

        for module in modules:
            self.download(module.info.id, download_callback)

        for threads in self.threads.values():
            threads.join()
        print("")
        print("module download fin!")

    def download_initial_models(self, callback: Callable[[list[ModuleDownloadStatus]], None]):
        modules = [x for x in self.get_modules() if x.info.id in INITIAL_MODELS and x.valid is False]
        # x.info.idをキーにした辞書配列でstatusを管理。
        status_dict = {x.info.id: ModuleDownloadStatus(id=x.info.id, status="processing", progress=0.0) for x in modules}

        # status_dictをdownloadのコールバックで更新する
        def download_callback(status: ModuleDownloadStatus):
            status_dict[status.id] = status
            callback(list(status_dict.values()))

        for module in modules:
            self.download(module.info.id, download_callback)

        for threads in self.threads.values():
            threads.join()
        print("")
        print("initial model download fin!")
