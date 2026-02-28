import { useState, useCallback, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "react-toastify";
import { Dialog } from "@/components/common/Dialog/Dialog";
import { Button } from "@/components/common/Button/Button";
import { useServerStore } from "@/stores/serverStore";
import { useUIStore } from "@/stores/uiStore";
import * as api from "@/api/endpoints";
import { uploadFile } from "@/api/fileUploader";
import type { SlotInfoMember } from "@/types";
import styles from "./ModelSlotManagerDialog.module.css";

type View = "main" | "upload" | "sample";

export const ModelSlotManagerDialog = () => {
  const { t } = useTranslation();
  const slots = useServerStore((s) => s.slots);
  const samples = useServerStore((s) => s.samples);
  const reloadSlots = useServerStore((s) => s.reloadSlots);
  const reloadSamples = useServerStore((s) => s.reloadSamples);
  const openDialog = useUIStore((s) => s.openDialog);
  const [view, setView] = useState<View>("main");
  const semanticFileRef = useRef<HTMLInputElement>(null);
  const synthesizerFileRef = useRef<HTMLInputElement>(null);
  const [semanticFile, setSemanticFile] = useState<File | null>(null);
  const [synthesizerFile, setSynthesizerFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleRename = useCallback(
    (slot: SlotInfoMember) => {
      openDialog("textInput", {
        title: t("model_slot_name_input_dialog_title"),
        message: t("model_slot_name_input_dialog_instruction"),
        defaultValue: slot.name,
        onSubmit: async (newName: string) => {
          try {
            await api.putSlot(slot.slot_index, { ...slot, name: newName });
            await reloadSlots();
            openDialog("modelSlotManager");
          } catch (e) {
            toast.error(`Rename failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadSlots, t],
  );

  const handleDelete = useCallback(
    (slot: SlotInfoMember) => {
      openDialog("confirm", {
        title: t("model_slot_delete_confirm_dialog_title"),
        message: t("model_slot_delete_confirm_dialog_instruction"),
        onConfirm: async () => {
          try {
            await api.deleteSlot(slot.slot_index);
            await reloadSlots();
            openDialog("modelSlotManager");
          } catch (e) {
            toast.error(`Delete failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadSlots, t],
  );

  const handleMove = useCallback(
    (slot: SlotInfoMember) => {
      const moveOptions = Array.from({ length: 20 }, (_, i) => ({
        value: String(i),
        label: `Slot ${i}`,
      }));
      openDialog("select", {
        title: t("model_slot_move_confirm_dialog_title"),
        message: t("model_slot_move_confirm_dialog_instruction"),
        options: moveOptions,
        onSelect: async (dst: string) => {
          try {
            await api.moveSlot({ src: slot.slot_index, dst: Number(dst) });
            await reloadSlots();
            openDialog("modelSlotManager");
          } catch (e) {
            toast.error(`Move failed: ${e}`);
          }
        },
      });
    },
    [openDialog, reloadSlots, t],
  );

  const handleUpload = useCallback(async () => {
    if (!semanticFile || !synthesizerFile) {
      toast.warning(t("model_slot_manager_fileupload_instruction"));
      return;
    }
    setUploading(true);
    try {
      const [semanticPath, synthesizerPath] = await Promise.all([
        uploadFile(semanticFile, (p) => {
          openDialog("progress", {
            title: t("dialog_uploading"),
            message: `Uploading semantic model...`,
            progress: p * 0.5,
          });
        }),
        uploadFile(synthesizerFile, (p) => {
          openDialog("progress", {
            title: t("dialog_uploading"),
            message: `Uploading synthesizer model...`,
            progress: 0.5 + p * 0.5,
          });
        }),
      ]);
      await api.postSlot({
        tts_type: "GPT-SoVITS",
        name: semanticFile.name.replace(/\.\w+$/, ""),
        terms_of_use_url: "",
        slot_index: null,
        icon_file: null,
        semantic_predictor_model_path: semanticPath,
        synthesizer_model_path: synthesizerPath,
      });
      await reloadSlots();
      toast.success("Model uploaded");
      setView("main");
      setSemanticFile(null);
      setSynthesizerFile(null);
    } catch (e) {
      toast.error(`Upload failed: ${e}`);
    } finally {
      setUploading(false);
      openDialog("modelSlotManager");
    }
  }, [semanticFile, synthesizerFile, reloadSlots, openDialog, t]);

  const handleSampleDownload = useCallback(
    async (sampleId: string, slotIndex: number) => {
      try {
        openDialog("wait", {
          title: t("dialog_sample_downloading_dialog_title"),
          message: t("dialog_sample_downloading_dialog_instruction"),
        });
        await api.downloadSample({ slot_index: slotIndex, sample_id: sampleId });
        await reloadSlots();
        await reloadSamples();
        toast.success("Sample downloaded");
        openDialog("modelSlotManager");
      } catch (e) {
        toast.error(`Download failed: ${e}`);
        openDialog("modelSlotManager");
      }
    },
    [openDialog, reloadSlots, reloadSamples, t],
  );

  const modelSamples = samples.filter((s) => s.tts_type === "GPT-SoVITS");

  if (view === "upload") {
    return (
      <Dialog title={t("model_slot_manager_fileupload_title")} wide>
        <p className={styles.instruction}>{t("model_slot_manager_fileupload_instruction")}</p>
        <div className={styles.uploadRow}>
          <span>GPT (.ckpt):</span>
          <Button variant="secondary" onClick={() => semanticFileRef.current?.click()}>
            {semanticFile ? semanticFile.name : t("model_slot_manager_fileupload_file_select")}
          </Button>
          <input
            ref={semanticFileRef}
            type="file"
            accept=".ckpt"
            style={{ display: "none" }}
            onChange={(e) => setSemanticFile(e.target.files?.[0] ?? null)}
          />
        </div>
        <div className={styles.uploadRow}>
          <span>SoVITS (.pth):</span>
          <Button variant="secondary" onClick={() => synthesizerFileRef.current?.click()}>
            {synthesizerFile ? synthesizerFile.name : t("model_slot_manager_fileupload_file_select")}
          </Button>
          <input
            ref={synthesizerFileRef}
            type="file"
            accept=".pth"
            style={{ display: "none" }}
            onChange={(e) => setSynthesizerFile(e.target.files?.[0] ?? null)}
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
          {modelSamples.map((sample) => (
            <div key={sample.id} className={styles.sampleItem}>
              <div className={styles.sampleInfo}>
                <span className={styles.sampleName}>{sample.name}</span>
                <span className={styles.sampleDesc}>{sample.description}</span>
              </div>
              <Button
                variant="secondary"
                onClick={() => {
                  const emptySlot = slots.find((s) => s.tts_type == null);
                  if (emptySlot) {
                    handleSampleDownload(sample.id, emptySlot.slot_index);
                  } else {
                    toast.warning("No empty slot");
                  }
                }}
              >
                {t("dialog_sample_download_button")}
              </Button>
            </div>
          ))}
          {modelSamples.length === 0 && <span>No samples available</span>}
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
    <Dialog title={t("model_slot_manager_main_title")} wide>
      <div className={styles.toolbar}>
        <Button variant="secondary" onClick={() => setView("upload")}>
          {t("model_slot_manager_main_upload")}
        </Button>
        <Button variant="secondary" onClick={() => setView("sample")}>
          {t("model_slot_manager_main_sample")}
        </Button>
      </div>
      <div className={styles.slotList}>
        {slots.map((slot) => (
          <div key={slot.slot_index} className={styles.slotItem}>
            <span className={styles.slotIndex}>[{slot.slot_index}]</span>
            <span className={styles.slotName}>{slot.name || "-"}</span>
            <span className={styles.slotType}>{slot.tts_type ?? "-"}</span>
            <div className={styles.slotActions}>
              {slot.tts_type && (
                <>
                  <Button variant="icon" onClick={() => handleRename(slot)} title={t("model_slot_manager_main_rename")}>
                    {t("model_slot_manager_main_rename")}
                  </Button>
                  <Button variant="icon" onClick={() => handleMove(slot)} title={t("model_slot_manager_main_move")}>
                    {t("model_slot_manager_main_move")}
                  </Button>
                  <Button variant="icon" onClick={() => handleDelete(slot)} title={t("model_slot_manager_main_delete")}>
                    {t("model_slot_manager_main_delete")}
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
