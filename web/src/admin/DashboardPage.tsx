import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Dashboard = {
  participant_count: number;
  active_user_count: number;
  bank_accuracy: unknown[];
  top_wrong_questions: unknown[];
  exam_score_distribution: unknown[];
  ranking_preview: unknown[];
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
        <p>内测整体运营概览</p>
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
          <span>题库统计项</span>
          <strong>{data?.bank_accuracy.length ?? 0}</strong>
        </div>
        <div className="metric">
          <span>考试统计项</span>
          <strong>{data?.exam_score_distribution.length ?? 0}</strong>
        </div>
      </div>
      <section className="dashboard-note">
        <h2>个人学习数据</h2>
        <p>员工个人答题、正确率、积分和错题数据已移动到员工管理中的员工详情。</p>
      </section>
    </section>
  );
}
