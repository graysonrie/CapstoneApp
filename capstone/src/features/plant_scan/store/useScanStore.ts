import { create } from "zustand";
import type { PlantScanResult } from "../types";

interface ScanStore {
  previousPath: string;
  pendingImagePath: string | null;
  imageSrc: string | null;
  result: PlantScanResult | null;
  scanStarted: boolean;
  setPendingScan: (previousPath: string, imagePath: string) => void;
  markScanStarted: () => boolean;
  setResult: (result: PlantScanResult, imageSrc: string) => void;
  clearPending: () => void;
}

export const useScanStore = create<ScanStore>((set, get) => ({
  previousPath: "/home",
  pendingImagePath: null,
  imageSrc: null,
  result: null,
  scanStarted: false,
  setPendingScan: (previousPath, imagePath) =>
    set({
      previousPath,
      pendingImagePath: imagePath,
      result: null,
      imageSrc: null,
      scanStarted: false,
    }),
  markScanStarted: () => {
    if (get().scanStarted) {
      return false;
    }
    set({ scanStarted: true });
    return true;
  },
  setResult: (result, imageSrc) =>
    set({ result, imageSrc, pendingImagePath: null }),
  clearPending: () => set({ pendingImagePath: null, scanStarted: false }),
}));
