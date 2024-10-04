import { FileUploaderClient } from "./FileUploaderClient";
import {
    // BeatriceV2ModelImportParam,
    // DownloadParam,
    GPUInfo,
    HttpException,
    // MergeParam,
    ModuleStatus,
    // MoveExportedOnnxModelParam,
    // MoveMergedModelParam,
    // MoveModelParam,
    // OnnxExportParam,
    // RVCModelImportParam,
    // SampleInfo,
    // ServerAudioDevice,
    // SetIconParam,
    // SlotInfoMember,
    VCClientErrorInfo,
    TTSConfiguration,
    SlotInfoMember,
    GPTSoVITSModelImportParam,
    MoveModelParam,
    SetIconParam,
    VoiceCharacter,
    VoiceCharacterImportParam,
    ReferenceVoiceImportParam,
    BasicVoiceType,
    MoveReferenceVoiceParam,
    ReferenceVoice,
    TTSType,
    GenerateVoiceParam,
} from "./const";

abstract class RestResult<T> {
    abstract isOk(): boolean;
    abstract get(): T;
}

class Ok<T> extends RestResult<T> {
    constructor(private value: T) {
        super();
    }

    isOk(): boolean {
        return true;
    }

    get(): T {
        return this.value;
    }
}

class Err<T> extends RestResult<T> {
    constructor(private error: HttpException) {
        super();
    }

    isOk(): boolean {
        return false;
    }

    get(): T {
        throw this.error;
    }
}
type ResponseType = 'json' | 'blob';

export class RestClient {
    #baseUrl: string;
    constructor() {
        this.#baseUrl = "";
    }

    setBaseUrl = (baseUrl: string): void => {
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.slice(0, -1);
        }
        this.#baseUrl = baseUrl;
    };

    execFetch = async <T>(request: Request, responseType: ResponseType = "json"): Promise<RestResult<T>> => {
        return new Promise<RestResult<T>>((resolve) => {
            fetch(request)
                .then(async (response) => {
                    if (response.ok) {
                        let data: T;
                        if (responseType === 'blob') {
                            data = (await response.blob()) as unknown as T;
                        } else {
                            data = (await response.json()) as T;
                        }
                        resolve(new Ok(data));
                    } else {
                        const info = await response.json();
                        if (info.detail != null) {
                            const detail = JSON.parse(info.detail) as VCClientErrorInfo;
                            const ex: HttpException = {
                                type: "ERR_HTTP_EXCEPTION",
                                status: response.status,
                                statusText: response.statusText,
                                code: detail.code,
                                reason: detail.reason,
                                action: detail.action,
                                detail: detail.detail,
                            };
                            resolve(new Err(ex));
                        } else {
                            const ex: HttpException = {
                                type: "ERR_HTTP_EXCEPTION",
                                status: response.status,
                                statusText: response.statusText,
                                code: info.code,
                                reason: "no detail",
                                action: "no action",
                                detail: info.detail,
                            };
                            resolve(new Err(ex));
                        }
                    }
                })
                .catch((error) => {
                    console.error(error);
                    const ex: HttpException = {
                        type: "ERR_HTTP_EXCEPTION",
                        status: 0,
                        statusText: "",
                        code: -1,
                        reason: `${error}`,
                        action: "",
                        detail: null,
                    };
                    resolve(new Err(ex));
                });
        });
    };

    getRequest = async <T>(path: string, responseType: ResponseType = "json"): Promise<T> => {
        let url: string = path.startsWith("/") ? `${this.#baseUrl}${path}` : `${this.#baseUrl}/${path}`;
        const request = new Request(url, {
            method: "GET",
        });
        const info = await this.execFetch<T>(request, responseType);

        if (!info.isOk()) {
            throw info.get();
        }
        return info.get();
    };

    postRequest = async <T>(path: string, body: any, responseType: ResponseType = "json"): Promise<T> => {
        let url: string = path.startsWith("/") ? `${this.#baseUrl}${path}` : `${this.#baseUrl}/${path}`;

        const request = new Request(url, {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "Content-Type": "application/json",
            },
        });
        const info = await this.execFetch<T>(request, responseType);

        if (!info.isOk()) {
            throw info.get();
        }
        return info.get();
    };

    putRequest = async <T>(path: string, body: any, responseType: ResponseType = "json"): Promise<T> => {
        let url: string = path.startsWith("/") ? `${this.#baseUrl}${path}` : `${this.#baseUrl}/${path}`;

        const request = new Request(url, {
            method: "PUT",
            body: JSON.stringify(body),
            headers: {
                "Content-Type": "application/json",
            },
        });
        const info = await this.execFetch<T>(request, responseType);

        if (!info.isOk()) {
            throw info.get();
        }
        return info.get();
    };

    deleteRequest = async <T>(path: string, body: any | null, responseType: ResponseType = "json"): Promise<T> => {
        let url: string = path.startsWith("/") ? `${this.#baseUrl}${path}` : `${this.#baseUrl}/${path}`;

        let request
        if (body != null) {
            request = new Request(url, {
                method: "DELETE",
                body: JSON.stringify(body),
                headers: {
                    "Content-Type": "application/json",
                },
            });
        } else {
            request = new Request(url, {
                method: "DELETE",
            });

        }
        const info = await this.execFetch<T>(request, responseType);

        if (!info.isOk()) {
            throw info.get();
        }
        return info.get();
    };
}

