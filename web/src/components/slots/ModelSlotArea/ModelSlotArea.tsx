import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { FaSortNumericDown, FaSortAlphaDown } from "react-icons/fa";
import { SectionHeader } from "@/components/common/SectionHeader/SectionHeader";
import { Button } from "@/components/common/Button/Button";
import { SlotTile } from "@/components/slots/SlotTile/SlotTile";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import type { SlotInfoMember } from "@/types";
import styles from "./ModelSlotArea.module.css";

const getIconUrl = (slot: SlotInfoMember): string | null => {
  if (!slot.icon_file) return null;
  return `/get_proxy?path=${encodeURIComponent(slot.icon_file)}`;
};

type SortMode = "index" | "name";

export const ModelSlotArea = () => {
  const { t } = useTranslation();
  const slots = useServerStore((s) => s.slots);
  const currentSlotIndex = useUIStore((s) => s.currentSlotIndex);
  const setCurrentSlotIndex = useUIStore((s) => s.setCurrentSlotIndex);
  const openDialog = useUIStore((s) => s.openDialog);
  const [sortMode, setSortMode] = useState<SortMode>("index");

  const sortedSlots = useMemo(() => {
    const filtered = slots.filter((s) => s.tts_type != null);
    if (sortMode === "name") {
      return [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    }
    return [...filtered].sort((a, b) => a.slot_index - b.slot_index);
  }, [slots, sortMode]);

  return (
    <div className={styles.area}>
      <SectionHeader title={t("model_slot_manager_main_title")}>
        <Button
          variant="icon"
          onClick={() => setSortMode(sortMode === "index" ? "name" : "index")}
          title={sortMode === "index" ? "Sort by name" : "Sort by index"}
        >
          {sortMode === "index" ? <FaSortNumericDown /> : <FaSortAlphaDown />}
        </Button>
        <Button variant="header" onClick={() => openDialog("modelSlotManager")}>
          {t("model_slot_edit")}
        </Button>
      </SectionHeader>
      <div className={styles.tileContainer}>
        {sortedSlots.map((slot) => (
          <SlotTile
            key={slot.slot_index}
            index={slot.slot_index}
            name={slot.name}
            ttsType={slot.tts_type}
            iconUrl={getIconUrl(slot)}
            selected={slot.slot_index === currentSlotIndex}
            onClick={() => setCurrentSlotIndex(slot.slot_index)}
          />
        ))}
        {sortedSlots.length === 0 && (
          <div className={styles.empty}>{t("model_slot_manager_main_blank_message")}</div>
        )}
      </div>
    </div>
  );
};
