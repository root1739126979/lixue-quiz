const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const ADMIN_TOKEN_KEY = "lixue_admin_token";
const EMPLOYEE_TOKEN_KEY = "lixue_employee_token";

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(path.startsWith("/admin") ? ADMIN_TOKEN_KEY : EMPLOYEE_TOKEN_KEY);
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail ?? message;
    } catch {
      const text = await response.text();
      if (text) message = text;
    }
    throw new Error(message);
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("text/csv")) {
    return (await response.text()) as T;
  }
  return response.json() as Promise<T>;
}
