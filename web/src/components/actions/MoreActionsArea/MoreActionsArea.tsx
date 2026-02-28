import { useTranslation } from "react-i18next";
import { SectionHeader } from "@/components/common/SectionHeader/SectionHeader";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import styles from "./MoreActionsArea.module.css";

export const MoreActionsArea = () => {
  const { t } = useTranslation();
  const openDialog = useUIStore((s) => s.openDialog);

  return (
    <div className={styles.area}>
      <SectionHeader title={t("config_area_more_actions_area_title")} />
      <div className={styles.buttons}>
        <Button variant="secondary" onClick={() => openDialog("advancedSetting")}>
          {t("config_area_more_actions_area_advanced_setting")}
        </Button>
        <Button variant="secondary" onClick={() => window.open("/api/operation/log", "_blank")}>
          {t("config_area_more_actions_area_open_log_viewer")}
        </Button>
      </div>
    </div>
  );
};
