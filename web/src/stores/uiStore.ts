import { create } from "zustand";
import * as api from "@/api/endpoints";
import type { DialogName } from "@/types";

type Theme = "light" | "dark";

type DialogProps = Record<string, unknown>;

type UIState = {
  theme: Theme;
  currentSlotIndex: number;
  currentVCIndex: number;
  currentVoiceIndexes: number[];
  dialogName: DialogName;
  dialogProps: DialogProps;
  outputDeviceId: string;
  monitorDeviceId: string;
  inputDeviceId: string;

  // Actions
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setCurrentSlotIndex: (index: number) => void;
  setCurrentVCIndex: (index: number) => void;
  setCurrentVoiceIndexes: (indexes: number[]) => void;
  toggleVoiceIndex: (index: number) => void;
  openDialog: (name: DialogName, props?: DialogProps) => void;
  updateDialogProps: (props: Partial<DialogProps>) => void;
  closeDialog: () => void;
  setOutputDeviceId: (id: string) => void;
  setMonitorDeviceId: (id: string) => void;
  setInputDeviceId: (id: string) => void;
};

const getInitialTheme = (): Theme => {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
};

export const useUIStore = create<UIState>((set, get) => ({
  theme: getInitialTheme(),
  currentSlotIndex: -1,
  currentVCIndex: -1,
  currentVoiceIndexes: [],
  dialogName: "none",
  dialogProps: {},
  outputDeviceId: localStorage.getItem("audioOutputDeviceId") ?? "",
  monitorDeviceId: localStorage.getItem("audioMonitorDeviceId") ?? "",
  inputDeviceId: localStorage.getItem("audioInputDeviceId") ?? "",

  setTheme: (theme) => {
    localStorage.setItem("theme", theme);
    document.documentElement.setAttribute("data-theme", theme);
    set({ theme });
  },

  toggleTheme: () => {
    const { theme, setTheme } = get();
    setTheme(theme === "light" ? "dark" : "light");
  },

  setCurrentSlotIndex: (index) => {
    set({ currentSlotIndex: index });
    api.getConfiguration().then((config) => {
      if (config.current_slot_index !== index) {
        api.putConfiguration({ ...config, current_slot_index: index });
      }
    });
  },

  setCurrentVCIndex: (index) => {
    set({ currentVCIndex: index, currentVoiceIndexes: [] });
    api.getConfiguration().then((config) => {
      if (config.current_vc_index !== index) {
        api.putConfiguration({ ...config, current_vc_index: index });
      }
    });
  },

  setCurrentVoiceIndexes: (indexes) => set({ currentVoiceIndexes: indexes }),

  toggleVoiceIndex: (index) => {
    const { currentVoiceIndexes } = get();
    if (currentVoiceIndexes.includes(index)) {
      set({ currentVoiceIndexes: currentVoiceIndexes.filter((i) => i !== index) });
    } else {
      set({ currentVoiceIndexes: [...currentVoiceIndexes, index] });
    }
  },

  openDialog: (name, props = {}) => set({ dialogName: name, dialogProps: props }),

  updateDialogProps: (props) => set((state) => ({ dialogProps: { ...state.dialogProps, ...props } })),

  closeDialog: () => set({ dialogName: "none", dialogProps: {} }),

  setOutputDeviceId: (id) => {
    localStorage.setItem("audioOutputDeviceId", id);
    set({ outputDeviceId: id });
  },

  setMonitorDeviceId: (id) => {
    localStorage.setItem("audioMonitorDeviceId", id);
    set({ monitorDeviceId: id });
  },

  setInputDeviceId: (id) => {
    localStorage.setItem("audioInputDeviceId", id);
    set({ inputDeviceId: id });
  },
}));
