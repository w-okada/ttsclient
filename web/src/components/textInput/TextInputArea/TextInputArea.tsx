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
import { useStreamingAudioPlayer } from "@/hooks/useStreamingAudioPlayer";
import * as api from "@/api/endpoints";
import { splitText } from "@/utils/textSplitter";
import type { LanguageType, CutMethod, GPTSoVITSSlotInfo } from "@/types";
import styles from "./TextInputArea.module.css";

export const TextInputArea = () => {
  const { t } = useTranslation();
  const slots = useServerStore((s) => s.slots);
  const currentVCIndex = useUIStore((s) => s.currentVCIndex);
  const currentSlotIndex = useUIStore((s) => s.currentSlotIndex);
  const currentVoiceIndexes = useUIStore((s) => s.currentVoiceIndexes);
  const openDialog = useUIStore((s) => s.openDialog);
  const outputDeviceId = useUIStore((s) => s.outputDeviceId);
  const monitorDeviceId = useUIStore((s) => s.monitorDeviceId);

  const [text, setText] = useState("");
  const [language, setLanguage] = useState<LanguageType>("all_ja");
  const [speed, setSpeed] = useState(1.0);
  const [cutMethod, setCutMethod] = useState<CutMethod>("Slice by every punct");
  const [silenceDuration, setSilenceDuration] = useState(200);
  const [maxTrim, setMaxTrim] = useState(500);
  const [generating, setGenerating] = useState(false);
  const [generationStartTime, setGenerationStartTime] = useState<number | null>(null);

  const silenceDurationSec = silenceDuration / 1000;
  const maxTrimSec = maxTrim / 1000;

  const streamingPlayer = useStreamingAudioPlayer({
    outputDeviceId,
    monitorDeviceId,
    silenceDuration: silenceDurationSec,
    maxTrim: maxTrimSec,
  });

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
    streamingPlayer.reset();
    openDialog("wait", {
      title: t("wait_dialog_title_generating"),
      message: t("wait_dialog_instruction_generating"),
    });

    try {
      const segments = splitText(text, cutMethod, language);
      const baseParam = {
        voice_character_slot_index: currentVCIndex,
        reference_voice_slot_index: currentVoiceIndexes[0],
        language,
        speed,
        cutMethod: null as CutMethod | null,
        sample_steps: null as number | null,
        phone_symbols: null as string[] | null,
      };

      // Phase 1: セグメント0を即時送信
      const firstResult = await api.generateVoice({
        ...baseParam,
        text: segments[0],
        deadline: Date.now() / 1000,
      });
      streamingPlayer.pushSegment(firstResult.blob);

      const firstDuration = parseFloat(firstResult.headers.get("X-Audio-Duration") ?? "0");

      // Phase 2: 残りを並行送信 (deadline付き)
      if (segments.length > 1) {
        const firstCharCount = segments[0].length;
        const durationPerChar = firstCharCount > 0 ? firstDuration / firstCharCount : 0;

        let cumulativeDuration = firstDuration;
        const now = Date.now() / 1000;

        const promises = segments.slice(1).map((segment, i) => {
          const deadline = now + cumulativeDuration;
          cumulativeDuration += durationPerChar * segment.length;
          return api.generateVoice({
            ...baseParam,
            text: segment,
            deadline,
          }).then((result) => ({ index: i, result }));
        });

        const results = await Promise.all(promises);
        // 順番通りに push
        results
          .sort((a, b) => a.index - b.index)
          .forEach(({ result }) => streamingPlayer.pushSegment(result.blob));
      }

      streamingPlayer.finish();
    } catch (e) {
      toast.error(`Generation failed: ${e}`);
    } finally {
      setGenerating(false);
      const { closeDialog } = useUIStore.getState();
      closeDialog();
    }
  }, [currentVCIndex, currentVoiceIndexes, text, language, speed, cutMethod, openDialog, t, streamingPlayer]);

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
            silenceDuration={silenceDuration}
            maxTrim={maxTrim}
            onLanguageChange={setLanguage}
            onSpeedChange={setSpeed}
            onCutMethodChange={setCutMethod}
            onSilenceDurationChange={setSilenceDuration}
            onMaxTrimChange={setMaxTrim}
          />
          <Button variant="primary" onClick={handleGenerate} disabled={generating || !text.trim()}>
            {t("text_input_area_submit_button")}
          </Button>
        </div>
        <div className={styles.right}>
          {gptSlot && <ModelSettings slot={gptSlot} />}
          <OutputArea
            blob={streamingPlayer.mergedBlob}
            isStreaming={streamingPlayer.isPlaying}
            startTime={generationStartTime}
          />
        </div>
      </div>
    </div>
  );
};
