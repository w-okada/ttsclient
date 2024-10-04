import { useEffect, useMemo } from "react";
import React from "react";
import { textInputArea } from "../../styles/textInputArea.css";
import { useTranslation } from "react-i18next";
import { CutMethod, LanguageType, GenerateVoiceParam, GPTSoVITSSlotInfo } from "tts-client-typescript-client-lib";
import { useAppState } from "../../002_AppStateProvider";
import { useAppRoot } from "../../001_AppRootProvider";
import { AUDIO_ELEMENT_FOR_PLAY_MONITOR, AUDIO_ELEMENT_FOR_PLAY_RESULT } from "../../const";
import { use } from "i18next";
import { BasicButton } from "../../styles/style-components/buttons/01_basic-button.css"
import { BasicInput } from "../../styles/style-components/inputs/01_basic-input.css";
import { normalButtonThema } from "../../styles/style-components/buttons/thema/button-thema.css";
import { useGuiState } from "../GuiStateProvider";
import { BasicAudio } from "../../styles/style-components/audios/01_basic-audio.css";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";
import { SectionHeader } from "../../styles/style-components/labels/02_section-header.css";
export const TextInputArea = () => {
    const { t } = useTranslation();
    const { triggerToast, serverConfigState } = useAppRoot();
    const { inferenceLanguage, setInferenceLanguage: setInferenceLanguage, speed, setSpeed, cutMethod, setCutMethod, curretVoiceCharacterSlotIndex, currentReferenceVoiceIndexes, audioOutput, audioMonitor, generatedVoice, setGeneratedVoice, elapsedTime, setElapsedTime } = useAppState();

    const { setDialog2Name, setDialog2Props } = useGuiState()
    useEffect(() => {
        if (generatedVoice == null) {
            return
        }

        const url = URL.createObjectURL(generatedVoice);
        const audioElemOutput = document.getElementById(AUDIO_ELEMENT_FOR_PLAY_RESULT) as HTMLAudioElement;
        const audioElemMonitor = document.getElementById(AUDIO_ELEMENT_FOR_PLAY_MONITOR) as HTMLAudioElement;
        audioElemOutput.src = url;
        audioElemMonitor.src = url;

    }, [generatedVoice])

    useEffect(() => {
        const updateSink = async () => {
            const audioElemOutput = document.getElementById(AUDIO_ELEMENT_FOR_PLAY_RESULT) as HTMLAudioElement
            if (!audioElemOutput) return
            if (audioOutput == "none") {
                audioElemOutput.volume = 0
                return
            }

            audioElemOutput.volume = 1
            await audioElemOutput.setSinkId(audioOutput)
            if (!generatedVoice) {
                return
            }
            const url = URL.createObjectURL(generatedVoice);
            audioElemOutput.src = url
        }
        updateSink()
    }, [audioOutput])

    useEffect(() => {
        const updateSink = async () => {
            const audioElemMonitor = document.getElementById(AUDIO_ELEMENT_FOR_PLAY_MONITOR) as HTMLAudioElement
            if (!audioElemMonitor) return
            if (audioMonitor == "none") {
                audioElemMonitor.volume = 0
                return
            }
            audioElemMonitor.volume = 1

            await audioElemMonitor.setSinkId(audioMonitor)
            if (!generatedVoice) {
                return
            }
            const url = URL.createObjectURL(generatedVoice);
            audioElemMonitor.src = url
        }
        updateSink()

    }, [audioMonitor])


    const area = useMemo(() => {
        if (!serverConfigState.serverConfiguration) return
        if (!serverConfigState.serverSlotInfos) return
        const slotIndex = serverConfigState.serverConfiguration.current_slot_index
        const slotInfo = serverConfigState.serverSlotInfos[slotIndex]
        if (!slotInfo) return

        let topK = 15
        let topP = 1.0
        let temperature = 1.0
        let batchSize = 20
        if (slotInfo.tts_type == "GPT-SoVITS") {
            const gptSovitsSlotImnfo = slotInfo as GPTSoVITSSlotInfo
            topK = gptSovitsSlotImnfo.top_k
            topP = gptSovitsSlotImnfo.top_p
            temperature = gptSovitsSlotImnfo.temperature
            batchSize = gptSovitsSlotImnfo.batch_size
        }

        const languageSelect = (
            <select
                defaultValue={inferenceLanguage}
                id="reference-voice-area-language-select"
                onChange={(e) => {
                    setInferenceLanguage(e.target.value as LanguageType);
                }}
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
        )
        const speedInput = (
            <input
                type="number"
                id="reference-voice-area-speed-input"
                defaultValue={speed}
                step="0.05"
                min="0.6"
                max="1.65"
                onChange={(e) => {
                    setSpeed(parseFloat(e.target.value));
                }}
                className={BasicInput()}
            />
        )
        const cutMethodSelect = (
            <select
                defaultValue={cutMethod}
                id="reference-voice-area-cut-method-select"
                onChange={(e) => {
                    setCutMethod(e.target.value as CutMethod);
                }}
                className={BasicInput()}
            >
                {CutMethod.map((x, index) => {
                    return (
                        <option key={x} value={x}>
                            {x}
                        </option>
                    )
                })}
            </select>
        )
        const runClicked = async () => {
            const text = (document.getElementById("text-input-area-textarea") as HTMLTextAreaElement).value;


            if (curretVoiceCharacterSlotIndex == null) {
                return
            }
            const voices = currentReferenceVoiceIndexes[curretVoiceCharacterSlotIndex]
            if (!voices || voices.length != 1) {
                triggerToast("error", `multi voice not implemented: ${voices}, ${voices.length}`)
                return
            }
            const voice = voices[0]

            const start = performance.now();
            const param: GenerateVoiceParam = {
                voice_character_slot_index: curretVoiceCharacterSlotIndex,
                reference_voice_slot_index: voice,
                text: text,
                language: inferenceLanguage,
                speed: speed,
                cutMethod: cutMethod,
            }
            try {
                const blob = await serverConfigState.generateVoice(param)

                if (blob == null) {
                    // TODO: error handling
                    console.log("blob is null")
                    return
                }
                setGeneratedVoice(blob)

            } catch (e) {
                console.error(e)
                // 1秒スリープ
                triggerToast("error", `error occured during generating voice`)
                await new Promise<void>((resolve) => {
                    setTimeout(() => {
                        resolve()
                    }, 1000)
                })
            }
            const end = performance.now();
            const elapsedTime = end - start;
            setElapsedTime(elapsedTime)
        }

        const topKOptions = Array(100).fill(0).map((x, i) => { return (<option key={i} value={i + 1}>{i + 1}</option>) })
        const topKSelect = (
            <select
                defaultValue={topK}
                id="reference-voice-area-top-k-select"
                onChange={(e) => {
                    if (!serverConfigState.serverConfiguration) return
                    if (!serverConfigState.serverSlotInfos) return


                    if (slotInfo.tts_type == "GPT-SoVITS") {
                        const gptSoVITSSlotInfo = slotInfo as GPTSoVITSSlotInfo
                        gptSoVITSSlotInfo.top_k = parseInt(e.target.value)
                        serverConfigState.updateServerSlotInfo(gptSoVITSSlotInfo)
                    }
                }}
                className={BasicInput()}
            >
                {topKOptions}
            </select >
        )
        const topPOptions = Array(100).fill(0).map((x, i) => { return (<option key={i} value={(i + 1) / 100}>{(i + 1) / 100}</option>) })
        const topPSelect = (
            <select
                defaultValue={topP}
                id="reference-voice-area-top-p-select"
                onChange={(e) => {
                    if (!serverConfigState.serverConfiguration) return
                    if (!serverConfigState.serverSlotInfos) return


                    if (slotInfo.tts_type == "GPT-SoVITS") {
                        const gptSoVITSSlotInfo = slotInfo as GPTSoVITSSlotInfo
                        gptSoVITSSlotInfo.top_p = parseFloat(e.target.value)
                        serverConfigState.updateServerSlotInfo(gptSoVITSSlotInfo)
                    }
                }}
                className={BasicInput()}
            >
                {topPOptions}
            </select >
        )
        const temperatureOptions = Array(100).fill(0).map((x, i) => { return (<option key={i} value={(i + 1) / 100}>{(i + 1) / 100}</option>) })
        const temperatureSelect = (
            <select
                defaultValue={temperature}
                id="reference-voice-area-temperature-select"
                onChange={(e) => {
                    if (!serverConfigState.serverConfiguration) return
                    if (!serverConfigState.serverSlotInfos) return

                    if (slotInfo.tts_type == "GPT-SoVITS") {
                        const gptSoVITSSlotInfo = slotInfo as GPTSoVITSSlotInfo
                        gptSoVITSSlotInfo.temperature = parseFloat(e.target.value)
                        serverConfigState.updateServerSlotInfo(gptSoVITSSlotInfo)
                    }
                }}
            >
                {temperatureOptions}
            </select >
        )

        const useFasterCheckBox = (
            <>
                <input type="checkbox" onChange={(e) => {
                    if (!serverConfigState.serverConfiguration) return
                    if (!serverConfigState.serverSlotInfos) return

                    if (slotInfo.tts_type == "GPT-SoVITS") {
                        const gptSoVITSSlotInfo = slotInfo as GPTSoVITSSlotInfo
                        gptSoVITSSlotInfo.enable_faster = e.target.checked
                        serverConfigState.updateServerSlotInfo(gptSoVITSSlotInfo)
                    }
                }} />
                <div>{t("text_input_area_enable faster inference_label")}</div>
            </>
        )

        const batchSizeOptions = Array(200).fill(0).map((x, i) => { return (<option key={i} value={i + 1}>{i + 1}</option>) })
        const batchSizeSelector = (
            <select
                defaultValue={batchSize}
                id="reference-voice-area-batch-size-select"
                onChange={(e) => {
                    if (!serverConfigState.serverConfiguration) return
                    if (!serverConfigState.serverSlotInfos) return

                    if (slotInfo.tts_type == "GPT-SoVITS") {
                        const gptSoVITSSlotInfo = slotInfo as GPTSoVITSSlotInfo
                        gptSoVITSSlotInfo.batch_size = parseInt(e.target.value)
                        serverConfigState.updateServerSlotInfo(gptSoVITSSlotInfo)
                    }
                }}
                className={BasicInput()}
            >
                {batchSizeOptions}
            </select>

        )


        return (
            <div className={textInputArea}>
                <div className={SectionHeader()}>
                    {t("text_input_area_title")}
                </div>
                <div style={{ display: "flex", flexDirection: "row", gap: "1rem" }}>
                    <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                        <div>{t("text_input_area_language_label")}</div>
                        <div>
                            {languageSelect}
                        </div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                        <div>{t("text_input_area_speed_label")}</div>
                        <div>
                            {speedInput}
                        </div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                        <div>{t("text_input_area_cut_method_label")}</div>
                        <div>
                            {cutMethodSelect}
                        </div>
                    </div>
                </div>

                <div style={{ display: "flex", flexDirection: "row", gap: "2rem" }}>
                    <div style={{ display: "flex", flexDirection: "column" }}>
                        <div className={BasicLabel({ width: "x-large" })}>{t("text_input_area_textarea-label")}</div>
                        <div>
                            <textarea id="text-input-area-textarea" rows={5} cols={50}></textarea>
                        </div>
                        <div style={{ textAlign: "right" }}>
                            <button id="text-input-area-submit-button" onClick={async () => {
                                setDialog2Props({
                                    title: t("wait_dialog_title_generating"),
                                    instruction: `${t("wait_dialog_instruction_generating")}`,
                                    defaultValue: "",
                                    resolve: () => { },
                                    options: null,
                                });
                                setDialog2Name("waitDialog");
                                await runClicked()
                                setDialog2Name("none");
                            }} className={`${BasicButton()} ${normalButtonThema}`}>{t("text_input_area_submit_button")}</button>
                        </div>
                    </div>




                    <div style={{ display: "flex", flexDirection: "column" }}>
                        <div className={BasicLabel({ width: "x-large" })}>{t("text_input_area_model_setting_label")}</div>

                        <div style={{ display: "flex", flexDirection: "row", gap: "1rem" }}>
                            <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                                {useFasterCheckBox}
                            </div>
                            <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                                <div>{t("text_input_area_batch_size_label")}</div>
                                <div>
                                    {batchSizeSelector}
                                </div>
                            </div>


                        </div>


                        <div style={{ display: "flex", flexDirection: "row", gap: "1rem" }}>
                            <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                                <div>{t("text_input_area_top_k_label")}</div>
                                <div>
                                    {topKSelect}
                                </div>
                            </div>
                            <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                                <div>{t("text_input_area_top_p_label")}</div>
                                <div>
                                    {topPSelect}
                                </div>
                            </div>
                            <div style={{ display: "flex", flexDirection: "row", gap: "0.3rem" }}>
                                <div>{t("text_input_area_temperature_label")}</div>
                                <div>
                                    {temperatureSelect}
                                </div>
                            </div>
                        </div>


                        <div className={BasicLabel({ width: "x-large" })}>{t("text_input_area_generated_voice_label")}[{elapsedTime.toFixed(0)}ms]</div>
                        <div style={{ display: "flex" }}>
                            <div style={{ width: "5rem" }}>{t("text_input_area_audio_device_output")}</div>
                            <audio controls id={AUDIO_ELEMENT_FOR_PLAY_RESULT} className={BasicAudio()}></audio>
                        </div>
                        <div style={{ display: "flex" }}>
                            <div style={{ width: "5rem" }}>{t("text_input_area_audio_device_monitor")}</div>
                            <audio controls id={AUDIO_ELEMENT_FOR_PLAY_MONITOR} className={BasicAudio()}></audio>
                        </div>
                        <div>
                            <button
                                className={`${BasicButton()} ${normalButtonThema}`}
                                disabled={!generatedVoice ? true : false} onClick={() => {
                                    if (!generatedVoice) {
                                        return
                                    }
                                    const a = document.createElement('a');
                                    const url = URL.createObjectURL(generatedVoice);
                                    a.href = url;
                                    a.download = 'output.wav';
                                    document.body.appendChild(a);
                                    a.click();
                                    document.body.removeChild(a);
                                    URL.revokeObjectURL(url);
                                }}>download</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }, [inferenceLanguage,
        speed,
        cutMethod,
        curretVoiceCharacterSlotIndex,
        currentReferenceVoiceIndexes,
        generatedVoice,
        serverConfigState.serverSlotInfos,
        serverConfigState.serverConfiguration,
        elapsedTime,
    ]);
    return area;
};
