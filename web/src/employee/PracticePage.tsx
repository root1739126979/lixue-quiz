import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { apiRequest } from "../api/client";
import type { PracticeQuestion } from "../api/types";

type Feedback = {
  is_correct: boolean;
  correct_answer: string;
  correct_answer_text: string;
  explanation: string;
  points_awarded: number;
};

export function PracticePage() {
  const { bankId } = useParams();
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [aiContent, setAiContent] = useState("");
  const { data } = useQuery({
    queryKey: ["practice", bankId],
    queryFn: () =>
      apiRequest<{ questions: PracticeQuestion[] }>("/practice/sessions", {
        method: "POST",
        body: JSON.stringify({ bank_id: Number(bankId), count: 10 }),
      }),
  });
  const questions = data?.questions ?? [];
  const question = questions[index];
  const selectedAnswer = useMemo(() => selected.slice().sort().join(","), [selected]);
  const submitAnswer = useMutation({
    mutationFn: () =>
      apiRequest<Feedback>("/practice/answers", {
        method: "POST",
        body: JSON.stringify({ question_id: question.id, selected_answer: selectedAnswer }),
      }),
    onSuccess: setFeedback,
  });
  const loadAi = useMutation({
    mutationFn: () =>
      apiRequest<{ content: string }>(`/questions/${question.id}/ai-explanation`, { method: "POST" }),
    onSuccess: (result) => setAiContent(result.content),
  });

  if (!question) return <p>暂无题目</p>;

  function toggle(label: string) {
    if (question.question_type === "multiple") {
      setSelected((current) =>
        current.includes(label)
          ? current.filter((item) => item !== label)
          : [...current, label],
      );
    } else {
      setSelected([label]);
    }
  }

  function nextQuestion() {
    setFeedback(null);
    setAiContent("");
    setSelected([]);
    setIndex((value) => Math.min(value + 1, questions.length - 1));
  }

  return (
    <section>
      <header className="page-header compact">
        <h1>练习答题</h1>
        <p>
          第 {index + 1} / {questions.length} 题
        </p>
      </header>
      <article className="question-panel">
        <h2>{question.stem}</h2>
        <div className="option-list">
          {question.options.map((option) => (
            <button
              className={selected.includes(option.label) ? "option selected" : "option"}
              key={option.label}
              onClick={() => toggle(option.label)}
              type="button"
            >
              <strong>{option.label}</strong>
              <span>{option.content}</span>
            </button>
          ))}
        </div>
      </article>
      {!feedback && (
        <button disabled={!selected.length || submitAnswer.isPending} onClick={() => submitAnswer.mutate()}>
          提交答案
        </button>
      )}
      {feedback && (
        <section className="feedback">
          <h2>{feedback.is_correct ? "回答正确" : "回答错误"}</h2>
          <p>正确答案：{feedback.correct_answer}</p>
          <p>{feedback.correct_answer_text}</p>
          <p>{feedback.explanation || "暂无原解析"}</p>
          <p>本次积分：{feedback.points_awarded}</p>
          <div className="actions">
            <button onClick={() => loadAi.mutate()} type="button">
              AI讲解
            </button>
            <button onClick={nextQuestion} type="button">
              下一题
            </button>
          </div>
          {loadAi.error && <p className="error">{loadAi.error.message}</p>}
          {aiContent && <div className="ai-box">{aiContent}</div>}
        </section>
      )}
    </section>
  );
}
