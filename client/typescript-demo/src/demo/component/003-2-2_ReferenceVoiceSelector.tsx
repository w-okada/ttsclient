import { useMemo } from "react";
import { characterAreaControl, characterAreaControlField, characterAreaControlTitle, characterAreaText } from "../../styles/characterArea.css";
import React from "react";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { useAppState } from "../../002_AppStateProvider";
import { BasicVoiceType } from "tts-client-typescript-client-lib";
import { Emotion, EmotionBlockButton, EmotionButton } from "../../styles/style-components/buttons/02_emotion-button.css";

export const ReferenceVoiceSelector = () => {
    const { serverConfigState, triggerToast } = useAppRoot();
    const { t } = useTranslation();
    const { currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex, setCurrentReferenceVoiceIndexes, referenceVoiceMode } = useAppState();

    const component = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (voiceCharacter == null) {
            return <></>;
        }
        const col = 25
        const row = 4
        const width = 14
        const gap = 5

        const tableWidth = (width + gap) * col

        const voiceBlockClicked = (index: number, ctrlPressed: boolean) => {
            // 既に選択済みだった場合。
            const indexes = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] || []
            if (indexes.includes(index)) {
                if (ctrlPressed) {
                    // コントロールが押されていたら、選択を解除する。
                    const newIndexes = indexes.filter(i => i !== index)
                    currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] = newIndexes
                    setCurrentReferenceVoiceIndexes({ ...currentReferenceVoiceIndexes })
                    return
                } else {
                    // コントロールが押されていなかったら、そのブロックだけ選択。
                    currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] = [index]
                    setCurrentReferenceVoiceIndexes({ ...currentReferenceVoiceIndexes })
                    return
                }
            }

            // 選択されていなかった場合。
            let newIndexes: number[] = []
            if (ctrlPressed) {
                newIndexes = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] || []
            }
            newIndexes.push(index)
            currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] = newIndexes
            setCurrentReferenceVoiceIndexes({ ...currentReferenceVoiceIndexes })
            return
        }

        const voiceBlocks = Array.from({ length: row }, (_, i) => {
            return Array.from({ length: col }, (_, j) => {
                const indexes = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] || []
                const cellIndex = i * col + j
                const selected = indexes.includes(cellIndex)
                const voices = voiceCharacter.reference_voices.filter(x => { return x.slot_index == cellIndex })
                let emotion: BasicVoiceType | "none" = "none"
                if (voices.length == 1) {
                    if (voices[0].voice_type in Emotion) {
                        emotion = voices[0].voice_type as BasicVoiceType
                    } else {
                        emotion = "other"
                    }
                }

                return (
                    <button key={cellIndex} className={EmotionBlockButton({ emotion: (emotion as BasicVoiceType), selected: selected })}
                        onClick={(e) => {
                            if (referenceVoiceMode == "edit") {
                                triggerToast("error", t("reference_voice_area_select_voice_error_in_edit_mode"))
                                return
                            }
                            voiceBlockClicked(cellIndex, e.ctrlKey);
                        }}
                    >
                    </button>
                )
            })
        }).map((x, i) => {
            return (
                <div key={i} style={{ width: tableWidth, display: "flex", gap: "3px", padding: `${gap}px` }}>
                    {x}
                </div>
            )
        })

        const selectVoiceType = (voiceType: string) => {
            if (referenceVoiceMode == "edit") {
                triggerToast("error", t("reference_voice_area_select_voice_error_in_edit_mode"))
                return
            }

            const reference_voices = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex].reference_voices
            const voiceIndexMatchType = reference_voices.filter(x => { return x.voice_type == voiceType }).map(x => { return x.slot_index })
            currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] = voiceIndexMatchType
            setCurrentReferenceVoiceIndexes({ ...currentReferenceVoiceIndexes })
        }
        const sideButtons = BasicVoiceType.map((x, i) => {
            return (
                <button key={x} className={EmotionButton({ emotion: x })}
                    onClick={() => { selectVoiceType(x) }}>{x}</button>
            )
        })

        return (
            <div style={{ display: "flex" }}>
                <div style={{ width: tableWidth, display: "flex", flexDirection: "column" }}>
                    {voiceBlocks}
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                    {sideButtons}
                </div>
            </div >
        );
    }, [serverConfigState.voiceCharacterSlotInfos, currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex, referenceVoiceMode]);

    return component
};
