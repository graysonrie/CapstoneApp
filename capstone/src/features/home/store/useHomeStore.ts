import { create } from "zustand";

interface Store {
  /** Starts off as true */
  isFirstVisit: boolean;
  /** Latched when first visit happens while offline */
  showOfflineNotice: boolean;
  setValues: (values: Partial<Store>) => void;
}

export const useHomeStore = create<Store>((set) => ({
  isFirstVisit: true,
  showOfflineNotice: false,
  setValues: (values) => set(values),
}));
