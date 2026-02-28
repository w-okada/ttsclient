import io
import logging
import shutil
import uuid
import zipfile
from pathlib import Path

from ttsclient.const import (
    MAX_REFERENCE_VOICE_SLOT_INDEX,
    MAX_VOICE_CHARACTER_SLOT_INDEX,
    USER_DICT_CSV_FILE,
    VOICE_CHARACTER_DIR,
    VOICE_CHARACTER_SLOT_PARAM_FILE,
)
from ttsclient.models.common import MoveModelParam, SetIconParam
from ttsclient.models.tts import OpenJTalkUserDictRecord
from ttsclient.models.voice_character import (
    ReferenceVoice,
    ReferenceVoiceImportParam,
    VoiceCharacter,
    VoiceCharacterImportParam,
)
from ttsclient.services.voice_character_importer import import_voice_character

logger = logging.getLogger(__name__)


def _load_slot_info(vc_dir: Path, slot_index: int) -> VoiceCharacter:
    """単一スロットの params.json を読み込む。"""
    json_file = vc_dir / str(slot_index) / VOICE_CHARACTER_SLOT_PARAM_FILE
    if not json_file.exists():
        return VoiceCharacter(tts_type=None, slot_index=slot_index)

    try:
        json_text = json_file.read_text(encoding="utf-8")
        return VoiceCharacter.model_validate_json(json_text)
    except Exception:
        logger.error("ボイスキャラクター %d の読み込みに失敗", slot_index, exc_info=True)
        return VoiceCharacter(tts_type="BROKEN", slot_index=slot_index)


def _reload_slot_infos(vc_dir: Path) -> list[VoiceCharacter]:
    """全スロットを走査して読み込む。"""
    return [_load_slot_info(vc_dir, i) for i in range(MAX_VOICE_CHARACTER_SLOT_INDEX)]


