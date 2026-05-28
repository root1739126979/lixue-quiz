import { Download } from "lucide-react";
import { apiRequest } from "../api/client";

const exports = [
  { label: "用户学习汇总", path: "/api/admin/exports/users" },
  { label: "答题记录", path: "/api/admin/exports/answers" },
  { label: "考试成绩", path: "/api/admin/exports/exams" },
];

export function ExportsPage() {
  async function download(item: { label: string; path: string }) {
    const content = await apiRequest<string>(item.path.replace(/^\/api/, ""));
    const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${item.label}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section>
      <header className="page-header">
        <h1>数据导出</h1>
        <p>下载 CSV 报表</p>
      </header>
      <div className="card-list admin-list">
        {exports.map((item) => (
          <article className="card" key={item.path}>
            <h2>{item.label}</h2>
            <button className="button-link" onClick={() => download(item)} type="button">
              <Download size={18} />
              下载 CSV
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
