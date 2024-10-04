import { useEffect, useMemo, useRef, useState } from "react";
import React from "react";
import {
    configSubAreaInputMedia,
    configSubAreaInputMediaCaptureButton,
    configSubAreaInputMediaCaptureButtonActive,
    configSubAreaInputMediaContainer,
    configSubAreaInputMediaEchoButton,
    configSubAreaInputMediaEchoButtonActive,
    configSubAreaInputMediaFileSelectIcon,
    configSubAreaRow,
    configSubAreaRowField14,
    configSubAreaRowTitle5,
} from "../../styles/configArea.css";
import { useAppRoot } from "../../001_AppRootProvider";
import { useTranslation } from "react-i18next";
import { left1Padding } from "../../styles/base.css";
import { AUDIO_ELEMENT_FOR_INPUT_MEDIA, AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK, AudioDeviceType } from "../../const";
import { isDesktopApp } from "../../util/isDesctopApp";
import { Logger } from "../../util/logger";
import { useAppState } from "../../002_AppStateProvider";
import { fileSelectorAsDataURL } from "tts-client-typescript-client-lib";
import { BasicInput } from "../../styles/style-components/inputs/01_basic-input.css";
import { BasicLabel } from "../../styles/style-components/labels/01_basic-label.css";

type AudioDeviceAreaDeviceSelectProps = {
    type: AudioDeviceType;
};

const InputType = {
    deviceId: "deviceId",
    file: "file",
    capture: "capture",
} as const;
type InputType = (typeof InputType)[keyof typeof InputType];

