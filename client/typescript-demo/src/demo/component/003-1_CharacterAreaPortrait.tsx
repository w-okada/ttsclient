import { useMemo } from "react";
import {
    portraitArea,
    portraitAreaAboutModelAndVoice,
    portraitAreaAboutModelAndVoicePopupLink,
    portraitAreaChangable,
    portraitAreaTermsOfUse,
    portraitContainer,
} from "../../styles/characterArea.css";
import React from "react";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { VoiceCharacterPortrait } from "./003-1-1_VoiceCharacterPortrait";
import { useAppState } from "../../002_AppStateProvider";
import { useGuiState } from "../GuiStateProvider";

export const CharacterAreaPortrait = () => {
    const { serverConfigState } = useAppRoot();
    const { currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex, referenceVoiceMode } = useAppState();
    const { setDialogName } = useGuiState();
    const { t } = useTranslation();

    const selectedTermOfUseUrlLink = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (voiceCharacter == null) {
            return <></>;
        }
        if (voiceCharacter.terms_of_use_url == null) {
            return <></>;
        }


        return (
            <div className={portraitAreaTermsOfUse}>
                <a href={voiceCharacter.terms_of_use_url} target="_blank" rel="noopener noreferrer" className="portrait-area-terms-of-use-link">
                    [{t("character_area_portrait_terms_of_use")}]
                </a>
            </div>
        );
    }, [serverConfigState.voiceCharacterSlotInfos, currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex]);

    const aboutModelAndVoice = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (!voiceCharacter == null) {
            return <></>;
        }
        if (voiceCharacter.description == null && voiceCharacter.credit == null) {
            return <></>;
        }
        return (
            <div className={portraitAreaAboutModelAndVoice}>
                <div
                    className={portraitAreaAboutModelAndVoicePopupLink}
                    onClick={() => {
                        setDialogName("aboutModelDialog");
                    }}
                >
                    [{t("character_area_portrait_about_model")}]
                </div>
            </div>
        );
    }, [serverConfigState.voiceCharacterSlotInfos, currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex]);
    // const statusArea = useMemo(() => {
    //     if (!slotInfo) {
    //         return <></>;
    //     }
    //     if (!serverConfigState.serverConfiguration) {
    //         return <></>;
    //     }
    //     if (!voiceChangerClientState.performanceData) {
    //         return <></>;
    //     }

    //     const performance = serverConfigState.serverConfiguration.enable_performance_monitor ? (
    //         <>
    //             <p>
    //                 vol[in]: <span id="status-vol">{(voiceChangerClientState.performanceData.input_volume_db || 0).toFixed(2) || 0}Db</span>
    //             </p>
    //             <p>
    //                 vol[out]: <span id="status-vol">{(voiceChangerClientState.performanceData.output_volume_db || 0).toFixed(2) || 0}Db</span>
    //             </p>
    //             <p>
    //                 convert: <span id="status-buf">{(voiceChangerClientState.performanceData.elapsed_time || 0).toFixed(2)}sec</span>
    //             </p>
    //         </>
    //     ) : (
    //         <></>
    //     );
    //     return (
    //         <div className={portraitAreaStatus}>
    //             <p>
    //                 <span className={portraitAreaStatusVctype}>{slotInfo?.voice_changer_type}</span>
    //             </p>
    //             {performance}
    //         </div>
    //     );
    // }, [slotInfo, serverConfigState.serverConfiguration?.enable_performance_monitor, voiceChangerClientState.performanceData]);
    const portraitClicked = () => {
        if (referenceVoiceMode == "view") {
            return
        }
        if (curretVoiceCharacterSlotIndex == null) {
            return
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (voiceCharacter == null) {
            return
        }
        const selectedReferenceVoiceIndexes = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex]
        if (selectedReferenceVoiceIndexes.length != 1) {
            return
        }


        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);
        fileInput.click();

        // ファイルが選択されたときの処理
        fileInput.onchange = async () => {
            if (!fileInput.files) {
                return
            }
            const file = fileInput.files[0];
            if (file) {
                serverConfigState.updateReferenceVoiceIconFile(curretVoiceCharacterSlotIndex, selectedReferenceVoiceIndexes[0], file, () => { });
            }

            // ファイル選択後にinput要素を削除
            document.body.removeChild(fileInput);
        }
    }

    const component = useMemo(() => {
        const portraitAreaClass = referenceVoiceMode == "view" ? portraitArea : portraitAreaChangable;
        return (

            <div className={portraitAreaClass}>
                <div className={portraitContainer} onClick={() => {
                    portraitClicked()
                }}>
                    <VoiceCharacterPortrait></VoiceCharacterPortrait>
                    {selectedTermOfUseUrlLink}
                    {aboutModelAndVoice}
                </div>
            </div>
        );
    }, [selectedTermOfUseUrlLink, aboutModelAndVoice, referenceVoiceMode]);
    return component;
};
