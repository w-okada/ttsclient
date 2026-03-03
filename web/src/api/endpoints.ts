import { get, post, put, del, postBlob, postBlobWithHeaders, postFormData, connectSSE } from "./client";
import type { BlobResponse } from "./client";
import type {
  TTSConfiguration,
  GPUInfo,
  ModuleStatus,
  ModuleDownloadStatus,
  SlotInfoMember,
  ModelImportParamMember,
  MoveModelParam,
  SetIconParam,
  VoiceCharacter,
  VoiceCharacterImportParam,
  ReferenceVoice,
  ReferenceVoiceImportParam,
  OpenJTalkUserDictRecord,
  GenerateVoiceParam,
  GetPhonesParam,
  GetPhonesResponse,
  GetJpTextToUserDictRecordsParam,
  SampleInfoMember,
  SampleDownloadParam,
  FileuploaderInfo,
  FileuploaderUploadFileChunkResult,
  FileuploaderConcatUploadedFileChunkResult,
} from "@/types";

type MessageResponse = { message: string };

// =============================================================
// Operation
// =============================================================

export const initialize = () => post<MessageResponse>("/api/operation/initialize");

export const downloadModulesSSE = (onProgress: (s: ModuleDownloadStatus[]) => void) =>
  connectSSE<ModuleDownloadStatus[]>("/api/operation/download-modules", onProgress);

export const downloadModelsSSE = (onProgress: (s: ModuleDownloadStatus[]) => void) =>
  connectSSE<ModuleDownloadStatus[]>("/api/operation/download-models", onProgress);

export const setupInitialModels = () => post<MessageResponse>("/api/operation/setup-initial-models");

// =============================================================
// Configuration
// =============================================================

export const getConfiguration = (reload = false) =>
  get<TTSConfiguration>("/api/configuration-manager/configuration", reload ? { reload: "true" } : undefined);

export const putConfiguration = (config: TTSConfiguration) =>
  put<TTSConfiguration>("/api/configuration-manager/configuration", config);

// =============================================================
// GPU Device
// =============================================================

export const getGPUDevices = (reload = false) =>
  get<GPUInfo[]>("/api/gpu-device-manager/devices", reload ? { reload: "true" } : undefined);

// =============================================================
// Module
// =============================================================

export const getModules = (reload = false) =>
  get<ModuleStatus[]>("/api/module-manager/modules", reload ? { reload: "true" } : undefined);

// =============================================================
// Slot (Model)
// =============================================================

export const getSlots = (reload = false) =>
  get<SlotInfoMember[]>("/api/slot-manager/slots", reload ? { reload: "true" } : undefined);

export const getSlot = (index: number, reload = false) =>
  get<SlotInfoMember>(`/api/slot-manager/slots/${index}`, reload ? { reload: "true" } : undefined);

export const postSlot = (param: ModelImportParamMember) => post<MessageResponse>("/api/slot-manager/slots", param);

export const putSlot = (index: number, slot: SlotInfoMember) =>
  put<MessageResponse>(`/api/slot-manager/slots/${index}`, slot);

export const deleteSlot = (index: number) => del<MessageResponse>(`/api/slot-manager/slots/${index}`);

export const moveSlot = (param: MoveModelParam) =>
  post<MessageResponse>("/api/slot-manager/slots/operation/move_model", param);

export const setSlotIcon = (index: number, param: SetIconParam) =>
  post<MessageResponse>(`/api/slot-manager/slots/${index}/operation/set_icon_file`, param);

export const generateOnnx = (index: number) =>
  post<MessageResponse>(`/api/slot-manager/slots/${index}/operation/generate_onnx`);

// =============================================================
// Voice Character
// =============================================================

export const getVoiceCharacters = (reload = false) =>
  get<VoiceCharacter[]>("/api/voice-character-slot-manager/slots", reload ? { reload: "true" } : undefined);

export const getVoiceCharacter = (index: number, reload = false) =>
  get<VoiceCharacter | null>(
    `/api/voice-character-slot-manager/slots/${index}`,
    reload ? { reload: "true" } : undefined,
  );

