import React, { useMemo } from "react";
import { closeButton, closeButtonRow, dialogFrame, dialogTitle, instructions } from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";

type ButtonsRowProps = {
    resolve: (value: boolean | null | PromiseLike<boolean | null>) => void;
};
const ButtonsRow = (props: ButtonsRowProps) => {
    const { t } = useTranslation();
    const { setDialog2Name, setDialog2Props } = useGuiState();
    return (
        <div className={closeButtonRow}>
            <div
                className={closeButton}
                onClick={() => {
                    const textInput = document.getElementById("text-input-dialog-text") as HTMLInputElement;
                    props.resolve(true);
                    setDialog2Name("none");
                    setDialog2Props(null);
                }}
            >
                {t("dialog_ok")}
            </div>
            <div
                className={closeButton}
                onClick={() => {
                    props.resolve(false);
                    setDialog2Name("none");
                    setDialog2Props(null);
                }}
            >
                {t("dialog_close")}
            </div>
        </div>
    );
};

export const ConfirmDialog = () => {
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

                <ButtonsRow resolve={dialog2Props.resolve}></ButtonsRow>
            </div>
        );
    }, [serverConfigState.serverSlotInfos]);

    return screen;
};
