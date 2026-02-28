import type { ReactNode } from "react";
import { useUIStore } from "@/stores/uiStore";
import styles from "./Dialog.module.css";

type Props = {
  title: string;
  children: ReactNode;
  onClose?: () => void;
  wide?: boolean;
};

export const Dialog = ({ title, children, onClose, wide }: Props) => {
  const closeDialog = useUIStore((s) => s.closeDialog);

  const handleClose = () => {
    onClose?.();
    closeDialog();
  };

  return (
    <div className={styles.overlay} onClick={handleClose}>
      <div
        className={`${styles.dialog} ${wide ? styles.wide : ""}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={styles.header}>
          <span className={styles.title}>{title}</span>
          <button className={styles.closeBtn} onClick={handleClose}>
            &times;
          </button>
        </div>
        <div className={styles.body}>{children}</div>
      </div>
    </div>
  );
};
