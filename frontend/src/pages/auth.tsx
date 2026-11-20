import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { z } from "zod";
import { AuthPanel, LanguageToggle, Logo } from "@/components/shell";
import { Button, Field, inputClass, useToast } from "@/components/ui";
import { ApiError, api, type AuthResult } from "@/lib/api";
import { homeFor, useAuth, type Role } from "@/store/auth";

// يختار نص الخطأ المناسب لفشل الشبكة أو فشل البريد.
function authMessage(error: unknown, fallback: string, network: string, mail: string) {
  if (error instanceof ApiError && error.code === "network") return network;
  if (error instanceof ApiError && (error.code === "email_not_configured" || error.code === "email_failed")) return mail;
  return error instanceof Error ? error.message : fallback;
}

// يحوّل الدور القادم من الرابط إلى دور معروف.
function roleOf(value: string | null): Role {
  if (value === "doctor" || value === "guardian" || value === "patient") return value;
  return "patient";
}

// يرتب نموذج المصادقة بجانب اللوحة التعريفية.
function AuthFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#efeae1] px-4 py-8">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl overflow-hidden rounded-[32px] bg-white shadow-card">
        <AuthPanel />
        <div className="relative flex-1 p-6 sm:p-10">
          <div className="mb-6 flex items-center justify-between">
            <LanguageToggle />
            <Link to="/" className="lg:hidden"><Logo /></Link>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}

// تعرض نموذج تسجيل الدخول.
export function LoginPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const role = roleOf(params.get("role"));
  const navigate = useNavigate();
  const setSession = useAuth((state) => state.setSession);
  const toast = useToast();
  const [show, setShow] = useState(false);
  const schema = z.object({
    email: z.string().email(),
    password: z.string().min(1),
  });
  const form = useForm<z.infer<typeof schema>>({ resolver: zodResolver(schema) });

  // يرسل بيانات الدخول ويفتح مساحة الدور.
  async function onSubmit(values: z.infer<typeof schema>) {
    try {
      const result = await api<AuthResult>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify(values),
      });
      setSession(result);
      navigate(result.home || homeFor(result.user.roles));
    } catch (error) {
      if (error instanceof ApiError && error.code === "email_not_verified") {
        navigate(`/verify-email?email=${encodeURIComponent(values.email)}`);
        return;
      }
      const message = error instanceof ApiError && error.code === "network" ? t("serverDown") : error instanceof Error ? error.message : t("loading");
      toast(message, "bad");
    }
  }

  return (
    <AuthFrame>
      <Link to="/start" className="text-sm font-semibold text-teal">{t("changeRole")}</Link>
      <p className="mt-6 text-sm font-semibold text-teal">{t(`role${role === "guardian" ? "Care" : role === "doctor" ? "Doctor" : "Patient"}`)}</p>
      <h1 className="mt-2 text-4xl font-extrabold">{t("welcomeBack")}</h1>
      <p className="mt-2 text-mist">{t("loginLead")}</p>
      <form className="mt-8 space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
        <Field label={t("email")} error={form.formState.errors.email?.message}>
          <input className={inputClass} type="email" autoComplete="email" {...form.register("email")} />
        </Field>
        <Field label={t("password")} error={form.formState.errors.password?.message}>
          <div className="relative">
            <input className={inputClass} type={show ? "text" : "password"} autoComplete="current-password" {...form.register("password")} />
            <button type="button" className="absolute end-3 top-3 text-sm font-semibold text-teal" onClick={() => setShow((value) => !value)}>{show ? t("hide") : t("show")}</button>
          </div>
        </Field>
        <div className="text-start">
          <Link to="/forgot-password" className="text-sm font-semibold text-teal">{t("forgot")}</Link>
        </div>
        <Button className="w-full" disabled={form.formState.isSubmitting}>{t("login")}</Button>
      </form>
      <p className="mt-6 text-sm text-mist">
        {t("noAccount")} <Link className="font-bold text-teal" to={`/register?role=${role}`}>{t("createOne")}</Link>
      </p>
    </AuthFrame>
  );
}

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(72),
  full_name: z.string().min(2),
  phone: z.string().optional(),
  accepted_privacy: z.literal(true),
  birth_date: z.string().optional(),
  gender: z.string().optional(),
  national_id: z.string().optional(),
  occupation: z.string().optional(),
  work_posture_notes: z.string().optional(),
  health_condition: z.string().optional(),
  pain_level: z.coerce.number().min(0).max(10).optional(),
  medical_history: z.string().optional(),
  medical_title: z.string().optional(),
  specialization: z.string().optional(),
  years_of_experience: z.coerce.number().min(0).max(80).optional(),
  clinic_name: z.string().optional(),
  license_number: z.string().optional(),
  issuing_authority: z.string().optional(),
  relationship_type: z.string().optional(),
  emergency_contact: z.boolean().optional(),
  patient_email: z.string().optional(),
}).superRefine((values, ctx) => {
  void values;
  void ctx;
});

