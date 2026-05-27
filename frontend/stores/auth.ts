/** Zustand auth store — persists JWT in localStorage. */
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/types/api";

interface AuthState {
  accessToken: string | null;
  user: User | null;
  hydrated: boolean;
  setAuth: (token: string, user: User) => void;
  setUser: (user: User) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      user: null,
      hydrated: false,
      setAuth: (token, user) => set({ accessToken: token, user }),
      setUser: (user) => set({ user }),
      clearAuth: () => set({ accessToken: null, user: null }),
      isAuthenticated: () => Boolean(get().accessToken),
    }),
    {
      name: "wa-saas-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) state.hydrated = true;
      },
    },
  ),
);
