import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiRequest } from "../api/client";

export function AdminLoginPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await apiRequest<{ token: string }>("/admin/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      localStorage.setItem("lixue_admin_token", result.token);
      navigate("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    }
  }

  return (
    <main className="login-page">
      <section className="login-brand">
        <h1>砺学后台</h1>
        <p>管理题库、员工和学习数据</p>
      </section>
      <form className="panel" onSubmit={submit}>
        <label>
          管理员账号
          <input value={username} onChange={(event) => setUsername(event.target.value)} />
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
        <button type="submit">进入后台</button>
      </form>
    </main>
  );
}
