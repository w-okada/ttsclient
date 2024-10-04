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
                    const selectInput = document.getElementById("select-input-dialog-select") as HTMLSelectElement;
                    props.resolve(selectInput.value);
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

export const SelectInputDialog = () => {
    const { serverConfigState, triggerToast } = useAppRoot();
    const { dialog2Props } = useGuiState();
    const { t } = useTranslation();
    if (dialog2Props == null) {
        triggerToast("error", "dialog2Props is null");
        return;
    }
    if (dialog2Props.options == null) {
        triggerToast("error", "dialog2Props options is null");
        return;
    }
    const screen = useMemo(() => {
        return (
            <div className={dialogFrame}>
                <div className={dialogTitle}>{dialog2Props.title}</div>
                <div className={instructions}>{dialog2Props.instruction}</div>

                <div className={textInputArea}>
                    <div className={textInputAreaLabel}>{t("model_slot_move_confirm_dialog_item_name")}:</div>
                    <div className={textInputAreaInput}>
                        <select id="select-input-dialog-select">
                            {dialog2Props.options?.map((option) => {
                                return <option value={option.value}>{option.label}</option>;
                            })}
                        </select>
                    </div>
                </div>
                <ButtonsRow resolve={dialog2Props.resolve}></ButtonsRow>
            </div>
        );
    }, [serverConfigState.serverSlotInfos]);

    return screen;
};
