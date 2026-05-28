import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";
import type { RankingItem } from "../api/types";

export function RankingPage() {
  const [bankId, setBankId] = useState<number | null>(null);
  const path = bankId ? `/rankings/banks/${bankId}` : "/rankings/global";
  const { data } = useQuery({
    queryKey: ["ranking", bankId],
    queryFn: () => apiRequest<{ items: RankingItem[] }>(path),
  });

  return (
    <section>
      <header className="page-header">
        <h1>排行榜</h1>
        <p>按积分和正确率排序</p>
      </header>
      <div className="segmented">
        <button className={!bankId ? "active" : ""} onClick={() => setBankId(null)}>
          全局榜
        </button>
        <button className={bankId === 1 ? "active" : ""} onClick={() => setBankId(1)}>
          题库榜
        </button>
      </div>
      <ol className="ranking-list">
        {data?.items.map((item) => (
          <li key={`${item.rank}-${item.name}`}>
            <strong>{item.rank}</strong>
            <span>{item.name}</span>
            <span>{item.department}</span>
            <b>{item.points}</b>
          </li>
        ))}
      </ol>
    </section>
  );
}
