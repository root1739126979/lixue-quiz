import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { apiRequest } from "../api/client";
import type { PracticeQuestion } from "../api/types";

type ExamAttempt = {
  attempt_id: number;
  questions: PracticeQuestion[];
  time_limit_minutes: number;
};

export function ExamPage() {
  const { bankId } = useParams();
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<{ score: number; correct_count: number; total_count: number } | null>(
    null,
  );
  const start = useMutation({
    mutationFn: () =>
      apiRequest<ExamAttempt>("/exams/attempts", {
        method: "POST",
        body: JSON.stringify({ bank_id: Number(bankId) }),
      }),
  });
  const submit = useMutation({
    mutationFn: () =>
      apiRequest<{ score: number; correct_count: number; total_count: number }>(
        `/exams/attempts/${start.data?.attempt_id}/submit`,
        {
          method: "POST",
          body: JSON.stringify({
            answers: Object.entries(answers).map(([question_id, selected_answer]) => ({
              question_id: Number(question_id),
              selected_answer,
            })),
          }),
        },
      ),
    onSuccess: setResult,
  });

  if (!start.data) {
    return (
      <section className="center-stack">
        <button onClick={() => start.mutate()}>开始模拟考试</button>
        {start.error && <p className="error">{start.error.message}</p>}
      </section>
    );
  }
  if (result) {
    return (
      <section>
        <h1>考试完成</h1>
        <div className="profile-card">
          <p>得分：{result.score}</p>
          <p>
            答对：{result.correct_count}/{result.total_count}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section>
      <header className="page-header compact">
        <h1>模拟考试</h1>
        <p>限时 {start.data.time_limit_minutes} 分钟</p>
      </header>
      {start.data.questions.map((question) => (
        <article className="question-panel" key={question.id}>
          <h2>{question.stem}</h2>
          <div className="option-list">
            {question.options.map((option) => (
              <button
                className={answers[question.id] === option.label ? "option selected" : "option"}
                key={option.label}
                onClick={() => setAnswers({ ...answers, [question.id]: option.label })}
                type="button"
              >
                <strong>{option.label}</strong>
                <span>{option.content}</span>
              </button>
            ))}
          </div>
        </article>
      ))}
      <button onClick={() => submit.mutate()}>交卷</button>
    </section>
  );
}
