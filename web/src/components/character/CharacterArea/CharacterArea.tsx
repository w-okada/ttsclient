import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import { Portrait } from "@/components/character/Portrait/Portrait";
import { CharacterControl } from "@/components/character/CharacterControl/CharacterControl";
import styles from "./CharacterArea.module.css";

export const CharacterArea = () => {
  const voiceCharacters = useServerStore((s) => s.voiceCharacters);
  const currentVCIndex = useUIStore((s) => s.currentVCIndex);

  const currentVC = voiceCharacters.find((vc) => vc.slot_index === currentVCIndex);

  if (!currentVC) return null;

  return (
    <div className={styles.area}>
      <Portrait voiceCharacter={currentVC} />
      <CharacterControl voiceCharacter={currentVC} />
    </div>
  );
};
