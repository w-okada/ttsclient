import { useMemo } from "react";
import { characterAreaControl, characterAreaControlField, characterAreaControlTitle, characterAreaText } from "../../styles/characterArea.css";
import React from "react";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { useAppState } from "../../002_AppStateProvider";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";

export const CharacterAreaControlName = () => {
    const { serverConfigState } = useAppRoot();
    const { t } = useTranslation();
    const { curretVoiceCharacterSlotIndex } = useAppState();

    const nameArea = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (voiceCharacter == null) {
            return <></>;
        }
        let name = voiceCharacter.name;
        return (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("character_area_control_name")}:</div>
                <div className={characterAreaControlField}>
                    <div className={characterAreaText}>{name}</div>
                </div>
            </div>
        );
    }, [serverConfigState.voiceCharacterSlotInfos, curretVoiceCharacterSlotIndex]);

    return nameArea;
};
