import { useMemo } from "react";
import React from "react";
import { configSubAreaRow, configSubAreaRowField15, configSubAreaRowTitle4 } from "../../styles/configArea.css";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { BasicInput } from "../../styles/style-components/inputs/01_basic-input.css";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";
import { TextLabel } from "../../styles/style-components/labels/00_text-label.css";

import { BackendMode, GPTSoVITSSlotInfo } from "tts-client-typescript-client-lib";

export const InferenceAreaBackend = () => {
    const { serverConfigState, guiSetting, runOnColab } = useAppRoot();
    const { t } = useTranslation();

    const options = useMemo(() => {
        if (!serverConfigState.serverGpuInfo) {
            return <></>;
        }
        const options = serverConfigState.serverGpuInfo.map((c) => {
            return (
                <option key={c.device_id_int} value={c.device_id_int}>
                    {c.name}[{c.device_id_int}]
                </option>
            );
        });
        return options;
    }, [serverConfigState.serverGpuInfo]);

    const GPUSecSelect = useMemo(() => {
        if (!serverConfigState.serverConfiguration) {
            return <></>;
        }
        const onGpuChanged = (val: number) => {
            if (!serverConfigState.serverConfiguration) {
                return <></>;
            }
            serverConfigState.serverConfiguration.gpu_device_id_int = val;
            serverConfigState.updateServerConfiguration(serverConfigState.serverConfiguration);
        };
        return (
            <select
                defaultValue={serverConfigState.serverConfiguration.gpu_device_id_int}
                onChange={(e) => {
                    onGpuChanged(Number(e.target.value));
                }}
                className={BasicInput()}
            >
                {options}
            </select>
        );
    }, [options, serverConfigState.serverConfiguration]);


    const BackendModeOption = useMemo(() => {
        return BackendMode.map((c) => {
            return (
                <option key={c} value={c}>
                    {c}
                </option>
            )
        })
    }, [])

    const BackendModeSelect = useMemo(() => {
        if (!serverConfigState.serverConfiguration) {
            return <></>;
        }
        const currentSlotId = serverConfigState.serverConfiguration?.current_slot_index

        if (!serverConfigState.serverSlotInfos) {
            return <></>
        }
        const currentSlot = serverConfigState.serverSlotInfos.find(x => { return x.slot_index == currentSlotId })
        if (!currentSlot) {
            console.warn("currentSlot is not found", currentSlotId)
            return <></>
        }

        if (currentSlot.tts_type != "GPT-SoVITS") {
            console.warn("currentSlot is not GPT-SoVITS", currentSlotId)
            return <></>
        }

        const gptSovitsSlot = currentSlot as GPTSoVITSSlotInfo
        if (gptSovitsSlot.onnx_encoder_path == null) {
            return <div className={TextLabel({ width: "x-large" })}>not onnx generated</div>
        }


        const selectedValue = gptSovitsSlot.backend_mode

        return (
            <select
                defaultValue={selectedValue}
                onChange={(e) => {
                    gptSovitsSlot.backend_mode = e.target.value as BackendMode
                    serverConfigState.updateServerSlotInfo(gptSovitsSlot)
                }}
                className={BasicInput()}
            >
                {BackendModeOption}
            </select>
        )
    }, [serverConfigState.serverConfiguration, serverConfigState.serverSlotInfos]);




    const component = useMemo(() => {
        // DirectMLは次のようなエラーが出るので使えなさそう。
        // DirectML scatter doesn't allow partially modified dimensions. Please update the dimension so that the indices and input only differ in the provided dimension.

        if (["cuda", "colab", "dml", ""].includes(guiSetting.edition || "") == false) {
            return <></>
        }

        return (
            <>
                <div className={configSubAreaRow}>
                    <div className={BasicLabel()}>{t("config_area_gpu")}:</div>
                    <div className={configSubAreaRowField15}>{GPUSecSelect}</div>
                </div>
                <div className={configSubAreaRow}>
                    <div className={BasicLabel()}>{t("config_area_backend")}:</div>
                    <div className={configSubAreaRowTitle4}>{BackendModeSelect}</div>
                </div>
            </>
        );
    }, [GPUSecSelect]);

    return component;
};