// تعرض نموذج إنشاء الحساب حسب الدور المختار.
export function RegisterPage() {
  const { t, i18n } = useTranslation();
  const [params] = useSearchParams();
  const role = roleOf(params.get("role"));
  const navigate = useNavigate();
  const toast = useToast();
  const [show, setShow] = useState(false);
  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: { accepted_privacy: true, gender: "female", pain_level: 3, emergency_contact: true, relationship_type: "parent", years_of_experience: 1 },
  });
  const birth = form.watch("birth_date");
  const age = birth ? Math.max(0, new Date().getFullYear() - new Date(birth).getFullYear()) : null;

  // يرسل بيانات التسجيل ثم ينقل المستخدم لصفحة الرمز.
  async function onSubmit(values: z.infer<typeof registerSchema>) {
    const payload: Record<string, unknown> = {
      role,
      email: values.email,
      password: values.password,
      full_name: values.full_name,
      phone: values.phone || null,
      locale: i18n.language.startsWith("en") ? "en" : "ar",
      accepted_privacy: true,
    };
    if (role === "patient") {
      if (!values.birth_date || !values.health_condition) {
        toast(t("condition"), "bad");
        return;
      }
      payload.patient = {
        birth_date: values.birth_date,
        gender: values.gender || "undisclosed",
        national_id: values.national_id || null,
        occupation: values.occupation || null,
        work_posture_notes: values.work_posture_notes || null,
        health_condition: values.health_condition,
        pain_level: values.pain_level ?? 0,
        medical_history: values.medical_history || null,
      };
    }
    if (role === "doctor") {
      if (!values.specialization || !values.license_number || !values.issuing_authority || !values.medical_title) {
        toast(t("license"), "bad");
        return;
      }
      payload.doctor = {
        medical_title: values.medical_title,
        specialization: values.specialization,
        years_of_experience: values.years_of_experience ?? 0,
        clinic_name: values.clinic_name || null,
        license_number: values.license_number,
        issuing_authority: values.issuing_authority,
      };
    }
    if (role === "guardian") {
      payload.guardian = {
        relationship_type: values.relationship_type || "other",
        emergency_contact: Boolean(values.emergency_contact),
        patient_email: values.patient_email || null,
      };
    }
    try {
      await api("/api/v1/auth/register", { method: "POST", body: JSON.stringify(payload) });
      navigate(`/verify-email?email=${encodeURIComponent(values.email)}`);
    } catch (error) {
      toast(authMessage(error, t("loading"), t("serverDown"), t("emailFailed")), "bad");
    }
  }

  return (
    <AuthFrame>
      <Link to="/start" className="text-sm font-semibold text-teal">{t("changeRole")}</Link>
      <p className="mt-6 text-sm font-semibold text-teal">{t(`role${role === "guardian" ? "Care" : role === "doctor" ? "Doctor" : "Patient"}`)}</p>
      <h1 className="mt-2 text-4xl font-extrabold">{t("createAccount")}</h1>
      <p className="mt-2 text-mist">{t("registerLead")}</p>
      <form className="mt-8 space-y-4" onSubmit={form.handleSubmit(onSubmit)}>
        <Field label={t("email")}><input className={inputClass} type="email" {...form.register("email")} /></Field>
        <Field label={t("fullName")}><input className={inputClass} {...form.register("full_name")} /></Field>
        <Field label={t("phone")}><input className={inputClass} {...form.register("phone")} /></Field>
        <Field label={t("password")}>
          <div className="relative">
            <input className={inputClass} type={show ? "text" : "password"} {...form.register("password")} />
            <button type="button" className="absolute end-3 top-3 text-sm font-semibold text-teal" onClick={() => setShow((value) => !value)}>{show ? t("hide") : t("show")}</button>
          </div>
        </Field>
        {role === "patient" ? (
          <>
            <Field label={`${t("birthDate")}${age !== null ? ` · ${t("age")} ${age}` : ""}`}>
              <input className={inputClass} type="date" {...form.register("birth_date")} />
            </Field>
            <Field label={t("gender")}>
              <select className={inputClass} {...form.register("gender")}>
                <option value="female">{t("female")}</option>
                <option value="male">{t("male")}</option>
                <option value="undisclosed">{t("undisclosed")}</option>
              </select>
            </Field>
            <Field label={`${t("nationalId")} (${t("optional")})`}><input className={inputClass} {...form.register("national_id")} /></Field>
            <Field label={t("occupation")}><input className={inputClass} {...form.register("occupation")} /></Field>
            <Field label={t("posture")}><input className={inputClass} {...form.register("work_posture_notes")} /></Field>
            <Field label={t("condition")}><input className={inputClass} {...form.register("health_condition")} /></Field>
            <Field label={t("pain")}><input className={inputClass} type="number" min={0} max={10} {...form.register("pain_level")} /></Field>
            <Field label={t("history")}><textarea className={`${inputClass} min-h-28 py-3`} {...form.register("medical_history")} /></Field>
          </>
        ) : null}
        {role === "doctor" ? (
          <>
            <Field label={t("titleField")}><input className={inputClass} {...form.register("medical_title")} /></Field>
            <Field label={t("specialty")}><input className={inputClass} {...form.register("specialization")} /></Field>
            <Field label={t("years")}><input className={inputClass} type="number" min={0} {...form.register("years_of_experience")} /></Field>
            <Field label={t("clinic")}><input className={inputClass} {...form.register("clinic_name")} /></Field>
            <Field label={t("license")}><input className={inputClass} {...form.register("license_number")} /></Field>
            <Field label={t("authority")}><input className={inputClass} {...form.register("issuing_authority")} /></Field>
          </>
        ) : null}
        {role === "guardian" ? (
          <>
            <Field label={t("relation")}>
              <select className={inputClass} {...form.register("relationship_type")}>
                <option value="parent">{t("parent")}</option>
                <option value="child">{t("child")}</option>
                <option value="spouse">{t("spouse")}</option>
                <option value="sibling">{t("sibling")}</option>
                <option value="other">{t("other")}</option>
              </select>
            </Field>
            <label className="flex min-h-12 items-center gap-3 text-sm font-semibold">
              <input type="checkbox" {...form.register("emergency_contact")} /> {t("emergency")}
            </label>
            <Field label={`${t("patientEmail")} (${t("optional")})`}><input className={inputClass} type="email" {...form.register("patient_email")} /></Field>
          </>
        ) : null}
        <label className="flex items-start gap-3 text-sm">
          <input type="checkbox" className="mt-1 h-5 w-5" {...form.register("accepted_privacy")} />
          <span>{t("agree")}</span>
        </label>
        <Button className="w-full" disabled={form.formState.isSubmitting}>{t("createAction")}</Button>
      </form>
      <p className="mt-6 text-sm text-mist">{t("haveAccount")} <Link className="font-bold text-teal" to={`/login?role=${role}`}>{t("login")}</Link></p>
    </AuthFrame>
  );
}

