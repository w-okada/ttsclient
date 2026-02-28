import type { ButtonHTMLAttributes, ReactNode } from "react";
import styles from "./Button.module.css";

type ButtonVariant = "primary" | "secondary" | "icon" | "header" | "slot";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  children: ReactNode;
};

export const Button = ({ variant = "secondary", className, children, ...rest }: Props) => (
  <button className={`${styles.button} ${styles[variant]} ${className ?? ""}`} {...rest}>
    {children}
  </button>
);
