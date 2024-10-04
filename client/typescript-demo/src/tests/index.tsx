import * as React from "react";
import {
    TTSRestClient,
    fileSelector,
    downloadAsWav,
    MoveModelParam,
    PerformanceData,
} from "tts-client-typescript-client-lib";
import { rowButton, rowDesc, rowTitle, split_4_2_4, testRowContainer } from "../styles";
import { useAppRoot } from "../001_AppRootProvider";
import { Logger } from "../util/logger";

export const Tests = () => {
    const { audioConfigState } = useAppRoot();
    const client = React.useRef<TTSRestClient>();
    const [inputAudioDevice, setInputAudioDevice] = React.useState<string>("none");
    const [outputAudioDevice, setOutputAudioDevice] = React.useState<string>("none");

    const setup = async () => {
        if (!client.current) {
            client.current = TTSRestClient.getInstance();
            // client.current.setBaseUrl("http://localhost:18000");
            client.current.setBaseUrl("");
        }

        if (audioConfigState.audioContext === null) {
            Logger.getLogger().info("audioContext is null");
            return;
        }
    };
    React.useEffect(() => {
        setup();
    }, [audioConfigState.audioContext]);

    const generateTestRow = (title: string, func: () => void) => {
        return (
            <div className={split_4_2_4}>
                <div className={rowTitle}>{title}</div>
                <div className={rowButton}>
                    <button onClick={func}>exec</button>
                </div>
                <div className={rowDesc}></div>
            </div>
        );
    };

    const generateInputAudioDeviceSelect = () => {
        if (audioConfigState.audioInputs.length == 0) return <div>no input device</div>;
        return (
            <select
                onChange={(e) => {
                    setInputAudioDevice(e.target.value);
                }}
                defaultValue={inputAudioDevice}
            >
                {audioConfigState.audioInputs.map((x) => {
                    return (
                        <option key={x.deviceId} value={x.deviceId}>
                            {x.label}
                        </option>
                    );
                })}
            </select>
        );
    };
    const generateOutputAudioDeviceSelect = () => {
        if (audioConfigState.audioOutputs.length == 0) return <div>no output device</div>;
        return (
            <select
                onChange={(e) => {
                    setOutputAudioDevice(e.target.value);
                }}
                defaultValue={outputAudioDevice}
            >
                {audioConfigState.audioOutputs.map((x) => {
                    return (
                        <option key={x.deviceId} value={x.deviceId}>
                            {x.label}
                        </option>
                    );
                })}
            </select>
        );
    };

    React.useEffect(() => {
        // const audioElem = document.getElementById("audio-elem") as HTMLAudioElement;
        // if (outputAudioDevice == "none") {
        //     audioElem.setSinkId("");
        //     audioElem.volume = 0;
        // } else {
        //     audioElem.setSinkId(outputAudioDevice);
        //     audioElem.volume = 1;
        // }
        // audioElem.play();
    }, [outputAudioDevice]);

    return (
        // <div className={othreTheme}>
        <div className={` ${testRowContainer}`}>
            <h1>TEST</h1>
            {generateTestRow("get config", async () => {
                const res = await client.current!.getServerConfiguration();
                Logger.getLogger().info(res);
            })}

            {generateTestRow("update config", async () => {
                const res = await client.current!.getServerConfiguration();
                res.current_slot_index = 5
                client.current!.updateServerConfiguration(res);
            })}
            {generateTestRow("Get Server GPU Device", async () => {
                const res = await client.current!.getServerGPUInfo();
                Logger.getLogger().info(res);
            })}
            {generateTestRow("Get Server Module Status", async () => {
                const res = await client.current!.getServerModuleStatus();
                Logger.getLogger().info(res);
            })}
            {generateTestRow("Get Server Slot Infos", async () => {
                const res = await client.current!.getServerSlotInfos();
                Logger.getLogger().info(res);
            })}
            {generateTestRow("Get Server Slot Info[0]", async () => {
                const slot = await client.current!.getServerSlotInfo(0);
                Logger.getLogger().info(slot);
            })}
            {generateTestRow("Upload Server Slot Info[1]", async () => {
                const semantic_predictor_model = await fileSelector("");
                // const synthesizer_path = await fileSelector("");

                client.current!.uploadGPTSoVITSModelFile(1, semantic_predictor_model, null, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {generateTestRow("Upload Server Slot Info[2]", async () => {

                client.current!.uploadGPTSoVITSModelFile(2, null, null, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {generateTestRow("Delete Server Slot Info[0]", async () => {
                const slot = await client.current!.getServerSlotInfo(0);
                Logger.getLogger().info(slot);
                await client.current!.deleteServerSlotInfo(0);
                const slot2 = await client.current!.getServerSlotInfo(0);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Delete Server Slot Info[1]", async () => {
                const slot = await client.current!.getServerSlotInfo(1);
                Logger.getLogger().info(slot);
                await client.current!.deleteServerSlotInfo(1);
                const slot2 = await client.current!.getServerSlotInfo(1);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Delete Server Slot Info[2]", async () => {
                const slot = await client.current!.getServerSlotInfo(2);
                Logger.getLogger().info(slot);
                await client.current!.deleteServerSlotInfo(2);
                const slot2 = await client.current!.getServerSlotInfo(2);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Update Server Slot Info[2]", async () => {
                const slot = await client.current!.getServerSlotInfo(2);
                Logger.getLogger().info(slot);
                slot.name = "aaaaaaaaaaa";
                slot.description = "bbbbbbbbbbbb";
                await client.current!.updateServerSlotInfo(slot);
                const slot2 = await client.current!.getServerSlotInfo(2);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Move Model[1->2]", async () => {
                const moveParam: MoveModelParam = {
                    src: 1,
                    dst: 2,
                };
                await client.current!.moveModel(moveParam);
            })}
            {generateTestRow("Set Icon file slot[1]", async () => {
                const file = await fileSelector("");
                client.current!.uploadIconFile(1, file, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}

            {/* VOICE CHARACTER */}
            {generateTestRow("Get Chara Slot Infos", async () => {
                const res = await client.current!.getVoiceCharacterSlotInfos();
                Logger.getLogger().info(res);
            })}
            {generateTestRow("Get Chara Slot Info[0]", async () => {
                const slot = await client.current!.getVoiceCharacterSlotInfo(0);
                Logger.getLogger().info(slot);
            })}
            {generateTestRow("Upload Chara Slot Info[0]", async () => {

                client.current!.uploadVoiceCharacterFile(0, "GPT-SoVITS", "chara_0", null, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {generateTestRow("Upload Chara Slot Info[1]", async () => {
                const zipFile = await fileSelector("");
                // const synthesizer_path = await fileSelector("");

                client.current!.uploadVoiceCharacterFile(1, "GPT-SoVITS", "chara_1", zipFile, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {generateTestRow("Delete Chara Slot Info[0]", async () => {
                const slot = await client.current!.getVoiceCharacterSlotInfo(0);
                Logger.getLogger().info(slot);
                await client.current!.deleteVoiceCharacterSlotInfo(0);
                const slot2 = await client.current!.getVoiceCharacterSlotInfo(0);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Delete Chara Slot Info[1]", async () => {
                const slot = await client.current!.getVoiceCharacterSlotInfo(1);
                Logger.getLogger().info(slot);
                await client.current!.deleteVoiceCharacterSlotInfo(1);
                const slot2 = await client.current!.getVoiceCharacterSlotInfo(1);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Update Chara Slot Info[0]", async () => {
                const slot = await client.current!.getVoiceCharacterSlotInfo(0);
                Logger.getLogger().info(slot);
                slot.name = "aaaaaaaaaaa";
                slot.description = "bbbbbbbbbbbb";
                await client.current!.updateServerSlotInfo(slot);
                const slot2 = await client.current!.getServerSlotInfo(0);
                Logger.getLogger().info(slot2);
            })}
            {generateTestRow("Move Chara Slot[0->1]", async () => {
                const moveParam: MoveModelParam = {
                    src: 0,
                    dst: 1,
                };
                await client.current!.moveVoiceCharacter(moveParam);
            })}
            {generateTestRow("Set Icon file Chara Slot[1]", async () => {
                const file = await fileSelector("");
                client.current!.uploadVoiceCharacterIconFile(1, file, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}

            {generateTestRow("add ref voice slot[0]", async () => {
                const file = await fileSelector("");
                client.current!.addReferenceVoice(0, 0, "anger", file, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {generateTestRow("del ref voice chara slot[0], ref voice [0]", async () => {
                client.current!.deleteReferenceVoice(0, 0);
            })}
            {generateTestRow("mov ref voice chara slot[0], ref voice [0]-[1]", async () => {
                client.current!.moveReferenceVoice(0, {
                    src: 0,
                    dst: 1
                })
            })}

            {generateTestRow("update ref voice chara slot[0], ref voice [0]", async () => {
                const slot = await client.current!.getVoiceCharacterSlotInfo(0);
                const referenceVoice = slot.reference_voices.filter(x => x.slot_index == 0)[0]
                referenceVoice.voice_type = "hiohoh"
                referenceVoice.text = "hiohoh"
                referenceVoice.language = "all_ja"

                await client.current!.updateReferenceVoice(0, 0, referenceVoice);

            })}

            {generateTestRow("Set Icon file  voice chara slot[0], ref voice [0]", async () => {
                const file = await fileSelector("");
                client.current!.uploadReferenceVoiceIconFile(0, 0, file, (progress: number, end: boolean) => {
                    Logger.getLogger().info(`file upload progress: ${progress}, end: ${end}`);
                });
            })}
            {/* {generateInputAudioDeviceSelect()}
            {generateOutputAudioDeviceSelect()}
            {generateTestRow("start vc", async () => {
                Logger.getLogger().info(`${inputAudioDevice}, ${outputAudioDevice}`);
                const setting = vcclient.current!.getClientSetting();
                setting.voiceChangerClientSetting.audioInput = inputAudioDevice;
                vcclient.current!.updateClientSetting(setting);
                vcclient.current!.start();
                vcclient.current!.startInputRecording();
                // vcclient.current!.startOutputRecording();
                const audioElem = document.getElementById("audio-elem")! as HTMLAudioElement;
                audioElem.srcObject = vcclient.current!.stream;
                audioElem.play();
            })}
            <div>
                <audio id="audio-elem"></audio>
            </div>

            {generateTestRow("stop vc", async () => {
                vcclient.current!.stop();
                const data = vcclient.current!.stopInputRecording();
                // const data = vcclient.current!.stopOutputRecording();
                downloadAsWav(data);
            })}

            {generateTestRow("start vc rec", async () => {
                const res = await client.current!.startRecording();
            })}
            {generateTestRow("stop vc rec", async () => {
                const res = await client.current!.stopRecording();
            })}

            {generateTestRow("Initialize Server", async () => {
                const res = await client.current!.initializeServer();
            })}


 */}
        </div>
    );
};

// const downloadRecord = (data: Float32Array) => {
//     const writeString = (view: DataView, offset: number, string: string) => {
//         for (var i = 0; i < string.length; i++) {
//             view.setUint8(offset + i, string.charCodeAt(i));
//         }
//     };

//     const floatTo16BitPCM = (output: DataView, offset: number, input: Float32Array) => {
//         for (var i = 0; i < input.length; i++, offset += 2) {
//             var s = Math.max(-1, Math.min(1, input[i]));
//             output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
//         }
//     };

//     const buffer = new ArrayBuffer(44 + data.length * 2);
//     const view = new DataView(buffer);

//     // https://www.youfit.co.jp/archives/1418
//     writeString(view, 0, "RIFF"); // RIFFヘッダ
//     view.setUint32(4, 32 + data.length * 2, true); // これ以降のファイルサイズ
//     writeString(view, 8, "WAVE"); // WAVEヘッダ
//     writeString(view, 12, "fmt "); // fmtチャンク
//     view.setUint32(16, 16, true); // fmtチャンクのバイト数
//     view.setUint16(20, 1, true); // フォーマットID
//     view.setUint16(22, 1, true); // チャンネル数
//     view.setUint32(24, 48000, true); // サンプリングレート
//     view.setUint32(28, 48000 * 2, true); // データ速度
//     view.setUint16(32, 2, true); // ブロックサイズ
//     view.setUint16(34, 16, true); // サンプルあたりのビット数
//     writeString(view, 36, "data"); // dataチャンク
//     view.setUint32(40, data.length * 2, true); // 波形データのバイト数
//     floatTo16BitPCM(view, 44, data); // 波形データ
//     const audioBlob = new Blob([view], { type: "audio/wav" });

//     const url = URL.createObjectURL(audioBlob);
//     const a = document.createElement("a");
//     a.href = url;
//     a.download = `output.wav`;
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
//     URL.revokeObjectURL(url);
// };
