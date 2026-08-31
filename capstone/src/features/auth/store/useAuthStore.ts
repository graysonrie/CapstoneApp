import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/features/auth/types";

type AuthState = {
  user: User | null;
  isSessionReady: boolean;
  setUser: (user: User) => void;
  clearUser: () => void;
  setSessionReady: (isSessionReady: boolean) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isSessionReady: false,
      setUser: (user) => set({ user }),
      clearUser: () => set({ user: null }),
      setSessionReady: (isSessionReady) => set({ isSessionReady }),
    }),
    {
      name: "auth",
      partialize: (state) => ({ user: state.user }),
    },
  ),
);
