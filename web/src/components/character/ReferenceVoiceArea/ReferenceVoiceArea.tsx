import { useState, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { FaPlay, FaStop } from "react-icons/fa";
import { Button } from "@/components/common/Button/Button";
import { Select } from "@/components/common/Select/Select";
import { useUIStore } from "@/stores/uiStore";
import { useServerStore } from "@/stores/serverStore";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";
import * as api from "@/api/endpoints";
import { uploadFile } from "@/api/fileUploader";
import type { VoiceCharacter, ReferenceVoice, LanguageType } from "@/types";
import { LANGUAGE_TYPES } from "@/types";
import styles from "./ReferenceVoiceArea.module.css";

type Props = {
  voiceCharacter: VoiceCharacter;
};

export const ReferenceVoiceArea = ({ voiceCharacter }: Props) => {
  const { t } = useTranslation();
  const currentVoiceIndexes = useUIStore((s) => s.currentVoiceIndexes);
  const reloadVoiceCharacters = useServerStore((s) => s.reloadVoiceCharacters);
  const [editMode, setEditMode] = useState(false);
  const [editText, setEditText] = useState("");
  const [editVoiceType, setEditVoiceType] = useState("");
  const [editLanguage, setEditLanguage] = useState<LanguageType>("all_ja");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { isPlaying, playUrl, stop } = useAudioPlayer();

  const selectedVoice: ReferenceVoice | null =
    currentVoiceIndexes.length === 1
      ? voiceCharacter.reference_voices.find((v) => v.slot_index === currentVoiceIndexes[0]) ?? null
      : null;

  const handlePlay = useCallback(() => {
    if (!selectedVoice) return;
    if (isPlaying) {
      stop();
      return;
    }
    const url = `/api/proxy/get?path=${encodeURIComponent(`voice_characters/${voiceCharacter.slot_index}/${selectedVoice.wav_file}`)}`;
    playUrl(url);
  }, [selectedVoice, isPlaying, stop, playUrl]);

  const handleEdit = useCallback(() => {
    if (!selectedVoice) return;
    setEditText(selectedVoice.text);
    setEditVoiceType(selectedVoice.voice_type);
    setEditLanguage(selectedVoice.language);
    setEditMode(true);
  }, [selectedVoice]);

  const handleSave = useCallback(async () => {
    if (!selectedVoice) return;
    try {
      await api.putReferenceVoice(voiceCharacter.slot_index, selectedVoice.slot_index, {
        ...selectedVoice,
        text: editText,
        voice_type: editVoiceType,
        language: editLanguage,
      });
      await reloadVoiceCharacters();
      setEditMode(false);
      toast.success("Saved");
    } catch (e) {
      toast.error(`Save failed: ${e}`);
    }
  }, [selectedVoice, voiceCharacter.slot_index, editText, editVoiceType, editLanguage, reloadVoiceCharacters]);

  const handleDelete = useCallback(async () => {
    if (!selectedVoice) return;
    try {
      await api.deleteReferenceVoice(voiceCharacter.slot_index, selectedVoice.slot_index);
      await reloadVoiceCharacters();
      toast.success("Deleted");
    } catch (e) {
      toast.error(`Delete failed: ${e}`);
    }
  }, [selectedVoice, voiceCharacter.slot_index, reloadVoiceCharacters]);

  const handleFileUpload = useCallback(
    async (file: File) => {
      try {
        const uploadedPath = await uploadFile(file);
        await api.postReferenceVoice(voiceCharacter.slot_index, {
          voice_type: "",
          wav_file: uploadedPath,
          slot_index: null,
          icon_file: null,
          text: null,
        });
        await reloadVoiceCharacters();
        toast.success("Uploaded");
      } catch (e) {
        toast.error(`Upload failed: ${e}`);
      }
    },
    [voiceCharacter.slot_index, reloadVoiceCharacters],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) handleFileUpload(file);
    },
    [handleFileUpload],
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFileUpload(file);
      e.target.value = "";
    },
    [handleFileUpload],
  );

  // Multiple selection info
  if (currentVoiceIndexes.length > 1) {
    return (
      <div className={styles.area}>
        <div className={styles.multiSelect}>{t("reference_voice_area_multiple_selection")}</div>
      </div>
    );
  }

  // No selection - show upload area
  if (!selectedVoice) {
    return (
      <div
        className={styles.uploadArea}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <span>{t("reference_voice_area_fileupload_area_text")}</span>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          className={styles.hiddenInput}
          onChange={handleFileInputChange}
        />
      </div>
    );
  }

  const languageOptions = LANGUAGE_TYPES.map((l) => ({ value: l, label: l }));
  const emotionOptions = voiceCharacter.emotion_types.map((e) => ({ value: e.name, label: e.name }));

  return (
    <div className={styles.area}>
      {/* View mode */}
      {!editMode && (
        <>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_audio")}</span>
            <Button variant="icon" onClick={handlePlay}>
              {isPlaying ? <FaStop /> : <FaPlay />}
            </Button>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_text")}</span>
            <span className={styles.value}>{selectedVoice.text || "-"}</span>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_category")}</span>
            <span className={styles.value}>{selectedVoice.voice_type || "-"}</span>
          </div>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_language")}</span>
            <span className={styles.value}>{selectedVoice.language}</span>
          </div>
          <div className={styles.actions}>
            <Button variant="secondary" onClick={handleEdit}>
              {t("reference_voice_area_edit_button")}
            </Button>
            <Button variant="secondary" onClick={handleDelete}>
              {t("reference_voice_area_delete_button")}
            </Button>
          </div>
        </>
      )}

      {/* Edit mode */}
      {editMode && (
        <>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_text")}</span>
            <textarea
              className={styles.textarea}
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
            />
          </div>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_category")}</span>
            {emotionOptions.length > 0 ? (
              <Select
                options={emotionOptions}
                value={editVoiceType}
                onChange={(e) => setEditVoiceType(e.target.value)}
              />
            ) : (
              <input
                className={styles.input}
                value={editVoiceType}
                onChange={(e) => setEditVoiceType(e.target.value)}
              />
            )}
          </div>
          <div className={styles.row}>
            <span className={styles.label}>{t("reference_voice_area_language")}</span>
            <Select
              options={languageOptions}
              value={editLanguage}
              onChange={(e) => setEditLanguage(e.target.value as LanguageType)}
            />
          </div>
          <div className={styles.actions}>
            <Button variant="primary" onClick={handleSave}>
              {t("reference_voice_area_save_button")}
            </Button>
            <Button variant="secondary" onClick={() => setEditMode(false)}>
              {t("reference_voice_area_cancel_button")}
            </Button>
          </div>
        </>
      )}
    </div>
  );
};
