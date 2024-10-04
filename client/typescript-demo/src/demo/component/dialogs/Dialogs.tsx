import React, { useEffect, useMemo, useState } from "react";
import { useGuiState } from "../../GuiStateProvider";
import { ModelSlotManagerMainDialog } from "./Dialogs_ModelSlotManagerMainDialog";
import { dialogContainer, dialogContainerShow } from "../../../styles/dialog.css";
import { ModelSlotManagerFileUploadDialog } from "./Dialogs_ModelSlotManagerFileUploadDialog";
import { StartingNoticeDialog } from "./Dialogs_StartingNoticeDialog";
import { VoiceCharacterSlotManagerMainDialog } from "./Dialogs_VoiceCharacterSlotManagerMainDialog";
import { VoiceCharacterSlotManagerFileUploadDialog } from "./Dialogs_VoiceCharacterSlotManagerFileUploadDialog";
import { AboutVoiceDialog } from "./Dialogs_AboutVoiceDialog";
import { AboutModelDialog } from "./Dialogs_AboutModelDialog";

export const Dialogs = () => {
    const guiState = useGuiState();
    const [targetSlotIndex, setTargetSlotIndex] = useState<number>(0);
    const openFileUploadDialog = (targetSlotIndex: number) => {
        setTargetSlotIndex(targetSlotIndex);
        guiState.setDialogName("modelSlotManagerFileUploaderDialog");
    };
    const openSampleDialog = (targetSlotIndex: number) => {
        setTargetSlotIndex(targetSlotIndex);
        guiState.setDialogName("modelSlotManagerSamplesDialog");
    };
    const openVoiceCharacterFileUploadDialog = (targetSlotIndex: number) => {
        setTargetSlotIndex(targetSlotIndex);
        guiState.setDialogName("voiceCharacterManagerFileUploaderDialog");
    }

    const currentDialog = useMemo(() => {
        if (guiState.dialogName === "none") {
            return <></>;
        } else if (guiState.dialogName === "startingNoticeDialog") {
            return <StartingNoticeDialog></StartingNoticeDialog>;
        } else if (guiState.dialogName === "modelSlotManagerMainDialog") {
            return <ModelSlotManagerMainDialog openFileUploadDialog={openFileUploadDialog} openSampleDialog={openSampleDialog}></ModelSlotManagerMainDialog>;
        } else if (guiState.dialogName === "modelSlotManagerFileUploaderDialog") {
            return <ModelSlotManagerFileUploadDialog slotIndex={targetSlotIndex}></ModelSlotManagerFileUploadDialog>;
        } else if (guiState.dialogName === "voiceCharacterManagerMainDialog") {
            return <VoiceCharacterSlotManagerMainDialog openFileUploadDialog={openVoiceCharacterFileUploadDialog}></VoiceCharacterSlotManagerMainDialog>;
        } else if (guiState.dialogName === "voiceCharacterManagerFileUploaderDialog") {
            return <VoiceCharacterSlotManagerFileUploadDialog slotIndex={targetSlotIndex}></VoiceCharacterSlotManagerFileUploadDialog>;

            // } else if (guiState.dialogName === "advancedSettingDialog") {
            //     return <AdvancedSettingDialog></AdvancedSettingDialog>;
        } else if (guiState.dialogName === "aboutModelDialog") {
            return <AboutModelDialog></AboutModelDialog>;
        } else if (guiState.dialogName === "aboutVoiceDialog") {
            return <AboutVoiceDialog></AboutVoiceDialog>;
        } else {
            return <></>;
        }
    }, [guiState.dialogName]);

    const dialog = (
        <div id="dialog-container" className={dialogContainer}>
            {currentDialog}
        </div>
    );

    useEffect(() => {
        const container = document.getElementById("dialog-container");
        if (!container) {
            return;
        }
        if (guiState.dialogName === "none") {
            container.classList.remove(`${dialogContainerShow}`);
        } else {
            container.classList.add(`${dialogContainerShow}`);
        }
    }, [guiState.dialogName]);

    return dialog;
};
