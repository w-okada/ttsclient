import React, { useMemo } from "react";
import {
    closeButton,
    closeButtonRow,
    dialogDonateLinkSpan,
    dialogDonateLinkSpanImg,
    dialogFixedSizeContent,
    dialogFrame,
    dialogNotice,
    dialogNoticeLinkArea,
    dialogTitle,
    instructions,
} from "../../../styles/dialog.css";
import { useGuiState } from "../../GuiStateProvider";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../../001_AppRootProvider";
import { isDesktopApp } from "../../../util/isDesctopApp";

type CloseButtonRowProps = {
    closeClicked: () => void;
};

const CloseButtonRow = (props: CloseButtonRowProps) => {
    const { t } = useTranslation();
    return (
        <div className={closeButtonRow}>
            <div
                className={closeButton}
                onClick={() => {
                    props.closeClicked();
                }}
            >
                {t("dialog_advanced_setting_button_close")}
            </div>
        </div>
    );
};

type StartingNoticeDialogProps = {};

export const StartingNoticeDialog = (props: StartingNoticeDialogProps) => {
    const { t } = useTranslation();
    const { generateGetPathFunc } = useAppRoot();
    const { setDialogName } = useGuiState();

    const backClicked = () => {
        setDialogName("none");
    };

    const coffeeLink = useMemo(() => {
        const iconUrl = generateGetPathFunc("/assets/icons/buymeacoffee.png");
        return isDesktopApp() ? (
            // @ts-ignore
            <span
                className={dialogDonateLinkSpan}
                onClick={() => {
                    // @ts-ignore
                    window.electronAPI.openBrowser("https://www.buymeacoffee.com/wokad");
                }}
            >
                <img className={dialogDonateLinkSpanImg} src={iconUrl} /> {t("dialog_starting_notice_coffee_icon_message")}
            </span>
        ) : (
            <a className={dialogDonateLinkSpan} href="https://www.buymeacoffee.com/wokad" target="_blank" rel="noopener noreferrer">
                <img className={dialogDonateLinkSpanImg} src={iconUrl} /> {t("dialog_starting_notice_coffee_icon_message")}
            </a>
        );
    }, []);

    const component = useMemo(() => {
        return (
            <div className={dialogFrame}>
                <div className={dialogTitle}>{t("dialog_starting_notice_title")}</div>
                <div className={instructions}>{t("dialog_starting_notice_instruction")}</div>
                <div className={dialogFixedSizeContent}>
                    <div className={dialogNotice}>{t("dialog_starting_notice_notice1")}</div>
                    <div className={dialogNoticeLinkArea}>{coffeeLink}</div>
                </div>

                <CloseButtonRow closeClicked={backClicked}></CloseButtonRow>
            </div>
        );
    }, []);
    return component;
};
