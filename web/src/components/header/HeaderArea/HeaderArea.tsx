import { useTranslation } from "react-i18next";
import { FaGithub, FaBook, FaSun, FaMoon } from "react-icons/fa";
import { toast } from "react-toastify";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import { useServerStore } from "@/stores/serverStore";
import * as api from "@/api/endpoints";
import styles from "./HeaderArea.module.css";

const GITHUB_URL = "https://github.com/w-okada/ttsclient";
const MANUAL_URL = "https://github.com/w-okada/ttsclient/wiki";

export const HeaderArea = () => {
  const { t, i18n } = useTranslation();
  const theme = useUIStore((s) => s.theme);
  const toggleTheme = useUIStore((s) => s.toggleTheme);
  const openDialog = useUIStore((s) => s.openDialog);
  const updateDialogProps = useUIStore((s) => s.updateDialogProps);
  const closeDialog = useUIStore((s) => s.closeDialog);
  const loadAll = useServerStore((s) => s.loadAll);

  const handleInitialize = async () => {
    openDialog("confirm", {
      title: t("header_initialize_confirm_dialog_title"),
      message: t("header_initialize_confirm_dialog_instruction"),
      onConfirm: async () => {
        try {
          await api.initialize();

          // モジュールダウンロード
          openDialog("progress", {
            title: t("header_initialize_downloading_modules"),
            message: "",
            progress: 0,
          });
          await api.downloadModulesSSE((statuses) => {
            const progress = statuses.reduce((sum, s) => sum + s.progress, 0) / statuses.length;
            const doneCount = statuses.filter((s) => s.status === "done").length;
            const errorCount = statuses.filter((s) => s.status === "error").length;
            const msg =
              errorCount > 0
                ? `${doneCount} / ${statuses.length} (${errorCount} errors)`
                : `${doneCount} / ${statuses.length}`;
            updateDialogProps({ progress, message: msg });
          });

          // 初期モデルダウンロード
          openDialog("progress", {
            title: t("header_initialize_downloading_models"),
            message: "",
            progress: 0,
          });
          await api.downloadModelsSSE((statuses) => {
            const progress = statuses.reduce((sum, s) => sum + s.progress, 0) / statuses.length;
            const doneCount = statuses.filter((s) => s.status === "done").length;
            const errorCount = statuses.filter((s) => s.status === "error").length;
            const msg =
              errorCount > 0
                ? `${doneCount} / ${statuses.length} (${errorCount} errors)`
                : `${doneCount} / ${statuses.length}`;
            updateDialogProps({ progress, message: msg });
          });

          closeDialog();
          await loadAll();
          toast.success(t("header_initialize_success"));
        } catch (e) {
          closeDialog();
          toast.error(`Initialize failed: ${e}`);
        }
      },
    });
  };

  const handleLanguageChange = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className={styles.header}>
      <div className={styles.titleArea}>
        <span className={styles.title}>TTSClient</span>
        <span className={styles.version}>v2</span>
      </div>
      <div className={styles.controls}>
        <Button
          variant="header"
          onClick={() => window.open(GITHUB_URL, "_blank")}
          title={t("header_github")}
        >
          <FaGithub />
        </Button>
        <Button
          variant="header"
          onClick={() => window.open(MANUAL_URL, "_blank")}
          title={t("header_manual")}
        >
          <FaBook />
        </Button>

        <select
          className={styles.langSelect}
          value={i18n.language}
          onChange={(e) => handleLanguageChange(e.target.value)}
        >
          <option value="ja">日本語</option>
          <option value="en">English</option>
        </select>

        <Button variant="header" onClick={handleInitialize}>
          {t("header_initialize")}
        </Button>

        <Button variant="header" onClick={toggleTheme} title={theme === "light" ? t("header_to_dark_label") : t("header_to_light_label")}>
          {theme === "light" ? <FaMoon /> : <FaSun />}
        </Button>
      </div>
    </div>
  );
};
