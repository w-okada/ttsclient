import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Dialog } from "@/components/common/Dialog/Dialog";
import { Button } from "@/components/common/Button/Button";
import { Select } from "@/components/common/Select/Select";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import { TRANSCRIBER_MODEL_SIZES, TRANSCRIBER_DEVICES, TRANSCRIBER_COMPUTE_TYPES } from "@/types";
import type { TranscriberModelSize, TranscriberDevice, TranscriberComputeType } from "@/types";
import styles from "./AdvancedSettingDialog.module.css";

export const AdvancedSettingDialog = () => {
  const { t } = useTranslation();
  const configuration = useServerStore((s) => s.configuration);
  const gpuDevices = useServerStore((s) => s.gpuDevices);
  const updateConfiguration = useServerStore((s) => s.updateConfiguration);
  const closeDialog = useUIStore((s) => s.closeDialog);

  if (!configuration) return null;

  const modelSizeOptions = TRANSCRIBER_MODEL_SIZES.map((s) => ({ value: s, label: s }));
  const deviceOptions = TRANSCRIBER_DEVICES.map((d) => ({ value: d, label: d }));
  const computeTypeOptions = TRANSCRIBER_COMPUTE_TYPES.map((c) => ({ value: c, label: c }));
  const gpuOptions = gpuDevices.map((g) => ({
    value: String(g.device_id_int),
    label: `${g.name} (${g.device_id_int})`,
  }));

  const handleUpdate = async (field: string, value: string | number | boolean) => {
    try {
      await updateConfiguration({ ...configuration, [field]: value });
    } catch (e) {
      toast.error(`Update failed: ${e}`);
    }
  };

  return (
    <Dialog title={t("dialog_advanced_setting_title")}>
      <div className={styles.settings}>
        {gpuOptions.length > 0 && (
          <div className={styles.row}>
            <span className={styles.label}>GPU</span>
            <Select
              options={gpuOptions}
              value={String(configuration.gpu_device_id_int)}
              onChange={(e) => handleUpdate("gpu_device_id_int", Number(e.target.value))}
            />
          </div>
        )}

        <div className={styles.row}>
          <span className={styles.label}>{t("dialog_advanced_setting_enable_transcribe_audio")}</span>
          <div className={styles.toggleButtons}>
            <Button
              variant={configuration.transcribe_audio ? "primary" : "secondary"}
              onClick={() => handleUpdate("transcribe_audio", true)}
            >
              {t("dialog_advanced_setting_enable_transcribe_audio_yes")}
            </Button>
            <Button
              variant={!configuration.transcribe_audio ? "primary" : "secondary"}
              onClick={() => handleUpdate("transcribe_audio", false)}
            >
              {t("dialog_advanced_setting_enable_transcribe_audio_no")}
            </Button>
          </div>
        </div>

        <div className={styles.row}>
          <span className={styles.label}>{t("dialog_advanced_setting_enable_transcribe_audio_model_size")}</span>
          <Select
            options={modelSizeOptions}
            value={configuration.transcriber_model_size}
            onChange={(e) => handleUpdate("transcriber_model_size", e.target.value as TranscriberModelSize)}
          />
        </div>

        <div className={styles.row}>
          <span className={styles.label}>{t("dialog_advanced_setting_enable_transcribe_audio_device")}</span>
          <Select
            options={deviceOptions}
            value={configuration.transcriber_device}
            onChange={(e) => handleUpdate("transcriber_device", e.target.value as TranscriberDevice)}
          />
        </div>

        <div className={styles.row}>
          <span className={styles.label}>{t("dialog_advanced_setting_enable_transcribe_audio_compute_type")}</span>
          <Select
            options={computeTypeOptions}
            value={configuration.transcriber_compute_type}
            onChange={(e) => handleUpdate("transcriber_compute_type", e.target.value as TranscriberComputeType)}
          />
        </div>
      </div>

      <div className={styles.actions}>
        <Button variant="secondary" onClick={closeDialog}>
          {t("dialog_advanced_setting_button_close")}
        </Button>
      </div>
    </Dialog>
  );
};
