import { useTranslation } from "react-i18next";
import { Dialog } from "./Dialog";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import styles from "./ConfirmDialog.module.css";

export const ConfirmDialog = () => {
  const { t } = useTranslation();
  const dialogProps = useUIStore((s) => s.dialogProps);
  const closeDialog = useUIStore((s) => s.closeDialog);

  const title = (dialogProps.title as string) ?? "";
  const message = (dialogProps.message as string) ?? "";
  const onConfirm = dialogProps.onConfirm as (() => void) | undefined;

  const handleConfirm = () => {
    onConfirm?.();
    closeDialog();
  };

  return (
    <Dialog title={title}>
      <p className={styles.message}>{message}</p>
      <div className={styles.actions}>
        <Button variant="primary" onClick={handleConfirm}>
          {t("dialog_ok")}
        </Button>
        <Button variant="secondary" onClick={closeDialog}>
          {t("dialog_close")}
        </Button>
      </div>
    </Dialog>
  );
};
