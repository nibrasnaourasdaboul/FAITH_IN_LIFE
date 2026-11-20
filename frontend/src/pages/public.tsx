import { Activity, Heart, Shield, UserRound, Users } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { PublicFooter, PublicHeader } from "@/components/shell";

const roles = [
  { to: "/register?role=patient", icon: Heart, tone: "bg-teal/10 text-teal", title: "forPatient", body: "forPatientBody", action: "enterPatient" },
  { to: "/register?role=doctor", icon: UserRound, tone: "bg-sky-100 text-sky-800", title: "forDoctor", body: "forDoctorBody", action: "enterDoctor" },
  { to: "/register?role=guardian", icon: Users, tone: "bg-orange-100 text-coral", title: "forCare", body: "forCareBody", action: "enterCare" },
] as const;

// تعرض الصفحة التعريفية الأولى للمنصة.
export function HomePage() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-cream">
      <PublicHeader />
      <main>
        <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-8 lg:grid-cols-2">
          <div className="order-2 lg:order-1">
            <div className="relative rounded-[32px] border border-teal/30 bg-white p-3 shadow-card">
              <div className="rounded-[26px] bg-[#d7ebe4] p-5">
                <div className="mb-6 flex items-center justify-between text-sm font-semibold text-teal">
                  <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-coral" />{t("todaySession")}</span>
                  <span>11:30</span>
                </div>
                <div className="relative mx-auto grid h-52 place-items-center">
                  <div className="h-40 w-24 rounded-full bg-coral/90" />
                  <div className="absolute bottom-6 h-3 w-40 rounded-full bg-teal/70" />
                  <div className="absolute start-4 top-2 rounded-2xl bg-white px-3 py-2 text-start shadow-card">
                    <p className="text-xs text-mist">{t("kneeAngle")}</p>
                    <p className="text-2xl font-extrabold">87°</p>
                  </div>
                </div>
                <div className="mt-4 flex items-end justify-between text-sm">
                  <span className="rounded-full bg-white px-3 py-1 font-bold text-teal">80%</span>
                  <span className="text-end">
                    <span className="block text-mist">{t("weeklyPlan")}</span>
                    <span className="font-bold">{t("sessionsOf")}</span>
                  </span>
                </div>
              </div>
              <div className="absolute -bottom-4 start-6 flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-card">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-teal/10 text-teal">✓</span>
                <span>
                  <span className="block text-sm font-bold">{t("progressNote")}</span>
                  <span className="text-xs text-mist">{t("progressHint")}</span>
                </span>
              </div>
            </div>
          </div>
          <div className="order-1 text-start lg:order-2">
            <p className="text-sm font-semibold text-teal">{t("homeEyebrow")}</p>
            <h1 className="mt-3 max-w-xl text-4xl font-extrabold leading-tight sm:text-5xl">{t("homeTitle")}</h1>
            <p className="mt-5 max-w-xl text-lg leading-8 text-mist">{t("homeLead")}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/start" className="inline-flex min-h-12 items-center rounded-full bg-teal px-5 font-semibold text-white">{t("discover")}</Link>
              <Link to="/how" className="inline-flex min-h-12 items-center rounded-full border border-line bg-white px-5 font-semibold">{t("howLink")}</Link>
            </div>
            <p className="mt-6 text-sm font-semibold text-teal">{t("recovering")}</p>
          </div>
        </section>

        <section className="mt-8 bg-teal-dark text-white">
          <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["+1,240", "statPeople"],
              ["94%", "statComfort"],
              ["3", "statRoles"],
              ["24/7", "statCare"],
            ].map(([value, key]) => (
              <div key={key} className="text-center">
                <p className="text-3xl font-extrabold">{value}</p>
                <p className="mt-1 text-sm text-white/75">{t(key)}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-16">
          <p className="text-sm font-semibold text-teal">{t("pathEyebrow")}</p>
          <h2 className="mt-2 max-w-xl text-4xl font-extrabold">{t("pathTitle")}</h2>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {[
              ["01", Activity, "step1", "step1Body"],
              ["02", Heart, "step2", "step2Body"],
              ["03", Shield, "step3", "step3Body"],
            ].map(([num, Icon, title, body]) => (
              <article key={String(title)} className="rounded-card bg-white p-6 shadow-card">
                <div className="flex items-center justify-between text-mist">
                  <span className="text-3xl font-bold">{num as string}</span>
                  <Icon className="text-coral" />
                </div>
                <h3 className="mt-8 text-xl font-extrabold">{t(title as string)}</h3>
                <p className="mt-2 leading-7 text-mist">{t(body as string)}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="bg-[#e7f0ea] py-16">
          <div className="mx-auto max-w-6xl px-4">
            <p className="text-center text-sm font-semibold text-teal">{t("rolesEyebrow")}</p>
            <h2 className="mt-2 text-center text-4xl font-extrabold">{t("rolesTitle")}</h2>
            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {roles.map((role) => (
                <article key={role.to} className="rounded-card bg-white p-6 shadow-card">
                  <span className={`grid h-12 w-12 place-items-center rounded-2xl ${role.tone}`}><role.icon /></span>
                  <h3 className="mt-6 text-xl font-extrabold">{t(role.title)}</h3>
                  <p className="mt-2 leading-7 text-mist">{t(role.body)}</p>
                  <Link to={role.to} className="mt-6 inline-flex font-semibold text-teal">{t(role.action)}</Link>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto grid max-w-6xl items-center gap-8 px-4 py-16 lg:grid-cols-2">
          <div className="rounded-card bg-sand p-8">
            <Shield className="text-teal" />
            <h2 className="mt-4 text-3xl font-extrabold">{t("privacyTitle")}</h2>
            <p className="mt-3 leading-8 text-mist">{t("privacyBody")}</p>
            <Link to="/privacy" className="mt-6 inline-flex min-h-12 items-center rounded-full bg-teal px-5 font-semibold text-white">{t("privacyCta")}</Link>
          </div>
          <div>
            <p className="text-sm font-semibold text-teal">{t("about")}</p>
            <h2 className="mt-2 text-4xl font-extrabold">{t("humanTitle")}</h2>
            <p className="mt-4 leading-8 text-mist">{t("humanBody")}</p>
            <div className="mt-6 flex flex-wrap gap-2">
              {[t("chipEncrypted"), t("chipDoctor"), t("chipHuman")].map((chip) => (
                <span key={chip} className="rounded-full bg-white px-4 py-2 text-sm font-semibold text-teal shadow-card">{chip}</span>
              ))}
            </div>
          </div>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}

// تطلب من الزائر اختيار دوره قبل الدخول.
export function RoleSelectPage() {
  const { t } = useTranslation();
  const cards = [
    { role: "patient", title: "rolePatient", body: "rolePatientBody", icon: Heart, tone: "bg-sand text-teal" },
    { role: "doctor", title: "roleDoctor", body: "roleDoctorBody", icon: UserRound, tone: "bg-[#efe7da] text-[#8a6232]" },
    { role: "guardian", title: "roleCare", body: "roleCareBody", icon: Users, tone: "bg-sand text-teal" },
  ];
  return (
    <div className="min-h-screen bg-cream">
      <PublicHeader />
      <main className="mx-auto max-w-6xl px-4 py-10 text-center">
        <p className="text-sm font-semibold text-teal">{t("chooseLead")}</p>
        <h1 className="mt-3 text-4xl font-extrabold sm:text-5xl">{t("chooseTitle")}</h1>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {cards.map((card) => (
            <Link key={card.role} to={`/login?role=${card.role}`} className="rounded-card bg-white p-6 text-start shadow-card transition hover:-translate-y-0.5">
              <span className={`grid h-14 w-14 place-items-center rounded-2xl ${card.tone}`}><card.icon /></span>
              <h2 className="mt-8 text-2xl font-extrabold">{t(card.title)}</h2>
              <p className="mt-2 text-mist">{t(card.body)}</p>
              <p className="mt-6 text-xs font-bold tracking-[0.16em] text-teal">{card.role.toUpperCase()}</p>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}

// تعرض صفحة نصية مثل كيف نساعد أو الخصوصية.
export function StoryPage({ title, body }: { title: string; body: string }) {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-cream">
      <PublicHeader />
      <main className="mx-auto max-w-3xl px-4 py-16 text-start">
        <h1 className="text-4xl font-extrabold">{t(title)}</h1>
        <p className="mt-6 text-lg leading-9 text-mist">{t(body)}</p>
      </main>
      <PublicFooter />
    </div>
  );
}
