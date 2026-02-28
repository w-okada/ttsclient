// =============================================================
// Constants / Literal Types
// =============================================================

export const TTS_TYPES = ["GPT-SoVITS", "BROKEN", "RESERVED_FOR_SAMPLE", "VoiceCharacter"] as const;
export type TTSType = (typeof TTS_TYPES)[number];

export const GPT_SOVITS_VERSIONS = ["v1", "v2"] as const;
export type GPTSoVITSVersion = (typeof GPT_SOVITS_VERSIONS)[number];

export const GPT_SOVITS_MODEL_VERSIONS = ["v1", "v2", "v2Pro", "v2ProPlus", "v3", "v4"] as const;
export type GPTSoVITSModelVersion = (typeof GPT_SOVITS_MODEL_VERSIONS)[number];

export const SYNTHESIZER_TYPES = [
  "SovitsSynthesizer",
  "SovitsSynthesizerV3",
  "SovitsSynthesizerV3Lora",
  "SovitsSynthesizerV4",
  "SovitsSynthesizerV4Lora",
] as const;
export type SynthesizerType = (typeof SYNTHESIZER_TYPES)[number];

export const BACKEND_MODES = ["all_torch", "all_onnx", "semantic_onnx", "synthesizer_onnx"] as const;
export type BackendMode = (typeof BACKEND_MODES)[number];

export const LANGUAGE_TYPES = [
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
] as const;
export type LanguageType = (typeof LANGUAGE_TYPES)[number];

export const CUT_METHODS = [
  "No slice",
  "Slice once every 4 sentences",
  "Slice per 50 characters",
  "Slice by Chinese punct",
  "Slice by English punct",
  "Slice by every punct",
] as const;
export type CutMethod = (typeof CUT_METHODS)[number];

export const CUT_METHODS_FOR_FASTER = ["cut0", "cut1", "cut2", "cut3", "cut4", "cut5"] as const;
export type CutMethodForFaster = (typeof CUT_METHODS_FOR_FASTER)[number];

export const TRANSCRIBER_MODEL_SIZES = [
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
] as const;
export type TranscriberModelSize = (typeof TRANSCRIBER_MODEL_SIZES)[number];

export const TRANSCRIBER_DEVICES = ["cpu", "cuda"] as const;
export type TranscriberDevice = (typeof TRANSCRIBER_DEVICES)[number];

export const TRANSCRIBER_COMPUTE_TYPES = [
  "int8",
  "int8_float32",
  "int8_float16",
  "int8_bfloat16",
  "int16",
  "float16",
  "bfloat16",
  "float32",
] as const;
export type TranscriberComputeType = (typeof TRANSCRIBER_COMPUTE_TYPES)[number];

export const DOWNLOAD_STATES = ["processing", "validating", "done", "error"] as const;
export type DownloadState = (typeof DOWNLOAD_STATES)[number];

// Max indices
export const MAX_SLOT_INDEX = 20;
export const MAX_VOICE_CHARACTER_SLOT_INDEX = 200;
export const MAX_REFERENCE_VOICE_SLOT_INDEX = 100;

// =============================================================
// Configuration
// =============================================================

export type TTSConfiguration = {
  current_slot_index: number;
  gpu_device_id_int: number;
  transcribe_audio: boolean;
  transcriber_model_size: TranscriberModelSize;
  transcriber_device: TranscriberDevice;
  transcriber_compute_type: TranscriberComputeType;
};

// =============================================================
// GPU
// =============================================================

export type GPUInfo = {
  name: string;
  device_id: string;
  adapter_ram: number;
  device_id_int: number;
  cuda_compute_version_major: number;
  cuda_compute_version_minor: number;
};

// =============================================================
// Module
// =============================================================

export type ModuleInfo = {
  id: string;
  display_name: string;
  url: string;
  save_to: string;
  hash: string;
};

export type ModuleStatus = {
  info: ModuleInfo;
  downloaded: boolean;
  valid: boolean;
};

export type ModuleDownloadStatus = {
  id: string;
  status: DownloadState;
  progress: number;
  error_message: string | null;
};

// =============================================================
// Slot (Model)
// =============================================================