export const BrowserAudioDeviceAreaDeviceSelect = (props: AudioDeviceAreaDeviceSelectProps) => {
    const { serverConfigState, audioConfigState } = useAppRoot();
    const { audioInput, audioOutput, audioMonitor, setAudioInput, setAudioOutput, setAudioMonitor } = useAppState()

    const { t } = useTranslation();
    const [inputType, setInputType] = useState<InputType>(InputType.deviceId);
    const [enableEchoback, setEnableEchoback] = useState(false);
    const audioSrcNode = useRef<MediaElementAudioSourceNode>();
    const displayMediaStream = useRef<MediaStream | null>(null);
    const [nowCapturing, setNowCapturing] = useState(false);

    const select = useMemo(() => {
        const onAudioInputChanged = (event) => {
            setAudioInput(event.target.value);
        };
        const onAudioOutputChanged = (event) => {
            setAudioOutput(event.target.value);
        };
        const onAudioMonitorChanged = (event) => {
            setAudioMonitor(event.target.value);
        };

        if (props.type == "Input") {
            const options = audioConfigState.audioInputs.map((c) => {
                return (
                    <option key={c.deviceId} value={c.deviceId}>
                        {c.label}
                    </option>
                );
            });
            let value;
            if (inputType == "file") {
                value = "file";
            } else if (inputType == "capture") {
                value = "screen";
            } else if (typeof audioInput === "string") {
                value = audioInput;
            } else {
                value = "none";
            }
            return (
                <select
                    value={value}
                    onChange={(event) => {
                        if (event.target.value != "file" && event.target.value != "screen") {
                            setInputType(InputType.deviceId);
                            onAudioInputChanged(event);
                        } else if (event.target.value == "file") {
                            setInputType(InputType.file);
                        } else if (event.target.value == "screen") {
                            setInputType(InputType.capture);
                        }
                    }}
                    className={BasicInput()}
                >
                    {options}
                </select>
            );
        } else if (props.type == "Output") {
            const options = audioConfigState.audioOutputs.map((c) => {
                return (
                    <option key={c.deviceId} value={c.deviceId}>
                        {c.label}
                    </option>
                );
            });
            const value = audioOutput;
            return (
                <select
                    value={value}
                    onChange={(event) => {
                        onAudioOutputChanged(event);
                    }}
                    className={BasicInput()}
                >
                    {options}
                </select>
            );
        } else if (props.type == "Monitor") {
            const options = audioConfigState.audioOutputs.map((c) => {
                return (
                    <option key={c.deviceId} value={c.deviceId}>
                        {c.label}
                    </option>
                );
            });
            const value = audioMonitor;
            return (
                <select
                    value={value}
                    onChange={(event) => {
                        onAudioMonitorChanged(event);
                    }}
                    className={BasicInput()}
                >
                    {options}
                </select>
            );
        } else {
            return <></>;
        }
    }, [
        inputType,
        audioConfigState.audioInputs,
        audioConfigState.audioOutputs,
        audioInput,
        audioOutput,
        audioMonitor,
    ]);

    const audioPlayerRow = useMemo(() => {
        if (inputType != "file") {
            return <></>;
        }

        const onFileLoadClicked = async () => {
            if (!audioConfigState.audioContext) {
                return;
            }
            const url = await fileSelectorAsDataURL("");

            // input stream for client.
            const audio = document.getElementById(AUDIO_ELEMENT_FOR_INPUT_MEDIA) as HTMLAudioElement;
            audio.pause();
            audio.srcObject = null;
            audio.src = url;
            await audio.play();
            if (!audioSrcNode.current) {
                audioSrcNode.current = audioConfigState.audioContext.createMediaElementSource(audio);
            }
            if (audioSrcNode.current.mediaElement != audio) {
                audioSrcNode.current = audioConfigState.audioContext.createMediaElementSource(audio);
            }

            const dst = audioConfigState.audioContext.createMediaStreamDestination();
            audioSrcNode.current.connect(dst);
            setAudioInput(dst.stream);

            const audio_echo = document.getElementById(AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK) as HTMLAudioElement;
            audio_echo.srcObject = dst.stream;
            audio_echo.play();
            audio_echo.volume = 0;
        };

        const onEnableEchobackClicked = () => {
            setEnableEchoback(!enableEchoback);
        };

        const echobackButtonClass = enableEchoback ? configSubAreaInputMediaEchoButtonActive : configSubAreaInputMediaEchoButton;
        return (
            <div className={configSubAreaRow}>
                <div className={configSubAreaInputMediaContainer}>
                    <audio id={AUDIO_ELEMENT_FOR_INPUT_MEDIA} controls controlsList="nodownload noplaybackrate" className={configSubAreaInputMedia}></audio>
                    <audio id={AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK} controls hidden></audio>
                    <img className={configSubAreaInputMediaFileSelectIcon} src="./assets/icons/folder.svg" onClick={onFileLoadClicked} />
                    <div
                        className={echobackButtonClass}
                        onClick={() => {
                            onEnableEchobackClicked();
                        }}
                    >
                        echo
                    </div>
                </div>
            </div>
        );
    }, [inputType, enableEchoback]);

    useEffect(() => {
        const setEchobackAudioOutput = async () => {
            if (props.type != "Input") {
                // ここ誤解しやすいようなので注意。file input/captureの時の出力を設定するので、
                // inputの場合のみ処理を行う。
                return;
            }
            const audio_echo = document.getElementById(AUDIO_ELEMENT_FOR_INPUT_MEDIA_ECHOBACK) as HTMLAudioElement;
            if (audio_echo == null) {
                return;
            }

            if (enableEchoback) {
                audio_echo.volume = 1;
            } else {
                audio_echo.volume = 0;
            }

            if (audioOutput != "none") {
                try {
                    await audio_echo.setSinkId(audioOutput);
                } catch (e) {
                    console.log("setSinkId is not supported?", e);
                }
            } else {
                // オーディオアウトが無効化されている場合は、ミュートで対応
                audio_echo.volume = 0;
            }
        };
        setEchobackAudioOutput();
    }, [inputType, enableEchoback, audioOutput]);

    const audioCaptureRow = useMemo(() => {
        if (inputType != "capture") {
            return <></>;
        }

        const onCaptureClicked = async () => {
            // 既存msをクローズ
            if (displayMediaStream.current) {
                displayMediaStream.current.getTracks().forEach((x) => {
                    x.stop();
                });
                displayMediaStream.current = null;
            }

            // すでにキャプチャ中ならここで終了。
            if (nowCapturing == true) {
                setNowCapturing(false);
                return;
            }
            // これからキャプチャする場合は以下続行。

            // 共有スタート
            try {
                if (isDesktopApp()) {
                    const constraints = {
                        audio: {
                            mandatory: {
                                chromeMediaSource: "desktop",
                            },
                        },
                        video: {
                            mandatory: {
                                chromeMediaSource: "desktop",
                            },
                        },
                    };
                    // @ts-ignore
                    displayMediaStream.current = await navigator.mediaDevices.getUserMedia(constraints);
                } else {
                    displayMediaStream.current = await navigator.mediaDevices.getDisplayMedia({
                        video: true,
                        audio: true,
                    });
                }
            } catch (e) {
                Logger.getLogger().info(e);
                return;
            }
            if (!displayMediaStream.current) {
                console.error("Capture failed, no media stream.");
                return;
            }
            if (displayMediaStream.current.getAudioTracks().length == 0) {
                displayMediaStream.current.getTracks().forEach((x) => {
                    x.stop();
                });
                displayMediaStream.current = null;
                console.error("Capture failed, no audio track.");
                return;
            }

            try {
                setAudioInput(displayMediaStream.current);
            } catch (e) {
                console.error(e);
            }
            setNowCapturing(true);
        };
        const className = nowCapturing ? configSubAreaInputMediaCaptureButtonActive : configSubAreaInputMediaCaptureButton;
        return (
            <div className={configSubAreaRow}>
                <div className={configSubAreaInputMediaContainer}>
                    <div
                        className={className}
                        onClick={() => {
                            onCaptureClicked();
                        }}
                    >
                        capture
                    </div>
                </div>
            </div>
        );
    }, [inputType, nowCapturing]);

    const name = useMemo(() => {
        if (props.type == "Input") {
            return t("config_area_audio_device_input");
        } else if (props.type == "Output") {
            return t("config_area_audio_device_output");
        } else if (props.type == "Monitor") {
            return t("config_area_audio_device_monitor");
        }
    }, []);

    const component = useMemo(() => {
        if (!serverConfigState) {
            return <></>;
        }

        return (
            <>
                <div className={configSubAreaRow}>
                    <div className={BasicLabel()}>{name}:</div>
                    <div className={configSubAreaRowField14}>{select}</div>
                </div>
                {audioPlayerRow}
                {audioCaptureRow}
            </>
        );
    }, [select, serverConfigState, audioPlayerRow, audioCaptureRow]);

    return component;
};
