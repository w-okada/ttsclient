import { useState, type ReactNode } from "react";
import styles from "./Tooltip.module.css";

type Props = {
  text: string;
  children: ReactNode;
};

export const Tooltip = ({ text, children }: Props) => {
  const [visible, setVisible] = useState(false);

  return (
    <div
      className={styles.wrapper}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && <div className={styles.tooltip}>{text}</div>}
    </div>
  );
};
