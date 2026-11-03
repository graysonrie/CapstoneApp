import { create } from "zustand";
import type { PlantScanResult } from "../types";

const PENDING_IMAGE_KEY = "scan-pending-image-path";
const PREVIOUS_PATH_KEY = "scan-previous-path";

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

function readStoredScan(): { previousPath: string; pendingImagePath: string | null } {
  if (typeof window === "undefined") {
    return { previousPath: "/home", pendingImagePath: null };
  }
  return {
    previousPath: sessionStorage.getItem(PREVIOUS_PATH_KEY) || "/home",
    pendingImagePath: sessionStorage.getItem(PENDING_IMAGE_KEY),
  };
}

function persistPendingScan(previousPath: string, imagePath: string) {
  if (typeof window === "undefined") {
    return;
  }
  sessionStorage.setItem(PREVIOUS_PATH_KEY, previousPath);
  sessionStorage.setItem(PENDING_IMAGE_KEY, imagePath);
}

function clearPersistedScan() {
  if (typeof window === "undefined") {
    return;
  }
  sessionStorage.removeItem(PREVIOUS_PATH_KEY);
  sessionStorage.removeItem(PENDING_IMAGE_KEY);
}

const stored = readStoredScan();

export const useScanStore = create<ScanStore>((set, get) => ({
  previousPath: stored.previousPath,
  pendingImagePath: stored.pendingImagePath,
  imageSrc: null,
  result: null,
  scanStarted: false,
  setPendingScan: (previousPath, imagePath) => {
    persistPendingScan(previousPath, imagePath);
    set({
      previousPath,
      pendingImagePath: imagePath,
      result: null,
      imageSrc: null,
      scanStarted: false,
    });
  },
  markScanStarted: () => {
    if (get().scanStarted) {
      return false;
    }
    set({ scanStarted: true });
    return true;
  },
  setResult: (result, imageSrc) => {
    clearPersistedScan();
    set({ result, imageSrc, pendingImagePath: null });
  },
  clearPending: () => {
    clearPersistedScan();
    set({ pendingImagePath: null, scanStarted: false });
  },
}));
