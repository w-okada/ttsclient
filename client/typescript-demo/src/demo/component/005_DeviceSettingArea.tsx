import { useMemo } from "react";
import React from "react";
import { useTranslation } from "react-i18next";
import { useAppRoot } from "../../001_AppRootProvider";
import { BrowserAudioDeviceAreaDeviceSelect } from "./005-1_BrowserAudioDeviceAreaDeviceSelect";
import { SectionHeader } from "../../styles/style-components/labels/02_section-header.css";
import { InferenceAreaBackend } from "./005-2_InferenceAreaBackend";

export const DeviceSettingArea = () => {
    const { t } = useTranslation();
    const { serverConfigState } = useAppRoot();

    const area = useMemo(() => {
        if (!serverConfigState.serverConfiguration) {
            return <></>;
        }
        return (
            <div style={{
                display: "flex", flexDirection: "column", padding: "20px", borderTop: "solid 1px #000000", gap: "15px"
            }}>
                <div className={SectionHeader()}>
                    {t("configuration_area_title")}
                </div >
                <div style={{ display: "flex", flexDirection: "row", gap: "2rem" }}>
                    <div style={{ width: "40%" }} >
                        {/* <BrowserAudioDeviceAreaDeviceSelect type={"Input"}></BrowserAudioDeviceAreaDeviceSelect> */}
                        <BrowserAudioDeviceAreaDeviceSelect type={"Output"}></BrowserAudioDeviceAreaDeviceSelect>
                        <BrowserAudioDeviceAreaDeviceSelect type={"Monitor"}></BrowserAudioDeviceAreaDeviceSelect>
                    </div>
                    <div style={{ width: "40%" }}>
                        <InferenceAreaBackend></InferenceAreaBackend>
                    </div>
                </div>
            </div >
        );

    }, [serverConfigState.serverConfiguration]);
    return area;
};
