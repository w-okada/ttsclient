import type { ReactNode } from "react";
import styles from "./SectionHeader.module.css";

type Props = {
  title: string;
  children?: ReactNode;
};

export const SectionHeader = ({ title, children }: Props) => (
  <div className={styles.header}>
    <span className={styles.title}>{title}</span>
    {children && <div className={styles.actions}>{children}</div>}
  </div>
);