export type SlotInfo = {
  tts_type: TTSType | null;
  slot_index: number;
  name: string;
  description: string;
  credit: string;
  terms_of_use_url: string;
  icon_file: string | null;
};

export type GPTSoVITSSlotInfo = SlotInfo & {
  tts_type: "GPT-SoVITS";
  version: GPTSoVITSVersion;
  model_version: GPTSoVITSModelVersion;
  if_lora_v3: boolean;
  enable_faster: boolean | null;
  semantic_predictor_model_path: string | null;
  synthesizer_model_path: string | null;

  // Hyperparameters
  top_k: number;
  top_p: number;
  temperature: number;
  if_freeze: boolean;

  // ONNX backend
  backend_mode: BackendMode;
  onnx_vq_model_path: string | null;
  onnx_spec_path: string | null;
  onnx_latent_path: string | null;
  onnx_encoder_path: string | null;
  onnx_fsdec_path: string | null;
  onnx_ssdec_path: string | null;

  // Faster mode
  batch_size: number;
  batch_threshold: number;
  split_bucket: boolean;
  return_fragment: boolean;
  fragment_interval: number;
  seed: number;
  parallel_infer: boolean;
  repetition_penalty: number;
};

export type ReservedForSampleSlotInfo = SlotInfo & {
  tts_type: "RESERVED_FOR_SAMPLE";
  progress: number;
};

export type SlotInfoMember = SlotInfo | GPTSoVITSSlotInfo | ReservedForSampleSlotInfo;

// Import params
export type ModelImportParam = {
  tts_type: TTSType;
  name: string;
  terms_of_use_url: string;
  slot_index: number | null;
  icon_file: string | null;
};

export type GPTSoVITSModelImportParam = ModelImportParam & {
  tts_type: "GPT-SoVITS";
  semantic_predictor_model_path: string | null;
  synthesizer_model_path: string | null;
};

export type ReservedForSampleModelImportParam = ModelImportParam & {
  tts_type: "RESERVED_FOR_SAMPLE";
  progress: number;
};

export type ModelImportParamMember = ModelImportParam | GPTSoVITSModelImportParam | ReservedForSampleModelImportParam;

// =============================================================
// Voice Character
// =============================================================

export type EmotionType = {
  name: string;
  color: string;
};

export type ReferenceVoice = {
  voice_type: string;
  slot_index: number;
  wav_file: string;
  text: string;
  language: LanguageType;
  icon_file: string | null;
};

export type VoiceCharacter = {
  tts_type: TTSType | null;
  slot_index: number;
  name: string;
  description: string;
  credit: string;
  terms_of_use_url: string;
  icon_file: string | null;
  reference_voices: ReferenceVoice[];
  emotion_types: EmotionType[];
  progress: number;
};

export type ReferenceVoiceImportParam = {
  voice_type: string;
  wav_file: string;
  slot_index: number | null;
  icon_file: string | null;
  text: string | null;
};

export type VoiceCharacterImportParam = {
  tts_type: TTSType;
  name: string;
  terms_of_use_url: string;
  slot_index: number | null;
  icon_file: string | null;
  zip_file: string | null;
};

// =============================================================
// TTS
// =============================================================

export type GenerateVoiceParam = {
  voice_character_slot_index: number;
  reference_voice_slot_index: number;
  text: string;
  language: LanguageType;
  speed: number;
  cutMethod: CutMethod;
  sample_steps: number | null;
  phone_symbols: string[] | null;
};

export type OpenJTalkUserDictRecord = {
  string: string;
  pos: string;
  pos_group1: string;
  pos_group2: string;
  pos_group3: string;
  ctype: string;
  cform: string;
  orig: string;
  read: string;
  pron: string;
  acc: number;
  mora_size: number;
  chain_rule: string;
  chain_flag: number;
};

export type GetJpTextToUserDictRecordsParam = {
  text: string;
  voice_character_slot_index: number;
};

export type GetPhonesParam = {
  text: string;
  language: LanguageType;
  voice_character_slot_index: number;
  user_dict_records: OpenJTalkUserDictRecord[] | null;
};

export type GetPhonesResponse = {
  phones: number[];
  phone_symbols: string[];
};

