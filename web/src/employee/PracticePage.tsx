import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { apiRequest } from "../api/client";
import type { PracticeQuestion } from "../api/types";

type Feedback = {
  is_correct: boolean;
  correct_answer: string;
  correct_answer_text: string;
  explanation: string;
  wrong_question_status: "none" | "open" | "mastered";
  points_awarded: number;
};

const typeLabels: Record<PracticeQuestion["question_type"], string> = {
  single: "单选题",
  multiple: "多选题",
  judgment: "判断题",
};

const typeHints: Record<PracticeQuestion["question_type"], string> = {
  single: "只选择一个答案",
  multiple: "可选择多个答案，提交时会自动按字母排序",
  judgment: "判断题按题目选项选择",
};

export function PracticePage() {
  const { bankId } = useParams();
  const [questionCount, setQuestionCount] = useState(10);
  const [questions, setQuestions] = useState<PracticeQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [aiContent, setAiContent] = useState("");
  const [aiRequested, setAiRequested] = useState(false);
  const [jumpOpen, setJumpOpen] = useState(false);
  const [completed, setCompleted] = useState(false);
  const question = questions[index];
  const selectedAnswer = useMemo(() => selected.slice().sort().join(","), [selected]);
  const startPractice = useMutation({
    mutationFn: () =>
      apiRequest<{ questions: PracticeQuestion[] }>("/practice/sessions", {
        method: "POST",
        body: JSON.stringify({ bank_id: Number(bankId), count: questionCount }),
      }),
    onSuccess: (result) => {
      setQuestions(result.questions);
      setIndex(0);
      setSelected([]);
      setFeedback(null);
      setAiContent("");
      setAiRequested(false);
      setJumpOpen(false);
      setCompleted(false);
    },
  });
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

  function resetQuestionState() {
    setFeedback(null);
    setAiContent("");
    setAiRequested(false);
    setSelected([]);
  }

  function toggle(label: string) {
    if (!question || feedback) return;
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
    if (index >= questions.length - 1) {
      setCompleted(true);
      return;
    }
    resetQuestionState();
    setIndex((value) => value + 1);
  }

  function jumpToQuestion(nextIndex: number) {
    resetQuestionState();
    setIndex(nextIndex);
    setJumpOpen(false);
    setCompleted(false);
  }

  function requestAiExplanation() {
    setAiRequested(true);
    loadAi.mutate();
  }

  if (!questions.length) {
    return (
      <section>
        <header className="page-header compact">
          <h1>练习答题</h1>
          <p>开始前选择本次练习题数</p>
        </header>
        <section className="panel practice-start">
          <label>
            本次练习题数
            <input
              max={50}
              min={1}
              onChange={(event) => setQuestionCount(Number(event.target.value))}
              type="number"
              value={questionCount}
            />
          </label>
          <div className="quick-counts">
            {[5, 10, 20, 50].map((count) => (
              <button
                className={questionCount === count ? "ghost-button active" : "ghost-button"}
                key={count}
                onClick={() => setQuestionCount(count)}
                type="button"
              >
                {count}题
              </button>
            ))}
          </div>
          <button disabled={startPractice.isPending} onClick={() => startPractice.mutate()} type="button">
            开始练习
          </button>
          {startPractice.error && <p className="error">{startPractice.error.message}</p>}
        </section>
      </section>
    );
  }

  if (completed) {
    return (
      <section>
        <header className="page-header compact">
          <h1>练习完成</h1>
          <p>本次共完成 {questions.length} 题</p>
        </header>
        <section className="panel center-stack">
          <p className="muted">可以重新开始一组练习，或返回题库选择其他题库。</p>
          <div className="actions">
            <button onClick={() => setQuestions([])} type="button">
              重新练习
            </button>
            <Link className="button-link" to="/banks">
              返回题库
            </Link>
          </div>
        </section>
      </section>
    );
  }

  if (!question) return <p>暂无题目</p>;

  return (
    <section>
      <header className="page-header compact">
        <div>
          <h1>练习答题</h1>
          <p>
            第 {index + 1} / {questions.length} 题
          </p>
        </div>
        <button className="secondary-button" onClick={() => setJumpOpen((value) => !value)} type="button">
          跳转题号
        </button>
      </header>
      {jumpOpen && (
        <section className="jump-panel">
          <h2>选择题号</h2>
          <div className="jump-grid">
            {questions.map((item, itemIndex) => (
              <button
                className={itemIndex === index ? "jump-item active" : "jump-item"}
                key={item.id}
                onClick={() => jumpToQuestion(itemIndex)}
                type="button"
              >
                {itemIndex + 1}
              </button>
            ))}
          </div>
        </section>
      )}
      <article className="question-panel">
        <div className="question-meta">
          <span className="type-badge">题型：{typeLabels[question.question_type]}</span>
          <span>{typeHints[question.question_type]}</span>
        </div>
        <h2>{question.stem}</h2>
        <div className="option-list">
          {question.options.map((option) => (
            <button
              className={selected.includes(option.label) ? "option selected" : "option"}
              disabled={Boolean(feedback)}
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
      {submitAnswer.error && <p className="error">{submitAnswer.error.message}</p>}
      {feedback && (
        <section className="feedback-split">
          <article className="feedback-card answer-card">
            <h2>{feedback.is_correct ? "回答正确" : "回答错误"}</h2>
            <div className="answer-compare">
              <div>
                <span>你的答案</span>
                <strong>{selectedAnswer || "未选择"}</strong>
              </div>
              <div>
                <span>正确答案</span>
                <strong>{feedback.correct_answer}</strong>
              </div>
            </div>
            <p>本次积分：{feedback.points_awarded}</p>
            <p>错题状态：{formatWrongStatus(feedback.wrong_question_status)}</p>
          </article>
          <article className="feedback-card analysis-card">
            <h2>本题目解析</h2>
            {feedback.correct_answer_text && <p>{feedback.correct_answer_text}</p>}
            <p>{feedback.explanation || "暂无原解析"}</p>
          </article>
          {aiRequested && (
            <article className="feedback-card ai-card">
              <h2>AI讲解</h2>
              {loadAi.isPending && <p className="muted">正在生成讲解...</p>}
              {loadAi.error && <p className="error">{loadAi.error.message}</p>}
              {aiContent && <div className="ai-box">{aiContent}</div>}
            </article>
          )}
          <div className="actions">
            <button disabled={loadAi.isPending} onClick={requestAiExplanation} type="button">
              AI讲解
            </button>
            <button onClick={nextQuestion} type="button">
              {index >= questions.length - 1 ? "完成练习" : "下一题"}
            </button>
          </div>
        </section>
      )}
    </section>
  );
}

function formatWrongStatus(status: Feedback["wrong_question_status"]) {
  if (status === "open") return "未掌握";
  if (status === "mastered") return "已掌握";
  return "无";
}
