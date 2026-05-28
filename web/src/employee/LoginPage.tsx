import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api/client";

export function LoginPage() {
  const navigate = useNavigate();
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await apiRequest<{ token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ account, password }),
      });
      localStorage.setItem("lixue_employee_token", result.token);
      navigate("/banks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    }
  }

  return (
    <main className="login-page">
      <section className="login-brand">
        <h1>砺学</h1>
        <p>多题库学习刷题平台</p>
      </section>
      <form onSubmit={submit} className="panel">
        <label>
          工号或手机号
          <input value={account} onChange={(event) => setAccount(event.target.value)} />
        </label>
        <label>
          密码
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            type="password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">登录</button>
      </form>
    </main>
  );
}
