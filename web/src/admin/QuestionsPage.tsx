import { ChangeEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Upload } from "lucide-react";
import { apiRequest } from "../api/client";

type Bank = { id: number; name: string };
type Question = { id: number; source_no: string; stem: string; question_type: string; is_active: boolean };

export function QuestionsPage() {
  const queryClient = useQueryClient();
  const [bankId, setBankId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const { data: banks } = useQuery({
    queryKey: ["admin-banks"],
    queryFn: () => apiRequest<{ items: Bank[] }>("/admin/banks"),
  });
  const { data: questions } = useQuery({
    queryKey: ["admin-questions", bankId],
    queryFn: () =>
      apiRequest<{ items: Question[] }>(bankId ? `/admin/questions?bank_id=${bankId}` : "/admin/questions"),
  });
  const upload = useMutation({
    mutationFn: (file: File) => {
      if (!bankId) throw new Error("请先选择题库");
      const form = new FormData();
      form.append("file", file);
      return apiRequest<{ imported_count: number; errors: unknown[] }>(
        `/admin/banks/${bankId}/questions/import`,
        { method: "POST", body: form },
      );
    },
    onSuccess: (result) => {
      setMessage(`导入 ${result.imported_count} 题，错误 ${result.errors.length} 行`);
      queryClient.invalidateQueries({ queryKey: ["admin-questions"] });
    },
  });

  function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) upload.mutate(file);
  }

  return (
    <section>
      <header className="page-header">
        <h1>题目维护</h1>
        <label className="file-button">
          <Upload size={18} />
          导入题目
          <input accept=".csv" onChange={onFile} type="file" />
        </label>
      </header>
      <div className="toolbar">
        <select value={bankId ?? ""} onChange={(event) => setBankId(Number(event.target.value) || null)}>
          <option value="">全部题库</option>
          {banks?.items.map((bank) => (
            <option key={bank.id} value={bank.id}>
              {bank.name}
            </option>
          ))}
        </select>
      </div>
      {message && <p className="notice">{message}</p>}
      {upload.error && <p className="error">{upload.error.message}</p>}
      <table>
        <thead>
          <tr>
            <th>题号</th>
            <th>题型</th>
            <th>题干</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {questions?.items.map((question) => (
            <tr key={question.id}>
              <td>{question.source_no}</td>
              <td>{question.question_type}</td>
              <td>{question.stem}</td>
              <td>{question.is_active ? "启用" : "停用"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
