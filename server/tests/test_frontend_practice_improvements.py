from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_frontend(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_practice_page_has_count_picker_question_type_jump_dialog_and_completion():
    page = read_frontend("web/src/employee/PracticePage.tsx")

    assert "questionCount" in page
    assert "开始练习" in page
    assert "题型" in page
    assert "typeLabels" in page
    assert "jump-panel" in page
    assert "jumpToQuestion" in page
    assert "练习完成" in page
    assert "完成练习" in page


def test_practice_feedback_is_split_into_answer_analysis_and_ai_sections():
    page = read_frontend("web/src/employee/PracticePage.tsx")

    assert "answer-card" in page
    assert "analysis-card" in page
    assert "ai-card" in page
    assert "你的答案" in page
    assert "正确答案" in page
    assert "本题目解析" in page
    assert "AI讲解" in page


def test_admin_employee_page_loads_selected_employee_summary():
    page = read_frontend("web/src/admin/EmployeesPage.tsx")

    assert "selectedEmployeeId" in page
    assert "/admin/employees/${selectedEmployeeId}/summary" in page
    assert "累计答题" in page
    assert "整体正确率" in page
    assert "总积分" in page
    assert "未掌握错题" in page


def test_dashboard_page_keeps_personal_metrics_out_of_global_overview():
    page = read_frontend("web/src/admin/DashboardPage.tsx")

    assert "累计答题" not in page
    assert "整体正确率" not in page
    assert "未掌握错题" not in page
