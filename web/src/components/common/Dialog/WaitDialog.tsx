import { Dialog } from "./Dialog";
import { useUIStore } from "@/stores/uiStore";
import styles from "./WaitDialog.module.css";

export const WaitDialog = () => {
  const dialogProps = useUIStore((s) => s.dialogProps);

  const title = (dialogProps.title as string) ?? "";
  const message = (dialogProps.message as string) ?? "";

  return (
    <Dialog title={title}>
      <div className={styles.content}>
        <div className={styles.spinner} />
        <p className={styles.message}>{message}</p>
      </div>
    </Dialog>
  );
};
