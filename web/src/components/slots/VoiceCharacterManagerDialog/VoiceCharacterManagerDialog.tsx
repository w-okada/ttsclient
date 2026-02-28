import { useState, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { FaDownload } from "react-icons/fa";
import { Dialog } from "@/components/common/Dialog/Dialog";
import { Button } from "@/components/common/Button/Button";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import * as api from "@/api/endpoints";
import { uploadFile } from "@/api/fileUploader";
import type { VoiceCharacter } from "@/types";
import styles from "./VoiceCharacterManagerDialog.module.css";

type View = "main" | "upload" | "sample";

export const VoiceCharacterManagerDialog = () => {
  const { t } = useTranslation();
  const voiceCharacters = useServerStore((s) => s.voiceCharacters);
  const samples = useServerStore((s) => s.samples);
  const reloadVoiceCharacters = useServerStore((s) => s.reloadVoiceCharacters);
  const reloadSamples = useServerStore((s) => s.reloadSamples);
  const openDialog = useUIStore((s) => s.openDialog);
  const [view, setView] = useState<View>("main");
  const [uploadName, setUploadName] = useState("");
  const zipFileRef = useRef<HTMLInputElement>(null);
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleNew = useCallback(() => {
    openDialog("textInput", {
      title: t("voice_character_slot_manager_main_new_title"),
      message: t("voice_character_slot_manager_main_new_instruction"),
      defaultValue: "",
      onSubmit: async (name: string) => {
        if (!name.trim()) {
          toast.warning(t("voice_character_slot_manager_main_new_error"));
          return;
        }
        try {
          await api.postVoiceCharacter({
            tts_type: "VoiceCharacter",
            name,
            terms_of_use_url: "",
            slot_index: null,
            icon_file: null,
            zip_file: null,
          });
          await reloadVoiceCharacters();
          openDialog("voiceCharacterManager");
        } catch (e) {
          toast.error(`Create failed: ${e}`);
        }
      },
    });
  }, [openDialog, reloadVoiceCharacters, t]);

  const handleRename = useCallback(
    (vc: VoiceCharacter) => {
      openDialog("textInput", {
        title: t("voice_character_slot_name_input_dialog_title"),
        message: t("voice_character_slot_name_input_dialog_instruction"),
        defaultValue: vc.name,
        onSubmit: async (newName: string) => {
          try {
            await api.putVoiceCharacter(vc.slot_index, { ...vc, name: newName });
            await reloadVoiceCharacters();
            openDialog("voiceCharacterManager");
          } catch (e) {
            toast.error(`Rename failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadVoiceCharacters, t],
  );

  const handleDelete = useCallback(
    (vc: VoiceCharacter) => {
      openDialog("confirm", {
        title: t("voice_character_slot_delete_confirm_dialog_title"),
        message: t("voice_character_slot_delete_confirm_dialog_instruction"),
        onConfirm: async () => {
          try {
            await api.deleteVoiceCharacter(vc.slot_index);
            await reloadVoiceCharacters();
            openDialog("voiceCharacterManager");
          } catch (e) {
            toast.error(`Delete failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadVoiceCharacters, t],
  );

  const handleMove = useCallback(
    (vc: VoiceCharacter) => {
      openDialog("textInput", {
        title: t("voice_character_slot_move_confirm_dialog_title"),
        message: t("voice_character_slot_move_confirm_dialog_instruction"),
        defaultValue: "",
        onSubmit: async (dst: string) => {
          try {
            await api.moveVoiceCharacter({ src: vc.slot_index, dst: Number(dst) });
            await reloadVoiceCharacters();
            openDialog("voiceCharacterManager");
          } catch (e) {
            toast.error(`Move failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadVoiceCharacters, t],
  );

  const handleZipDownload = useCallback(
    async (vc: VoiceCharacter) => {
      try {
        openDialog("wait", {
          title: t("reference_voice_area_download_waiting_dialog_title"),
          message: t("reference_voice_area_download_waiting_dialog_instruction"),
        });
        const blob = await api.zipAndDownloadVoices(vc.slot_index);
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${vc.name}.zip`;
        a.click();
        URL.revokeObjectURL(url);
        openDialog("voiceCharacterManager");
      } catch (e) {
        toast.error(`Download failed: ${e}`);
        openDialog("voiceCharacterManager");
      }
    },
    [openDialog, t],
  );

  const handleUpload = useCallback(async () => {
    if (!uploadName.trim()) {
      toast.warning(t("voice_character_slot_manager_fileupload_name_input_error"));
      return;
    }
    if (!zipFile) {
      toast.warning(t("voice_character_slot_manager_fileupload_zip_input_error"));
      return;
    }
    setUploading(true);
    try {
      const zipPath = await uploadFile(zipFile, (p) => {
        openDialog("progress", {
          title: t("dialog_uploading"),
          message: `Uploading ZIP...`,
          progress: p,
        });
      });
      await api.postVoiceCharacter({
        tts_type: "VoiceCharacter",
        name: uploadName,
        terms_of_use_url: "",
        slot_index: null,
        icon_file: null,
        zip_file: zipPath,
      });
      await reloadVoiceCharacters();
      toast.success("Voice character uploaded");
      setView("main");
      setUploadName("");
      setZipFile(null);
    } catch (e) {
      toast.error(`Upload failed: ${e}`);
    } finally {
      setUploading(false);
      openDialog("voiceCharacterManager");
    }
  }, [uploadName, zipFile, reloadVoiceCharacters, openDialog, t]);

  const handleSampleDownload = useCallback(
    async (sampleId: string) => {
      try {
        const emptySlot = voiceCharacters.find((vc) => vc.tts_type == null);
        const slotIndex = emptySlot?.slot_index ?? voiceCharacters.length;
        openDialog("wait", {
          title: t("dialog_sample_downloading_dialog_title"),
          message: t("dialog_sample_downloading_dialog_instruction"),
        });
        await api.downloadSample({ slot_index: slotIndex, sample_id: sampleId });
        await reloadVoiceCharacters();
        await reloadSamples();
        toast.success("Sample downloaded");
        openDialog("voiceCharacterManager");
      } catch (e) {
        toast.error(`Download failed: ${e}`);
        openDialog("voiceCharacterManager");
      }
    },
    [voiceCharacters, openDialog, reloadVoiceCharacters, reloadSamples, t],
  );

  const vcSamples = samples.filter((s) => s.tts_type === "VoiceCharacter");

  if (view === "upload") {
    return (
      <Dialog title={t("voice_character_slot_manager_fileupload_title")} wide>
        <p className={styles.instruction}>{t("voice_character_slot_manager_fileupload_instruction")}</p>
        <div className={styles.uploadRow}>
          <span>{t("voice_character_slot_manager_fileupload_name_input_label")}:</span>
          <input
            className={styles.nameInput}
            value={uploadName}
            onChange={(e) => setUploadName(e.target.value)}
          />
        </div>
        <div className={styles.uploadRow}>
          <span>ZIP:</span>
          <Button variant="secondary" onClick={() => zipFileRef.current?.click()}>
            {zipFile ? zipFile.name : t("voice_character_slot_manager_fileupload_file_select")}
          </Button>
          <input
            ref={zipFileRef}
            type="file"
            accept=".zip"
            style={{ display: "none" }}
            onChange={(e) => setZipFile(e.target.files?.[0] ?? null)}
          />
        </div>
        <div className={styles.actions}>
          <Button variant="primary" onClick={handleUpload} disabled={uploading}>
            {uploading ? t("dialog_uploading") : t("dialog_upload")}
          </Button>
          <Button variant="secondary" onClick={() => setView("main")}>
            {t("dialog_back")}
          </Button>
        </div>
      </Dialog>
    );
  }

  if (view === "sample") {
    return (
      <Dialog title={t("dialog_sample_title")} wide>
        <p className={styles.instruction}>{t("dialog_sample_instruction")}</p>
        <div className={styles.sampleList}>
          {vcSamples.map((sample) => (
            <div key={sample.id} className={styles.sampleItem}>
              <div className={styles.sampleInfo}>
                <span className={styles.sampleName}>{sample.name}</span>
                <span className={styles.sampleDesc}>{sample.description}</span>
              </div>
              <Button variant="secondary" onClick={() => handleSampleDownload(sample.id)}>
                {t("dialog_sample_download_button")}
              </Button>
            </div>
          ))}
          {vcSamples.length === 0 && <span>No samples available</span>}
        </div>
        <div className={styles.actions}>
          <Button variant="secondary" onClick={() => setView("main")}>
            {t("dialog_back")}
          </Button>
        </div>
      </Dialog>
    );
  }

  return (
    <Dialog title={t("voice_character_slot_manager_main_title")} wide>
      <div className={styles.toolbar}>
        <Button variant="secondary" onClick={handleNew}>
          {t("voice_character_slot_manager_main_new")}
        </Button>
        <Button variant="secondary" onClick={() => setView("upload")}>
          {t("voice_character_slot_manager_main_upload")}
        </Button>
        <Button variant="secondary" onClick={() => setView("sample")}>
          {t("voice_character_slot_manager_main_sample")}
        </Button>
      </div>
      <div className={styles.vcList}>
        {voiceCharacters.map((vc) => (
          <div key={vc.slot_index} className={styles.vcItem}>
            <span className={styles.vcIndex}>[{vc.slot_index}]</span>
            <span className={styles.vcName}>{vc.name || "-"}</span>
            <span className={styles.vcType}>{vc.tts_type ?? "-"}</span>
            <span className={styles.vcVoiceCount}>{vc.reference_voices.length} voices</span>
            <div className={styles.vcActions}>
              {vc.tts_type && (
                <>
                  <Button variant="icon" onClick={() => handleRename(vc)} title={t("voice_character_slot_manager_main_rename")}>
                    {t("voice_character_slot_manager_main_rename")}
                  </Button>
                  <Button variant="icon" onClick={() => handleMove(vc)} title={t("voice_character_slot_manager_main_move")}>
                    {t("voice_character_slot_manager_main_move")}
                  </Button>
                  <Button variant="icon" onClick={() => handleZipDownload(vc)} title={t("voice_character_slot_manager_main_download")}>
                    <FaDownload />
                  </Button>
                  <Button variant="icon" onClick={() => handleDelete(vc)} title={t("voice_character_slot_manager_main_delete")}>
                    {t("voice_character_slot_manager_main_delete")}
                  </Button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </Dialog>
  );
};
