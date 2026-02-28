import { useTranslation } from "react-i18next";
import { Select } from "@/components/common/Select/Select";
import { LANGUAGE_TYPES, CUT_METHODS } from "@/types";
import type { LanguageType, CutMethod } from "@/types";
import styles from "./CommonSettings.module.css";

type Props = {
  language: LanguageType;
  speed: number;
  cutMethod: CutMethod;
  onLanguageChange: (v: LanguageType) => void;
  onSpeedChange: (v: number) => void;
  onCutMethodChange: (v: CutMethod) => void;
};

export const CommonSettings = ({
  language,
  speed,
  cutMethod,
  onLanguageChange,
  onSpeedChange,
  onCutMethodChange,
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
    </div>
  );
};
