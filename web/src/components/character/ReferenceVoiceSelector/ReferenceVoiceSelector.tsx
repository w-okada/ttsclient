import { useMemo, useCallback } from "react";
import { useUIStore } from "@/stores/uiStore";
import { Button } from "@/components/common/Button/Button";
import { EMOTION_COLORS } from "@/types";
import type { VoiceCharacter } from "@/types";
import styles from "./ReferenceVoiceSelector.module.css";

type Props = {
  voiceCharacter: VoiceCharacter;
};

const GRID_COLS = 25;
const GRID_ROWS = 4;

export const ReferenceVoiceSelector = ({ voiceCharacter }: Props) => {
  const currentVoiceIndexes = useUIStore((s) => s.currentVoiceIndexes);
  const setCurrentVoiceIndexes = useUIStore((s) => s.setCurrentVoiceIndexes);
  const toggleVoiceIndex = useUIStore((s) => s.toggleVoiceIndex);
  const { reference_voices, emotion_types } = voiceCharacter;

  const voiceColorMap = useMemo(() => {
    const map = new Map<number, string>();
    reference_voices.forEach((v) => {
      const emotionIndex = emotion_types.findIndex((e) => e.name === v.voice_type);
      if (emotionIndex >= 0) {
        map.set(v.slot_index, emotion_types[emotionIndex].color);
      } else {
        const colorIndex = emotion_types.length > 0 ? emotion_types.length : 0;
        map.set(v.slot_index, EMOTION_COLORS[colorIndex % EMOTION_COLORS.length]);
      }
    });
    return map;
  }, [reference_voices, emotion_types]);

  const occupiedIndexes = useMemo(
    () => new Set(reference_voices.map((v) => v.slot_index)),
    [reference_voices],
  );

  const handleCellClick = useCallback(
    (index: number, ctrlKey: boolean) => {
      if (!occupiedIndexes.has(index)) return;
      if (ctrlKey) {
        toggleVoiceIndex(index);
      } else {
        setCurrentVoiceIndexes([index]);
      }
    },
    [occupiedIndexes, toggleVoiceIndex, setCurrentVoiceIndexes],
  );

  const handleEmotionFilter = useCallback(
    (emotionName: string) => {
      const indexes = reference_voices
        .filter((v) => v.voice_type === emotionName)
        .map((v) => v.slot_index);
      setCurrentVoiceIndexes(indexes);
    },
    [reference_voices, setCurrentVoiceIndexes],
  );

  const cells = useMemo(() => {
    const result = [];
    for (let i = 0; i < GRID_ROWS * GRID_COLS; i++) {
      const occupied = occupiedIndexes.has(i);
      const selected = currentVoiceIndexes.includes(i);
      const color = voiceColorMap.get(i);
      result.push({ index: i, occupied, selected, color });
    }
    return result;
  }, [occupiedIndexes, currentVoiceIndexes, voiceColorMap]);

  return (
    <div className={styles.container}>
      {emotion_types.length > 0 && (
        <div className={styles.emotionButtons}>
          {emotion_types.map((e) => (
            <Button
              key={e.name}
              variant="icon"
              className={styles.emotionBtn}
              style={{ backgroundColor: e.color }}
              onClick={() => handleEmotionFilter(e.name)}
              title={e.name}
            >
              {e.name}
            </Button>
          ))}
        </div>
      )}
      <div className={styles.grid} style={{ gridTemplateColumns: `repeat(${GRID_COLS}, 1fr)` }}>
        {cells.map((cell) => (
          <button
            key={cell.index}
            className={`${styles.cell} ${cell.occupied ? styles.occupied : ""} ${cell.selected ? styles.selected : ""}`}
            style={cell.color ? { backgroundColor: cell.color } : undefined}
            onClick={(e) => handleCellClick(cell.index, e.ctrlKey || e.metaKey)}
          />
        ))}
      </div>
    </div>
  );
};