class VoiceCharacterSlotManager:
    _instance: "VoiceCharacterSlotManager | None" = None

    def __init__(self) -> None:
        self._slots: list[VoiceCharacter] = []
        self._transcriber: object | None = None
        self._transcriber_config: tuple | None = None

    @classmethod
    def get_instance(cls) -> "VoiceCharacterSlotManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def reload(self) -> list[VoiceCharacter]:
        self._slots = _reload_slot_infos(VOICE_CHARACTER_DIR)
        logger.info("ボイスキャラクター情報を読み込みました: %d 件", len(self._slots))
        return self._slots

    def get_slot_infos(self) -> list[VoiceCharacter]:
        return self._slots

    def get_slot_info(self, index: int) -> VoiceCharacter | None:
        for slot in self._slots:
            if slot.slot_index == index:
                return slot
        return None

    def get_blank_slot_index(self) -> int:
        self.reload()
        used = {s.slot_index for s in self._slots if s.tts_type is not None}
        for i in range(MAX_VOICE_CHARACTER_SLOT_INDEX):
            if i not in used:
                return i
        raise RuntimeError("空きスロットがありません")

    def set_new_slot(self, import_param: VoiceCharacterImportParam, *, remove_src: bool = False) -> None:
        if import_param.slot_index is None:
            import_param.slot_index = self.get_blank_slot_index()

        existing = self.get_slot_info(import_param.slot_index)
        assert existing is not None and existing.tts_type is None, f"スロット {import_param.slot_index} は既に使用中です"

        logger.info("新規ボイスキャラクター設定: %s", import_param)
        import_voice_character(VOICE_CHARACTER_DIR, import_param, remove_src)
        self.reload()

    def update_slot_info(self, slot_info: VoiceCharacter) -> None:
        existing = self.get_slot_info(slot_info.slot_index)
        assert existing is not None and existing.tts_type is not None, f"スロット {slot_info.slot_index} は存在しません"

        slot_dir = VOICE_CHARACTER_DIR / str(slot_info.slot_index)
        slot_dir.mkdir(parents=True, exist_ok=True)
        config_file = slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE
        config_file.write_text(slot_info.model_dump_json(indent=4), encoding="utf-8")

        idx = next(i for i, s in enumerate(self._slots) if s.slot_index == slot_info.slot_index)
        self._slots[idx] = slot_info

    def delete_slot(self, index: int) -> None:
        slot_dir = VOICE_CHARACTER_DIR / str(index)
        if slot_dir.exists():
            shutil.rmtree(slot_dir, ignore_errors=True)
        self.reload()

    def move_model_slot(self, param: MoveModelParam) -> None:
        assert param.dst < MAX_VOICE_CHARACTER_SLOT_INDEX, f"dst {param.dst} が MAX を超えています"

        dst_slot = self.get_slot_info(param.dst)
        assert dst_slot is not None and dst_slot.tts_type is None, f"移動先 {param.dst} は既に使用中です"
        src_slot = self.get_slot_info(param.src)
        assert src_slot is not None and src_slot.tts_type is not None, f"移動元 {param.src} は存在しません"

        src_path = VOICE_CHARACTER_DIR / str(param.src)
        dst_path = VOICE_CHARACTER_DIR / str(param.dst)
        if src_path.exists():
            shutil.move(src_path, dst_path)

        src_slot.slot_index = param.dst
        config_file = dst_path / VOICE_CHARACTER_SLOT_PARAM_FILE
        config_file.write_text(src_slot.model_dump_json(indent=4), encoding="utf-8")
        self.reload()

    def set_icon_file(self, index: int, param: SetIconParam) -> None:
        slot_info = self.get_slot_info(index)
        assert slot_info is not None and slot_info.tts_type is not None, f"スロット {index} は存在しません"

        try:
            icon_name = uuid.uuid4()
            icon_dst = VOICE_CHARACTER_DIR / str(index) / f"{icon_name}{param.icon_file.suffix}"
            shutil.move(param.icon_file, icon_dst)
            slot_info.icon_file = Path(icon_dst.name)
            self.update_slot_info(slot_info)
        finally:
            if param.icon_file.exists():
                param.icon_file.unlink()

    # --- 参照音声管理 ---

    def _get_voice_blank_slot_index(self, vc_index: int) -> int:
        vc = self.get_slot_info(vc_index)
        assert vc is not None and vc.tts_type is not None
        used = {v.slot_index for v in vc.reference_voices}
        for i in range(MAX_REFERENCE_VOICE_SLOT_INDEX):
            if i not in used:
                return i
        raise RuntimeError("参照音声の空きスロットがありません")

    def add_voice_audio(self, index: int, param: ReferenceVoiceImportParam, *, remove_src: bool = False) -> None:
        from ttsclient.services.configuration_manager import ConfigurationManager

        config = ConfigurationManager.get_instance().get_tts_configuration()

        try:
            vc = self.get_slot_info(index)
            assert vc is not None and vc.tts_type is not None, f"スロット {index} は存在しません"

            if param.slot_index is None:
                param.slot_index = self._get_voice_blank_slot_index(index)
            assert param.slot_index < MAX_REFERENCE_VOICE_SLOT_INDEX

            # WAV を UUID ファイル名でコピー
            wav_name = uuid.uuid4()
            audio_dst = VOICE_CHARACTER_DIR / str(index) / f"{wav_name}.wav"
            shutil.move(param.wav_file, audio_dst)

            # オプショナル: librosa でパディング/トリミング
            self._normalize_audio(audio_dst)

            # オプショナル: faster-whisper で書き起こし
            text = ""
            if config.transcribe_audio and param.text is None:
                text = self._transcribe(audio_dst, config)

            # アイコンファイル処理
            icon_file_name: Path | None = None
            if param.icon_file is not None:
                icon_name = uuid.uuid4()
                icon_dst = VOICE_CHARACTER_DIR / str(index) / f"{icon_name}{param.icon_file.suffix}"
                shutil.move(param.icon_file, icon_dst)
                icon_file_name = Path(icon_dst.name)

            voice = ReferenceVoice(
                voice_type=param.voice_type,
                slot_index=param.slot_index,
                wav_file=Path(audio_dst.name),
                text=param.text if param.text is not None else text,
                language="all_ja",
                icon_file=icon_file_name,
            )
            vc.reference_voices.append(voice)
            self.update_slot_info(vc)
        finally:
            if remove_src and param.wav_file.exists():
                param.wav_file.unlink()

    def update_voice_audio(self, index: int, voice_index: int, voice: ReferenceVoice) -> None:
        vc = self.get_slot_info(index)
        assert vc is not None and vc.tts_type is not None

        target = self._find_voice(vc, voice_index)
        target.voice_type = voice.voice_type
        target.text = voice.text
        target.language = voice.language
        self.update_slot_info(vc)

    def delete_voice_audio(self, index: int, voice_index: int) -> None:
        vc = self.get_slot_info(index)
        assert vc is not None and vc.tts_type is not None

        target = self._find_voice(vc, voice_index)
        wav_path = VOICE_CHARACTER_DIR / str(index) / target.wav_file
        if wav_path.exists():
            wav_path.unlink()

        vc.reference_voices = [v for v in vc.reference_voices if v.slot_index != voice_index]
        self.update_slot_info(vc)

    def move_voice_audio(self, index: int, param: MoveModelParam) -> None:
        vc = self.get_slot_info(index)
        assert vc is not None and vc.tts_type is not None
        assert param.dst < MAX_REFERENCE_VOICE_SLOT_INDEX

        src_voice = self._find_voice(vc, param.src)
        dst_voices = [v for v in vc.reference_voices if v.slot_index == param.dst]
        assert len(dst_voices) == 0, f"移動先 voice_index {param.dst} は既に使用中です"

        # UUID ファイル名なので slot_index 変更のみ
        src_voice.slot_index = param.dst
        self.update_slot_info(vc)

    def set_voice_icon_file(self, index: int, voice_index: int, param: SetIconParam) -> None:
        vc = self.get_slot_info(index)
        assert vc is not None and vc.tts_type is not None

        target = self._find_voice(vc, voice_index)
        try:
            icon_name = uuid.uuid4()
            icon_dst = VOICE_CHARACTER_DIR / str(index) / f"{icon_name}{param.icon_file.suffix}"
            shutil.move(param.icon_file, icon_dst)
            target.icon_file = Path(icon_dst.name)
            self.update_slot_info(vc)
        finally:
            if param.icon_file.exists():
                param.icon_file.unlink()

    def add_user_dict_record(self, index: int, param: OpenJTalkUserDictRecord) -> None:
        slot_info = self.get_slot_info(index)
        assert slot_info is not None and slot_info.tts_type is not None

        user_dict_file = VOICE_CHARACTER_DIR / str(index) / USER_DICT_CSV_FILE

        entry = (
            f"{param.string},*,*,-32767,{param.pos},{param.pos_group1},{param.pos_group2},"
            f"{param.pos_group3},{param.ctype},{param.cform},{param.orig},{param.read},"
            f"{param.pron},{param.acc}/{param.mora_size},{param.chain_rule}\n"
        )

        existing: list[str] = []
        if user_dict_file.exists():
            existing = user_dict_file.read_text(encoding="utf-8").splitlines(keepends=True)

        # 同じ表層形のエントリを除去してから追加
        updated = [e for e in existing if e.split(",")[0] != param.string]
        updated.append(entry)

        user_dict_file.write_text("".join(updated), encoding="utf-8")
        self.reload()

    def zip_and_download(self, index: int) -> tuple[str, io.BytesIO]:
        slot_info = self.get_slot_info(index)
        assert slot_info is not None and slot_info.tts_type is not None
        slot_dir = VOICE_CHARACTER_DIR / str(index)
        assert slot_dir.exists(), f"スロットディレクトリが存在しません: {slot_dir}"

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in slot_dir.rglob("*"):
                if file_path.is_file():
                    zf.write(file_path, file_path.relative_to(slot_dir))
        buffer.seek(0)
        return slot_info.name, buffer

    def reserve_slot_for_sample(self, slot_index: int, progress: float = 0.0) -> None:
        """サンプルダウンロード用にスロットを予約する。"""
        existing = self.get_slot_info(slot_index)
        assert existing is not None and existing.tts_type is None

        # RESERVED_FOR_SAMPLE として VoiceCharacter を直接書き込む
        slot_dir = VOICE_CHARACTER_DIR / str(slot_index)
        slot_dir.mkdir(parents=True, exist_ok=True)
        vc = VoiceCharacter(
            tts_type="RESERVED_FOR_SAMPLE",
            slot_index=slot_index,
            name="RESERVED_FOR_SAMPLE",
            progress=progress,
        )
        config_file = slot_dir / VOICE_CHARACTER_SLOT_PARAM_FILE
        config_file.write_text(vc.model_dump_json(indent=4), encoding="utf-8")
        self.reload()

    def release_slot_from_reserved_for_sample(self, slot_index: int) -> None:
        """サンプル用に予約していたスロットを解放する。"""
        self.delete_slot(slot_index)

    # --- プライベートヘルパー ---

    def _find_voice(self, vc: VoiceCharacter, voice_index: int) -> ReferenceVoice:
        matches = [v for v in vc.reference_voices if v.slot_index == voice_index]
        assert len(matches) == 1, f"voice_index {voice_index} が見つかりません"
        return matches[0]

    def _normalize_audio(self, audio_path: Path) -> None:
        """3秒未満はパディング、10秒超はトリミング。librosa がなければスキップ。"""
        try:
            import librosa
            import soundfile as sf
        except ImportError:
            return

        y, sr = librosa.load(audio_path, sr=None)
        if len(y) < sr * 3:
            y = librosa.util.fix_length(y, size=sr * 3)
            sf.write(audio_path, y, sr)
        elif len(y) > sr * 10:
            y = y[: sr * 10]
            sf.write(audio_path, y, sr)

    def _transcribe(self, audio_path: Path, config: object) -> str:
        """faster-whisper で音声を書き起こす。利用不可ならスキップ。"""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            return ""

        from ttsclient.models.tts_configuration import TTSConfiguration

        assert isinstance(config, TTSConfiguration)
        current_config = (config.transcriber_model_size, config.transcriber_device, config.transcriber_compute_type)

        if self._transcriber is None or self._transcriber_config != current_config:
            logger.info("Transcriber 初期化: %s", current_config)
            self._transcriber = WhisperModel(
                config.transcriber_model_size,
                device=config.transcriber_device,
                compute_type=config.transcriber_compute_type,
            )
            self._transcriber_config = current_config

        try:
            segments, info = self._transcriber.transcribe(  # type: ignore[union-attr]
                str(audio_path),
                beam_size=5,
                vad_filter=True,
                without_timestamps=True,
            )
            logger.info("検出言語: %s (確率: %.2f)", info.language, info.language_probability)
            return "".join(seg.text for seg in segments)
        except Exception:
            logger.error("書き起こしに失敗", exc_info=True)
            return ""
