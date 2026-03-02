import { useTranslation } from "react-i18next";
import { Select } from "@/components/common/Select/Select";
import { LANGUAGE_TYPES, CUT_METHODS } from "@/types";
import type { LanguageType, CutMethod } from "@/types";
import styles from "./CommonSettings.module.css";

type Props = {
  language: LanguageType;
  speed: number;
  cutMethod: CutMethod;
  silenceDuration: number;
  maxTrim: number;
  onLanguageChange: (v: LanguageType) => void;
  onSpeedChange: (v: number) => void;
  onCutMethodChange: (v: CutMethod) => void;
  onSilenceDurationChange: (v: number) => void;
  onMaxTrimChange: (v: number) => void;
};

export const CommonSettings = ({
  language,
  speed,
  cutMethod,
  silenceDuration,
  maxTrim,
  onLanguageChange,
  onSpeedChange,
  onCutMethodChange,
  onSilenceDurationChange,
  onMaxTrimChange,
}: Props) => {
  const { t } = useTranslation();

  const languageOptions = LANGUAGE_TYPES.map((l) => ({ value: l, label: l }));
  const cutMethodOptions = CUT_METHODS.map((m) => ({ value: m, label: m }));

  return (
    <div className={styles.settings}>
      <Select
        label={t("text_input_area_language_label")}
        options={languageOptions}
        value={language}
        onChange={(e) => onLanguageChange(e.target.value as LanguageType)}
      />
      <label className={styles.speedLabel}>
        <span>{t("text_input_area_speed_label")}</span>
        <input
          type="range"
          min="0.5"
          max="2.0"
          step="0.1"
          value={speed}
          onChange={(e) => onSpeedChange(Number(e.target.value))}
          className={styles.slider}
        />
        <span className={styles.speedValue}>{speed.toFixed(1)}</span>
      </label>
      <Select
        label={t("text_input_area_cut_method_label")}
        options={cutMethodOptions}
        value={cutMethod}
        onChange={(e) => onCutMethodChange(e.target.value as CutMethod)}
      />
      {cutMethod !== "No slice" && (
        <div className={styles.trimRow}>
          <label className={styles.trimLabel}>
            <span>{t("text_input_area_silence_duration_label")}</span>
            <input
              type="number"
              min="0"
              max="5000"
              step="50"
              value={silenceDuration}
              onChange={(e) => onSilenceDurationChange(Math.max(0, Number(e.target.value)))}
              className={styles.trimInput}
            />
            <span>ms</span>
          </label>
          <label className={styles.trimLabel}>
            <span>{t("text_input_area_max_trim_label")}</span>
            <input
              type="number"
              min="0"
              max="2000"
              step="50"
              value={maxTrim}
              onChange={(e) => onMaxTrimChange(Math.max(0, Number(e.target.value)))}
              className={styles.trimInput}
            />
            <span>ms</span>
          </label>
        </div>
      )}
    </div>
  );
};
