import { create } from "zustand";
import { API_BASE } from "@/lib/api";

export interface LlmModel {
  name: string;
}

interface LlmState {
  providers: Record<string, LlmModel[]>;
  selectedProvider: string;
  selectedModel: string;
  loaded: boolean;
  refresh: () => Promise<void>;
  select: (provider: string, model: string) => void;
}

const FALLBACK_MODELS: Record<string, LlmModel[]> = {
  ollama: [{ name: "llama3.2:3b" }],
};

/** Global LLM state (WEBAPP_SOTA_STANDARDS VI): providers, selection, and
 *  discovery live here — never per-page useState. Persists to the same
 *  localStorage keys the Settings page has always used. */
export const useLlmStore = create<LlmState>()((set) => ({
  providers: {},
  selectedProvider: "ollama",
  selectedModel: "",
  loaded: false,
  refresh: async () => {
    try {
      const r = await fetch(`${API_BASE}/api/llm/providers`);
      const d: Record<string, LlmModel[]> = await r.json();
      set({ providers: d });
      const savedP = localStorage.getItem("llm_provider") || "ollama";
      const savedM = localStorage.getItem("llm_model") || "";
      const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
      set({
        selectedProvider: savedP,
        selectedModel:
          savedM && models.some((m) => m.name === savedM)
            ? savedM
            : models[0]?.name || "",
        loaded: true,
      });
    } catch {
      set({
        providers: FALLBACK_MODELS,
        selectedModel: localStorage.getItem("llm_model") || "llama3.2:3b",
        loaded: true,
      });
    }
  },
  select: (provider, model) => {
    localStorage.setItem("llm_provider", provider);
    localStorage.setItem("llm_model", model);
    set({ selectedProvider: provider, selectedModel: model });
  },
}));
