import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AdminLayout } from "./admin/AdminLayout";
import { AdminLoginPage } from "./admin/AdminLoginPage";
import { DashboardPage } from "./admin/DashboardPage";
import { EmployeesPage } from "./admin/EmployeesPage";
import { ExportsPage } from "./admin/ExportsPage";
import { LlmConfigPage } from "./admin/LlmConfigPage";
import { PointRulesPage } from "./admin/PointRulesPage";
import { QuestionBanksPage } from "./admin/QuestionBanksPage";
import { QuestionsPage } from "./admin/QuestionsPage";
import { BankSelectPage } from "./employee/BankSelectPage";
import { EmployeeLayout } from "./employee/EmployeeLayout";
import { ExamPage } from "./employee/ExamPage";
import { LoginPage } from "./employee/LoginPage";
import { PracticePage } from "./employee/PracticePage";
import { ProfilePage } from "./employee/ProfilePage";
import { RankingPage } from "./employee/RankingPage";
import { WrongQuestionsPage } from "./employee/WrongQuestionsPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route element={<EmployeeLayout />}>
          <Route path="/banks" element={<BankSelectPage />} />
          <Route path="/practice/:bankId" element={<PracticePage />} />
          <Route path="/wrong" element={<WrongQuestionsPage />} />
          <Route path="/ranking" element={<RankingPage />} />
          <Route path="/exam/:bankId" element={<ExamPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="employees" element={<EmployeesPage />} />
          <Route path="banks" element={<QuestionBanksPage />} />
          <Route path="questions" element={<QuestionsPage />} />
          <Route path="points" element={<PointRulesPage />} />
          <Route path="llm" element={<LlmConfigPage />} />
          <Route path="exports" element={<ExportsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
