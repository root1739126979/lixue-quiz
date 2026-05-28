from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_frontend(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_frontend_uses_separate_tokens_for_admin_and_employee_sessions():
    client = read_frontend("web/src/api/client.ts")
    admin_login = read_frontend("web/src/admin/AdminLoginPage.tsx")
    employee_login = read_frontend("web/src/employee/LoginPage.tsx")

    assert "lixue_admin_token" in client
    assert "lixue_employee_token" in client
    assert 'path.startsWith("/admin")' in client
    assert 'localStorage.setItem("lixue_admin_token"' in admin_login
    assert 'localStorage.setItem("lixue_employee_token"' in employee_login
    assert "lixue_token" not in client


def test_question_bank_page_surfaces_create_and_toggle_errors():
    page = read_frontend("web/src/admin/QuestionBanksPage.tsx")

    assert "create.error" in page
    assert "toggle.error" in page
    assert "dataError" in page
    assert "create.isPending" in page
    assert "toggle.isPending" in page
