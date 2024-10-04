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
    uploadStatusArea,
} from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";
import { checkExtention } from "../../../util/checkExctension";
import { Logger } from "../../../util/logger";
import { UploadFile, UploadFileKind } from "../../../const";
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

type ModelSlotManagerFileUploadDialogProps = {
    slotIndex: number | null;
};

type GPTSoVITSFileChooserProps = {
    setUploadFile: (file: UploadFile) => void;
    uploadFiles: UploadFile[];
};
const GPTSoVITSFileChooser = (props: GPTSoVITSFileChooserProps) => {
    const { t } = useTranslation();
    const { triggerToast } = useAppRoot();
    const [isModelFileSelecting, setIsModelFileSelecting] = useState<boolean>(false);
    const [isIndexFileSelecting, setIsIndexFileSelecting] = useState<boolean>(false);

    const semanticPredictorModelFile = useMemo(() => {
        const semanticPredictorModelFile = props.uploadFiles.find((x) => x.kind === "semanticPredictorModelFile") || null;
        return (
            <div className={fileInputArea}>
                <div className={fileInputAreaLabel}>semantic: </div>
                <div className={fileInputAreaValue}>
                    {isModelFileSelecting ? t("model_slot_manager_fileupload_file_selecting") : semanticPredictorModelFile?.file.name || ""}
                </div>
                <div
                    className={fileInputAreaButton}
                    onClick={async () => {
                        setIsModelFileSelecting(true);
                        await selectFile("semanticPredictorModelFile");
                        setIsModelFileSelecting(false);
                    }}
                >
                    {t("model_slot_manager_fileupload_file_select")}
                </div>
            </div>
        );
    }, [props.uploadFiles, props.setUploadFile, isModelFileSelecting]);

    const synthesizerModelFile = useMemo(() => {
        const synthesizerModelFile = props.uploadFiles.find((x) => x.kind === "synthesizerModelFile") || null;
        return (
            <div className={fileInputArea}>
                <div className={fileInputAreaLabel}>synthesize: </div>
                <div className={fileInputAreaValue}>
                    {isIndexFileSelecting ? t("model_slot_manager_fileupload_file_selecting") : synthesizerModelFile?.file.name || ""}
                </div>
                <div
                    className={fileInputAreaButton}
                    onClick={async () => {
                        setIsIndexFileSelecting(true);
                        await selectFile("synthesizerModelFile");
                        setIsIndexFileSelecting(false);
                    }}
                >
                    {t("model_slot_manager_fileupload_file_select")}
                </div>
            </div>
        );
    }, [props.uploadFiles, props.setUploadFile, isIndexFileSelecting]);

    const selectFile = async (kind: UploadFileKind) => {
        let file: File | null = null;
        try {
            file = await fileSelector("");
        } catch (e) {
            console.log(e);
        }
        if (file == null) {
            return;
        }

        if (kind == "semanticPredictorModelFile") {
            if (checkExtention(file.name, ["ckpt"]) == false) {
                triggerToast("error", t("model_slot_manager_fileupload_file_select_rvc_model_error"));
                return;
            }
            props.setUploadFile({ kind: kind, file: file });
        } else if (kind == "synthesizerModelFile") {
            if (checkExtention(file.name, ["pth"]) == false) {
                triggerToast("error", t("model_slot_manager_fileupload_file_select_rvc_index_error"));
                return;
            }
            props.setUploadFile({ kind: kind, file: file });
        }
    };
    return (
        <>
            {semanticPredictorModelFile}
            {synthesizerModelFile}
        </>
    );
};


export const ModelSlotManagerFileUploadDialog = (props: ModelSlotManagerFileUploadDialogProps) => {
    const { t } = useTranslation();
    const { serverConfigState, triggerToast } = useAppRoot();
    const { setDialogName } = useGuiState();

    const [tTSType, setTTSType] = useState<TTSType>("GPT-SoVITS");
    const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([]);

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

    const setUploadFile = (file: UploadFile) => {
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
        if (tTSType == "GPT-SoVITS") {
            setUploadProgress(0);
            const semanticPredictorModelFile = uploadFiles.find((x) => x.kind === "semanticPredictorModelFile");
            const synthesizerModelFile = uploadFiles.find((x) => x.kind === "synthesizerModelFile");
            try {
                const files: UploadFile[] = [];
                if(semanticPredictorModelFile){
                    files.push(semanticPredictorModelFile);
                }
                if (synthesizerModelFile) {
                    files.push(synthesizerModelFile);
                }
                await serverConfigState.uploadModelFile(props.slotIndex, tTSType, files, (progress, end) => {
                    Logger.getLogger().info("progress", progress, end);
                    setUploadProgress(Math.floor(progress - 1));
                });
            } catch (e) {
                triggerToast("error", `upload failed: ${e.detail || ""}`);
                Logger.getLogger().error(`upload failed: ${e.detail || ""}`);
            }
            setDialogName("modelSlotManagerMainDialog");
            setUploadProgress(100);
            setUploadProgress(0);
        }
    };
    const backClicked = () => {
        clearUploadFiles();
        setDialogName("modelSlotManagerMainDialog");
    };

    let fileChooserArea = <></>;
    if (tTSType == "GPT-SoVITS") {
        fileChooserArea = <GPTSoVITSFileChooser setUploadFile={setUploadFile} uploadFiles={uploadFiles}></GPTSoVITSFileChooser>;
    }

    return (
        <div className={dialogFrame}>
            <div className={dialogTitle}>{t("model_slot_manager_fileupload_title")}</div>
            <div className={instructions}>{t("model_slot_manager_fileupload_instruction")}</div>
            <div className={dialogFixedSizeContent}>
                <div className={selectInputArea}>
                    <div className={selectInputAreaLabel}>TTS Type: </div>
                    <div className={selectInputAreaInput}>{voiceChangerTypeSelector}</div>
                </div>
                {fileChooserArea}
                <div className={uploadStatusArea}>{uploadProgress > 0 ? uploadProgress + "%" : " "}</div>
            </div>

            <CloseButtonRow uploadClicked={uploadClicked} backClicked={backClicked} isUploading={uploadProgress > 0}></CloseButtonRow>
        </div>
    );
};