// تعرض خانة إدخال رمز التحقق القادم من البريد.
export function VerifyPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const email = params.get("email") || "";
  const navigate = useNavigate();
  const setSession = useAuth((state) => state.setSession);
  const toast = useToast();
  const [code, setCode] = useState("");

  // يرسل الرمز ويفتح الحساب بعد نجاح التحقق.
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    try {
      const result = await api<AuthResult>("/api/v1/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ email, code }),
      });
      setSession(result);
      navigate(result.home || homeFor(result.user.roles));
    } catch (error) {
      toast(authMessage(error, t("loading"), t("serverDown"), t("emailFailed")), "bad");
    }
  }

  return (
    <AuthFrame>
      <h1 className="text-4xl font-extrabold">{t("verifyTitle")}</h1>
      <p className="mt-2 text-mist">{t("verifyLead")}</p>
      <p className="mt-2 font-semibold">{email}</p>
      <form className="mt-8 space-y-4" onSubmit={submit}>
        <Field label={t("code")}>
          <input className={`${inputClass} text-center text-2xl tracking-[0.4em]`} inputMode="numeric" maxLength={6} value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))} />
        </Field>
        <Button className="w-full">{t("verifyAction")}</Button>
      </form>
      <button
        className="mt-4 text-sm font-semibold text-teal"
        onClick={async () => {
          try {
            await api("/api/v1/auth/resend-otp", { method: "POST", body: JSON.stringify({ email, purpose: "verify" }) });
            setCode("");
            toast(t("codeSent"));
          } catch (error) {
            toast(authMessage(error, t("loading"), t("serverDown"), t("emailFailed")), "bad");
          }
        }}
      >
        {t("resend")}
      </button>
    </AuthFrame>
  );
}

