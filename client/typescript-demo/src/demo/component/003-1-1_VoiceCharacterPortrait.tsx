import { useMemo } from "react";
import { portrait } from "../../styles/characterArea.css";
import React from "react";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { useAppState } from "../../002_AppStateProvider";

export const VoiceCharacterPortrait = () => {
    const { t } = useTranslation();
    const { serverConfigState, generateGetPathFunc } = useAppRoot();
    const { currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex } = useAppState();

    const portraitComponent = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (!voiceCharacter) {
            return <></>;
        }

        const selectedReferenceVoiceIndexes = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex]
        let iconUrl = ""
        if (!selectedReferenceVoiceIndexes) {
            // 選択中の音声が無い場合は、キャラクターアイコンを使用。
            iconUrl = voiceCharacter.icon_file != null ? "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voiceCharacter.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";

        } else if (selectedReferenceVoiceIndexes.length == 1) {
            // 選択中の音声が一つの場合は、その音声のアイコンを使用。音声にアイコンが無ければキャラクターアイコンを使用。
            const currentVoiceIndex = selectedReferenceVoiceIndexes[0]
            const voice = voiceCharacter.reference_voices.filter((voice) => voice.slot_index == currentVoiceIndex)[0]
            if (!voice) {
                // 音声が未登録の場合、キャラアイコンを使用。
                iconUrl = voiceCharacter.icon_file != null ? "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voiceCharacter.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";
            } else if (voice.icon_file) {
                // 音声にアイコンがある場合
                iconUrl = "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voice.icon_file.split(/[\/\\]/).pop()
            } else {
                // 音声にアイコンが無い場合、キャラアイコンを使用。
                iconUrl = voiceCharacter.icon_file != null ? "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voiceCharacter.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";
            }
        } else {
            // 複数の音声が選択されている場合は、キャラクターアイコンを使用。
            iconUrl = voiceCharacter.icon_file != null ? "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voiceCharacter.icon_file.split(/[\/\\]/).pop() : "./assets/icons/human.png";
        }

        iconUrl = generateGetPathFunc(iconUrl)


        const portraitComponent = <img className={portrait} src={iconUrl} alt={voiceCharacter.name} />;
        return portraitComponent;
    }, [serverConfigState.voiceCharacterSlotInfos, currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex]);
    return portraitComponent;
};
