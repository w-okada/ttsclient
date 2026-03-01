import { useState, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { SectionHeader } from "@/components/common/SectionHeader/SectionHeader";
import { Button } from "@/components/common/Button/Button";
import { CommonSettings } from "@/components/textInput/CommonSettings/CommonSettings";
import { ModelSettings } from "@/components/textInput/ModelSettings/ModelSettings";
import { OutputArea } from "@/components/textInput/OutputArea/OutputArea";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import * as api from "@/api/endpoints";
import type { LanguageType, CutMethod, GPTSoVITSSlotInfo } from "@/types";
import styles from "./TextInputArea.module.css";

export const TextInputArea = () => {
  const { t } = useTranslation();
  const slots = useServerStore((s) => s.slots);
  const currentVCIndex = useUIStore((s) => s.currentVCIndex);
  const currentSlotIndex = useUIStore((s) => s.currentSlotIndex);
  const currentVoiceIndexes = useUIStore((s) => s.currentVoiceIndexes);
  const openDialog = useUIStore((s) => s.openDialog);

  const [text, setText] = useState("");
  const [language, setLanguage] = useState<LanguageType>("all_ja");
  const [speed, setSpeed] = useState(1.0);
  const [cutMethod, setCutMethod] = useState<CutMethod>("No slice");
  const [generatedBlob, setGeneratedBlob] = useState<Blob | null>(null);
  const [generating, setGenerating] = useState(false);
  const [generationStartTime, setGenerationStartTime] = useState<number | null>(null);

  const currentSlot = slots.find((s) => s.slot_index === currentSlotIndex);
  const isGPTSoVITS = currentSlot?.tts_type === "GPT-SoVITS";
  const gptSlot = isGPTSoVITS ? (currentSlot as GPTSoVITSSlotInfo) : null;

  const handleGenerate = useCallback(async () => {
    if (currentVCIndex < 0 || currentVoiceIndexes.length === 0) {
      toast.warning(t("reference_voice_area_no_selection"));
      return;
    }
    if (!text.trim()) return;

    setGenerationStartTime(performance.now());
    setGenerating(true);
    openDialog("wait", {
      title: t("wait_dialog_title_generating"),
      message: t("wait_dialog_instruction_generating"),
    });

    try {
      const blob = await api.generateVoice({
        voice_character_slot_index: currentVCIndex,
        reference_voice_slot_index: currentVoiceIndexes[0],
        text,
        language,
        speed,
        cutMethod,
        sample_steps: null,
        phone_symbols: null,
      });
      setGeneratedBlob(blob);
    } catch (e) {
      toast.error(`Generation failed: ${e}`);
    } finally {
      setGenerating(false);
      const { closeDialog } = useUIStore.getState();
      closeDialog();
    }
  }, [currentVCIndex, currentVoiceIndexes, text, language, speed, cutMethod, openDialog, t]);

  return (
    <div className={styles.area}>
      <SectionHeader title={t("text_input_area_title")} />
      <div className={styles.content}>
        <div className={styles.left}>
          <textarea
            className={styles.textarea}
            placeholder={t("text_input_area_textarea-label")}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <CommonSettings
            language={language}
            speed={speed}
            cutMethod={cutMethod}
            onLanguageChange={setLanguage}
            onSpeedChange={setSpeed}
            onCutMethodChange={setCutMethod}
          />
          <Button variant="primary" onClick={handleGenerate} disabled={generating || !text.trim()}>
            {t("text_input_area_submit_button")}
          </Button>
        </div>
        <div className={styles.right}>
          {gptSlot && <ModelSettings slot={gptSlot} />}
          <OutputArea blob={generatedBlob} startTime={generationStartTime} />
        </div>
      </div>
    </div>
  );
};
