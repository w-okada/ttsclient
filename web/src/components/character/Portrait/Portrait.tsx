import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Button } from "@/components/common/Button/Button";
import { useUIStore } from "@/stores/uiStore";
import { useServerStore } from "@/stores/serverStore";
import * as api from "@/api/endpoints";
import { uploadFile } from "@/api/fileUploader";
import type { VoiceCharacter } from "@/types";
import styles from "./Portrait.module.css";

type Props = {
  voiceCharacter: VoiceCharacter;
};

const ALLOWED_ICON_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif"];

export const Portrait = ({ voiceCharacter }: Props) => {
  const { t } = useTranslation();
  const openDialog = useUIStore((s) => s.openDialog);
  const reloadVoiceCharacters = useServerStore((s) => s.reloadVoiceCharacters);

  const iconUrl = voiceCharacter.icon_file
    ? `/get_proxy?path=${encodeURIComponent(voiceCharacter.icon_file)}`
    : null;

  const handleIconDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (!file) return;
      const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      if (!ALLOWED_ICON_EXTENSIONS.includes(ext)) {
        toast.error(t("voice_character_slot_manager_main_change_icon_ext_error"));
        return;
      }
      try {
        const uploadedPath = await uploadFile(file);
        await api.setVoiceCharacterIcon(voiceCharacter.slot_index, { icon_file: uploadedPath });
        await reloadVoiceCharacters();
        toast.success("Icon updated");
      } catch (e) {
        toast.error(`Icon upload failed: ${e}`);
      }
    },
    [voiceCharacter.slot_index, reloadVoiceCharacters, t],
  );

  return (
    <div className={styles.portrait} onDragOver={(e) => e.preventDefault()} onDrop={handleIconDrop}>
      <div className={styles.iconFrame}>
        {iconUrl ? (
          <img className={styles.icon} src={iconUrl} alt={voiceCharacter.name} />
        ) : (
          <div className={styles.iconPlaceholder}>{voiceCharacter.name?.[0] ?? "?"}</div>
        )}
      </div>
      <div className={styles.links}>
        {voiceCharacter.terms_of_use_url && (
          <a href={voiceCharacter.terms_of_use_url} target="_blank" rel="noopener noreferrer">
            {t("character_area_portrait_terms_of_use")}
          </a>
        )}
        <Button
          variant="icon"
          onClick={() =>
            openDialog("aboutModel", {
              title: t("character_area_portrait_about_model"),
              voiceCharacter,
            })
          }
        >
          {t("character_area_portrait_about_model")}
        </Button>
      </div>
    </div>
  );
};
