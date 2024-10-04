import React, { useMemo } from "react";
import { useTranslation } from "react-i18next";
import { isDesktopApp } from "../../util/isDesctopApp";
import {
    button,
    headerArea,
    iconArea,
    iconGroup,
    title,
    titleArea,
    titleVersion,
    tooltip,
    tooltipText,
    tooltipText100px,
} from "../../styles/header.css";
import { useAppRoot } from "../../001_AppRootProvider";
import { useGuiState } from "../GuiStateProvider";
import { useAppState } from "../../002_AppStateProvider";
import { Logger } from "../../util/logger";
import { HeaderIcon } from "../../styles/style-components/icons/01_header-icon.css";
import { BasicButton } from "../../styles/style-components/buttons/01_basic-button.css";
import { BasicInput } from "../../styles/style-components/inputs/01_basic-input.css";
import { headerButtonThema } from "../../styles/style-components/buttons/thema/button-thema.css";

export type HeaderAreaProps = {};

export const HeaderArea = (props: HeaderAreaProps) => {
    const { t, i18n } = useTranslation();
    const { guiSetting, serverConfigState, generateGetPathFunc } = useAppRoot();
    const { setDialog2Name, setDialog2Props } = useGuiState();
    const { displayColorMode, setDisplayColorMode } = useAppState();

    const githubLink = useMemo(() => {
        const iconUrl = generateGetPathFunc("/assets/icons/github.svg");
        return isDesktopApp() ? (
            <span
                className={tooltip}
                onClick={() => {
                    // @ts-ignore
                    window.electronAPI.openBrowser("https://github.com/w-okada/ttsclient");
                }}
            >
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={tooltipText}>{t("header_github")}</div>
            </span>
        ) : (
            <a className={tooltip} href="https://github.com/w-okada/ttsclient" target="_blank" rel="noopener noreferrer">
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={tooltipText}>{t("header_github")}</div>
            </a>
        );
    }, [i18n.language]);

    const manualLink = useMemo(() => {
        const iconUrl = generateGetPathFunc("/assets/icons/help-circle.svg");
        return isDesktopApp() ? (
            <span
                className={tooltip}
                onClick={() => {
                    // @ts-ignore
                    window.electronAPI.openBrowser("https://github.com/w-okada/voice-changer/blob/master/tutorials/tutorial_rvc_ja_latest.md");
                }}
            >
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_manual")}</div>
            </span>
        ) : (
            <a
                className={tooltip}
                href="https://github.com/w-okada/voice-changer/blob/master/tutorials/tutorial_rvc_ja_latest.md"
                target="_blank"
                rel="noopener noreferrer"
            >
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_manual")}</div>
            </a>
        );
    }, [i18n.language]);

    const toolLink = useMemo(() => {
        const iconUrl = generateGetPathFunc("/assets/icons/monitor.svg");
        return isDesktopApp() ? (
            <span
                className={tooltip}
                onClick={() => {
                    // @ts-ignore
                    window.electronAPI.openBrowser("https://w-okada.github.io/screen-recorder-ts/");
                }}
            >
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_screen_recorder")}</div>
            </span>
        ) : (
            <a className={tooltip} href="https://w-okada.github.io/screen-recorder-ts/" target="_blank" rel="noopener noreferrer">
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_screen_recorder")}</div>
            </a>
        );
    }, [i18n.language]);

    const coffeeLink = useMemo(() => {
        const iconUrl = generateGetPathFunc("/assets/icons/buymeacoffee.png");
        return isDesktopApp() ? (
            <span
                className={tooltip}
                onClick={() => {
                    // @ts-ignore
                    window.electronAPI.openBrowser("https://www.buymeacoffee.com/wokad");
                }}
            >
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_support")}</div>
            </span>
        ) : (
            <a className={tooltip} href="https://www.buymeacoffee.com/wokad" target="_blank" rel="noopener noreferrer">
                <img src={iconUrl} className={HeaderIcon()} />
                <div className={`${tooltipText} ${tooltipText100px}`}>{t("header_support")}</div>
            </a>
        );
    }, [i18n.language]);

    const langSelector = useMemo(() => {
        if (!guiSetting.setting) {
            return <> </>;
        }
        const languages = guiSetting.setting.lang;
        return (
            <div>
                <span>{t("header_language")}:</span>
                <select
                    defaultValue={i18n.language}
                    onChange={(event) => {
                        Logger.getLogger().info("change lang", event.target.value, i18n.language);
                        i18n.changeLanguage(event.target.value);
                        location.reload();
                    }}
                    className={BasicInput()}
                >
                    {languages.map((lang) => (
                        <option key={lang} value={lang}>
                            {lang}
                        </option>
                    ))}
                </select>
            </div>
        );
    }, [i18n.language, guiSetting.setting?.lang]);

    const initializeButton = useMemo(() => {
        const onClearSettingClicked = async () => {
            let ok = false;
            const p = new Promise<boolean>((resolve) => {
                setDialog2Props({
                    title: t("header_initialize_confirm_dialog_title"),
                    instruction: `${t("header_initialize_confirm_dialog_instruction")}`,
                    defaultValue: "",
                    resolve: resolve,
                    options: null,
                });
                setDialog2Name("confirmDialog");
            });
            const res = await p;
            if (res == true) {
                ok = true;
            } else {
                ok = false;
            }

            if (ok) {
                await serverConfigState.initializeServer();
                // await voiceChangerClientState.clearDb();
                // location.reload();
            }
        };

        return (
            <button className={`${BasicButton()} ${headerButtonThema}`} onClick={onClearSettingClicked}>
                {t("header_initialize")}
            </button>
        );
    }, [i18n.language, displayColorMode]);


    const displayColorModeButton = useMemo(() => {
        return (
            <button className={`${BasicButton()} ${headerButtonThema}`} onClick={() => {
                setDisplayColorMode(displayColorMode == "light" ? "dark" : "light")
            }}>{displayColorMode == "light" ? t("header_to_dark_label") : t("header_to_light_label")}</button>
        );
    }, [displayColorMode]);

    const header = useMemo(() => {
        return (
            <div className={headerArea}>
                <div className={titleArea}>
                    <span className={title}>Text To Speech Client</span>
                    <span></span>
                    <span className={titleVersion}>{guiSetting.version}</span>
                    <span className={titleVersion}>{guiSetting.edition}</span>
                </div>
                <div className={iconArea}>
                    <span className={iconGroup}>
                        {githubLink}
                        {manualLink}
                        {toolLink}
                        {coffeeLink}
                        {/* {licenseButton} */}
                    </span>
                    <span className={iconGroup}>{langSelector}</span>
                    <span className={iconGroup}>
                        {initializeButton}
                        {displayColorModeButton}
                    </span>
                </div>
            </div>
        );
    }, [guiSetting.version, guiSetting.edition, i18n.language, displayColorModeButton]);

    return header;
};
