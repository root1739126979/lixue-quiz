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

export function EmployeesPage() {
  const [message, setMessage] = useState("");
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["employees"],
    queryFn: () => apiRequest<{ items: Employee[] }>("/admin/employees"),
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
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>工号</th>
            <th>手机号</th>
            <th>部门</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {data?.items.map((employee) => (
            <tr key={employee.id}>
              <td>{employee.name}</td>
              <td>{employee.work_no}</td>
              <td>{employee.phone}</td>
              <td>{employee.department}</td>
              <td>{employee.is_active ? "启用" : "停用"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
