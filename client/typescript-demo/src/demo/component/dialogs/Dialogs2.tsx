import React, { useEffect, useMemo } from "react";
import { useGuiState } from "../../GuiStateProvider";
import { dialog2ContainerShow, dialogContainer } from "../../../styles/dialog.css";
import { TextInputDialog } from "./Dialogs2_TextInputDialog";
import { ConfirmDialog } from "./Dialogs2_ConfirmDialog";
import { WaitDialog } from "./Dialogs2_WaitDialog";
import { SelectInputDialog } from "./Dialogs2_SelectInputDialog";

export const Dialogs2 = () => {
    const guiState = useGuiState();

    const currentDialog = useMemo(() => {
        if (guiState.dialog2Name === "none") {
            return <></>;
        } else if (guiState.dialog2Name === "textInputDialog") {
            return <TextInputDialog></TextInputDialog>;
        } else if (guiState.dialog2Name === "confirmDialog") {
            return <ConfirmDialog></ConfirmDialog>;
        } else if (guiState.dialog2Name === "waitDialog") {
            return <WaitDialog></WaitDialog>;
        } else if (guiState.dialog2Name === "selectInputDialog") {
            return <SelectInputDialog></SelectInputDialog>;
        } else {
            <>unknown dialog {guiState.dialog2Name}</>;
        }
    }, [guiState.dialog2Name]);

    const dialog = (
        <div id="dialog2-container" className={dialogContainer}>
            {currentDialog}
        </div>
    );

    useEffect(() => {
        const container = document.getElementById("dialog2-container");
        if (!container) {
            return;
        }
        if (guiState.dialog2Name === "none") {
            container.classList.remove(`${dialog2ContainerShow}`);
        } else {
            container.classList.add(`${dialog2ContainerShow}`);
        }
    }, [guiState.dialog2Name]);

    return dialog;
};
