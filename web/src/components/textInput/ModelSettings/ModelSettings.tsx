import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { useServerStore } from "@/stores/serverStore";
import * as api from "@/api/endpoints";
import type { GPTSoVITSSlotInfo } from "@/types";
import styles from "./ModelSettings.module.css";

type Props = {
  slot: GPTSoVITSSlotInfo;
};

export const ModelSettings = ({ slot }: Props) => {
  const { t } = useTranslation();
  const reloadSlots = useServerStore((s) => s.reloadSlots);

  const handleChange = useCallback(
    async (field: keyof GPTSoVITSSlotInfo, value: number | boolean) => {
      try {
        await api.putSlot(slot.slot_index, { ...slot, [field]: value });
        await reloadSlots();
      } catch (e) {
        toast.error(`Update failed: ${e}`);
      }
    },
    [slot, reloadSlots],
  );

  return (
    <div className={styles.settings}>
      <span className={styles.title}>{t("text_input_area_model_setting_label")}</span>

      <label className={styles.row}>
        <span>{t("text_input_area_top_k_label")}</span>
        <input
          type="number"
          className={styles.input}
          value={slot.top_k}
          min={1}
          max={100}
          onChange={(e) => handleChange("top_k", Number(e.target.value))}
        />
      </label>

      <label className={styles.row}>
        <span>{t("text_input_area_top_p_label")}</span>
        <input
          type="number"
          className={styles.input}
          value={slot.top_p}
          min={0}
          max={1}
          step={0.05}
          onChange={(e) => handleChange("top_p", Number(e.target.value))}
        />
      </label>

      <label className={styles.row}>
        <span>{t("text_input_area_temperature_label")}</span>
        <input
          type="number"
          className={styles.input}
          value={slot.temperature}
          min={0}
          max={2}
          step={0.05}
          onChange={(e) => handleChange("temperature", Number(e.target.value))}
        />
      </label>

      {slot.enable_faster && (
        <>
          <label className={styles.row}>
            <span>{t("text_input_area_batch_size_label")}</span>
            <input
              type="number"
              className={styles.input}
              value={slot.batch_size}
              min={1}
              max={32}
              onChange={(e) => handleChange("batch_size", Number(e.target.value))}
            />
          </label>
          <label className={styles.row}>
            <span>Seed</span>
            <input
              type="number"
              className={styles.input}
              value={slot.seed}
              onChange={(e) => handleChange("seed", Number(e.target.value))}
            />
          </label>
        </>
      )}
    </div>
  );
};
