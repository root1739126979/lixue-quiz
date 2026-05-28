import { ChangeEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Upload } from "lucide-react";
import { apiRequest } from "../api/client";

type Employee = {
  id: number;
  name: string;
  work_no: string;
  phone: string;
  department: string;
  is_active: boolean;
};

type EmployeeSummary = Employee & {
  answer_count: number;
  accuracy: number;
  total_points: number;
  open_wrong_count: number;
};

export function EmployeesPage() {
  const [message, setMessage] = useState("");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["employees"],
    queryFn: () => apiRequest<{ items: Employee[] }>("/admin/employees"),
  });
  const selectedEmployee = data?.items.find((employee) => employee.id === selectedEmployeeId);
  const { data: summary, error: summaryError } = useQuery({
    enabled: selectedEmployeeId !== null,
    queryKey: ["employee-summary", selectedEmployeeId],
    queryFn: () =>
      apiRequest<EmployeeSummary>(`/admin/employees/${selectedEmployeeId}/summary`),
  });
  const upload = useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return apiRequest<{ imported_count: number; errors: unknown[] }>("/admin/employees/import", {
        method: "POST",
        body: form,
      });
    },
    onSuccess: (result) => {
      setMessage(`导入 ${result.imported_count} 人，错误 ${result.errors.length} 行`);
      queryClient.invalidateQueries({ queryKey: ["employees"] });
      if (selectedEmployeeId !== null) {
        queryClient.invalidateQueries({ queryKey: ["employee-summary", selectedEmployeeId] });
      }
    },
  });

  function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) upload.mutate(file);
  }

  return (
    <section>
      <header className="page-header">
        <h1>员工管理</h1>
        <label className="file-button">
          <Upload size={18} />
          导入员工
          <input accept=".csv,.xlsx" onChange={onFile} type="file" />
        </label>
      </header>
      {message && <p className="notice">{message}</p>}
      {upload.error && <p className="error">{upload.error.message}</p>}
      <div className="employee-layout">
        <table>
          <thead>
            <tr>
              <th>姓名</th>
              <th>工号</th>
              <th>手机号</th>
              <th>部门</th>
              <th>状态</th>
              <th>详情</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((employee) => (
              <tr
                className={selectedEmployeeId === employee.id ? "selected-row" : ""}
                key={employee.id}
              >
                <td>{employee.name}</td>
                <td>{employee.work_no}</td>
                <td>{employee.phone}</td>
                <td>{employee.department}</td>
                <td>{employee.is_active ? "启用" : "停用"}</td>
                <td>
                  <button
                    className="table-action"
                    onClick={() => setSelectedEmployeeId(employee.id)}
                    type="button"
                  >
                    查看
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <aside className="employee-detail">
          <h2>员工学习数据</h2>
          {!selectedEmployee && <p className="muted">选择一名员工后查看个人统计。</p>}
          {summaryError && <p className="error">{summaryError.message}</p>}
          {selectedEmployee && !summary && !summaryError && <p className="muted">正在加载...</p>}
          {summary && (
            <>
              <div className="employee-heading">
                <strong>{summary.name}</strong>
                <span>{summary.department || "未填写部门"}</span>
              </div>
              <div className="metrics-grid">
                <div className="metric">
                  <span>累计答题</span>
                  <strong>{summary.answer_count}</strong>
                </div>
                <div className="metric">
                  <span>整体正确率</span>
                  <strong>{summary.accuracy}%</strong>
                </div>
                <div className="metric">
                  <span>总积分</span>
                  <strong>{summary.total_points}</strong>
                </div>
                <div className="metric">
                  <span>未掌握错题</span>
                  <strong>{summary.open_wrong_count}</strong>
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </section>
  );
}
