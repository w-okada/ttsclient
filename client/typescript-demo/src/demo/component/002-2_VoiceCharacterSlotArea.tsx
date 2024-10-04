import React, { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { FaSortAlphaDown, FaSortNumericDown } from "react-icons/fa";
import {
    button,
    buttonActive,
    buttonGroup,
    buttons,
    modelSlotArea,
    modelSlotArea2,
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
import { useAppState } from "../../002_AppStateProvider";
export type VoiceCharacterSlotAreaProps = {};

const SortTypes = {
    slot: "slot",
    name: "name",
} as const;
export type SortTypes = (typeof SortTypes)[keyof typeof SortTypes];

export const VoiceCharacterSlotArea = (_props: VoiceCharacterSlotAreaProps) => {
    const { serverConfigState, triggerToast, generateGetPathFunc } = useAppRoot();
    const { curretVoiceCharacterSlotIndex, setCurretVoiceCharacterSlotIndex, referenceVoiceMode } = useAppState()
    const guiState = useGuiState();
    const { t } = useTranslation();
    const [sortType, setSortType] = useState<SortTypes>("slot");

    const modelTiles = useMemo(() => {
        if (!serverConfigState.voiceCharacterSlotInfos) {
            return <></>;
        }
        const voiceCharacterSlots =
            sortType == "slot"
                ? serverConfigState.voiceCharacterSlotInfos.slice().sort((a, b) => {
                    return a.slot_index - b.slot_index;
                })
                : serverConfigState.voiceCharacterSlotInfos.slice().sort((a, b) => {
                    return a.name.localeCompare(b.name);
                });

        return voiceCharacterSlots
            .map((x, index) => {
                if (x.tts_type == null) {
                    return null;
                }
                const tileContainerClass =
                    x.slot_index == curretVoiceCharacterSlotIndex
                        ? `${modelSlotTileContainer} ${modelSlotTileContainerSelected}`
                        : modelSlotTileContainer;
                const name = x.name.length > 8 ? x.name.substring(0, 7) + "..." : x.name;
                let icon = x.icon_file != null ? "voice_characters" + "/" + x.slot_index + "/" + x.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";
                icon = generateGetPathFunc(icon)

                const iconElem =
                    x.icon_file != null ? (
                        <>
                            <img className={modelSlotTileIcon} src={icon} alt={x.name} />
                            {/* <div className={modelSlotTileVctype}>{x.tts_type}</div> */}
                        </>
                    ) : (
                        <>
                            <div className={modelSlotTileIconNoEntry}>no image</div>
                            {/* <div className={modelSlotTileVctype}>{x.tts_type}</div> */}
                        </>
                    );

                const clickAction = async () => {
                    if (referenceVoiceMode == "edit") {
                        triggerToast("error", t("reference_voice_area_select_voice_error_in_edit_mode"))
                        return
                    }
                    setCurretVoiceCharacterSlotIndex(x.slot_index)
                };

                return (
                    <div key={index} className={tileContainerClass} onClick={clickAction}>
                        <div className={modelSlotTileIconDiv}>{iconElem}</div>
                        <div className={modelSlotTileDscription}>{name}</div>
                    </div>
                );
            })
            .filter((x) => x != null);
    }, [serverConfigState.voiceCharacterSlotInfos, curretVoiceCharacterSlotIndex, sortType, referenceVoiceMode]);

    const voiceCharacterlSlot = useMemo(() => {
        const onModelSlotEditClicked = () => {
            guiState.setDialogName(DialogName.voiceCharacterManagerMainDialog);
        };
        const sortSlotByIdClass = sortType == "slot" ? `${button} ${buttonActive}` : `${button}`;
        const sortSlotByNameClass = sortType == "name" ? `${button} ${buttonActive}` : `${button}`;
        return (
            <div className={modelSlotArea2}>
                <div className={modelSlotTitle}>Voice Character</div>

                <div className={modelSlotPane}>
                    <div className={modelSlotTilesContainer}>{modelTiles}</div>
                    <div className={buttons}>
                        <div className={buttonGroup}>
                            <div
                                className={sortSlotByIdClass}
                                onClick={() => {
                                    setSortType("slot");
                                }}
                            >
                                <FaSortNumericDown />
                            </div>
                            <div
                                className={sortSlotByNameClass}
                                onClick={() => {
                                    setSortType("name");
                                }}
                            >
                                <FaSortAlphaDown />
                            </div>
                        </div>
                        <div className={buttonGroup}>
                            <div className={button} onClick={onModelSlotEditClicked}>
                                {t("voice_character_slot_edit")}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }, [modelTiles, sortType]);

    return voiceCharacterlSlot;
};
