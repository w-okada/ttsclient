import { Dialog } from "./Dialog";
import { useUIStore } from "@/stores/uiStore";
import styles from "./ProgressDialog.module.css";

export const ProgressDialog = () => {
  const dialogProps = useUIStore((s) => s.dialogProps);

  const title = (dialogProps.title as string) ?? "";
  const message = (dialogProps.message as string) ?? "";
  const progress = (dialogProps.progress as number) ?? 0;

  return (
    <Dialog title={title}>
      <p className={styles.message}>{message}</p>
      <div className={styles.barOuter}>
        <div className={styles.barInner} style={{ width: `${Math.round(progress * 100)}%` }} />
      </div>
      <span className={styles.percent}>{Math.round(progress * 100)}%</span>
    </Dialog>
  );
};
