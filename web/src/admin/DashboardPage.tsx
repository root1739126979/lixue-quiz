import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Dashboard = {
  participant_count: number;
  active_user_count: number;
  answer_count: number;
  overall_accuracy: number;
  open_wrong_count: number;
};

export function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => apiRequest<Dashboard>("/admin/dashboard"),
  });

  return (
    <section>
      <header className="page-header">
        <h1>数据看板</h1>
        <p>内测学习数据概览</p>
      </header>
      <div className="metrics-grid wide">
        <div className="metric">
          <span>参与人数</span>
          <strong>{data?.participant_count ?? 0}</strong>
        </div>
        <div className="metric">
          <span>活跃人数</span>
          <strong>{data?.active_user_count ?? 0}</strong>
        </div>
        <div className="metric">
          <span>累计答题</span>
          <strong>{data?.answer_count ?? 0}</strong>
        </div>
        <div className="metric">
          <span>整体正确率</span>
          <strong>{data?.overall_accuracy ?? 0}%</strong>
        </div>
        <div className="metric">
          <span>未掌握错题</span>
          <strong>{data?.open_wrong_count ?? 0}</strong>
        </div>
      </div>
    </section>
  );
}