export class TTSRestClient {
    private static _instance: TTSRestClient | null = null;
    restClient: RestClient;
    fileUploaderClient: FileUploaderClient;
    enableFlatPath: boolean = false;

    private constructor() {
        this.restClient = new RestClient();
        this.fileUploaderClient = new FileUploaderClient();
    }

    static getInstance = (): TTSRestClient => {
        if (TTSRestClient._instance === null) {
            TTSRestClient._instance = new TTSRestClient();
        }
        return TTSRestClient._instance;
    };

    setBaseUrl = (baseUrl: string): void => {
        this.restClient.setBaseUrl(baseUrl);
        this.fileUploaderClient.setBaseUrl(baseUrl);
    };

    setEnableFlatPath = (enable: boolean): void => {
        this.enableFlatPath = enable;
        this.fileUploaderClient.setEnableFlatPath(enable);
        console.log("setEnableFlatPath", this.enableFlatPath)
    };

    generatePath = (path: string): string => {
        if (this.enableFlatPath) {
            return path[0] + path.slice(1).replace(/\//g, "_");
        }
        return path;
    };

    initializeServer = async () => {
        const path = this.generatePath(`/api/operation/initialize`);
        await this.restClient.postRequest<null>(path, null);
    };

    getServerConfiguration = async (): Promise<TTSConfiguration> => {
        const path = this.generatePath(`/api/configuration-manager/configuration`);
        const conf = await this.restClient.getRequest<TTSConfiguration>(path);
        return conf;
    };

    updateServerConfiguration = async (conf: TTSConfiguration) => {
        const path = this.generatePath(`/api/configuration-manager/configuration`);
        await this.restClient.putRequest<null>(path, conf);
    };

    getServerGPUInfo = async (): Promise<GPUInfo[]> => {
        const path = this.generatePath(`/api/gpu-device-manager/devices`);
        const info = await this.restClient.getRequest<GPUInfo[]>(path);
        return info;
    };

    getServerModuleStatus = async (): Promise<ModuleStatus> => {
        const path = this.generatePath(`/api/module-manager/modules`);
        const info = await this.restClient.getRequest<ModuleStatus>(path);
        return info;
    };

    getServerSlotInfos = async (): Promise<SlotInfoMember[]> => {
        const path = this.generatePath(`/api/slot-manager/slots`);
        console.log("getServerSlotInfos path", path)
        const infos = await this.restClient.getRequest<SlotInfoMember[]>(path);
        return infos;
    };

    getServerSlotInfo = async (slotIndex: number): Promise<SlotInfoMember> => {
        const path = this.generatePath(`/api/slot-manager/slots/${slotIndex}`);
        const info = await this.restClient.getRequest<SlotInfoMember>(path);
        return info;
    };


    uploadFile = async (dir: string, file: File, onprogress: (progress: number, end: boolean) => void) => {
        const chunk_num = await this.fileUploaderClient.uploadFile(dir, file, onprogress);
        await this.fileUploaderClient.concatUploadedFile(file.name, chunk_num);
    };
    uploadGPTSoVITSModelFile = async (slot_index: number | null, semanticPredictorModelFile: File | null, synthesizerModelFile: File | null, onprogress: (progress: number, end: boolean) => void) => {

        let uploadFileNum = 0
        if (semanticPredictorModelFile != null) {
            uploadFileNum += 1
        }
        if (synthesizerModelFile != null) {
            uploadFileNum += 1
        }

        let progressSum = 0
        if (semanticPredictorModelFile != null) {
            await this.uploadFile("", semanticPredictorModelFile, (progress: number, _end: boolean) => {
                console.log("progress [A]", progress)
                onprogress(progress / uploadFileNum, false);

            });
            progressSum += (100 / uploadFileNum)
        }
        if (synthesizerModelFile != null) {
            await this.uploadFile("", synthesizerModelFile, (progress: number, _end: boolean) => {
                console.log("progress [B]", progress)
                onprogress(progress / uploadFileNum + progressSum, false);
            });
            progressSum += (100 / uploadFileNum)
        }

        const path = this.generatePath(`/api/slot-manager/slots`);
        const rvcImportParam: GPTSoVITSModelImportParam = {
            slot_index: slot_index ?? null,
            tts_type: "GPT-SoVITS",
            name: synthesizerModelFile ? synthesizerModelFile.name : "GPT-SoVITS",
            semantic_predictor_model: semanticPredictorModelFile?.name ?? null,
            synthesizer_path: synthesizerModelFile?.name ?? null,
        };
        await this.restClient.postRequest<null>(path, rvcImportParam);
        return;
    };

    deleteServerSlotInfo = async (slotIndex: number) => {
        const path = this.generatePath(`/api/slot-manager/slots/${slotIndex}`);
        await this.restClient.deleteRequest<null>(path, null);
    };

    updateServerSlotInfo = async (slotInfo: SlotInfoMember) => {
        const path = this.generatePath(`/api/slot-manager/slots/${slotInfo.slot_index}`);
        await this.restClient.putRequest<null>(path, slotInfo);
    };

    moveModel = async (moveParam: MoveModelParam) => {
        const path = this.generatePath(`/api/slot-manager/slots/operation/move_model`);
        await this.restClient.postRequest<null>(path, moveParam);
    };

    uploadIconFile = async (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        await this.uploadFile("", iconFile, (progress: number, _end: boolean) => {
            onprogress(progress, false);
        });
        const path = this.generatePath(`/api/slot-manager/slots/${slotIndex}/operation/set_icon_file`);
        const param: SetIconParam = {
            icon_file: iconFile.name,
        };
        await this.restClient.postRequest<null>(path, param);
    };

    generateOnnx = async (slotIndex: number) => {
        const path = this.generatePath(`/api/slot-manager/slots/${slotIndex}/operation/generate_onnx`);
        await this.restClient.postRequest<null>(path, null);

    };

    getVoiceCharacterSlotInfos = async (): Promise<VoiceCharacter[]> => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots`);
        const infos = await this.restClient.getRequest<VoiceCharacter[]>(path);
        return infos;
    };

    getVoiceCharacterSlotInfo = async (slotIndex: number): Promise<VoiceCharacter> => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}`);
        const info = await this.restClient.getRequest<VoiceCharacter>(path);
        return info;
    };
    uploadVoiceCharacterFile = async (slot_index: number | null, tTSType: TTSType, name: string, zipFile: File | null, onprogress: (progress: number, end: boolean) => void) => {

        let uploadFileNum = 0
        if (zipFile != null) {
            uploadFileNum += 1
        }

        if (zipFile != null) {
            await this.uploadFile("", zipFile, (progress: number, _end: boolean) => {
                onprogress(progress / uploadFileNum, false);
            });
        }

        const path = this.generatePath(`/api/voice-character-slot-manager/slots`);
        const voiceCharacterImportParam: VoiceCharacterImportParam = {
            slot_index: slot_index ?? null,
            tts_type: tTSType,
            name: name,
            zip_file: zipFile?.name ?? null,
            terms_of_use_url: " ",
            icon_file: null
        };
        await this.restClient.postRequest<null>(path, voiceCharacterImportParam);
        return;
    };

    deleteVoiceCharacterSlotInfo = async (slotIndex: number) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}`);
        await this.restClient.deleteRequest<null>(path, null);
    };

    updateVoiceCharacterSlotInfo = async (slotInfo: VoiceCharacter) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotInfo.slot_index}`);
        await this.restClient.putRequest<null>(path, slotInfo);
    };

    moveVoiceCharacter = async (moveParam: MoveModelParam) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/operation/move_model`);
        await this.restClient.postRequest<null>(path, moveParam);
    };

    downloadVoiceCharacter = async (slotIndex: number) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}/voices/operation/zip_and_download`);
        const blob = await this.restClient.postRequest<Blob>(path, null, "blob");
        return blob
    }

    uploadVoiceCharacterIconFile = async (slotIndex: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        await this.uploadFile("", iconFile, (progress: number, _end: boolean) => {
            onprogress(progress, false);
        });
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}/operation/set_icon_file`);
        const param: SetIconParam = {
            icon_file: iconFile.name,
        };
        await this.restClient.postRequest<null>(path, param);
    };

    addReferenceVoice = async (slotIndex: number, voice_index: number | null, voiceType: BasicVoiceType | string, wavFile: File, onprogress: (progress: number, end: boolean) => void) => {
        await this.uploadFile("", wavFile, (progress: number, _end: boolean) => {
            onprogress(progress, false);
        });

        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}/voices`);
        const param: ReferenceVoiceImportParam = {
            voice_type: voiceType,
            wav_file: wavFile.name,
            voice_character_slot_index: slotIndex,
            slot_index: voice_index
        }
        await this.restClient.postRequest<null>(path, param);
    }

    deleteReferenceVoice = async (voiceCharacterSlotIndex: number, voice_index: number) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${voiceCharacterSlotIndex}/voices/${voice_index}`);
        await this.restClient.deleteRequest<null>(path, null);
    }

    updateReferenceVoice = async (voiceCharacterSlotIndex: number, voice_index: number, reference_voice: ReferenceVoice) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${voiceCharacterSlotIndex}/voices/${voice_index}`);
        await this.restClient.putRequest<null>(path, reference_voice);
    }


    moveReferenceVoice = async (voiceCharacterSlotIndex: number, param: MoveReferenceVoiceParam) => {
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${voiceCharacterSlotIndex}/voices/operation/move_voice`);
        await this.restClient.postRequest<null>(path, param);
    }

    uploadReferenceVoiceIconFile = async (slotIndex: number, voice_index: number, iconFile: File, onprogress: (progress: number, end: boolean) => void) => {
        await this.uploadFile("", iconFile, (progress: number, _end: boolean) => {
            onprogress(progress, false);
        });
        const path = this.generatePath(`/api/voice-character-slot-manager/slots/${slotIndex}/voices/${voice_index}/operation/set_icon_file`);
        const param: SetIconParam = {
            icon_file: iconFile.name,
        };
        await this.restClient.postRequest<null>(path, param);
    };

    // 実行
    generateVoice = async (param: GenerateVoiceParam) => {
        const path = this.generatePath(`/api/tts-manager/operation/generateVoice`);
        const blob = await this.restClient.postRequest<Blob>(path, param, "blob");
        return blob
    }

    // startRecording = async () => {
    //     const path = this.generatePath(`/api/voice-changer/operation/start_recording`);
    //     await this.restClient.postRequest<null>(path, null);
    // };

    // stopRecording = async () => {
    //     const path = this.generatePath(`/api/voice-changer/operation/stop_recording`);
    //     await this.restClient.postRequest<null>(path, null);
    // };

    // startServerDevice = async () => {
    //     const path = this.generatePath(`/api/voice-changer/operation/start_server_device`);
    //     await this.restClient.postRequest<null>(path, null);
    // };

    // stopServerDevice = async () => {
    //     const path = this.generatePath(`/api/voice-changer/operation/stop_server_device`);
    //     await this.restClient.postRequest<null>(path, null);
    // };

    // getVoiceChangerManagerInfo = async () => {
    //     const path = this.generatePath(`/api/voice-changer-manager/information`);
    //     const info = await this.restClient.getRequest<VoiceChangerManagerInfo>(path);
    //     return info;
    // };
}
