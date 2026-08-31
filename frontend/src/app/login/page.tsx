"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { LogIn } from "lucide-react";

import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("operator");
  const [password, setPassword] = useState("operator12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(username, password);
      router.push("/operator");
    } catch {
      setError("Неверный логин или пароль.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-panel px-4">
      <form onSubmit={submit} className="w-full max-w-sm rounded-md border border-line bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Вход в кассу</h1>
        <div className="mt-6 space-y-4">
          <label className="block text-sm font-medium">
            Логин
            <input className="mt-1 h-11 w-full rounded-md border border-line px-3" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" autoFocus />
          </label>
          <label className="block text-sm font-medium">
            Пароль
            <input className="mt-1 h-11 w-full rounded-md border border-line px-3" value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </label>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
          <button disabled={loading} className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-accent px-4 font-semibold text-white disabled:opacity-60">
            <LogIn size={18} />
            {loading ? "Вход..." : "Войти"}
          </button>
        </div>
      </form>
    </main>
  );
}
