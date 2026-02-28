import { useState, useEffect } from "react";

export type AudioDeviceInfo = {
  deviceId: string;
  label: string;
  kind: MediaDeviceKind;
};

export const useAudioDevices = () => {
  const [devices, setDevices] = useState<AudioDeviceInfo[]>([]);

  useEffect(() => {
    const enumerate = async () => {
      try {
        // Request microphone permission first so that device labels are available
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach((t) => t.stop());

        const mediaDevices = await navigator.mediaDevices.enumerateDevices();
        setDevices(
          mediaDevices
            .filter((d) => d.kind === "audiooutput" || d.kind === "audioinput")
            .map((d) => ({
              deviceId: d.deviceId,
              label: d.label || `${d.kind} (${d.deviceId.slice(0, 8)})`,
              kind: d.kind,
            })),
        );
      } catch {
        // Permission denied or not available
      }
    };
    enumerate();
    navigator.mediaDevices?.addEventListener("devicechange", enumerate);
    return () => {
      navigator.mediaDevices?.removeEventListener("devicechange", enumerate);
    };
  }, []);

  const outputDevices = devices.filter((d) => d.kind === "audiooutput");
  const inputDevices = devices.filter((d) => d.kind === "audioinput");

  return { outputDevices, inputDevices };
};
