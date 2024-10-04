export const AUDIO_ELEMENT_FOR_PLAY_RESULT = "audio-result"; // 変換後の出力用プレイヤー
export const AUDIO_ELEMENT_FOR_PLAY_MONITOR = "audio-monitor"; //  変換後のモニター用プレイヤー
export const AUDIO_ELEMENT_FOR_SERVER_IO_ANALYZER_INPUT = "AUDIO_ELEMENT_FOR_SERVER_IO_ANALYZER_INPUT";
export const AUDIO_ELEMENT_FOR_SERVER_IO_ANALYZER_OUTPUT = "AUDIO_ELEMENT_FOR_SERVER_IO_ANALYZER_OUTPUT";

export const AUDIO_ELEMENT_FOR_INPUT_MEDIA = "AUDIO_ELEMENT_FOR_INPUT_MEDIA";
export const AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK = "AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK";

const AppMode = {
    App: "App",
    LogViewer: "LogViewer",
    JsonViewer: "JsonViewer",
    ApiTest: "ApiTest",
} as const;
export type AppMode = (typeof AppMode)[keyof typeof AppMode];

export const ToastLevel = {
    Info: "Info",
    Success: "Success",
    Warning: "Warning",
    Error: "Error",
} as const;
export type ToastLevel = (typeof ToastLevel)[keyof typeof ToastLevel];

export const AudioDeviceType = {
    Input: "Input",
    Output: "Output",
    Monitor: "Monitor",
} as const;
export type AudioDeviceType = (typeof AudioDeviceType)[keyof typeof AudioDeviceType];

export const PlayerType = {
    in: "in",
    out: "out",
} as const;
export type PlayerType = (typeof PlayerType)[keyof typeof PlayerType];

export const UploadFileKinds = ["semanticPredictorModelFile", "synthesizerModelFile"] as const;
export type UploadFileKind = (typeof UploadFileKinds)[number];

export type UploadFile = {
    kind: UploadFileKind;
    file: File;
};


export const VoiceCharacterUploadFileKinds = ["zipFile"] as const;
export type VoiceCharacterUploadFileKind = (typeof VoiceCharacterUploadFileKinds)[number];

export type VoiceCharacterUploadFile = {
    kind: VoiceCharacterUploadFileKind;
    file: File;
};

// export const VoiceTypeColor = {
//     "anger": "#ffdede",
//     "disgust": "#bee0ec",
//     "fear": "#f2e9ff",
//     "happy": "#f4ff00",
//     "sad": "#e2e9f7",
//     "surprise": "#f1e687",
//     "other": "#dffceb",
// } as const;
// export type VoiceTypeColor = (typeof VoiceTypeColor)[keyof typeof VoiceTypeColor];