import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type Bank = {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  exam_question_count: number;
  exam_time_limit_minutes: number;
};

export function QuestionBanksPage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const { data, error: dataError, isLoading } = useQuery({
    queryKey: ["admin-banks"],
    queryFn: () => apiRequest<{ items: Bank[] }>("/admin/banks"),
  });
  const create = useMutation({
    mutationFn: () =>
      apiRequest<Bank>("/admin/banks", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          exam_question_count: 20,
          exam_time_limit_minutes: 30,
        }),
      }),
    onSuccess: () => {
      setName("");
      setDescription("");
      queryClient.invalidateQueries({ queryKey: ["admin-banks"] });
    },
  });
  const toggle = useMutation({
    mutationFn: (bank: Bank) =>
      apiRequest(`/admin/banks/${bank.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !bank.is_active }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-banks"] }),
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (name.trim() && !create.isPending) create.mutate();
  }

  return (
    <section>
      <header className="page-header">
        <h1>题库管理</h1>
        <p>创建、启用或停用题库</p>
      </header>
      <form className="inline-form" onSubmit={submit}>
        <input value={name} onChange={(event) => setName(event.target.value)} placeholder="题库名称" />
        <input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="说明" />
        <button disabled={!name.trim() || create.isPending} type="submit">
          {create.isPending ? "创建中..." : "创建题库"}
        </button>
      </form>
      {isLoading && <p className="notice">正在加载题库...</p>}
      {dataError && <p className="error">{dataError.message}</p>}
      {create.error && <p className="error">{create.error.message}</p>}
      {toggle.error && <p className="error">{toggle.error.message}</p>}
      {create.isSuccess && <p className="notice">题库已创建</p>}
      <div className="card-list admin-list">
        {data?.items.map((bank) => (
          <article className="card" key={bank.id}>
            <h2>{bank.name}</h2>
            <p>{bank.description}</p>
            <div className="metrics">
              <span>{bank.exam_question_count} 题考试</span>
              <span>{bank.exam_time_limit_minutes} 分钟</span>
              <span>{bank.is_active ? "启用" : "停用"}</span>
            </div>
            <button disabled={toggle.isPending} onClick={() => toggle.mutate(bank)}>
              {bank.is_active ? "停用" : "启用"}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
