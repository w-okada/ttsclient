import { useTranslation } from "react-i18next";
import { ReferenceVoiceSelector } from "@/components/character/ReferenceVoiceSelector/ReferenceVoiceSelector";
import { ReferenceVoiceArea } from "@/components/character/ReferenceVoiceArea/ReferenceVoiceArea";
import type { VoiceCharacter } from "@/types";
import styles from "./CharacterControl.module.css";

type Props = {
  voiceCharacter: VoiceCharacter;
};

export const CharacterControl = ({ voiceCharacter }: Props) => {
  const { t } = useTranslation();

  return (
    <div className={styles.control}>
      <div className={styles.nameRow}>
        <span className={styles.label}>{t("character_area_control_name")}</span>
        <span className={styles.name}>{voiceCharacter.name}</span>
      </div>
      <ReferenceVoiceSelector voiceCharacter={voiceCharacter} />
      <ReferenceVoiceArea voiceCharacter={voiceCharacter} />
    </div>
  );
};
