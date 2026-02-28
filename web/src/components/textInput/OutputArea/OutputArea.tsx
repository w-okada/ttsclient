import { useEffect, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { FaDownload } from "react-icons/fa";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import styles from "./OutputArea.module.css";

type AudioElementWithSinkId = HTMLAudioElement & { setSinkId?: (id: string) => Promise<void> };

const applySinkId = async (audio: AudioElementWithSinkId, deviceId: string) => {
  if (!deviceId || !audio.setSinkId) return;
  try {
    await audio.setSinkId(deviceId);
  } catch {
    // setSinkId is not supported in all browsers
  }
};

type Props = {
  blob: Blob | null;
};

export const OutputArea = ({ blob }: Props) => {
  const { t } = useTranslation();
  const outputDeviceId = useUIStore((s) => s.outputDeviceId);
  const monitorDeviceId = useUIStore((s) => s.monitorDeviceId);
  const audioRef = useRef<HTMLAudioElement>(null);
  const monitorRef = useRef<HTMLAudioElement>(null);
  const urlRef = useRef<string | null>(null);

  // Apply setSinkId when outputDeviceId changes
  useEffect(() => {
    if (audioRef.current) applySinkId(audioRef.current as AudioElementWithSinkId, outputDeviceId);
  }, [outputDeviceId]);

  // Apply setSinkId when monitorDeviceId changes
  useEffect(() => {
    if (monitorRef.current)
      applySinkId(monitorRef.current as AudioElementWithSinkId, monitorDeviceId);
  }, [monitorDeviceId]);

  useEffect(() => {
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    if (blob) {
      const url = URL.createObjectURL(blob);
      urlRef.current = url;
      if (audioRef.current) {
        applySinkId(audioRef.current as AudioElementWithSinkId, outputDeviceId);
        audioRef.current.src = url;
        audioRef.current.play();
      }
      if (monitorDeviceId && monitorRef.current) {
        applySinkId(monitorRef.current as AudioElementWithSinkId, monitorDeviceId);
        monitorRef.current.src = url;
        monitorRef.current.play();
      }
    }
    return () => {
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    };
  }, [blob]);

  const handleDownload = useCallback(() => {
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `generated_${Date.now()}.wav`;
    a.click();
    URL.revokeObjectURL(url);
  }, [blob]);

  return (
    <div className={styles.output}>
      <span className={styles.label}>{t("text_input_area_generated_voice_label")}</span>
      <audio ref={audioRef} controls className={styles.audio} />
      {monitorDeviceId && <audio ref={monitorRef} style={{ display: "none" }} />}
      <Button variant="icon" onClick={handleDownload} disabled={!blob}>
        <FaDownload />
      </Button>
    </div>
  );
};
