import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Dialog } from "./Dialog";
import { Button } from "@/components/common/Button/Button";
import { Select } from "@/components/common/Select/Select";
import { useUIStore } from "@/stores/uiStore";
import styles from "./SelectDialog.module.css";

type SelectOption = { value: string; label: string };

export const SelectDialog = () => {
  const { t } = useTranslation();
  const dialogProps = useUIStore((s) => s.dialogProps);
  const closeDialog = useUIStore((s) => s.closeDialog);

  const title = (dialogProps.title as string) ?? "";
  const message = (dialogProps.message as string) ?? "";
  const options = (dialogProps.options as SelectOption[]) ?? [];
  const onSelect = dialogProps.onSelect as ((value: string) => void) | undefined;

  const [value, setValue] = useState(options[0]?.value ?? "");

  const handleSubmit = () => {
    onSelect?.(value);
    closeDialog();
  };

  return (
    <Dialog title={title}>
      <p className={styles.message}>{message}</p>
      <Select options={options} value={value} onChange={(e) => setValue(e.target.value)} />
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
