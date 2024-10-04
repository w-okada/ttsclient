import React, { useMemo } from "react";
import { closeButton, closeButtonRow, dialogFrame, dialogTitle, instructions } from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";

export const WaitDialog = () => {
    const { serverConfigState, triggerToast } = useAppRoot();
    const { dialog2Props } = useGuiState();

    if (dialog2Props == null) {
        triggerToast("error", "dialog2Props is null");
        return;
    }

    const screen = useMemo(() => {
        return (
            <div className={dialogFrame}>
                <div className={dialogTitle}>{dialog2Props.title}</div>
                <div className={instructions}>{dialog2Props.instruction}</div>
            </div>
        );
    }, [serverConfigState.serverSlotInfos]);

    return screen;
};
