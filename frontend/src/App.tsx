import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Protected } from "@/components/guards";
import { api } from "@/lib/api";
import { DeniedPage, ForgotPage, LoginPage, NotFoundPage, RegisterPage, ResetPage, VerifyPage } from "@/pages/auth";
import { HomePage, RoleSelectPage, StoryPage } from "@/pages/public";
import { useAuth, type AuthUser } from "@/store/auth";
import {
  AdminHome,
  AdminLayout,
  AdminLicensesPage,
  AdminUsersPage,
  GuardianHome,
  GuardianLayout,
  DoctorHome,
  DoctorLayout,
  ModulePage,
  PatientHome,
  PatientLayout,
  PatientsPage,
  SettingsPage,
} from "@/pages/workspace";

// يستعيد جلسة المستخدم المحفوظة عند فتح التطبيق.
function Boot() {
  const hydrated = useAuth((state) => state.hydrated);
  const token = useAuth((state) => state.accessToken);
  const setUser = useAuth((state) => state.setUser);
  const clear = useAuth((state) => state.clear);
  useEffect(() => {
    if (useAuth.persist.hasHydrated()) useAuth.getState().setHydrated();
    return useAuth.persist.onFinishHydration(() => useAuth.getState().setHydrated());
  }, []);
  useEffect(() => {
    if (!hydrated || !token) return;
    api<AuthUser>("/api/v1/users/me").then(setUser).catch(() => clear());
  }, [hydrated, token, setUser, clear]);
  return null;
}

// يعرّف مسارات الصفحات العامة وصفحات الأدوار.
export function App() {
  return (
    <BrowserRouter>
      <Boot />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/start" element={<RoleSelectPage />} />
        <Route path="/how" element={<StoryPage title="howTitle" body="howBody" />} />
        <Route path="/about" element={<StoryPage title="aboutTitle" body="aboutBody" />} />
        <Route path="/privacy" element={<StoryPage title="privacyTitle" body="privacyPage" />} />
        <Route path="/help" element={<StoryPage title="howTitle" body="howBody" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-email" element={<VerifyPage />} />
        <Route path="/forgot-password" element={<ForgotPage />} />
        <Route path="/reset-password" element={<ResetPage />} />
        <Route path="/unauthorized" element={<DeniedPage />} />

        <Route path="/app/patient" element={<Protected roles={["patient"]}><PatientLayout /></Protected>}>
          <Route index element={<PatientHome />} />
          <Route path="record" element={<ModulePage title="record" />} />
          <Route path="plan" element={<ModulePage title="plan" />} />
          <Route path="sessions" element={<ModulePage title="sessions" />} />
          <Route path="exercises" element={<ModulePage title="exercises" />} />
          <Route path="appointments" element={<ModulePage title="appointments" />} />
          <Route path="chat" element={<ModulePage title="chat" />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="/app/doctor" element={<Protected roles={["doctor"]}><DoctorLayout /></Protected>}>
          <Route index element={<DoctorHome />} />
          <Route path="patients" element={<PatientsPage />} />
          <Route path="motion" element={<ModulePage title="motion" />} />
          <Route path="community" element={<ModulePage title="community" />} />
          <Route path="knowledge" element={<ModulePage title="knowledge" />} />
          <Route path="chats" element={<ModulePage title="chats" />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="/app/guardian" element={<Protected roles={["guardian"]}><GuardianLayout /></Protected>}>
          <Route index element={<GuardianHome />} />
          <Route path="reports" element={<ModulePage title="reports" />} />
          <Route path="alerts" element={<ModulePage title="alerts" />} />
          <Route path="session" element={<ModulePage title="watch" />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="/app/admin" element={<Protected roles={["admin"]}><AdminLayout /></Protected>}>
          <Route index element={<AdminHome />} />
          <Route path="users" element={<AdminUsersPage />} />
          <Route path="licenses" element={<AdminLicensesPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="/app" element={<Navigate to="/" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
