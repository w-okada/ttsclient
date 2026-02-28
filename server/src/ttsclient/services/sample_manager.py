import logging
import math
from pathlib import Path

import requests

from ttsclient.models.sample import (
    GPTSoVITSSampleInfo,
    SampleDownloadParam,
    SampleDownloadStatus,
    SampleInfoMember,
    VoiceCharacterSampleInfo,
)
from ttsclient.models.slot import GPTSoVITSModelImportParam
from ttsclient.models.voice_character import VoiceCharacterImportParam

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 1024 * 1024  # 1MB

REGISTERED_SAMPLES: list[SampleInfoMember] = [
    GPTSoVITSSampleInfo(
        id="Zundamon_official_v2",
        tts_type="GPT-SoVITS",
        lang="ja-JP",
        tag=[],
        name="ずんだもん(公式提供版)",
        terms_of_use_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/terms_of_use.txt",
        icon_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/icon.png",
        credit="",
        description="",
        semantic_predictor_model_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/zudamon_style_1-e15.ckpt",
        synthesizer_model_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/zudamon_style_1_e8_s96.pth",
        version="v2",
        model_version="v2",
        lora_v3=False,
    ),
    VoiceCharacterSampleInfo(
        id="VC_Zundamon_official",
        tts_type="VoiceCharacter",
        lang="ja-JP",
        tag=[],
        name="ずんだもん",
        terms_of_use_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/voice_character_terms_of_use.txt",
        icon_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/voice_character_zundamon_icon.png",
        credit="",
        description="",
        zip_url="https://huggingface.co/wok000/gpt-sovits-models/resolve/main/zundamon/voice_character_zundamon.zip",
    ),
]


class SampleManager:
    _instance: "SampleManager | None" = None

    def __init__(self) -> None:
        self._samples: list[SampleInfoMember] = []

    @classmethod
    def get_instance(cls) -> "SampleManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[SampleInfoMember]:
        self._samples = list(REGISTERED_SAMPLES)
        logger.info("サンプル一覧を設定: %d 件", len(self._samples))
        return self._samples

    def get_samples(self) -> list[SampleInfoMember]:
        return self._samples

    def download(self, upload_dir: Path, param: SampleDownloadParam) -> None:
        from ttsclient.services.slot_manager import SlotManager
        from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

        sample = self._find_sample(param.sample_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        if isinstance(sample, VoiceCharacterSampleInfo):
            self._download_voice_character_sample(upload_dir, param, sample, VoiceCharacterSlotManager.get_instance())
        elif isinstance(sample, GPTSoVITSSampleInfo):
            self._download_gpt_sovits_sample(upload_dir, param, sample, SlotManager.get_instance())
        else:
            raise RuntimeError(f"不明なサンプル種別: {sample.tts_type}")

    def _download_voice_character_sample(
        self,
        upload_dir: Path,
        param: SampleDownloadParam,
        sample: VoiceCharacterSampleInfo,
        vc_mgr: object,
    ) -> None:
        from ttsclient.services.voice_character_slot_manager import VoiceCharacterSlotManager

        assert isinstance(vc_mgr, VoiceCharacterSlotManager)

        vc_mgr.reserve_slot_for_sample(param.slot_index)

        urls = [sample.zip_url]
        if sample.icon_url:
            urls.append(sample.icon_url)

        try:
            self._download_files(upload_dir, urls, sample.id)
        except Exception:
            logger.error("サンプルダウンロード失敗: %s", sample.id, exc_info=True)

        vc_mgr.release_slot_from_reserved_for_sample(param.slot_index)

        import_param = VoiceCharacterImportParam(
            slot_index=param.slot_index,
            name="",
            tts_type="VoiceCharacter",
            zip_file=upload_dir / sample.zip_url.split("/")[-1],
        )
        vc_mgr.set_new_slot(import_param)

    def _download_gpt_sovits_sample(
        self,
        upload_dir: Path,
        param: SampleDownloadParam,
        sample: GPTSoVITSSampleInfo,
        slot_mgr: object,
    ) -> None:
        from ttsclient.services.slot_manager import SlotManager

        assert isinstance(slot_mgr, SlotManager)

        slot_mgr.reserve_slot_for_sample(param.slot_index)

        urls: list[str] = []
        if sample.semantic_predictor_model_url:
            urls.append(sample.semantic_predictor_model_url)
        if sample.synthesizer_model_url:
            urls.append(sample.synthesizer_model_url)
        if sample.icon_url:
            urls.append(sample.icon_url)

        try:
            self._download_files(upload_dir, urls, sample.id)
        except Exception:
            logger.error("サンプルダウンロード失敗: %s", sample.id, exc_info=True)

        slot_mgr.release_slot_from_reserved_for_sample(param.slot_index)

        import_param = GPTSoVITSModelImportParam(
            slot_index=param.slot_index,
            name=sample.name,
            terms_of_use_url=sample.terms_of_use_url,
            semantic_predictor_model_path=upload_dir / sample.semantic_predictor_model_url.split("/")[-1] if sample.semantic_predictor_model_url else None,
            synthesizer_model_path=upload_dir / sample.synthesizer_model_url.split("/")[-1] if sample.synthesizer_model_url else None,
            icon_file=upload_dir / sample.icon_url.split("/")[-1] if sample.icon_url else None,
        )
        slot_mgr.set_new_slot(import_param)

    def _download_files(self, upload_dir: Path, urls: list[str], sample_id: str) -> None:
        """複数 URL をダウンロードし、進捗をログ出力する。"""
        for url_index, url in enumerate(urls):
            resp = requests.get(url, stream=True, allow_redirects=True, timeout=30)
            resp.raise_for_status()
            content_length = int(resp.headers.get("content-length", 1024 * 1024 * 1024))
            chunk_num = math.ceil(content_length / _CHUNK_SIZE)
            save_to = upload_dir / url.split("/")[-1]

            with open(save_to, "wb") as f:
                for i, chunk in enumerate(resp.iter_content(chunk_size=_CHUNK_SIZE)):
                    f.write(chunk)

            file_progress = 1.0
            total_progress = round(file_progress / len(urls) + (1 / len(urls)) * url_index, 2)
            logger.info("ダウンロード進捗 [%s]: ファイル %d/%d 完了 (%.0f%%)", sample_id, url_index + 1, len(urls), total_progress * 100)

    def _find_sample(self, sample_id: str) -> SampleInfoMember:
        matches = [s for s in self._samples if s.id == sample_id]
        if len(matches) != 1:
            raise RuntimeError(f"サンプル {sample_id} が見つかりません")
        return matches[0]
