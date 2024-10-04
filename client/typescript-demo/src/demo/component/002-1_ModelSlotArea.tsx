import React, { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { FaSortAlphaDown, FaSortNumericDown } from "react-icons/fa";
import {
    button,
    buttonActive,
    buttonGroup,
    buttons,
    modelSlotArea,
    modelSlotPane,
    modelSlotTileContainer,
    modelSlotTileContainerSelected,
    modelSlotTileDscription,
    modelSlotTileIcon,
    modelSlotTileIconDiv,
    modelSlotTileIconNoEntry,
    modelSlotTileVctype,
    modelSlotTilesContainer,
    modelSlotTitle,
} from "../../styles/modelSlot.css";
import { useAppRoot } from "../../001_AppRootProvider";
import { DialogName, useGuiState } from "../GuiStateProvider";
import { BasicButton } from "../../styles/style-components/buttons/01_basic-button.css";
import { modelSlotButtonThema } from "../../styles/style-components/buttons/thema/button-thema.css";
export type ModelSlotAreaProps = {};

const SortTypes = {
    slot: "slot",
    name: "name",
} as const;
export type SortTypes = (typeof SortTypes)[keyof typeof SortTypes];

export const ModelSlotArea = (_props: ModelSlotAreaProps) => {
    const { serverConfigState, generateGetPathFunc } = useAppRoot();
    const guiState = useGuiState();
    const { t } = useTranslation();
    const [sortType, setSortType] = useState<SortTypes>("slot");

    const modelTiles = useMemo(() => {
        if (!serverConfigState.serverSlotInfos) {
            return <></>;
        }
        const modelSlots =
            sortType == "slot"
                ? serverConfigState.serverSlotInfos
                : serverConfigState.serverSlotInfos.slice().sort((a, b) => {
                    return a.name.localeCompare(b.name);
                });

        return modelSlots
            .map((x, index) => {
                if (x.tts_type == null) {
                    return null;
                }
                const tileContainerClass =
                    x.slot_index == serverConfigState.serverConfiguration?.current_slot_index
                        ? `${modelSlotTileContainer} ${modelSlotTileContainerSelected}`
                        : modelSlotTileContainer;
                const name = x.name.length > 8 ? x.name.substring(0, 7) + "..." : x.name;

                // const modelDir = x.slotIndex == "Beatrice-JVS" ? "model_dir_static" : serverSetting.serverSetting.voiceChangerParams.model_dir;
                // const icon = x.icon_file != null ? x.icon_file : "./assets/icons/human.png";
                let icon = x.icon_file != null ? "models" + "/" + x.slot_index + "/" + x.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";
                icon = generateGetPathFunc(icon)
                console.log("icon url", icon);

                const iconElem =
                    x.icon_file != null ? (
                        <>
                            <img className={modelSlotTileIcon} src={icon} alt={x.name} />
                            <div className={modelSlotTileVctype}>{x.tts_type}</div>
                        </>
                    ) : (
                        <>
                            <div className={modelSlotTileIconNoEntry}>no image</div>
                            <div className={modelSlotTileVctype}>{x.tts_type}</div>
                        </>
                    );

                const clickAction = async () => {
                    // @ts-ignore
                    if (serverConfigState.serverConfiguration == null) {
                        return;
                    }
                    serverConfigState.serverConfiguration.current_slot_index = x.slot_index;
                    serverConfigState.updateServerConfiguration(serverConfigState.serverConfiguration);
                    // const dummyModelSlotIndex = Math.floor(Date.now() / 1000) * 1000 + x.slotIndex;
                    // await serverSetting.updateServerSettings({ ...serverSetting.serverSetting, modelSlotIndex: dummyModelSlotIndex });
                    // setTimeout(() => {
                    //     // quick hack
                    //     getInfo();
                    // }, 1000 * 2);
                };

                return (
                    <div key={index} className={tileContainerClass} onClick={clickAction}>
                        <div className={modelSlotTileIconDiv}>{iconElem}</div>
                        <div className={modelSlotTileDscription}>{name}</div>
                    </div>
                );
            })
            .filter((x) => x != null);
    }, [serverConfigState.serverSlotInfos, serverConfigState.serverConfiguration, sortType]);

    const modelSlot = useMemo(() => {
        const onModelSlotEditClicked = () => {
            guiState.setDialogName(DialogName.modelSlotManagerMainDialog);
        };
        return (
            <div className={modelSlotArea}>
                <div className={modelSlotTitle}>Model</div>
                <div className={modelSlotPane}>
                    <div className={modelSlotTilesContainer}>{modelTiles}</div>
                    <div className={buttons}>
                        <div className={buttonGroup}>
                            <div
                                className={`${BasicButton({ width: "small", active: sortType == "slot" ? true : false })} ${modelSlotButtonThema}`}
                                onClick={() => {
                                    setSortType("slot");
                                }}
                            >
                                <FaSortNumericDown />
                            </div>
                            <div
                                className={`${BasicButton({ width: "small", active: sortType == "name" ? true : false })} ${modelSlotButtonThema}`}
                                onClick={() => {
                                    setSortType("name");
                                }}

                            >
                                <FaSortAlphaDown />
                            </div>
                        </div>
                        <div className={buttonGroup}>
                            <div
                                className={`${BasicButton({ width: "small" })} ${modelSlotButtonThema}`}
                                onClick={onModelSlotEditClicked}>
                                {t("model_slot_edit")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }, [modelTiles, sortType]);

    return modelSlot;
};
