import { create } from "zustand";

interface Store {
  password: string;
  email: string;
  setValues: (values: Partial<Store>) => void;
}

export const useAuthFormStore = create<Store>((set) => ({
  password: "",
  email: "",
  setValues: (values) => set(values),
}));