export const postVoiceCharacter = (param: VoiceCharacterImportParam) =>
  post<MessageResponse>("/api/voice-character-slot-manager/slots", param);

export const putVoiceCharacter = (index: number, vc: VoiceCharacter) =>
  put<MessageResponse>(`/api/voice-character-slot-manager/slots/${index}`, vc);

export const deleteVoiceCharacter = (index: number) =>
  del<MessageResponse>(`/api/voice-character-slot-manager/slots/${index}`);

export const moveVoiceCharacter = (param: MoveModelParam) =>
  post<MessageResponse>("/api/voice-character-slot-manager/slots/operation/move_model", param);

export const setVoiceCharacterIcon = (index: number, param: SetIconParam) =>
  post<MessageResponse>(`/api/voice-character-slot-manager/slots/${index}/operation/set_icon_file`, param);

// =============================================================
// Reference Voice
// =============================================================

export const postReferenceVoice = (vcIndex: number, param: ReferenceVoiceImportParam) =>
  post<MessageResponse>(`/api/voice-character-slot-manager/slots/${vcIndex}/voices`, param);

export const putReferenceVoice = (vcIndex: number, voiceIndex: number, voice: ReferenceVoice) =>
  put<MessageResponse>(`/api/voice-character-slot-manager/slots/${vcIndex}/voices/${voiceIndex}`, voice);

export const deleteReferenceVoice = (vcIndex: number, voiceIndex: number) =>
  del<MessageResponse>(`/api/voice-character-slot-manager/slots/${vcIndex}/voices/${voiceIndex}`);

export const moveReferenceVoice = (vcIndex: number, param: MoveModelParam) =>
  post<MessageResponse>(`/api/voice-character-slot-manager/slots/${vcIndex}/voices/operation/move_voice`, param);

export const zipAndDownloadVoices = (vcIndex: number) =>
  postBlob(`/api/voice-character-slot-manager/slots/${vcIndex}/voices/operation/zip_and_download`);

export const setReferenceVoiceIcon = (vcIndex: number, voiceIndex: number, param: SetIconParam) =>
  post<MessageResponse>(
    `/api/voice-character-slot-manager/slots/${vcIndex}/voices/${voiceIndex}/operation/set_icon_file`,
    param,
  );

export const addUserDictRecord = (vcIndex: number, record: OpenJTalkUserDictRecord) =>
  post<MessageResponse>(
    `/api/voice-character-slot-manager/slots/${vcIndex}/voices/operation/add_user_dict_record`,
    record,
  );

// =============================================================
// TTS
// =============================================================

export const generateVoice = (param: GenerateVoiceParam): Promise<BlobResponse> =>
  postBlobWithHeaders("/api/tts-manager/operation/generateVoice", param);

export const getPhones = (param: GetPhonesParam) =>
  post<GetPhonesResponse>("/api/tts-manager/operation/getPhones", param);

export const getJpTextToUserDictRecords = (param: GetJpTextToUserDictRecordsParam) =>
  post<OpenJTalkUserDictRecord[]>("/api/tts-manager/operation/getJpTextToUserDictRecords", param);

// =============================================================
// Sample
// =============================================================

export const getSamples = (reload = false) =>
  get<SampleInfoMember[]>("/api/sample-manager/samples", reload ? { reload: "true" } : undefined);

export const downloadSample = (param: SampleDownloadParam) =>
  post<MessageResponse>("/api/sample-manager/samples/operation/download", param);

// =============================================================
// File Uploader
// =============================================================

export const getUploaderInfo = () => get<FileuploaderInfo>("/api/uploader/info");

export const uploadFileChunk = (file: Blob, filename: string, index: number) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("filename", filename);
  formData.append("index", index.toString());
  return postFormData<FileuploaderUploadFileChunkResult>("/api/uploader/upload_file_chunk", formData);
};

export const concatUploadedFileChunk = (filename: string, chunkNum: number) => {
  const formData = new FormData();
  formData.append("filename", filename);
  formData.append("filename_chunk_num", chunkNum.toString());
  return postFormData<FileuploaderConcatUploadedFileChunkResult>(
    "/api/uploader/concat_uploaded_file_chunk",
    formData,
  );
};
