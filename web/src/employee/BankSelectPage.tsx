import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";
import type { BankSummary } from "../api/types";

export function BankSelectPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["banks"],
    queryFn: () => apiRequest<{ items: BankSummary[] }>("/banks"),
  });

  return (
    <section>
      <header className="page-header">
        <h1>选择题库</h1>
        <p>按题库进入练习或模拟考试</p>
      </header>
      {isLoading && <p className="muted">加载中...</p>}
      {error && <p className="error">{error instanceof Error ? error.message : "加载失败"}</p>}
      <div className="card-list">
        {data?.items.map((bank) => (
          <article className="card" key={bank.id}>
            <h2>{bank.name}</h2>
            <p>{bank.description}</p>
            <div className="metrics">
              <span>{bank.question_count} 题</span>
              <span>正确率 {bank.accuracy}%</span>
              <span>{bank.points} 分</span>
            </div>
            <div className="actions">
              <Link to={`/practice/${bank.id}`}>开始练习</Link>
              <Link to={`/exam/${bank.id}`}>模拟考试</Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
