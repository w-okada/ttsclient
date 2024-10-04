export const MAX_SLOT_INDEX = 20;
export const MAX_VOICE_CHARACTER_SLOT_INDEX = 200
export const MAX_REFERENCE_VOICE_SLOT_INDEX = 20
////////////////////////////////////////////
// REST Params
////////////////////////////////////////////
export type TTSConfiguration = {
    current_slot_index: number;
    gpu_device_id_int: number;
};

export const AudioDeviceType = {
    audioinput: "audioinput",
    audiooutpu: "audiooutput",
} as const;
export type AudioDeviceType = (typeof AudioDeviceType)[keyof typeof AudioDeviceType];

export const VoiceChangerInputMode = {
    server: "server",
    client: "client",
} as const;
export type VoiceChangerInputMode = (typeof VoiceChangerInputMode)[keyof typeof VoiceChangerInputMode];

export type GPUInfo = {
    name: string;
    device_id: string;
    adapter_ram: number;
    device_id_int: number;
};

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

export const TTSTypes = ["GPT-SoVITS"] as const;
export type TTSType = (typeof TTSTypes)[number];

export type SlotInfoMember = SlotInfo | GPTSoVITSSlotInfo;
export type SlotInfo = {
    slot_index: number;
    tts_type: TTSType | null;
    name: string;
    description: string;
    credit: string;
    terms_of_use_url: string;
    icon_file: string | null;
};
export type GPTSoVITSSlotInfo = SlotInfo & {
    tts_type: "GPT-SoVITS";
    enable_faster: boolean
    semantic_predictor_model: string;
    synthesizer_path: string;
    top_k: number;
    top_p: number;
    temperature: number;
    if_freeze: number;


    backend_mode: BackendMode;
    onnx_vq_model_path: string | null
    onnx_spec_path: string | null
    onnx_latent_path: string | null
    onnx_encoder_path: string | null
    onnx_fsdec_path: string | null
    onnx_ssdec_path: string | null


    batch_size: number   // only for faster
    batch_threshold: number // only for faster
    split_bucket: boolean   // only for faster
    return_fragment: boolean   // only for faster
    fragment_interval: number   // only for faster
    seed: number     // only for faster
    parallel_infer: boolean  // only for faster
    repetition_penalty: number   // only for faster

};

export type ModelImportParamMember = ModelImportParam | GPTSoVITSModelImportParam;

export type ModelImportParam = {
    tts_type: TTSType;
    name: string;
    slot_index?: number | null;
    icon_file?: string | null;
};

export type GPTSoVITSModelImportParam = ModelImportParam & {
    tts_type: "GPT-SoVITS";
    semantic_predictor_model: string | null;
    synthesizer_path?: string | null;
};

export type MoveModelParam = {
    src: number;
    dst: number;
};

export type SetIconParam = {
    icon_file: string;
};


export type DownloadParam = {
    slot_index: number;
    sample_id: string;
};


export const BasicVoiceType = ["anger", "disgust", "fear", "happy", "sad", "surprise", "other"] as const;
export type BasicVoiceType = (typeof BasicVoiceType)[number];

export const LanguageType = [
    "all_zh",  // 全部按中文识别
    "en",  // 全部按英文识别#######不变
    "all_ja",  // 全部按日文识别
    "all_yue",  // 全部按中文识别
    // "all_ko",  // 全部按韩文识别
    "zh",  // 按中英混合识别####不变
    "ja",  // 按日英混合识别####不变
    "yue",  // 按粤英混合识别####不变
    // "ko",  // 按韩英混合识别####不变
    "auto", // 多语种启动切分识别语种
    "auto_yue",  // 多语种启动切分识别语种

] as const
export type LanguageType = (typeof LanguageType)[number];
export const CutMethod = [
    "No slice",
    "Slice once every 4 sentences",
    "Slice per 50 characters",
    "Slice by Chinese punct",
    "Slice by English punct",
    "Slice by every punct",
] as const
export type CutMethod = (typeof CutMethod)[number];

export const BackendMode = ["all_torch", "all_onnx", "semantic_onnx", "synthesizer_onnx"] as const
export type BackendMode = (typeof BackendMode)[number]


export type ReferenceVoice = {
    slot_index: number
    voice_type: BasicVoiceType | string
    wav_file: string
    text: string
    language: LanguageType
    icon_file: string | null
    speed: number
}

export type VoiceCharacter = {
    slot_index: number;
    tts_type: TTSType | null;
    name: string;
    description: string;
    credit: string;
    terms_of_use_url: string;
    icon_file: string | null;
    reference_voices: ReferenceVoice[];
};

export type VoiceCharacterImportParam = {
    tts_type: TTSType
    name: string
    terms_of_use_url: string
    slot_index: number | null
    icon_file: string | null
    zip_file: string | null
}

