import { useEffect, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { FaDownload } from "react-icons/fa";
import { Button } from "@/components/common/Button/Button";
import styles from "./OutputArea.module.css";

type Props = {
  blob: Blob | null;
};

export const OutputArea = ({ blob }: Props) => {
  const { t } = useTranslation();
  const audioRef = useRef<HTMLAudioElement>(null);
  const urlRef = useRef<string | null>(null);

  useEffect(() => {
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    if (blob) {
      const url = URL.createObjectURL(blob);
      urlRef.current = url;
      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.play();
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
      <Button variant="icon" onClick={handleDownload} disabled={!blob}>
        <FaDownload />
      </Button>
    </div>
  );
};
