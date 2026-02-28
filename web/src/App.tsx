import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import { HeaderArea } from "@/components/header/HeaderArea/HeaderArea";
import { ModelSlotArea } from "@/components/slots/ModelSlotArea/ModelSlotArea";
import { VoiceCharacterSlotArea } from "@/components/slots/VoiceCharacterSlotArea/VoiceCharacterSlotArea";
import { CharacterArea } from "@/components/character/CharacterArea/CharacterArea";
import { TextInputArea } from "@/components/textInput/TextInputArea/TextInputArea";
import { DeviceSettingArea } from "@/components/device/DeviceSettingArea/DeviceSettingArea";
import { MoreActionsArea } from "@/components/actions/MoreActionsArea/MoreActionsArea";
import { DialogRoot } from "@/components/common/Dialog/DialogRoot";
import styles from "./App.module.css";

export const App = () => {
  const { ready } = useTranslation();
  const loadAll = useServerStore((s) => s.loadAll);
  const loading = useServerStore((s) => s.loading);
  const theme = useUIStore((s) => s.theme);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    loadAll().catch((e) => {
      setLoadError(true);
      toast.error(`Failed to load data: ${e}`);
    });
  }, [loadAll]);

  if (!ready) return null;

  return (
    <div className={styles.container}>
      <HeaderArea />
      {loading ? (
        <div className={styles.loading}>
          <div className={styles.spinner} />
          <span>Loading...</span>
        </div>
      ) : loadError ? (
        <div className={styles.error}>
          <p>Failed to connect to server.</p>
          <button className={styles.retryBtn} onClick={() => { setLoadError(false); loadAll().catch(() => setLoadError(true)); }}>
            Retry
          </button>
        </div>
      ) : (
        <>
          <ModelSlotArea />
          <VoiceCharacterSlotArea />
          <CharacterArea />
          <TextInputArea />
          <DeviceSettingArea />
          <MoreActionsArea />
        </>
      )}
      <DialogRoot />
    </div>
  );
};
