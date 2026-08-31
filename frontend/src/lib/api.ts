import type { ApiError, Paginated, Product, Sale, SaleLineInput } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export function getToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("accessToken");
}

export function setTokens(access: string, refresh: string) {
  window.localStorage.setItem("accessToken", access);
  window.localStorage.setItem("refreshToken", refresh);
}

export function clearTokens() {
  window.localStorage.removeItem("accessToken");
  window.localStorage.removeItem("refreshToken");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers
    }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw data as ApiError;
  }
  return data as T;
}

export async function login(username: string, password: string) {
  const data = await request<{ access: string; refresh: string }>("/auth/token/", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
  setTokens(data.access, data.refresh);
  return data;
}

export async function searchProducts(query: string) {
  const params = new URLSearchParams({ is_active: "true" });
  if (query.trim()) params.set("q", query.trim());
  return request<Paginated<Product>>(`/products/?${params.toString()}`);
}

export async function createSale(items: SaleLineInput[], payment_method = "cash", comment = "") {
  const key = crypto.randomUUID();
  return request<Sale>("/sales/", {
    method: "POST",
    headers: { "Idempotency-Key": key },
    body: JSON.stringify({ items, payment_method, comment })
  });
}
