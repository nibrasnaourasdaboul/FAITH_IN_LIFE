import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bell,
  Calendar,
  Dumbbell,
  FolderHeart,
  Home,
  LayoutDashboard,
  MessageCircle,
  Shield,
  Users,
} from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, Outlet } from "react-router-dom";
import { AppShell, Avatar } from "@/components/shell";
import { Button, Card, Field, inputClass, Skeleton, useToast } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth, type AuthUser } from "@/store/auth";

const days = ["س", "ح", "ن", "ث", "ر", "خ", "ج"];

// يختار تحية الصباح أو المساء حسب الساعة.
function greetingKey() {
  const hour = new Date().getHours();
  return hour < 17 ? "goodMorning" : "goodEvening";
}

// يرسم قائمة مساحة المريض.
export function PatientLayout() {
  const { t } = useTranslation();
  const items = [
    { to: "/app/patient", label: t("overview"), icon: <Home size={18} />, end: true },
    { to: "/app/patient/record", label: t("record"), icon: <FolderHeart size={18} /> },
    { to: "/app/patient/plan", label: t("plan"), icon: <Dumbbell size={18} /> },
    { to: "/app/patient/sessions", label: t("sessions"), icon: <Calendar size={18} /> },
    { to: "/app/patient/exercises", label: t("exercises"), icon: <Dumbbell size={18} /> },
    { to: "/app/patient/appointments", label: t("appointments"), icon: <Calendar size={18} /> },
    { to: "/app/patient/chat", label: t("chat"), icon: <MessageCircle size={18} /> },
  ];
  return <AppShell items={items} settingsTo="/app/patient/settings"><Outlet /></AppShell>;
}

// يرسم قائمة مساحة الطبيب.
export function DoctorLayout() {
  const { t } = useTranslation();
  const items = [
    { to: "/app/doctor", label: t("overview"), icon: <Home size={18} />, end: true },
    { to: "/app/doctor/patients", label: t("patients"), icon: <Users size={18} /> },
    { to: "/app/doctor/motion", label: t("motion"), icon: <LayoutDashboard size={18} /> },
    { to: "/app/doctor/community", label: t("community"), icon: <Users size={18} /> },
    { to: "/app/doctor/knowledge", label: t("knowledge"), icon: <FolderHeart size={18} /> },
    { to: "/app/doctor/chats", label: t("chats"), icon: <MessageCircle size={18} /> },
  ];
  return <AppShell items={items} settingsTo="/app/doctor/settings"><Outlet /></AppShell>;
}

// يرسم قائمة مساحة الوصي.
export function GuardianLayout() {
  const { t } = useTranslation();
  const items = [
    { to: "/app/guardian", label: t("overview"), icon: <Home size={18} />, end: true },
    { to: "/app/guardian/reports", label: t("reports"), icon: <FolderHeart size={18} /> },
    { to: "/app/guardian/alerts", label: t("alerts"), icon: <Bell size={18} /> },
    { to: "/app/guardian/session", label: t("watch"), icon: <Calendar size={18} /> },
  ];
  return <AppShell items={items} settingsTo="/app/guardian/settings"><Outlet /></AppShell>;
}

// يرسم قائمة مساحة المدير.
export function AdminLayout() {
  const { t } = useTranslation();
  const items = [
    { to: "/app/admin", label: t("overview"), icon: <Home size={18} />, end: true },
    { to: "/app/admin/users", label: t("users"), icon: <Users size={18} /> },
    { to: "/app/admin/licenses", label: t("licenses"), icon: <Shield size={18} /> },
  ];
  return <AppShell items={items} settingsTo="/app/admin/settings"><Outlet /></AppShell>;
}

// يعرض عنوان الصفحة وشرحها المختصر.
export function PageTitle({ kicker, title, body }: { kicker: string; title: string; body?: string }) {
  return (
    <header className="mb-6 text-start">
      <p className="text-sm font-semibold text-teal">{kicker}</p>
      <h1 className="mt-1 text-3xl font-extrabold sm:text-4xl">{title}</h1>
      {body ? <p className="mt-2 text-mist">{body}</p> : null}
    </header>
  );
}

