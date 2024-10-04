import { useEffect, useMemo } from "react";
import { characterAreaControl, characterAreaControlField, characterAreaControlFieldFullWidth, characterAreaControlTitle, characterAreaText } from "../../styles/characterArea.css";
import React from "react";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { useAppState } from "../../002_AppStateProvider";
import { BasicVoiceType, LanguageType } from "tts-client-typescript-client-lib";
import { BasicButton } from "../../styles/style-components/buttons/01_basic-button.css";
import { normalButtonThema } from "../../styles/style-components/buttons/thema/button-thema.css";
import { BasicInput } from "../../styles/style-components/inputs/01_basic-input.css";
import { BasicAudio } from "../../styles/style-components/audios/01_basic-audio.css";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";
import { useGuiState } from "../GuiStateProvider";

export const ReferenceVoiceArea = () => {
    const { serverConfigState, triggerToast, generateGetPathFunc } = useAppRoot();
    const { t } = useTranslation();
    const { currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex, referenceVoiceMode, setReferenceVoiceMode } = useAppState();
    const { setDialog2Props, setDialog2Name } = useGuiState()

    const handleFiles = (files) => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        files.forEach(file => {
            console.log('ファイル名:', file.name);
            const voiceIndex = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex]
            if (!voiceIndex || voiceIndex.length != 1) {
                console.warn("voiceIndex is invalid", voiceIndex)
                return
            }
            serverConfigState.addReferenceVoice(curretVoiceCharacterSlotIndex, voiceIndex[0], "misc", file, (progress: number, end: boolean) => {
                console.log("progress", progress, end)
            })
        });
    }

    useEffect(() => {
        const dropArea = document.getElementById("reference-voice-area-audio-drop-area") as HTMLDivElement;
        const fileElem = document.getElementById("reference-voice-area-audio-file-elem") as HTMLInputElement;

        if (!dropArea || !fileElem) {
            return;
        }

        const handleDragOver = (e) => {
            e.preventDefault();
            dropArea.style.borderColor = '#ffc062';
        };

        const handleDragLeave = () => {
            dropArea.style.borderColor = '#2fcd93';
        };

        const handleDrop = (e) => {
            e.preventDefault();
            dropArea.style.borderColor = '#2fcd93';
            const files = [...(e.dataTransfer?.files || [])];
            handleFiles(files);
        };

        const handleClick = () => {
            console.log("clicked");
            fileElem.click();
        };

        const handleChange = (e) => {
            const input = e.target as HTMLInputElement;
            const files = [...(input.files ?? [])];
            handleFiles(files);
        };

        dropArea.addEventListener('dragover', handleDragOver);
        dropArea.addEventListener('dragleave', handleDragLeave);
        dropArea.addEventListener('drop', handleDrop);
        dropArea.addEventListener('click', handleClick);
        fileElem.addEventListener('change', handleChange);

        return () => {
            dropArea.removeEventListener('dragover', handleDragOver);
            dropArea.removeEventListener('dragleave', handleDragLeave);
            dropArea.removeEventListener('drop', handleDrop);
            dropArea.removeEventListener('click', handleClick);
            fileElem.removeEventListener('change', handleChange);
        };
    }, [handleFiles]);


    const component = useMemo(() => {
        if (curretVoiceCharacterSlotIndex == null) {
            return <></>;
        }
        const voiceCharacter = serverConfigState.voiceCharacterSlotInfos[curretVoiceCharacterSlotIndex];
        if (!voiceCharacter) {
            return <></>;
        }
        const selectedVoices = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex] || []
        if (selectedVoices.length == 0) {
            return <>{t("reference_voice_area_no_selection")}</>
        }
        if (selectedVoices.length > 1) {
            return <>{t("reference_voice_area_multiple_selection")}</>
        }



        const selectedId = selectedVoices[0]
        const voices = voiceCharacter.reference_voices.filter(v => v.slot_index == selectedId)
        if (voices.length > 1) {
            throw new Error(`multiple voices are registered in one index, ${voices.length}`)
        }
        if (voices.length == 0) {
            // 未登録の場合
            return (
                <>
                    <div id="reference-voice-area-audio-drop-area" style={{
                        border: "5px solid #2fcd93", padding: "1rem", borderRadius: "10px"
                    }
                    }>
                        <p>{t("reference_voice_area_fileupload_area_text")}</p>
                    </div >
                    <input type="file" hidden id="reference-voice-area-audio-file-elem" />
                </>
            );

        }

        // if (voices[0]) {
        //     audioUrl = voice.wav_file
        //     text = voice.text
        // }
        let audioUrl = "voice_characters" + "/" + voiceCharacter.slot_index + "/" + voices[0].wav_file.split(/[\/\\]/).pop()
        audioUrl = generateGetPathFunc(audioUrl)
        const text = voices[0].text
        const category = voices[0].voice_type
        const language = voices[0].language

        const audioArea = (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("reference_voice_area_audio")}:</div>
                <div className={characterAreaControlField}>
                    <audio controls src={audioUrl} className={BasicAudio()} />
                </div>
            </div>
        )
        const textArea = (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("reference_voice_area_text")}:</div>
                <div className={characterAreaControlFieldFullWidth}>
                    {text}
                </div>
            </div>
        )
        const textAreaInEditMode = (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("reference_voice_area_text")}:</div>
                <div className={characterAreaControlFieldFullWidth}>
                    <input className={BasicInput()} id="reference-voice-area-text-input" type="text" defaultValue={text}></input>
                </div>
            </div>
        )
        const categoryArea = (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("reference_voice_area_category")}:</div>
                <div className={characterAreaControlField}>
                    {category}
                </div>
            </div>
        )

        const categoryAreaInEditMode = (
            <div className={characterAreaControl}>
                <div className={BasicLabel()}>{t("reference_voice_area_category")}:</div>
                <div className={characterAreaControlField}>
                    <select
                        defaultValue={category}
                        id="reference-voice-area-category-select"
                        className={BasicInput()}
                    >
                        {BasicVoiceType.map((x, index) => {
                            return (
                                <option key={x} value={x}>
                                    {x}
                                </option>
                            )
                        })}
                    </select>
                </div>
            </div>
        )

        const languageArea = (
            <div className={characterAreaControl}>
                <div className={characterAreaControlTitle}>{t("reference_voice_area_language")}:</div>
                <div className={characterAreaControlField}>
                    {language}
                </div>
            </div>
        )

        const languageAreaInEditMode = (
            <div className={characterAreaControl}>
                <div className={characterAreaControlTitle}>{t("reference_voice_area_language")}:</div>
                <div className={characterAreaControlField}>
                    <select
                        defaultValue={language}
                        id="reference-voice-area-language-select"
                        className={BasicInput()}
                    >
                        {LanguageType.map((x, index) => {
                            return (
                                <option key={x} value={x}>
                                    {x}
                                </option>
                            )
                        })}
                    </select>
                </div>
            </div>
        )

        const downloadClicked = async () => {
            const blob = await serverConfigState.downloadVoiceCharacter(curretVoiceCharacterSlotIndex)
            if (!blob) {
                triggerToast("error", t("reference_voice_area_download_error"))
                return
            }
            const a = document.createElement('a');
            const url = URL.createObjectURL(blob);
            a.href = url;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        const buttonArea = (
            <div className={characterAreaControl}>
                <button
                    onClick={() => { setReferenceVoiceMode("edit") }}
                    className={`${BasicButton()} ${normalButtonThema}`}
                >{t("reference_voice_area_edit_button")}</button>
                <button
                    onClick={() => { serverConfigState.deleteReferenceVoice(curretVoiceCharacterSlotIndex, selectedId) }}
                    className={`${BasicButton()} ${normalButtonThema}`}
                >{t("reference_voice_area_delete_button")}</button>
                <button
                    onClick={async () => {
                        setDialog2Props({
                            title: t("reference_voice_area_download_waiting_dialog_title"),
                            instruction: `${t("reference_voice_area_download_waiting_dialog_instruction")}`,
                            defaultValue: "",
                            resolve: () => { },
                            options: null,
                        });
                        setDialog2Name("waitDialog");
                        await downloadClicked()
                        setDialog2Name("none");




                    }}
                    className={`${BasicButton()} ${normalButtonThema}`}
                >{t("reference_voice_area_download_button")}</button>

            </div>
        )
        const buttonAreaInEditMode = (
            <div className={characterAreaControl}>
                <button
                    onClick={() => {
                        const newVoice = voices[0]
                        const textArea = document.getElementById("reference-voice-area-text-input") as HTMLInputElement
                        const categorySelect = document.getElementById("reference-voice-area-category-select") as HTMLSelectElement
                        const languageSelect = document.getElementById("reference-voice-area-language-select") as HTMLSelectElement

                        newVoice.text = textArea.value
                        newVoice.voice_type = categorySelect.value as BasicVoiceType
                        newVoice.language = languageSelect.value as LanguageType
                        serverConfigState.updateReferenceVoice(curretVoiceCharacterSlotIndex, selectedId, newVoice)
                        setReferenceVoiceMode("view")

                    }}
                    className={`${BasicButton()} ${normalButtonThema}`}
                >{t("reference_voice_area_save_button")}</button>
                <div
                    onClick={() => { setReferenceVoiceMode("view") }}
                    className={`${BasicButton()} ${normalButtonThema}`}
                >{t("reference_voice_area_cancel_button")}</div>
            </div>
        )

        if (referenceVoiceMode == "view") {
            return (
                <>
                    {audioArea}
                    {textArea}
                    {categoryArea}
                    {languageArea}
                    {buttonArea}
                </>
            );

        } else {
            return (
                <>
                    {audioArea}
                    {textAreaInEditMode}
                    {categoryAreaInEditMode}
                    {languageAreaInEditMode}
                    {buttonAreaInEditMode}
                </>
            );
        }

    }, [serverConfigState.voiceCharacterSlotInfos, currentReferenceVoiceIndexes, curretVoiceCharacterSlotIndex, referenceVoiceMode]);

    return component
};
