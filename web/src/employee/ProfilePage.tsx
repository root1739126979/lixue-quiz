import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Profile = {
  name: string;
  department: string;
  total_points: number;
  answer_count: number;
  accuracy: number;
  wrong_count: number;
};

export function ProfilePage() {
  const { data } = useQuery({
    queryKey: ["profile"],
    queryFn: () => apiRequest<Profile>("/me"),
  });

  return (
    <section>
      <header className="page-header">
        <h1>个人中心</h1>
        <p>学习数据汇总</p>
      </header>
      <div className="profile-card">
        <h2>{data?.name}</h2>
        <p>{data?.department}</p>
        <div className="metrics-grid">
          <div className="metric">
            <span>总积分</span>
            <strong>{data?.total_points ?? 0}</strong>
          </div>
          <div className="metric">
            <span>累计答题</span>
            <strong>{data?.answer_count ?? 0}</strong>
          </div>
          <div className="metric">
            <span>正确率</span>
            <strong>{data?.accuracy ?? 0}%</strong>
          </div>
          <div className="metric">
            <span>错题数</span>
            <strong>{data?.wrong_count ?? 0}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}
