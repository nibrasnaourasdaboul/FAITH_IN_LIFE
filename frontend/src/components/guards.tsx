import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth, type Role } from "@/store/auth";
import { Skeleton } from "./ui";

// يمنع فتح الصفحة قبل تسجيل الدخول أو إذا كان الدور غير مناسب.
export function Protected({ roles, children }: { roles?: Role[]; children: ReactNode }) {
  const hydrated = useAuth((state) => state.hydrated);
  const token = useAuth((state) => state.accessToken);
  const user = useAuth((state) => state.user);
  const location = useLocation();
  if (!hydrated) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 p-8">
        <Skeleton className="h-12 w-48" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }
  if (!token || !user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !roles.some((role) => user.roles.includes(role))) return <Navigate to="/unauthorized" replace />;
  return children;
}