// =============================================================
// Sample
// =============================================================

export type SampleDownloadParam = {
  slot_index: number;
  sample_id: string;
};

export type SampleDownloadStatus = {
  id: string;
  status: DownloadState;
  progress: number;
  error_message: string | null;
};

export type SampleInfo = {
  id: string;
  tts_type: TTSType;
  lang: string;
  tag: string[];
  name: string;
  terms_of_use_url: string;
  icon_url: string | null;
  credit: string;
  description: string;
};

export type GPTSoVITSSampleInfo = SampleInfo & {
  semantic_predictor_model_url: string | null;
  synthesizer_model_url: string | null;
  version: string;
  model_version: string;
  lora_v3: boolean;
};

export type VoiceCharacterSampleInfo = SampleInfo & {
  zip_url: string;
};

export type SampleInfoMember = SampleInfo | GPTSoVITSSampleInfo | VoiceCharacterSampleInfo;

// =============================================================
// Common
// =============================================================

export type MoveModelParam = {
  src: number;
  dst: number;
};

export type SetIconParam = {
  icon_file: string;
};

// =============================================================
// File Uploader
// =============================================================

export type UploadableFile = {
  title: string;
  filename: string;
};

export type FileuploaderInfo = {
  uploadable_files: UploadableFile[];
};

export type FileuploaderUploadFileChunkResult = {
  uploaded_filename: string;
};

export type FileuploaderConcatUploadedFileChunkResult = {
  generated_filename: string;
};

// =============================================================
// Emotion Colors
// =============================================================

export const EMOTION_COLORS: string[] = [
  "#BDD9FF", "#DCE1EA", "#FEA3BC", "#ABD373", "#FEE6E2",
  "#ECB4A7", "#B5D5DA", "#67B18A", "#D6B8DA", "#BEB75E",
  "#AFBDCA", "#B9A2B4", "#C4B684", "#A49367", "#D3C9C7",
  "#A2BEDB", "#DACD9E", "#BBC2D6", "#57637A", "#FAE3D3",
  "#DBD8C5", "#015D2B", "#083F56", "#237C94", "#CECDD5",
  "#2E8ED8", "#9FBD6D", "#BECD7E", "#96C0C2", "#E8DDDB",
  "#4B6943", "#DE403B", "#F6735F", "#EC9782", "#EEB685",
  "#D7B4CA", "#999AC7", "#DDC8E7", "#BEC3D6", "#E4E3C4",
  "#D2A2B0", "#C5D364", "#EA8A4A", "#87756B", "#EAE4E7",
  "#F5D7D9", "#EBA6A7", "#AC4839", "#365A2E", "#F4B17D",
  "#7F8142", "#815E58", "#E5864C", "#9444EF", "#FDD88A",
  "#BFC0A1", "#6B875F", "#B9C2D1", "#305455", "#DDC6CC",
  "#686EA8", "#A2ADC3", "#E6B2BD", "#CB5F88", "#DDC677",
  "#E8BCD8", "#AB1354", "#C6639C", "#00817C", "#F2F2F3",
  "#F5D9F2", "#9898CC", "#E8D8F4", "#C9D1F7", "#BDDCF7",
  "#8296D3", "#B7AFDF", "#EAC9E4", "#FFD0C8", "#FBDEDF",
  "#A782AD", "#C73AAC", "#7C3D71", "#B5B5A4", "#F1EEF0",
  "#EFB4BA", "#E14F42", "#ED8C6A", "#90B9B4", "#FCF4F2",
  "#576E8E", "#D09DD2", "#A097B4", "#332B66", "#C7BCCC",
  "#BA2737", "#E5CEBC", "#EAC9CA", "#B26D6E", "#E0707E",
];

// =============================================================
// Dialog types
// =============================================================

export type DialogName =
  | "none"
  | "confirm"
  | "textInput"
  | "select"
  | "progress"
  | "wait"
  | "modelSlotManager"
  | "voiceCharacterManager"
  | "advancedSetting"
  | "sample"
  | "aboutModel"
  | "aboutVoice"
  | "emotionColor"
  | "startingNotice";
