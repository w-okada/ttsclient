import { create } from "zustand";
import * as api from "@/api/endpoints";
import type {
  TTSConfiguration,
  GPUInfo,
  ModuleStatus,
  SlotInfoMember,
  VoiceCharacter,
  SampleInfoMember,
} from "@/types";

type ServerState = {
  slots: SlotInfoMember[];
  voiceCharacters: VoiceCharacter[];
  modules: ModuleStatus[];
  configuration: TTSConfiguration | null;
  gpuDevices: GPUInfo[];
  samples: SampleInfoMember[];
  loading: boolean;

  // Actions
  loadAll: () => Promise<void>;
  reloadSlots: () => Promise<void>;
  reloadVoiceCharacters: () => Promise<void>;
  reloadModules: () => Promise<void>;
  reloadConfiguration: () => Promise<void>;
  reloadGPUDevices: () => Promise<void>;
  reloadSamples: () => Promise<void>;
  updateConfiguration: (config: TTSConfiguration) => Promise<void>;
};

export const useServerStore = create<ServerState>((set, get) => ({
  slots: [],
  voiceCharacters: [],
  modules: [],
  configuration: null,
  gpuDevices: [],
  samples: [],
  loading: false,

  loadAll: async () => {
    set({ loading: true });
    try {
      const [slots, voiceCharacters, modules, configuration, gpuDevices, samples] = await Promise.all([
        api.getSlots(),
        api.getVoiceCharacters(),
        api.getModules(),
        api.getConfiguration(),
        api.getGPUDevices(),
        api.getSamples(),
      ]);
      set({ slots, voiceCharacters, modules, configuration, gpuDevices, samples });
    } finally {
      set({ loading: false });
    }
  },

  reloadSlots: async () => {
    const slots = await api.getSlots(true);
    set({ slots });
  },

  reloadVoiceCharacters: async () => {
    const voiceCharacters = await api.getVoiceCharacters(true);
    set({ voiceCharacters });
  },

  reloadModules: async () => {
    const modules = await api.getModules(true);
    set({ modules });
  },

  reloadConfiguration: async () => {
    const configuration = await api.getConfiguration(true);
    set({ configuration });
  },

  reloadGPUDevices: async () => {
    const gpuDevices = await api.getGPUDevices(true);
    set({ gpuDevices });
  },

  reloadSamples: async () => {
    const samples = await api.getSamples(true);
    set({ samples });
  },

  updateConfiguration: async (config: TTSConfiguration) => {
    const updated = await api.putConfiguration(config);
    set({ configuration: updated });
    // Reload slots after configuration change (slot index may affect display)
    const { reloadSlots } = get();
    await reloadSlots();
  },
}));
