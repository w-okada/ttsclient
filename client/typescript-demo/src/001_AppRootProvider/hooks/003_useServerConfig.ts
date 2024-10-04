import { useEffect, useRef, useState } from "react";
import {
    GPUInfo,
    ModuleStatus,
    SlotInfoMember,
    TTSRestClient,
    TTSConfiguration,
    VOICE_CHANGER_CLIENT_EXCEPTION,
    VoiceCharacter,
    MoveModelParam,
    TTSType,
    ReferenceVoice,
    GenerateVoiceParam,
} from "tts-client-typescript-client-lib";
import { UploadFile, VoiceCharacterUploadFile } from "../../const";

export type ServerConfigState = {
    serverConfiguration?: TTSConfiguration;
    serverGpuInfo?: GPUInfo[];
    serverModuleStatus?: ModuleStatus;
    serverSlotInfos?: SlotInfoMember[];
    voiceCharacterSlotInfos: VoiceCharacter[]
    // voiceChangerManagerInfo?: VoiceChangerManagerInfo;
};

export type ServerConfigStateAndMethod = ServerConfigState & {
    reloadServerConfiguration: () => Promise<void>;
    reloadServerGpuInfo: () => Promise<void>;
    reloadServerModuleStatus: () => Promise<void>;
    reloadServerSlotInfos: () => Promise<void>;
    reloadVoiceCharacterSlotInfos: () => Promise<void>;
    initializeServer: () => Promise<void>
    updateServerConfiguration: (conf: TTSConfiguration) => Promise<void>;
    uploadModelFile: (
        slotIndex: number | null,
        tTSType: TTSType,
        files: UploadFile[],
        onprogress: (progress: number, end: boolean) => void,
    ) => Promise<void>;
    updateServerSlotInfo: (slotInfo: SlotInfoMember) => Promise<void>;
    deleteServerSlotInfo: (slotIndex: number) => Promise<void>;
    uploadIconFile: (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => Promise<void>;
    generateOnnx: (slotIndex: number) => Promise<void>
    moveModel: (src: number, dst: number) => Promise<void>;
    downloadVoiceCharacter: (voiceCharacterSlotIndex: number) => Promise<Blob | null>;
    uploadVoiceCharacterFile: (
        slotIndex: number | null,
        tTSType: TTSType,
        name: string,
        files: VoiceCharacterUploadFile[],
        onprogress: (progress: number, end: boolean) => void
    ) => Promise<void>
    updateVoiceCharacterSlotInfo: (voiceCharacter: VoiceCharacter) => Promise<void>
    deleteVoiceCharacterSlotInfo: (slotIndex: number) => Promise<void>
    uploadVoiceCharacterIconFile: (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => Promise<void>
    moveVoiceCharacter: (src: number, dst: number) => Promise<void>

    addReferenceVoice: (slotIndex: number, voiceIndex: number, voiceType: string, wavFile: File, onprogress: (progress: number, end: boolean) => void) => Promise<void>
    updateReferenceVoice: (voiceCharacterSlotIndex: number, voiceIndex: number, referenceVoice: ReferenceVoice) => Promise<void>
    deleteReferenceVoice: (voiceCharacterSlotIndex: number, voiceIndex: number) => Promise<void>
    updateReferenceVoiceIconFile: (voiceCharacterSlotIndex: number, voiceIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => Promise<void>

    generateVoice: (genearteVoiceParam: GenerateVoiceParam) => Promise<Blob | null>
};

export type UseServerConfigProps = {
    exceptionCallback: (message: string) => void;
    flatPath: boolean;
    serverBaseUrl: string;

};
// サーバ情報取得と更新。音声変換以外のRESTでの操作が集まっている。
export const useServerConfig = (props: UseServerConfigProps): ServerConfigStateAndMethod => {
    const restClient = useRef<TTSRestClient>();
    const [serverConfiguration, setServerConfiguration] = useState<TTSConfiguration>();
    const [serverGpuInfo, setServerGpuInfo] = useState<GPUInfo[]>();
    const [serverModuleStatus, setServerModuleStatus] = useState<ModuleStatus>();
    const [serverSlotInfos, setServerSlotInfos] = useState<SlotInfoMember[]>([]);
    const [voiceCharacterSlotInfos, setVoiceCharacterSlotInfos] = useState<VoiceCharacter[]>([]);
    // const [voiceChangerManagerInfo, setVoiceChangerManagerInfo] = useState<VoiceChangerManagerInfo>();

    useEffect(() => {
        restClient.current = TTSRestClient.getInstance();
        console.log("props.flatPath, props.serverBaseUrl", props.flatPath, props.serverBaseUrl)
        restClient.current.setEnableFlatPath(props.flatPath);
        restClient.current.setBaseUrl(props.serverBaseUrl);

        restClient.current.getServerConfiguration();
        reloadServerConfiguration();
        reloadServerGpuInfo();
        reloadServerModuleStatus();
        reloadServerSlotInfos();
        reloadVoiceCharacterSlotInfos();
        // reloadVoiceChangerManagerInfos();
    }, [props.flatPath, props.serverBaseUrl]);

    useEffect(() => {

    }, []);

    // サーバ情報取得系
    const reloadServerConfiguration = async () => {
        if (!restClient.current) {
            return;
        }
        const conf = await restClient.current.getServerConfiguration();
        setServerConfiguration(conf);
    };
    const reloadServerGpuInfo = async () => {
        if (!restClient.current) {
            return;
        }
        const gpuInfo = await restClient.current.getServerGPUInfo();
        setServerGpuInfo(gpuInfo);
    };

    const reloadServerModuleStatus = async () => {
        if (!restClient.current) {
            return;
        }
        const moduleStatus = await restClient.current.getServerModuleStatus();
        setServerModuleStatus(moduleStatus);
    };


    const reloadServerSlotInfos = async () => {
        if (!restClient.current) {
            return;
        }
        const slotInfos = await restClient.current.getServerSlotInfos();
        setServerSlotInfos(slotInfos);
    };

    const reloadVoiceCharacterSlotInfos = async () => {
        if (!restClient.current) {
            return;
        }
        const voiceCharacterSlotInfos = await restClient.current.getVoiceCharacterSlotInfos();
        setVoiceCharacterSlotInfos(voiceCharacterSlotInfos);
    }


    // 設定系
    // 共通のエラーハンドリング関数
    const withErrorHandling = async (fn: () => Promise<void>) => {
        try {
            await fn();
        } catch (error) {
            console.info("[RestClient] Error occurred:", error);
            if (error.type == VOICE_CHANGER_CLIENT_EXCEPTION.ERR_HTTP_EXCEPTION) {
                const message = `${error.status}[${error.statusText}]: ${error.reason} ${error.action}`;
                props.exceptionCallback(message);
            } else {
                throw error;
            }
        }
    };

    const updateServerConfiguration = async (conf: TTSConfiguration) => {
        await withErrorHandling(async () => {
            await _updateServerConfiguration(conf);
        });
    };

    const _updateServerConfiguration = async (conf: TTSConfiguration) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.updateServerConfiguration(conf);
        reloadServerConfiguration();
    };

    //  モデルスロット
    const uploadModelFile = async (
        slotIndex: number | null,
        tTSType: TTSType,
        files: UploadFile[],
        onprogress: (progress: number, end: boolean) => void,
    ) => {
        if (!restClient.current) {
            return;
        }
        if (tTSType === "GPT-SoVITS") {
            const semanticPredictorModelFile = files.find((f) => f.kind === "semanticPredictorModelFile")?.file || null;
            const synthesizerModelFile = files.find((f) => f.kind === "synthesizerModelFile")?.file || null;
            await restClient.current.uploadGPTSoVITSModelFile(slotIndex, semanticPredictorModelFile, synthesizerModelFile, onprogress);
        } else {
            throw new Error("Not supported voice changer type");
        }
        reloadServerSlotInfos();
    };
    const updateServerSlotInfo = async (slotInfo: SlotInfoMember) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.updateServerSlotInfo(slotInfo);
        reloadServerSlotInfos();
    };
    const deleteServerSlotInfo = async (slotIndex: number) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.deleteServerSlotInfo(slotIndex);
        reloadServerSlotInfos();
    };
    const uploadIconFile = async (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.uploadIconFile(slotIndex, iconFile, onprogress);
        reloadServerSlotInfos();
    };
    const generateOnnx = async (slotIndex: number) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.generateOnnx(slotIndex);
        reloadServerSlotInfos();
    };
    const moveModel = async (src: number, dst: number) => {
        if (!restClient.current) {
            return;
        }
        const moveParam: MoveModelParam = {
            src: src,
            dst: dst,
        };
        await restClient.current.moveModel(moveParam);
        reloadServerSlotInfos();
    };

    //  Voice Character
    const uploadVoiceCharacterFile = async (
        slotIndex: number | null,
        tTSType: TTSType,
        name: string,
        files: VoiceCharacterUploadFile[],
        onprogress: (progress: number, end: boolean) => void,
    ) => {
        const zipFile = files.find((f) => f.kind === "zipFile")?.file || null;
        await restClient.current?.uploadVoiceCharacterFile(slotIndex, tTSType, name, zipFile, onprogress)
        reloadVoiceCharacterSlotInfos();
    }
    const updateVoiceCharacterSlotInfo = async (voiceCharacter: VoiceCharacter) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.updateVoiceCharacterSlotInfo(voiceCharacter);
        reloadVoiceCharacterSlotInfos();
    };

    const deleteVoiceCharacterSlotInfo = async (slotIndex: number) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.deleteVoiceCharacterSlotInfo(slotIndex);
        reloadVoiceCharacterSlotInfos();
    };
    const uploadVoiceCharacterIconFile = async (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.uploadVoiceCharacterIconFile(slotIndex, iconFile, onprogress);
        reloadVoiceCharacterSlotInfos();
    };

    const moveVoiceCharacter = async (src: number, dst: number) => {
        if (!restClient.current) {
            return;
        }
        const moveParam: MoveModelParam = {
            src: src,
            dst: dst,
        };
        await restClient.current.moveVoiceCharacter(moveParam);
        reloadVoiceCharacterSlotInfos();
    };
    const downloadVoiceCharacter = async (voiceCharacterSlotIndex: number) => {
        if (!restClient.current) {
            return null;
        }
        return await restClient.current.downloadVoiceCharacter(voiceCharacterSlotIndex);
    };


    //  Voice Character Reference Voice
    const addReferenceVoice = async (slotIndex: number, voiceIndex: number, voiceType: string, wavFile: File, onprogress: (progress: number, end: boolean) => void) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.addReferenceVoice(slotIndex, voiceIndex, voiceType, wavFile, onprogress);
        reloadVoiceCharacterSlotInfos();
    }
    const updateReferenceVoice = async (voiceCharacterSlotIndex: number, voiceIndex: number, referenceVoice: ReferenceVoice) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.updateReferenceVoice(voiceCharacterSlotIndex, voiceIndex, referenceVoice);
        reloadVoiceCharacterSlotInfos();
    }
    const deleteReferenceVoice = async (voiceCharacterSlotIndex: number, voiceIndex: number) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.deleteReferenceVoice(voiceCharacterSlotIndex, voiceIndex);
        reloadVoiceCharacterSlotInfos();
    }
    const updateReferenceVoiceIconFile = async (voiceCharacterSlotIndex: number, voiceIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.uploadReferenceVoiceIconFile(voiceCharacterSlotIndex, voiceIndex, iconFile, onprogress);
        reloadVoiceCharacterSlotInfos();
    }


    // オペレーション系
    const generateVoice = async (genearteVoiceParam: GenerateVoiceParam) => {
        if (!restClient.current) {
            return null;
        }
        const blob = await restClient.current.generateVoice(genearteVoiceParam);
        return blob

    }

    const initializeServer = async () => {
        if (!restClient.current) {
            return;
        }
        await restClient.current.initializeServer();
        reloadServerSlotInfos();
        reloadVoiceCharacterSlotInfos();
    };


    const res = {
        serverConfiguration,
        serverGpuInfo,
        serverModuleStatus,
        serverSlotInfos,
        voiceCharacterSlotInfos,
        reloadServerConfiguration,
        reloadServerGpuInfo,
        reloadServerModuleStatus,
        reloadServerSlotInfos,
        reloadVoiceCharacterSlotInfos,
        updateServerConfiguration,
        uploadModelFile,
        updateServerSlotInfo,
        deleteServerSlotInfo,
        uploadIconFile,
        generateOnnx,
        moveModel,
        uploadVoiceCharacterFile,
        updateVoiceCharacterSlotInfo,
        deleteVoiceCharacterSlotInfo,
        uploadVoiceCharacterIconFile,
        moveVoiceCharacter,
        downloadVoiceCharacter,

        addReferenceVoice,
        updateReferenceVoice,
        deleteReferenceVoice,
        updateReferenceVoiceIconFile,
        // startRecording,
        // stopRecording,
        // startServerDevice,
        // stopServerDevice,
        initializeServer,
        generateVoice,
    };
    return res;
};