export type ReferenceVoiceImportParam = {
    voice_type: BasicVoiceType | string
    wav_file: string
    voice_character_slot_index: number
    slot_index: number | null
}


export type MoveReferenceVoiceParam = {
    src: number
    dst: number
}

export type GenerateVoiceParam = {
    voice_character_slot_index: number
    reference_voice_slot_index: number
    text: string
    language: LanguageType
    speed: number
    cutMethod: CutMethod
}

////////////////////////////////////////////
// VoiceChangerClient Settings
////////////////////////////////////////////
export type ClientSetting = {
    voiceChangerClientSetting: VoiceChangerClientSetting;
    workletNodeSetting: WorkletNodeSetting;
    workletSetting: WorkletSetting;
};
// (1) VoiceChangerClientSetting
export const SampleRate = {
    "48000": 48000,
} as const;
export type SampleRate = (typeof SampleRate)[keyof typeof SampleRate];

export type VoiceChangerClientSetting = {
    audioInput: string | MediaStream;
    sampleRate: SampleRate; // 48000Hz
    echoCancel: boolean;
    noiseSuppression: boolean;
    noiseSuppression2: boolean;

    inputGain: number;
    outputGain: number;
    monitorGain: number;

    passThroughConfirmationSkip: boolean;
};
// (2) WorkletNodeSetting
export const Protocols = ["sio", "rest", "internal"] as const;
export type Protocol = (typeof Protocols)[number];

export const SendingSampleRate = {
    "48000": 48000,
    "44100": 44100,
    "24000": 24000,
} as const;
export type SendingSampleRate = (typeof SendingSampleRate)[keyof typeof SendingSampleRate];

export const DownSamplingMode = {
    decimate: "decimate",
    average: "average",
} as const;
export type DownSamplingMode = (typeof DownSamplingMode)[keyof typeof DownSamplingMode];

export type WorkletNodeSetting = {
    serverUrl: string;
    protocol: Protocol;
    sendingSampleRate: SendingSampleRate;
    // sendingChunkNum: number;
    sendingChunkSec: number;
    sendingChunkAsBulk: boolean;
    enableFlatPath: boolean;
    workOnColab: boolean;
};
// (3) WorkletSetting
export type WorkletSetting = {
    numTrancateTreshold: number;
    outputBufferFactor: number;
};

// (misc) default ClientSetting
export const DefaultClientSettng: ClientSetting = {
    voiceChangerClientSetting: {
        audioInput: "none",
        sampleRate: 48000,
        echoCancel: false,
        noiseSuppression: false,
        noiseSuppression2: false,
        inputGain: 1.0,
        outputGain: 1.0,
        monitorGain: 1.0,
        passThroughConfirmationSkip: false,
    },
    workletNodeSetting: {
        serverUrl: "",
        protocol: "rest",
        sendingSampleRate: 48000,
        // sendingChunkNum: 3,
        sendingChunkSec: 0.1,
        sendingChunkAsBulk: false,
        enableFlatPath: false,
        workOnColab: false,
    },
    workletSetting: {
        numTrancateTreshold: 100,
        outputBufferFactor: 5,
    },
};
////////////////////////////////////
// VoiceChangerClient Exceptions
////////////////////////////////////
export const VOICE_CHANGER_CLIENT_EXCEPTION = {
    ERR_SIO_CONNECT_FAILED: "ERR_SIO_CONNECT_FAILED",
    ERR_SIO_INVALID_RESPONSE: "ERR_SIO_INVALID_RESPONSE",
    ERR_REST_INVALID_RESPONSE: "ERR_REST_INVALID_RESPONSE",
    ERR_MIC_STREAM_NOT_INITIALIZED: "ERR_MIC_STREAM_NOT_INITIALIZED",
    ERR_INTERNAL_AUDIO_PROCESS_CALLBACK_IS_NOT_INITIALIZED: "ERR_INTERNAL_AUDIO_PROCESS_CALLBACK_IS_NOT_INITIALIZED",
    ERR_HTTP_EXCEPTION: "ERR_HTTP_EXCEPTION",
} as const;
export type VOICE_CHANGER_CLIENT_EXCEPTION = (typeof VOICE_CHANGER_CLIENT_EXCEPTION)[keyof typeof VOICE_CHANGER_CLIENT_EXCEPTION];

export type HttpException = {
    type: VOICE_CHANGER_CLIENT_EXCEPTION;
    status: number;
    statusText: string;
    code: number;
    reason: string;
    action: string;
    detail: string | null;
};

////////////////////////////////////
// Performance
////////////////////////////////////
export type PerformanceData = {
    input_size: number;
    output_size: number;
    elapsed_time: number;
    input_volume_db: number;
    output_volume_db: number;
    data_num: number;
};

////////////////////////////////////
// Exception
////////////////////////////////////
export type VCClientErrorInfo = {
    code: number;
    reason: string;
    action: string;
    detail: string | null;
};
















