import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Dialog } from "./Dialog";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import styles from "./TextInputDialog.module.css";

export const TextInputDialog = () => {
  const { t } = useTranslation();
  const dialogProps = useUIStore((s) => s.dialogProps);
  const closeDialog = useUIStore((s) => s.closeDialog);

  const title = (dialogProps.title as string) ?? "";
  const message = (dialogProps.message as string) ?? "";
  const defaultValue = (dialogProps.defaultValue as string) ?? "";
  const onSubmit = dialogProps.onSubmit as ((value: string) => void) | undefined;

  const [value, setValue] = useState(defaultValue);

  const handleSubmit = () => {
    onSubmit?.(value);
    closeDialog();
  };

  return (
    <Dialog title={title}>
      <p className={styles.message}>{message}</p>
      <input
        className={styles.input}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        autoFocus
        onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
      />
      <div className={styles.actions}>
        <Button variant="primary" onClick={handleSubmit}>
          {t("dialog_ok")}
        </Button>
        <Button variant="secondary" onClick={closeDialog}>
          {t("dialog_close")}
        </Button>
      </div>
    </Dialog>
  );
};
