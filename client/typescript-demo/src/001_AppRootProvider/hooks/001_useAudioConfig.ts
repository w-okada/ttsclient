import { useEffect, useRef, useState } from "react";
import { Logger } from "../../util/logger";
import { t } from "i18next";

export type AudioConfigState = {
    audioContext: AudioContext | null;
    audioInputs: MediaDeviceInfo[];
    audioOutputs: MediaDeviceInfo[];
};
export type AudioConfigStateAndMethods = AudioConfigState & {
    reloadDeviceInfo: () => Promise<void>;
};

export type UseAudioConfigProps = {
    createAudioContextDelay: number;
};

// ブラウザのオーディオ基本情報。
export const useAudioConfig = (props: UseAudioConfigProps): AudioConfigStateAndMethods => {
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
    const [audioInputs, setAudioInputs] = useState<MediaDeviceInfo[]>([]);
    const [audioOutputs, setAudioOutputs] = useState<MediaDeviceInfo[]>([]);

    const audioContextCreated = useRef<boolean>(false);

    useEffect(() => {
        const createAudioContext = () => {
            if (audioContextCreated.current == true) {
                return;
            }
            audioContextCreated.current = true;

            const url = new URL(window.location.href);
            const params = url.searchParams;
            const sampleRate = params.get("sample_rate") || null;
            let ctx: AudioContext;
            if (sampleRate) {
                if (sampleRate == "default") {
                    Logger.getLogger().info(`Sample rate: default`);
                    ctx = new AudioContext();
                } else {
                    Logger.getLogger().info(`Sample rate: ${sampleRate}`);
                    ctx = new AudioContext({ sampleRate: Number(sampleRate) });
                }
            } else {
                Logger.getLogger().info(`Sample rate: default(48000)`);
                ctx = new AudioContext({ sampleRate: 48000 });
            }

            Logger.getLogger().info(ctx);
            setAudioContext(ctx);

            document.removeEventListener("touchstart", delayedCreateAudioContext);
            document.removeEventListener("mousedown", delayedCreateAudioContext);
            // document.removeEventListener("touchstart", createAudioContext);
            // document.removeEventListener("mousedown", createAudioContext);
        };
        const delayedCreateAudioContext = () => {
            setTimeout(() => {
                createAudioContext();
            }, props.createAudioContextDelay);
        };
        document.addEventListener("touchstart", delayedCreateAudioContext, false);
        document.addEventListener("mousedown", delayedCreateAudioContext, false);
        // document.addEventListener("touchstart", createAudioContext, false);
        // document.addEventListener("mousedown", createAudioContext, false);
    }, []);

    useEffect(() => {
        if (audioContext == null) {
            return;
        }
        reloadDeviceInfo();
    }, [audioContext]);

    const reloadDeviceInfo = async () => {
        if (audioContext === null) {
            return;
        }
        // デバイスチェックの空振り
        try {
            const ms = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
            ms.getTracks().forEach((x) => {
                x.stop();
            });
        } catch (e) {
            console.warn("Enumerate device error::", e);
        }
        const mediaDeviceInfos = await navigator.mediaDevices.enumerateDevices();

        const newAudioInputs = mediaDeviceInfos.filter((x) => {
            return x.kind == "audioinput";
        });
        newAudioInputs.push({
            deviceId: "none",
            groupId: "none",
            kind: "audioinput",
            label: "none",
            toJSON: () => {},
        });
        newAudioInputs.push({
            deviceId: "file",
            groupId: "file",
            kind: "audioinput",
            label: "file",
            toJSON: () => {},
        });
        newAudioInputs.push({
            deviceId: "screen",
            groupId: "screen",
            kind: "audioinput",
            label: "system(only win)",
            toJSON: () => {},
        });
        setAudioInputs(newAudioInputs);

        const newAudioOutputs = mediaDeviceInfos.filter((x) => {
            return x.kind == "audiooutput";
        });
        newAudioOutputs.push({
            deviceId: "none",
            groupId: "none",
            kind: "audiooutput",
            label: "none",
            toJSON: () => {},
        });
        setAudioOutputs(newAudioOutputs);
    };

    const ret: AudioConfigStateAndMethods = {
        audioContext,
        audioInputs,
        audioOutputs,
        reloadDeviceInfo,
    };

    return ret;
};