// تطلب البريد لإرسال رمز استعادة كلمة المرور.
export function ForgotPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const toast = useToast();
  const [email, setEmail] = useState("");
  return (
    <AuthFrame>
      <h1 className="text-4xl font-extrabold">{t("forgotTitle")}</h1>
      <p className="mt-2 text-mist">{t("forgotLead")}</p>
      <form
        className="mt-8 space-y-4"
        onSubmit={async (event) => {
          event.preventDefault();
          try {
            await api("/api/v1/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
            toast(t("codeSent"));
            navigate(`/reset-password?email=${encodeURIComponent(email)}`);
          } catch (error) {
            toast(authMessage(error, t("loading"), t("serverDown"), t("emailFailed")), "bad");
          }
        }}
      >
        <Field label={t("email")}><input className={inputClass} type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></Field>
        <Button className="w-full">{t("sendCode")}</Button>
      </form>
    </AuthFrame>
  );
}

// تستقبل الرمز وكلمة المرور الجديدة.
export function ResetPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [email, setEmail] = useState(params.get("email") || "");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  return (
    <AuthFrame>
      <h1 className="text-4xl font-extrabold">{t("resetTitle")}</h1>
      <p className="mt-2 text-mist">{t("resetLead")}</p>
      <form
        className="mt-8 space-y-4"
        onSubmit={async (event) => {
          event.preventDefault();
          try {
            await api("/api/v1/auth/reset-password", {
              method: "POST",
              body: JSON.stringify({ email, code, new_password: password }),
            });
            toast(t("saved"));
            navigate("/login");
          } catch (error) {
            toast(error instanceof Error ? error.message : t("loading"), "bad");
          }
        }}
      >
        <Field label={t("email")}><input className={inputClass} type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></Field>
        <Field label={t("code")}><input className={`${inputClass} tracking-[0.3em]`} value={code} onChange={(event) => setCode(event.target.value)} required /></Field>
        <Field label={t("newPassword")}><input className={inputClass} type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></Field>
        <Button className="w-full">{t("resetAction")}</Button>
      </form>
    </AuthFrame>
  );
}

// تعرض صفحة عند فتح مسار غير موجود.
export function NotFoundPage() {
  const { t } = useTranslation();
  return (
    <div className="grid min-h-screen place-items-center bg-cream px-4 text-center">
      <div>
        <h1 className="text-4xl font-extrabold">{t("notFoundTitle")}</h1>
        <p className="mt-3 text-mist">{t("notFoundBody")}</p>
        <Link to="/" className="mt-6 inline-flex min-h-12 items-center rounded-full bg-teal px-5 font-semibold text-white">{t("goHome")}</Link>
      </div>
    </div>
  );
}

// تعرض صفحة عند محاولة دخول مساحة غير مسموحة.
export function DeniedPage() {
  const { t } = useTranslation();
  const user = useAuth((state) => state.user);
  return (
    <div className="grid min-h-screen place-items-center bg-cream px-4 text-center">
      <div>
        <h1 className="text-4xl font-extrabold">{t("deniedTitle")}</h1>
        <p className="mt-3 text-mist">{t("deniedBody")}</p>
        <Link to={user ? homeFor(user.roles) : "/"} className="mt-6 inline-flex min-h-12 items-center rounded-full bg-teal px-5 font-semibold text-white">{t("goDash")}</Link>
      </div>
    </div>
  );
}
