from pathlib import Path
from typing import Literal, TypeAlias

# Application
APP_NAME = "TTSClient"
VERSION = "2.0.0"

# TTS タイプ
TTSType: TypeAlias = Literal["GPT-SoVITS", "BROKEN", "RESERVED_FOR_SAMPLE", "VoiceCharacter"]

# GPT-SoVITS バージョン
GPTSoVITSVersion: TypeAlias = Literal["v1", "v2"]
GPTSoVITSModelVersion: TypeAlias = Literal["v1", "v2", "v2Pro", "v2ProPlus", "v3", "v4"]

# 構成要素タイプ
SemanticPredictorType: TypeAlias = Literal["GPTSemanticPredictor"]
PhoneExtractorType: TypeAlias = Literal["BertPhoneExtractor"]
SynthesizerType: TypeAlias = Literal[
    "SovitsSynthesizer",
    "SovitsSynthesizerV3",
    "SovitsSynthesizerV3Lora",
    "SovitsSynthesizerV4",
    "SovitsSynthesizerV4Lora",
]
EmbedderType: TypeAlias = Literal["cnhubert"]

# バックエンドモード
BackendMode: TypeAlias = Literal["all_torch", "all_onnx", "semantic_onnx", "synthesizer_onnx"]

# 言語タイプ
LanguageType: TypeAlias = Literal[
    "all_zh",
    "en",
    "all_ja",
    "all_yue",
    "all_ko",
    "zh",
    "ja",
    "yue",
    "ko",
    "auto",
    "auto_yue",
]

# テキスト分割方法
CutMethod: TypeAlias = Literal[
    "No slice",
    "Slice once every 4 sentences",
    "Slice per 50 characters",
    "Slice by Chinese punct",
    "Slice by English punct",
    "Slice by every punct",
]

# Faster モード用カット方法
CutMethodForFaster: TypeAlias = Literal["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"]

# Faster-Whisper 設定
TranscriberModelSize: TypeAlias = Literal[
    "tiny",
    "base",
    "small",
    "medium",
    "large-v1",
    "large-v2",
    "large-v3",
    "large",
    "distil-large-v2",
    "distil-large-v3",
    "large-v3-turbo",
    "turbo",
]
TranscriberDevice: TypeAlias = Literal["cpu", "cuda"]
TranscriberComputeType: TypeAlias = Literal[
    "int8",
    "int8_float32",
    "int8_float16",
    "int8_bfloat16",
    "int16",
    "float16",
    "bfloat16",
    "float32",
]

# ダウンロード状態
DownloadState: TypeAlias = Literal["processing", "validating", "done", "error"]

# ログ
LOG_FILE = Path("./ttsclient.log")

# ディレクトリ設定
SSL_KEY_DIR = Path("./ssl_key")
MODULE_DIR = Path("./modules")
MODEL_DIR = Path("./models")
VOICE_CHARACTER_DIR = Path("./voice_characters")
SETTINGS_DIR = Path("./settings")
CONFIG_FILE = SETTINGS_DIR / "tts_conf.json"
UPLOAD_DIR = Path("./upload_dir")

# スロット設定
MAX_SLOT_INDEX = 20
MAX_VOICE_CHARACTER_SLOT_INDEX = 200
MAX_REFERENCE_VOICE_SLOT_INDEX = 100
SLOT_PARAM_FILE = "params.json"
VOICE_CHARACTER_SLOT_PARAM_FILE = "params.json"
USER_DICT_CSV_FILE = "user_dict.csv"

# v1 互換エイリアス（推論エンジンコード用）
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
ModelDir = MODEL_DIR
VoiceCharacterDir = VOICE_CHARACTER_DIR
ModuleDir = MODULE_DIR
LOGGER_NAME = "ttsclient"
GPT_SOVITS_USER_DICT_PATH = _PROJECT_ROOT / "third_party" / "GPT-SoVITS" / "GPT_SoVITS" / "text" / "ja_userdic" / "userdict.csv"
OPENJTALK_USER_DICT_CSV_FILE = "user_dict.csv"
OPENJTALK_USER_DICT_TEMP_CSV_FILE = "user_dict_tmp.csv"
OPENJTALK_USER_DICT_FILE = "user_dict.dict"
