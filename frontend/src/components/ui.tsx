import { X } from "lucide-react";
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

type Toast = { id: number; message: string; tone: "ok" | "bad" };

const ToastContext = createContext<(message: string, tone?: "ok" | "bad") => void>(() => undefined);

// يعرض رسائل التنبيه العابرة أسفل الشاشة.
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = useCallback((message: string, tone: "ok" | "bad" = "ok") => {
    const id = Date.now() + Math.random();
    setToasts((current) => [...current, { id, message, tone }]);
    window.setTimeout(() => setToasts((current) => current.filter((item) => item.id !== id)), 4200);
  }, []);
  const value = useMemo(() => push, [push]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-4 start-4 z-50 flex w-[min(100%-2rem,24rem)] flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-2xl px-4 py-3 text-sm shadow-card ${toast.tone === "bad" ? "bg-ink text-white" : "bg-teal text-white"}`}
            role="status"
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

// يتيح لأي صفحة إظهار رسالة تنبيه.
export function useToast() {
  return useContext(ToastContext);
}

// يرسم زراً موحّداً في الواجهة.
export function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "soft" | "danger" }) {
  const styles = {
    primary: "bg-teal text-white hover:bg-teal-dark",
    ghost: "bg-white text-teal border border-line hover:bg-sand",
    soft: "bg-sand text-ink hover:bg-white",
    danger: "bg-white text-red-700 border border-red-200 hover:bg-red-50",
  }[variant];
  return (
    <button
      className={`inline-flex min-h-12 items-center justify-center gap-2 rounded-full px-5 text-base font-semibold transition disabled:opacity-60 ${styles} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

// يرسم حقل إدخال مع عنوانه.
export function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: ReactNode;
}) {
  return (
    <label className="block text-start">
      <span className="mb-2 block text-sm font-semibold text-ink">{label}</span>
      {children}
      {error ? <span className="mt-1 block text-sm text-red-700">{error}</span> : null}
    </label>
  );
}

export const inputClass =
  "min-h-12 w-full rounded-2xl border border-line bg-white px-4 text-base text-ink outline-none transition placeholder:text-mist/70 focus:border-teal";

// يرسم بطاقة بيضاء لمحتوى الصفحة.
export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-card bg-white p-5 shadow-card sm:p-6 ${className}`}>{children}</section>;
}

// يعرض شكلاً مؤقتاً أثناء تحميل البيانات.
export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-2xl bg-line/80 ${className}`} />;
}

// يفتح نافذة فوق الصفحة لإجراء مؤكد.
export function Modal({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-ink/40 p-4 sm:items-center" role="dialog" aria-modal="true">
      <div className="w-full max-w-lg rounded-card bg-cream p-5 shadow-card">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-xl font-bold">{title}</h2>
          <button className="grid h-11 w-11 place-items-center rounded-full bg-white" onClick={onClose} aria-label="close">
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
