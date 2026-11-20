import { useAuth, type AuthUser } from "@/store/auth";

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

type ErrorBody = {
  detail?: string | { code?: string; message?: string } | { msg?: string }[];
};

// يحوّل رد الخطأ القادم من الخادم إلى رسالة مفهومة.
function readError(status: number, body: ErrorBody) {
  const detail = body.detail;
  if (Array.isArray(detail)) {
    return new ApiError(status, detail.map((item) => item.msg).filter(Boolean).join(" "), "validation");
  }
  if (detail && typeof detail === "object") {
    return new ApiError(status, detail.message || "Request failed", detail.code);
  }
  if (typeof detail === "string") return new ApiError(status, detail);
  return new ApiError(status, "Request failed");
}

// يجدّد رمز الدخول إذا انتهت صلاحيته.
async function refreshAccess(): Promise<string | null> {
  const refreshToken = useAuth.getState().refreshToken;
  if (!refreshToken) return null;
  const response = await fetch("/api/v1/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    useAuth.getState().clear();
    return null;
  }
  const data = (await response.json()) as { access_token: string; refresh_token: string };
  useAuth.setState({ accessToken: data.access_token, refreshToken: data.refresh_token });
  return data.access_token;
}

// يرسل الطلب إلى الخادم ويُرجع البيانات أو يرمي الخطأ.
export async function api<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers);
  const token = useAuth.getState().accessToken;
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  let response: Response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch {
    throw new ApiError(0, "The server is not reachable.", "network");
  }
  if (response.status === 401 && retry && !path.includes("/auth/")) {
    const next = await refreshAccess();
    if (next) return api<T>(path, options, false);
  }
  if (response.status === 204) return undefined as T;
  const body = (await response.json().catch(() => ({}))) as ErrorBody & T;
  if (!response.ok) throw readError(response.status, body);
  return body as T;
}

export type AuthResult = {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
  home?: string;
};
