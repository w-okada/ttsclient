import { useState } from "react";
import { useTranslation } from "react-i18next";
import { SectionHeader } from "@/components/common/SectionHeader/SectionHeader";
import { Select } from "@/components/common/Select/Select";
import { useServerStore } from "@/stores/serverStore";
import { useAudioDevices } from "@/hooks/useAudioDevices";
import styles from "./DeviceSettingArea.module.css";

export const DeviceSettingArea = () => {
  const { t } = useTranslation();
  const gpuDevices = useServerStore((s) => s.gpuDevices);
  const configuration = useServerStore((s) => s.configuration);
  const updateConfiguration = useServerStore((s) => s.updateConfiguration);
  const { outputDevices, inputDevices } = useAudioDevices();

  const [outputDeviceId, setOutputDeviceId] = useState("");
  const [monitorDeviceId, setMonitorDeviceId] = useState("");
  const [inputDeviceId, setInputDeviceId] = useState("");

  const gpuOptions = gpuDevices.map((g) => ({
    value: String(g.device_id_int),
    label: `${g.name} (${g.device_id_int})`,
  }));

  const outputOptions = outputDevices.map((d) => ({ value: d.deviceId, label: d.label }));
  const inputOptions = inputDevices.map((d) => ({ value: d.deviceId, label: d.label }));

  const handleGPUChange = async (value: string) => {
    if (!configuration) return;
    await updateConfiguration({ ...configuration, gpu_device_id_int: Number(value) });
  };

  return (
    <div className={styles.area}>
      <SectionHeader title={t("configuration_area_title")} />
      <div className={styles.grid}>
        {gpuOptions.length > 0 && (
          <Select
            label={t("config_area_gpu")}
            options={gpuOptions}
            value={String(configuration?.gpu_device_id_int ?? -1)}
            onChange={(e) => handleGPUChange(e.target.value)}
          />
        )}
        <Select
          label={t("config_area_audio_device_output")}
          options={outputOptions}
          value={outputDeviceId}
          onChange={(e) => setOutputDeviceId(e.target.value)}
        />
        <Select
          label={t("config_area_audio_device_monitor")}
          options={outputOptions}
          value={monitorDeviceId}
          onChange={(e) => setMonitorDeviceId(e.target.value)}
        />
        <Select
          label={t("config_area_audio_device_input")}
          options={inputOptions}
          value={inputDeviceId}
          onChange={(e) => setInputDeviceId(e.target.value)}
        />
      </div>
    </div>
  );
};
