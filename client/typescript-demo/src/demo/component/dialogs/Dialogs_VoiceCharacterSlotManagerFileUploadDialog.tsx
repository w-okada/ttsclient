import React, { useMemo, useState } from "react";
import {
    closeButton,
    closeButtonRow,
    dialogFixedSizeContent,
    dialogFrame,
    dialogTitle,
    fileInputArea,
    fileInputAreaButton,
    fileInputAreaLabel,
    fileInputAreaValue,
    instructions,
    selectInputArea,
    selectInputAreaInput,
    selectInputAreaLabel,
    textInputArea,
    textInputAreaInput,
    textInputAreaLabel,
    uploadStatusArea,
} from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";
import { checkExtention } from "../../../util/checkExctension";
import { Logger } from "../../../util/logger";
import { VoiceCharacterUploadFile, VoiceCharacterUploadFileKind } from "../../../const";
import { fileSelector, TTSType, TTSTypes } from "tts-client-typescript-client-lib";
type CloseButtonRowProps = {
    uploadClicked: () => void;
    backClicked: () => void;
    isUploading: boolean;
};

const CloseButtonRow = (props: CloseButtonRowProps) => {
    const { t } = useTranslation();
    return (
        <div className={closeButtonRow}>
            <div
                className={closeButton}
                onClick={() => {
                    if (props.isUploading) {
                        return;
                    }
                    props.uploadClicked();
                }}
            >
                {props.isUploading ? t("dialog_uploading") : t("dialog_upload")}
            </div>
            <div
                className={closeButton}
                onClick={() => {
                    props.backClicked();
                }}
            >
                {t("dialog_back")}
            </div>
        </div>
    );
};

type VoiceCharacterSlotManagerFileUploadDialogProps = {
    slotIndex: number | null;
};

type VoiceCharacterFileChooserProps = {
    setUploadFile: (file: VoiceCharacterUploadFile) => void;
    uploadFiles: VoiceCharacterUploadFile[];
};
const VoiceCharacterFileChooser = (props: VoiceCharacterFileChooserProps) => {
    const { t } = useTranslation();
    const { triggerToast } = useAppRoot();
    const [isZipFileSelecting, setIsZipFileSelecting] = useState<boolean>(false);

    const zipFile = useMemo(() => {
        const zipFile = props.uploadFiles.find((x) => x.kind === "zipFile" ) || null;
        return (
            <div className={fileInputArea}>
                <div className={fileInputAreaLabel}>zip: </div>
                <div className={fileInputAreaValue}>
                    {isZipFileSelecting ? t("voice_character_slot_manager_fileupload_file_selecting") : zipFile?.file.name || ""}
                </div>
                <div
                    className={fileInputAreaButton}
                    onClick={async () => {
                        setIsZipFileSelecting(true);
                        await selectFile("zipFile");
                        setIsZipFileSelecting(false);
                    }}
                >
                    {t("voice_character_slot_manager_fileupload_file_select")}
                </div>
            </div>
        );
    }, [props.uploadFiles, props.setUploadFile, isZipFileSelecting]);


    const selectFile = async (kind: VoiceCharacterUploadFileKind) => {
        let file: File | null = null;
        try {
            file = await fileSelector("");
        } catch (e) {
            console.log(e);
        }
        if (file == null) {
            return;
        }

        if (kind == "zipFile") {
            if (checkExtention(file.name, ["zip"]) == false) {
                triggerToast("error", t("voice_character_slot_manager_fileupload_name_input_error"));
                return;
            }
            props.setUploadFile({ kind: kind, file: file });
        }
    };
    return (
        <>
            {zipFile}
        </>
    );
};


export const VoiceCharacterSlotManagerFileUploadDialog = (props: VoiceCharacterSlotManagerFileUploadDialogProps) => {
    const { t } = useTranslation();
    const { serverConfigState, triggerToast } = useAppRoot();
    const { setDialogName } = useGuiState();

    const [tTSType, setTTSType] = useState<TTSType>("GPT-SoVITS");
    const [uploadFiles, setUploadFiles] = useState<VoiceCharacterUploadFile[]>([]);

    const [uploadProgress, setUploadProgress] = useState<number>(0);

    const voiceChangerTypeSelector = useMemo(() => {

        return (
            <select
                defaultValue={tTSType}
                onChange={(event) => {
                    setTTSType(event.target.value as TTSType);
                }}
            >
                {TTSTypes.map((x) => {
                    return (
                        <option key={x} value={x}>
                            {x}
                        </option>
                    );
                })}
            </select>
        );
    }, [tTSType]);

    const setUploadFile = (file: VoiceCharacterUploadFile) => {
        const newUploadFiles = uploadFiles.filter((x) => {
            return x.kind != file.kind;
        });
        newUploadFiles.push(file);
        setUploadFiles(newUploadFiles);
    };
    const clearUploadFiles = () => {
        setUploadFiles([]);
    };
    const uploadClicked = async () => {
        const nameInput = document.getElementById("voice-character-slot-manager-fileUpload-dialog-name-input-text")! as HTMLInputElement;
        const name = nameInput.value
        if(name == ""){
            triggerToast("error", t("voice_character_slot_manager_fileupload_name_input_error"));
            return
        }
        if (tTSType == "GPT-SoVITS") {

            setUploadProgress(0);
            const zipFile = uploadFiles.find((x) => x.kind === "zipFile");
            try {
                const files: VoiceCharacterUploadFile[] = [];
                if(zipFile){
                    files.push(zipFile);
                }
                await serverConfigState.uploadVoiceCharacterFile(props.slotIndex, tTSType, name, files, (progress, end) => {
                    Logger.getLogger().info("progress", progress, end);
                    setUploadProgress(Math.floor(progress - 1));
                });
            } catch (e) {
                triggerToast("error", `upload failed: ${e.detail || ""}`);
                Logger.getLogger().error(`upload failed: ${e.detail || ""}`);
            }
            setDialogName("voiceCharacterManagerMainDialog");
            setUploadProgress(100);
            setUploadProgress(0);
        }
    };
    const backClicked = () => {
        clearUploadFiles();
        setDialogName("voiceCharacterManagerMainDialog");
    };

    let fileChooserArea = <></>;
    if (tTSType == "GPT-SoVITS") {
        fileChooserArea = <VoiceCharacterFileChooser setUploadFile={setUploadFile} uploadFiles={uploadFiles}></VoiceCharacterFileChooser>;
    }

    return (
        <div className={dialogFrame}>
            <div className={dialogTitle}>{t("voice_character_slot_manager_fileupload_title")}</div>
            <div className={instructions}>{t("voice_character_slot_manager_fileupload_instruction")}</div>
            <div className={dialogFixedSizeContent}>
                <div className={selectInputArea}>
                    <div className={selectInputAreaLabel}>TTS Type: </div>
                    <div className={selectInputAreaInput}>{voiceChangerTypeSelector}</div>
                </div>
                <div className={textInputArea}>
                    <div className={textInputAreaLabel}>{t("voice_character_slot_manager_fileupload_name_input_label")}:</div>
                    <div className={textInputAreaInput}>
                        <input id="voice-character-slot-manager-fileUpload-dialog-name-input-text" type="text"></input>
                    </div>
                </div>
                {fileChooserArea}
                <div className={uploadStatusArea}>{uploadProgress > 0 ? uploadProgress + "%" : " "}</div>
            </div>

            <CloseButtonRow uploadClicked={uploadClicked} backClicked={backClicked} isUploading={uploadProgress > 0}></CloseButtonRow>
        </div>
    );
};