// تعرض ملخص يوم المريض.
export function PatientHome() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  const links = useQuery({ queryKey: ["links"], queryFn: () => api<LinkRow[]>("/api/v1/users/me/links") });
  const pending = (links.data || []).filter((link) => link.link_status === "pending");
  return (
    <div>
      <PageTitle kicker={t(greetingKey())} title={`${t(greetingKey())}، ${user?.full_name || ""}`} body={t("patientHello")} />
      {pending.length > 0 ? <LinkInbox rows={pending} /> : null}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="text-sm font-semibold text-mist">{t("commitment")}</p>
          <p className="mt-4 text-4xl font-extrabold">0%</p>
          <div className="mt-4 h-2 rounded-full bg-sand"><div className="h-2 w-0 rounded-full bg-teal" /></div>
          <p className="mt-3 text-sm text-mist">{t("noSessionsYet")}</p>
        </Card>
        <Card className="flex flex-col justify-between">
          <p className="text-sm font-semibold text-mist">{t("todaySession")}</p>
          <p className="py-8 text-mist">{t("noSessionsYet")}</p>
          <Button disabled>{t("sessions")}</Button>
        </Card>
        <Card>
          <p className="font-bold">{t("doctorMessage")}</p>
          <p className="mt-3 leading-7 text-mist">{t("noMessage")}</p>
        </Card>
        <Card>
          <p className="font-bold">{t("weekJourney")}</p>
          <div className="mt-4 grid grid-cols-7 gap-2">
            {days.map((day) => (
              <div key={day} className="grid h-16 place-items-end rounded-2xl bg-sand pb-2 text-sm font-bold text-mist">{day}</div>
            ))}
          </div>
        </Card>
      </div>
      <p className="mt-4 rounded-full bg-[#f8ebe3] px-4 py-3 text-sm text-[#8a4b32]">{t("safety")}</p>
    </div>
  );
}

