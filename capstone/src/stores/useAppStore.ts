import { create } from "zustand";

/** App specific store. Nothing to do with the iOS App Store */
interface Store {
  /** Should be true if pinging the server failed */
  isConfirmedOffline: boolean;
  setValues: (values: Partial<Store>) => void;
}

export const useAppStore = create<Store>((set) => ({
  isConfirmedOffline: false,

  setValues: (values) => set(values),
}));
