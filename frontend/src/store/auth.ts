import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Role = "patient" | "doctor" | "guardian" | "admin";

export type AuthUser = {
  user_id: string;
  email: string;
  phone: string | null;
  full_name: string;
  account_status: string;
  email_verified: boolean;
  preferred_locale: string;
  avatar_uri: string | null;
  roles: Role[];
  profile: Record<string, unknown>;
};

type SessionPayload = {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
};

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  hydrated: boolean;
  setSession: (payload: SessionPayload) => void;
  setUser: (user: AuthUser) => void;
  setAccessToken: (token: string) => void;
  clear: () => void;
  setHydrated: () => void;
};

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      hydrated: false,
      setSession: (payload) =>
        set({
          accessToken: payload.access_token,
          refreshToken: payload.refresh_token,
          user: payload.user,
        }),
      setUser: (user) => set({ user }),
      setAccessToken: (accessToken) => set({ accessToken }),
      clear: () => set({ accessToken: null, refreshToken: null, user: null }),
      setHydrated: () => set({ hydrated: true }),
    }),
    {
      name: "faith-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated();
      },
    },
  ),
);

// يختار الصفحة الرئيسية حسب دور المستخدم.
export function homeFor(roles: string[]) {
  if (roles.includes("admin")) return "/app/admin";
  if (roles.includes("doctor")) return "/app/doctor";
  if (roles.includes("guardian")) return "/app/guardian";
  return "/app/patient";
}