// تعرض ملخص عمل الطبيب.
export function DoctorHome() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  const verified = Boolean(user?.profile.is_verified);
  return (
    <div>
      <PageTitle kicker={t(greetingKey())} title={`${t(greetingKey())}، ${user?.full_name || ""}`} body={t("doctorHello")} />
      {!verified ? <p className="mb-4 rounded-2xl bg-sand px-4 py-3 text-sm font-semibold text-teal">{t("licensePending")}</p> : <p className="mb-4 text-sm font-semibold text-teal">{t("licenseApproved")}</p>}
      <div className="grid gap-4 md:grid-cols-3">
        {[
          [t("patients"), "0", t("assigned")],
          [t("motion"), "0", t("reviews")],
          [t("comfort"), "—", t("noSessionsYet")],
        ].map(([label, value, hint]) => (
          <Card key={label}>
            <p className="text-sm text-mist">{label}</p>
            <p className="mt-3 text-4xl font-extrabold">{value}</p>
            <p className="mt-2 text-sm text-mist">{hint}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}

// تعرض ملخص متابعة الوصي.
export function GuardianHome() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  const links = useQuery({ queryKey: ["links"], queryFn: () => api<LinkRow[]>("/api/v1/users/me/links") });
  return (
    <div>
      <PageTitle kicker={t(greetingKey())} title={`${t("roleCare")}، ${user?.full_name || ""}`} body={t("careHello")} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="font-bold text-coral">{t("calm")}</p>
          <p className="mt-3 leading-7 text-mist">{t("calmBody")}</p>
          <Link to="/app/guardian/alerts" className="mt-4 inline-flex font-semibold text-teal">{t("openAlerts")}</Link>
        </Card>
        <Card>
          <p className="text-sm text-mist">{t("todaySession")}</p>
          <p className="py-6 text-mist">{t("noSessionsYet")}</p>
          <Link to="/app/guardian/session" className="inline-flex min-h-12 items-center rounded-full bg-coral px-5 font-semibold text-white">{t("watchSession")}</Link>
        </Card>
      </div>
      <div className="mt-4 grid gap-4 md:grid-cols-3">
        <Card><p className="font-bold">{t("careTeam")}</p><p className="mt-2 text-sm text-mist">{t("careTeamBody")}</p></Card>
        <Card><p className="font-bold">{t("alerts")}</p><p className="mt-2 text-sm text-mist">{t("calmBody")}</p></Card>
        <Card><p className="font-bold">{t("reports")}</p><p className="mt-2 text-sm text-mist">{t("emptyModule")}</p></Card>
      </div>
      <div className="mt-4">
        <LinkAsk />
        <div className="mt-4">{links.isLoading ? <Skeleton className="h-24" /> : <LinkList rows={links.data || []} />}</div>
      </div>
    </div>
  );
}

// تعرض ملخص مهام المدير.
export function AdminHome() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  return (
    <div>
      <PageTitle kicker={t("adminArea")} title={`${t(greetingKey())}، ${user?.full_name || ""}`} body={t("adminHello")} />
      <div className="grid gap-4 md:grid-cols-2">
        <Link to="/app/admin/users" className="rounded-card bg-white p-6 shadow-card"><Users /><h2 className="mt-4 text-2xl font-extrabold">{t("users")}</h2></Link>
        <Link to="/app/admin/licenses" className="rounded-card bg-white p-6 shadow-card"><Shield /><h2 className="mt-4 text-2xl font-extrabold">{t("licenses")}</h2></Link>
      </div>
    </div>
  );
}

// تعرض صفحة قسم سريري لم يُفعّل محتواه بعد.
export function ModulePage({ title }: { title: string }) {
  const { t } = useTranslation();
  return (
    <div>
      <PageTitle kicker={t("accountReady")} title={t(title)} />
      <Card>
        <p className="leading-8 text-mist">{t("emptyModule")}</p>
      </Card>
    </div>
  );
}

type LinkRow = {
  link_id: string;
  link_status: string | null;
  patient_name: string | null;
  guardian_name: string | null;
  relationship_type: string | null;
};

// تعرض طلبات الربط التي ينتظرها المريض.
function LinkInbox({ rows }: { rows: LinkRow[] }) {
  const { t } = useTranslation();
  const toast = useToast();
  const client = useQueryClient();
  const decide = useMutation({
    mutationFn: (input: { id: string; decision: string }) =>
      api(`/api/v1/users/me/links/${input.id}/decision`, { method: "POST", body: JSON.stringify({ decision: input.decision }) }),
    onSuccess: async () => {
      toast(t("saved"));
      await client.invalidateQueries({ queryKey: ["links"] });
    },
    onError: (error: Error) => toast(error.message, "bad"),
  });
  if (rows.length === 0) return null;
  return (
    <Card className="mb-4">
      <h2 className="text-lg font-extrabold">{t("pendingLinks")}</h2>
      <div className="mt-4 space-y-3">
        {rows.map((row) => (
          <div key={row.link_id} className="flex flex-col gap-3 rounded-2xl bg-sand p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-start">
              <p className="font-bold">{row.guardian_name}</p>
              <p className="text-sm text-mist">{row.relationship_type}</p>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => decide.mutate({ id: row.link_id, decision: "approved" })}>{t("approve")}</Button>
              <Button variant="ghost" onClick={() => decide.mutate({ id: row.link_id, decision: "rejected" })}>{t("reject")}</Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

// تعرض الروابط القائمة بين الوصي والمريض.
function LinkList({ rows }: { rows: LinkRow[] }) {
  const { t } = useTranslation();
  if (rows.length === 0) return <p className="text-sm text-mist">{t("noLinks")}</p>;
  return (
    <div className="space-y-2">
      {rows.map((row) => (
        <div key={row.link_id} className="flex items-center justify-between rounded-2xl bg-white px-4 py-3 shadow-card">
          <span className="font-semibold">{row.patient_name || row.guardian_name}</span>
          <span className="text-sm text-teal">{row.link_status}</span>
        </div>
      ))}
    </div>
  );
}

// يرسل طلب ربط الوصي بمريض عبر بريده أو هويته.
function LinkAsk() {
  const { t } = useTranslation();
  const toast = useToast();
  const client = useQueryClient();
  const [email, setEmail] = useState("");
  const [nationalId, setNationalId] = useState("");
  return (
    <Card>
      <h2 className="text-lg font-extrabold">{t("linkAsk")}</h2>
      <p className="mt-2 text-sm leading-7 text-mist">{t("linkHelp")}</p>
      <form
        className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]"
        onSubmit={async (event) => {
          event.preventDefault();
          try {
            await api("/api/v1/users/me/links", {
              method: "POST",
              body: JSON.stringify({ patient_email: email || null, national_id: nationalId || null }),
            });
            toast(t("requestSent"));
            setEmail("");
            setNationalId("");
            await client.invalidateQueries({ queryKey: ["links"] });
          } catch (error) {
            toast(error instanceof Error ? error.message : t("loading"), "bad");
          }
        }}
      >
        <input className={inputClass} placeholder={t("email")} value={email} onChange={(event) => setEmail(event.target.value)} />
        <input className={inputClass} placeholder={t("nationalId")} value={nationalId} onChange={(event) => setNationalId(event.target.value)} />
        <Button type="submit">{t("sendRequest")}</Button>
      </form>
    </Card>
  );
}

type Prefs = {
  medical_alerts_enabled?: boolean;
  session_reminders_enabled?: boolean;
  emergency_alerts_enabled?: boolean;
  community_share_enabled?: boolean;
};

// تعرض إعدادات الحساب والتنبيهات والجلسات.
export function SettingsPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const user = useAuth((state) => state.user);
  const setUser = useAuth((state) => state.setUser);
  const profile = (user?.profile || {}) as Prefs & { preferences?: Prefs };
  const prefs = profile.preferences || {};
  const [name, setName] = useState(user?.full_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const sessions = useQuery({ queryKey: ["sessions"], queryFn: () => api<SessionRow[]>("/api/v1/users/me/sessions") });
  const links = useQuery({ queryKey: ["links"], queryFn: () => api<LinkRow[]>("/api/v1/users/me/links") });
  const isPatient = user?.roles.includes("patient");
  const isGuardian = user?.roles.includes("guardian");

  // يحفظ تعديلات الملف الشخصي.
  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    const updated = await api<AuthUser>("/api/v1/users/me", { method: "PATCH", body: JSON.stringify({ full_name: name, phone }) });
    setUser(updated);
    toast(t("saved"));
  }

  // يحفظ مفاتيح التنبيه فور تغييرها.
  async function savePrefs(patch: Prefs) {
    await api("/api/v1/users/me/preferences", { method: "PATCH", body: JSON.stringify(patch) });
    const updated = await api<AuthUser>("/api/v1/users/me");
    setUser(updated);
    toast(t("saved"));
  }

  return (
    <div>
      <PageTitle kicker={t("settings")} title={t("settings")} body={t("privacyPage")} />
      <form onSubmit={saveProfile}>
        <Card>
          <h2 className="text-lg font-extrabold">{t("profile")}</h2>
          <div className="mt-4 flex items-center gap-4">
            <Avatar name={name} uri={user?.avatar_uri} />
            <label className="cursor-pointer text-sm font-semibold text-teal">
              {t("upload")}
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={async (event) => {
                  const file = event.target.files?.[0];
                  if (!file) return;
                  const body = new FormData();
                  body.append("file", file);
                  const updated = await api<AuthUser>("/api/v1/users/me/avatar", { method: "POST", body });
                  setUser(updated);
                  toast(t("saved"));
                }}
              />
            </label>
          </div>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <Field label={t("fullName")}><input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} /></Field>
            <Field label={t("email")}><input className={inputClass} value={user?.email || ""} disabled /></Field>
            <Field label={t("phone")}><input className={inputClass} value={phone} onChange={(event) => setPhone(event.target.value)} /></Field>
          </div>
          <Button className="mt-4" type="submit">{t("save")}</Button>
        </Card>
      </form>

      <Card className="mt-4">
        <h2 className="text-lg font-extrabold">{t("privacyNotices")}</h2>
        <div className="mt-4 divide-y divide-line">
          <Toggle label={t("sessionReminders")} checked={Boolean(prefs.session_reminders_enabled)} onChange={(value) => void savePrefs({ session_reminders_enabled: value })} />
          <Toggle label={t("progressAlerts")} checked={Boolean(prefs.medical_alerts_enabled)} onChange={(value) => void savePrefs({ medical_alerts_enabled: value })} />
          <Toggle label={t("emergencyAlerts")} checked={prefs.emergency_alerts_enabled !== false} onChange={(value) => void savePrefs({ emergency_alerts_enabled: value })} />
          {isPatient ? <Toggle label={t("communityShare")} checked={Boolean(profile.community_share_enabled)} onChange={(value) => void savePrefs({ community_share_enabled: value })} /> : null}
        </div>
      </Card>

      <Card className="mt-4">
        <h2 className="text-lg font-extrabold">{t("changePassword")}</h2>
        <form
          className="mt-4 grid gap-3 md:grid-cols-2"
          onSubmit={async (event) => {
            event.preventDefault();
            try {
              await api("/api/v1/users/me/password", { method: "POST", body: JSON.stringify({ current_password: current, new_password: next }) });
              setCurrent("");
              setNext("");
              toast(t("saved"));
            } catch (error) {
              toast(error instanceof Error ? error.message : t("loading"), "bad");
            }
          }}
        >
          <input className={inputClass} type="password" placeholder={t("currentPassword")} value={current} onChange={(event) => setCurrent(event.target.value)} required />
          <input className={inputClass} type="password" placeholder={t("newPassword")} value={next} onChange={(event) => setNext(event.target.value)} minLength={8} required />
          <Button type="submit">{t("save")}</Button>
        </form>
      </Card>

      {isPatient ? <div className="mt-4">{links.isLoading ? <Skeleton className="h-24" /> : <LinkInbox rows={(links.data || []).filter((row) => row.link_status === "pending")} />}</div> : null}
      {isGuardian ? <div className="mt-4"><LinkAsk /></div> : null}

      <Card className="mt-4">
        <h2 className="text-lg font-extrabold">{t("sessionsDevices")}</h2>
        <div className="mt-4 space-y-3">
          {sessions.isLoading ? <Skeleton className="h-16" /> : null}
          {(sessions.data || []).map((row) => (
            <div key={row.session_id} className="flex flex-col gap-2 rounded-2xl bg-sand p-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-start">
                <p className="text-sm font-semibold">{row.device_label}</p>
                <p className="text-xs text-mist">{row.ip_address} · {row.status === "active" ? t("active") : t("ended")}</p>
              </div>
              {row.status === "active" ? (
                <Button
                  variant="ghost"
                  onClick={async () => {
                    await api(`/api/v1/users/me/sessions/${row.session_id}`, { method: "DELETE" });
                    await sessions.refetch();
                  }}
                >
                  {t("endSession")}
                </Button>
              ) : null}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

// يرسم مفتاح تشغيل وإيقاف للإعداد.
function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex min-h-14 items-center justify-between gap-4 py-3 text-start">
      <span className="font-semibold">{label}</span>
      <input type="checkbox" className="h-6 w-11 accent-teal" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  );
}

type SessionRow = { session_id: string; device_label: string; ip_address: string | null; status: string | null };

type AdminUser = AuthUser;
type LicenseRow = {
  license_id: string;
  license_number: string | null;
  issuing_authority: string | null;
  doctor_name: string | null;
  email: string | null;
  medical_title: string | null;
  status: string | null;
};

// تعرض الحسابات وتتيح إيقافها أو إعادتها.
export function AdminUsersPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const [q, setQ] = useState("");
  const [reason, setReason] = useState("");
  const users = useQuery({
    queryKey: ["admin-users", q],
    queryFn: () => api<AdminUser[]>(`/api/v1/admin/users${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  });
  return (
    <div>
      <PageTitle kicker={t("adminArea")} title={t("users")} />
      <input className={`${inputClass} mb-4`} placeholder={t("search")} value={q} onChange={(event) => setQ(event.target.value)} />
      <Field label={t("reason")}><input className={inputClass} value={reason} onChange={(event) => setReason(event.target.value)} /></Field>
      <div className="mt-4 space-y-3">
        {users.isLoading ? <Skeleton className="h-24" /> : null}
        {(users.data || []).length === 0 && !users.isLoading ? <p className="text-mist">{t("noUsers")}</p> : null}
        {(users.data || []).map((account) => (
          <Card key={account.user_id}>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="text-start">
                <p className="font-extrabold">{account.full_name}</p>
                <p className="text-sm text-mist">{account.email} · {account.roles.join(", ")} · {account.account_status}</p>
              </div>
              <div className="flex gap-2">
                {account.account_status === "banned" ? (
                  <Button
                    variant="ghost"
                    onClick={async () => {
                      await api(`/api/v1/admin/users/${account.user_id}/unban`, { method: "POST" });
                      toast(t("saved"));
                      await users.refetch();
                    }}
                  >
                    {t("restore")}
                  </Button>
                ) : (
                  <Button
                    variant="danger"
                    onClick={async () => {
                      if (reason.trim().length < 3) {
                        toast(t("reason"), "bad");
                        return;
                      }
                      await api(`/api/v1/admin/users/${account.user_id}/ban`, { method: "POST", body: JSON.stringify({ reason }) });
                      toast(t("saved"));
                      await users.refetch();
                    }}
                  >
                    {t("ban")}
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

// تعرض تراخيص الأطباء وتتيح مراجعتها.
export function AdminLicensesPage() {
  const { t } = useTranslation();
  const toast = useToast();
  const [notes, setNotes] = useState("");
  const licenses = useQuery({ queryKey: ["licenses"], queryFn: () => api<LicenseRow[]>("/api/v1/admin/licenses") });
  return (
    <div>
      <PageTitle kicker={t("adminArea")} title={t("licenses")} />
      <Field label={t("notes")}><textarea className={`${inputClass} min-h-24 py-3`} value={notes} onChange={(event) => setNotes(event.target.value)} /></Field>
      <div className="mt-4 space-y-3">
        {(licenses.data || []).length === 0 && !licenses.isLoading ? <p className="text-mist">{t("noLicenses")}</p> : null}
        {(licenses.data || []).map((license) => (
          <Card key={license.license_id}>
            <p className="font-extrabold">{license.doctor_name}</p>
            <p className="text-sm text-mist">{license.medical_title} · {license.license_number} · {license.issuing_authority}</p>
            <div className="mt-3 flex gap-2">
              <Button
                onClick={async () => {
                  await api(`/api/v1/admin/licenses/${license.license_id}/review`, { method: "POST", body: JSON.stringify({ decision: "approved", notes }) });
                  toast(t("saved"));
                  await licenses.refetch();
                }}
              >
                {t("approve")}
              </Button>
              <Button
                variant="ghost"
                onClick={async () => {
                  await api(`/api/v1/admin/licenses/${license.license_id}/review`, { method: "POST", body: JSON.stringify({ decision: "rejected", notes }) });
                  toast(t("saved"));
                  await licenses.refetch();
                }}
              >
                {t("reject")}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

// تعرض قائمة مرضى الطبيب.
export function PatientsPage() {
  const { t } = useTranslation();
  const [q, setQ] = useState("");
  return (
    <div>
      <PageTitle kicker={t("roleDoctor")} title={t("patients")} />
      <Card>
        <input className={inputClass} placeholder={t("searchPatients")} value={q} onChange={(event) => setQ(event.target.value)} />
        {q ? null : <p className="mt-8 leading-8 text-mist">{t("noPatients")}</p>}
        {q ? <p className="mt-8 leading-8 text-mist">{t("noPatients")}</p> : null}
      </Card>
    </div>
  );
}
