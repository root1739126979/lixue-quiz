import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type WrongQuestion = {
  question_id: number;
  bank_name: string;
  stem: string;
  correct_answer: string;
  explanation: string;
  wrong_count: number;
};

export function WrongQuestionsPage() {
  const queryClient = useQueryClient();
  const { data } = useQuery({
    queryKey: ["wrong-questions"],
    queryFn: () => apiRequest<{ items: WrongQuestion[] }>("/wrong-questions"),
  });
  const master = useMutation({
    mutationFn: (questionId: number) =>
      apiRequest(`/wrong-questions/${questionId}/master`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wrong-questions"] }),
  });

  return (
    <section>
      <header className="page-header">
        <h1>错题库</h1>
        <p>重做并清理未掌握题目</p>
      </header>
      <div className="card-list">
        {data?.items.map((item) => (
          <article className="card" key={item.question_id}>
            <p className="muted">
              {item.bank_name} · 错 {item.wrong_count} 次
            </p>
            <h2>{item.stem}</h2>
            <p>正确答案：{item.correct_answer}</p>
            <p>{item.explanation || "暂无原解析"}</p>
            <button onClick={() => master.mutate(item.question_id)}>标记掌握</button>
          </article>
        ))}
      </div>
    </section>
  );
}
