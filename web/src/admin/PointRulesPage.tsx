import { FormEvent, useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiRequest } from "../api/client";

type PointRules = {
  answer_base_points: number;
  correct_bonus_points: number;
  wrong_retry_correct_points: number;
  exam_complete_points: number;
  daily_point_limit: number;
};

export function PointRulesPage() {
  const [rules, setRules] = useState<PointRules | null>(null);
  const { data } = useQuery({
    queryKey: ["point-rules"],
    queryFn: () => apiRequest<PointRules>("/admin/point-rules"),
  });
  const save = useMutation({
    mutationFn: () =>
      apiRequest<PointRules>("/admin/point-rules", {
        method: "PUT",
        body: JSON.stringify(rules),
      }),
  });

  useEffect(() => {
    if (data) setRules(data);
  }, [data]);

  function update(key: keyof PointRules, value: string) {
    setRules((current) => (current ? { ...current, [key]: Number(value) } : current));
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate();
  }

  if (!rules) return <p>加载中...</p>;

  return (
    <section>
      <header className="page-header">
        <h1>积分规则</h1>
        <p>规则变更只影响后续行为</p>
      </header>
      <form className="settings-form" onSubmit={submit}>
        {Object.entries(rules).map(([key, value]) => (
          <label key={key}>
            {labels[key as keyof PointRules]}
            <input
              min={0}
              onChange={(event) => update(key as keyof PointRules, event.target.value)}
              type="number"
              value={value}
            />
          </label>
        ))}
        <button type="submit">保存规则</button>
      </form>
      {save.isSuccess && <p className="notice">已保存</p>}
    </section>
  );
}

const labels: Record<keyof PointRules, string> = {
  answer_base_points: "答题基础分",
  correct_bonus_points: "答对额外分",
  wrong_retry_correct_points: "错题重做答对分",
  exam_complete_points: "完成考试分",
  daily_point_limit: "每日积分上限",
};
