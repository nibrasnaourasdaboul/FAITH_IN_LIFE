import { ArrowRight, Heart, Menu, X } from "lucide-react";
import { useState, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import { NavLink, Link, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { homeFor, useAuth } from "@/store/auth";

// يعرض شعار المنصة.
export function Logo({ light = false }: { light?: boolean }) {
  const { t } = useTranslation();
  return (
    <span className={`flex items-center gap-3 ${light ? "text-white" : "text-ink"}`}>
      <span className="grid h-11 w-11 place-items-center rounded-2xl bg-coral text-white">
        <Heart size={20} fill="currentColor" />
      </span>
      <span className="text-start leading-tight">
        <span className="block text-sm font-bold">{t("brand")}</span>
        <span className={`block text-[11px] tracking-[0.16em] ${light ? "text-white/70" : "text-mist"}`}>{t("brandEn")}</span>
      </span>
    </span>
  );
}

// يبدّل لغة الواجهة بين العربية والإنجليزية.
export function LanguageToggle({ light = false }: { light?: boolean }) {
  const { i18n, t } = useTranslation();
  const next = i18n.language.startsWith("en") ? "ar" : "en";
  return (
    <button
      className={`min-h-11 rounded-full px-3 text-sm font-semibold ${light ? "text-white" : "text-teal"}`}
      onClick={() => void i18n.changeLanguage(next)}
    >
      {t("language")}
    </button>
  );
}

// يعرض شريط الصفحات العامة.
export function PublicHeader() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  return (
    <header className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-5">
      <Link to="/" aria-label={t("brand")}>
        <Logo />
      </Link>
      <nav className="hidden items-center gap-6 text-sm font-semibold text-teal md:flex">
        <Link to="/how">{t("help")}</Link>
        <Link to="/about">{t("about")}</Link>
        <Link to="/privacy">{t("privacy")}</Link>
      </nav>
      <div className="flex items-center gap-2">
        <LanguageToggle />
        {user ? (
          <Link to={homeFor(user.roles)} className="hidden min-h-12 items-center rounded-full bg-teal px-4 text-sm font-semibold text-white sm:inline-flex">
            {t("goDash")}
          </Link>
        ) : (
          <>
            <Link to="/login" className="hidden min-h-12 items-center rounded-full border border-line bg-white px-4 text-sm font-semibold text-ink sm:inline-flex">
              {t("login")}
            </Link>
            <Link to="/start" className="inline-flex min-h-12 items-center gap-2 rounded-full bg-teal px-4 text-sm font-semibold text-white">
              {t("start")}
              <ArrowRight className="rtl:rotate-180" size={16} />
            </Link>
          </>
        )}
      </div>
    </header>
  );
}

// يعرض تذييل الصفحات العامة.
export function PublicFooter() {
  const { t } = useTranslation();
  return (
    <footer className="bg-teal-dark text-white">
      <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-4 py-8 md:flex-row md:items-center">
        <p className="text-sm text-white/80">© {new Date().getFullYear()} Faith in Life — {t("footerNote")}</p>
        <nav className="flex flex-wrap gap-5 text-sm font-semibold">
          <Link to="/how">{t("help")}</Link>
          <Link to="/privacy">{t("privacy")}</Link>
          <Link to="/start">{t("settings")}</Link>
        </nav>
        <Logo light />
      </div>
    </footer>
  );
}

// يعرض اللوحة الخضراء بجانب نماذج الدخول والتسجيل.
export function AuthPanel() {
  const { t } = useTranslation();
  return (
    <aside className="relative flex min-h-[280px] flex-col justify-between bg-teal p-8 text-white lg:min-h-full lg:w-[42%]">
      <div className="flex items-start justify-between">
        <Logo light />
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-white/10">
          <Heart />
        </span>
      </div>
      <div>
        <h2 className="max-w-xs text-4xl font-extrabold leading-tight">{t("panelTitle")}</h2>
        <p className="mt-4 max-w-sm text-white/80">{t("panelBody")}</p>
      </div>
      <p className="flex items-center gap-2 text-sm text-white/80">
        <span className="grid h-8 w-8 place-items-center rounded-full bg-white/10">✓</span>
        {t("privacyFirst")}
      </p>
    </aside>
  );
}

// يرسم القائمة الجانبية وإطار الصفحات الداخلية.
export function AppShell({
  items,
  settingsTo,
  children,
}: {
  items: { to: string; label: string; icon: ReactNode; end?: boolean }[];
  settingsTo: string;
  children: ReactNode;
}) {
  const { t, i18n } = useTranslation();
  const user = useAuth((state) => state.user);
  const clear = useAuth((state) => state.clear);
  const refreshToken = useAuth((state) => state.refreshToken);
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const locale = i18n.language.startsWith("en") ? "en" : "ar";
  const dateLabel = new Intl.DateTimeFormat(locale, { weekday: "long", day: "numeric", month: "long" }).format(new Date());

  // ينهي الجلسة ويعيد المستخدم إلى صفحة الدخول.
  async function signOut() {
    try {
      await api("/api/v1/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) });
    } catch {
      /* local sign-out still proceeds */
    }
    clear();
    navigate("/");
  }

  const sidebar = (
    <div className="flex h-full flex-col px-4 py-5 text-white">
      <Logo light />
      <p className="mt-8 px-2 text-xs text-white/60">{t("accountReady")}</p>
      <nav className="mt-3 flex flex-1 flex-col gap-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            onClick={() => setOpen(false)}
            className={({ isActive }) =>
              `flex min-h-12 items-center gap-3 rounded-2xl px-3 text-sm font-semibold ${isActive ? "bg-white/15" : "hover:bg-white/10"}`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-4 border-t border-white/15 pt-4">
        <NavLink to={settingsTo} onClick={() => setOpen(false)} className="flex min-h-12 items-center gap-3 rounded-2xl px-3 text-sm font-semibold hover:bg-white/10">
          {t("settings")}
        </NavLink>
        <button onClick={() => void signOut()} className="flex min-h-12 w-full items-center gap-3 rounded-2xl px-3 text-start text-sm font-semibold hover:bg-white/10">
          {t("logout")}
        </button>
        <div className="mt-3 flex items-center gap-3 rounded-2xl bg-white/10 p-3">
          <Avatar name={user?.full_name || ""} uri={user?.avatar_uri} />
          <div className="min-w-0 text-start">
            <p className="truncate text-sm font-bold">{user?.full_name}</p>
            <p className="truncate text-xs text-white/70">{user?.roles[0]}</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-cream lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="hidden bg-teal-dark lg:block">{sidebar}</aside>
      <div className="min-w-0">
        <div className="flex items-center justify-between px-4 py-4 lg:hidden">
          <button className="grid h-12 w-12 place-items-center rounded-2xl bg-white" onClick={() => setOpen(true)} aria-label="menu">
            <Menu />
          </button>
          <LanguageToggle />
        </div>
        {open ? (
          <div className="fixed inset-0 z-30 bg-ink/40 lg:hidden" onClick={() => setOpen(false)}>
            <div className="ms-auto h-full w-[min(100%,320px)] bg-teal-dark" onClick={(event) => event.stopPropagation()}>
              <button className="absolute end-3 top-3 grid h-11 w-11 place-items-center rounded-full bg-white text-ink" onClick={() => setOpen(false)}>
                <X size={18} />
              </button>
              {sidebar}
            </div>
          </div>
        ) : null}
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
          <div className="mb-6 hidden items-center justify-between lg:flex">
            <p className="text-sm text-mist">{dateLabel}</p>
            <LanguageToggle />
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

// يعرض صورة الحساب أو الحرف الأول من الاسم.
export function Avatar({ name, uri }: { name: string; uri?: string | null }) {
  if (uri) return <img src={uri} alt="" className="h-11 w-11 rounded-full object-cover" />;
  const letter = name.trim().charAt(0) || "•";
  return <span className="grid h-11 w-11 place-items-center rounded-full bg-sand font-bold text-teal">{letter}</span>;
}
