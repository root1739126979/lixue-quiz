export type Option = {
  label: string;
  content: string;
};

export type BankSummary = {
  id: number;
  name: string;
  description: string;
  question_count: number;
  practiced_count: number;
  accuracy: number;
  points: number;
  has_exam: boolean;
};

export type PracticeQuestion = {
  id: number;
  question_type: "single" | "multiple" | "judgment";
  stem: string;
  options: Option[];
};

export type RankingItem = {
  rank: number;
  name: string;
  department: string;
  points: number;
  accuracy: number;
};
