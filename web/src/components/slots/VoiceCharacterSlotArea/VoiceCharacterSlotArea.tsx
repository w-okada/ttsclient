import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { FaSortNumericDown, FaSortAlphaDown } from "react-icons/fa";
import { SectionHeader } from "@/components/common/SectionHeader/SectionHeader";
import { Button } from "@/components/common/Button/Button";
import { SlotTile } from "@/components/slots/SlotTile/SlotTile";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import type { VoiceCharacter } from "@/types";
import styles from "./VoiceCharacterSlotArea.module.css";

const getIconUrl = (vc: VoiceCharacter): string | null => {
  if (!vc.icon_file) return null;
  return `/api/proxy/get?path=${encodeURIComponent(`voice_characters/${vc.slot_index}/${vc.icon_file}`)}`;
};

type SortMode = "index" | "name";

export const VoiceCharacterSlotArea = () => {
  const { t } = useTranslation();
  const voiceCharacters = useServerStore((s) => s.voiceCharacters);
  const currentVCIndex = useUIStore((s) => s.currentVCIndex);
  const setCurrentVCIndex = useUIStore((s) => s.setCurrentVCIndex);
  const openDialog = useUIStore((s) => s.openDialog);
  const [sortMode, setSortMode] = useState<SortMode>("index");

  const sortedVCs = useMemo(() => {
    const filtered = voiceCharacters.filter((vc) => vc.tts_type != null);
    if (sortMode === "name") {
      return [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    }
    return [...filtered].sort((a, b) => a.slot_index - b.slot_index);
  }, [voiceCharacters, sortMode]);

  return (
    <div className={styles.area}>
      <SectionHeader title={t("voice_character_slot_manager_main_title")}>
        <Button
          variant="icon"
          onClick={() => setSortMode(sortMode === "index" ? "name" : "index")}
          title={sortMode === "index" ? "Sort by name" : "Sort by index"}
        >
          {sortMode === "index" ? <FaSortNumericDown /> : <FaSortAlphaDown />}
        </Button>
        <Button variant="header" onClick={() => openDialog("voiceCharacterManager")}>
          {t("voice_character_slot_edit")}
        </Button>
      </SectionHeader>
      <div className={styles.tileContainer}>
        {sortedVCs.map((vc) => (
          <SlotTile
            key={vc.slot_index}
            index={vc.slot_index}
            name={vc.name}
            ttsType={vc.tts_type}
            iconUrl={getIconUrl(vc)}
            selected={vc.slot_index === currentVCIndex}
            onClick={() => setCurrentVCIndex(vc.slot_index)}
          />
        ))}
        {sortedVCs.length === 0 && (
          <div className={styles.empty}>{t("voice_character_slot_manager_main_blank_message")}</div>
        )}
      </div>
    </div>
  );
};
