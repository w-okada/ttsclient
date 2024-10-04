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

type AboutVoiceDialogProps = {};

export const AboutVoiceDialog = (props: AboutVoiceDialogProps) => {
    const { t } = useTranslation();
    // const { slotInfo } = useAppRoot();

    return (
        <div className={dialogFrame}>
            <div className={dialogTitle}>{t("dialog_about_voice_title")}</div>
            <div className={instructions}></div>
            <div className={dialogFixedSizeContent}>
                <div className={aboutModelModelName}>
                    {/* {voice.name}(pitch: {voice.average_pitch}) */}
                </div>
                <div className={aboutModelModelDescription}>
                    <pre className={aboutModelModelDescriptionPre}>
                        {/* {voice.description} */}
                    </pre>
                </div>
            </div>

            <CloseButtonRow></CloseButtonRow>
        </div>
    );
};
