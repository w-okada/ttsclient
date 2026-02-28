import type { SelectHTMLAttributes } from "react";
import styles from "./Select.module.css";

type Option = {
  value: string;
  label: string;
};

type Props = SelectHTMLAttributes<HTMLSelectElement> & {
  options: Option[];
  label?: string;
};

export const Select = ({ options, label, className, ...rest }: Props) => (
  <label className={`${styles.wrapper} ${className ?? ""}`}>
    {label && <span className={styles.label}>{label}</span>}
    <select className={styles.select} {...rest}>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  </label>
);
