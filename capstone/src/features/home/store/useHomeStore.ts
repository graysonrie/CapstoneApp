import { create } from "zustand";

interface Store {
  /** Starts off as true */
  isFirstVisit: boolean;
  setValues: (values: Partial<Store>) => void;
}

export const useHomeStore = create<Store>((set) => ({
  isFirstVisit: true,
  setValues: (values) => set(values),
}));
