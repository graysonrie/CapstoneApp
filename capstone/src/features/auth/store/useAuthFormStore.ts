import { create } from "zustand";

interface Store {
  name: string;
  password: string;
  email: string;
  setValues: (values: Partial<Store>) => void;
}

export const useAuthFormStore = create<Store>((set) => ({
  name: "",
  password: "",
  email: "",
  setValues: (values) => set(values),
}));
