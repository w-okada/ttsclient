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
  const loadAll = useServerStore((s) => s.loadAll);

  const handleInitialize = async () => {
    openDialog("confirm", {
      title: t("header_initialize_confirm_dialog_title"),
      message: t("header_initialize_confirm_dialog_instruction"),
      onConfirm: async () => {
        try {
          await api.initialize();
          await loadAll();
          toast.success("Initialized");
        } catch (e) {
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
