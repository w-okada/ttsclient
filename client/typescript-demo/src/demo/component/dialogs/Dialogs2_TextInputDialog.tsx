import React, { useMemo } from "react";
import {
    closeButton,
    closeButtonRow,
    dialogFrame,
    dialogTitle,
    instructions,
    textInputArea,
    textInputAreaInput,
    textInputAreaLabel,
} from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";

type ButtonsRowProps = {
    resolve: (value: string | null | PromiseLike<string | null>) => void;
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
                    props.resolve(textInput.value);
                    setDialog2Name("none");
                    setDialog2Props(null);
                }}
            >
                {t("dialog_ok")}
            </div>
            <div
                className={closeButton}
                onClick={() => {
                    props.resolve(null);
                    setDialog2Name("none");
                    setDialog2Props(null);
                }}
            >
                {t("dialog_close")}
            </div>
        </div>
    );
};

export const TextInputDialog = () => {
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

                <div className={textInputArea}>
                    <div className={textInputAreaLabel}>input: </div>
                    <div className={textInputAreaInput}>
                        <input id="text-input-dialog-text" type="text" defaultValue={dialog2Props.defaultValue}></input>
                    </div>
                </div>
                <ButtonsRow resolve={dialog2Props.resolve}></ButtonsRow>
            </div>
        );
    }, [serverConfigState.serverSlotInfos]);

    return screen;
};
