import { useUIStore } from "@/stores/uiStore";
import { ConfirmDialog } from "./ConfirmDialog";
import { TextInputDialog } from "./TextInputDialog";
import { SelectDialog } from "./SelectDialog";
import { ProgressDialog } from "./ProgressDialog";
import { WaitDialog } from "./WaitDialog";
import { ModelSlotManagerDialog } from "@/components/slots/ModelSlotManagerDialog/ModelSlotManagerDialog";
import { VoiceCharacterManagerDialog } from "@/components/slots/VoiceCharacterManagerDialog/VoiceCharacterManagerDialog";
import { AdvancedSettingDialog } from "@/components/actions/AdvancedSettingDialog/AdvancedSettingDialog";

export const DialogRoot = () => {
  const dialogName = useUIStore((s) => s.dialogName);

  switch (dialogName) {
    case "confirm":
      return <ConfirmDialog />;
    case "textInput":
      return <TextInputDialog />;
    case "select":
      return <SelectDialog />;
    case "progress":
      return <ProgressDialog />;
    case "wait":
      return <WaitDialog />;
    case "modelSlotManager":
      return <ModelSlotManagerDialog />;
    case "voiceCharacterManager":
      return <VoiceCharacterManagerDialog />;
    case "advancedSetting":
      return <AdvancedSettingDialog />;
    default:
      return null;
  }
};
