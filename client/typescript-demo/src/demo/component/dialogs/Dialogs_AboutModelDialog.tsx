import React from "react";
import {
    aboutModelModelDescription,
    aboutModelModelDescriptionPre,
    aboutModelModelName,
    closeButton,
    closeButtonRow,
    dialogFixedSizeContent,
    dialogFrame,
    dialogTitle,
    instructions,
} from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";

type CloseButtonRowProps = {};

const CloseButtonRow = (props: CloseButtonRowProps) => {
    const { t } = useTranslation();
    const { setDialogName } = useGuiState();
    return (
        <div className={closeButtonRow}>
            <div
                className={closeButton}
                onClick={() => {
                    setDialogName("none");
                }}
            >
                {t("dialog_close")}
            </div>
        </div>
    );
};

type AboutModelDialogProps = {};

export const AboutModelDialog = (props: AboutModelDialogProps) => {
    const { t } = useTranslation();

    return (
        <div className={dialogFrame}>
            <div className={dialogTitle}>{t("dialog_about_model_title")}VOICE</div>
            <div className={instructions}></div>
            <div className={dialogFixedSizeContent}>
                <div className={aboutModelModelName}>
                    {/* {modelName}({modelVersion}) */}
                </div>
                <div className={aboutModelModelDescription}>
                    <pre className={aboutModelModelDescriptionPre}>
                        {/* {modelDescription} */}
                    </pre>
                </div>
            </div>

            <CloseButtonRow></CloseButtonRow>
        </div>
    );
};
