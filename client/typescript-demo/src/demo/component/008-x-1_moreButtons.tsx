import { useMemo } from "react";
import React from "react";
import {
    configSubAreaButtonContainer,
    configSubAreaButtonContainerButton,
    configSubAreaRow,
    configSubAreaRowTitle7,
    configSubAreaRowField30,
} from "../../styles/configArea.css";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { left1Padding } from "../../styles/base.css";
import { AudioDeviceType } from "../../const";
import { isDesktopApp } from "../../util/isDesctopApp";
import { useGuiState } from "../GuiStateProvider";
import { Logger } from "../../util/logger";
import { BasicButton } from "../../styles/style-components/buttons/01_basic-button.css";
import { normalButtonThema } from "../../styles/style-components/buttons/thema/button-thema.css";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";

export const MoreActionsButtons = () => {
    const { serverConfigState, audioConfigState } = useAppRoot();
    const { t } = useTranslation();
    const { setDialogName } = useGuiState();

    const component = useMemo(() => {
        const onOpenAdvacnedSettingClicked = async () => {
            setDialogName("advancedSettingDialog");
        };
        const onOpenLogViewerClicked = async () => {
            if (isDesktopApp()) {
                const url = new URL(window.location.href);
                const baseUrl = `${url.protocol}//${url.hostname}${url.port ? ":" + url.port : ""}`;
                // @ts-ignore
                window.electronAPI.openBrowser(`${baseUrl}/?app_mode=LogViewer`);
            } else {
                // ブラウザを開く
                window.open("/?app_mode=LogViewer", "_blank", "noopener,noreferrer");

                // // @ts-ignore
                // window.electronAPI.openBrowser("https://github.com/w-okada/voice-changer");
            }
        };

        const onDownloadLogClicked = async () => {
            const clientLogs = Logger.getLogger().getLogs();
            const clientogTexts = clientLogs
                .map((log) => {
                    return `${log.timestamp}\t${log.level}\t${log.message.join("\t")}`;
                })
                .reduce((prev, current) => {
                    return `${prev}\n${current}`;
                }, "");

            const serverLogRes = await fetch("/vcclient.log");
            const serverLogTexts = await serverLogRes.text();

            const outputLogs = "===== Server Logs =======\n" + serverLogTexts + "====== Client Logs ======\n" + clientogTexts;

            // Blobオブジェクトを作成
            const blob = new Blob([outputLogs], { type: "application/json" });

            // ダウンロード用のリンクを動的に作成
            const a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "logs.txt";
            document.body.appendChild(a);
            a.click();

            // 一度使用したリンクは削除
            document.body.removeChild(a);
        };

        return (
            <div className={configSubAreaRow}>
                <div className={BasicLabel()}>{t("config_area_more_actions_area_title")}:</div>
                <div className={configSubAreaRowField30}>
                    <div className={configSubAreaButtonContainer}>
                        {/* <div onClick={onOpenAdvacnedSettingClicked} className={configSubAreaButtonContainerButton}>
                            {t("config_area_more_actions_area_advanced_setting")}
                        </div> */}
                        <button onClick={onOpenLogViewerClicked} className={`${BasicButton()} ${normalButtonThema}`}>
                            {t("config_area_more_actions_area_open_log_viewer")}
                        </button>
                        <button onClick={onDownloadLogClicked} className={`${BasicButton({ width: "large" })} ${normalButtonThema}`}>
                            {t("config_area_more_actions_area_download_log")}
                        </button>
                    </div>
                </div>
            </div>
        );
    }, [serverConfigState]);

    return component;
};
