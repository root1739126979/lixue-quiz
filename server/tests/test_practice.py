from pathlib import Path

from app.services.scoring import is_answer_correct, points_for_answer


def import_bank_with_questions(client, admin_headers):
    bank_id = client.post(
        "/api/admin/banks", json={"name": "设备知识题库"}, headers=admin_headers
    ).json()["id"]
    with Path("../question/questions.csv").open("rb") as file:
        client.post(
            f"/api/admin/banks/{bank_id}/questions/import",
            files={"file": ("questions.csv", file, "text/csv")},
            headers=admin_headers,
        )
    return bank_id


def login_employee(client, admin_headers):
    client.post(
        "/api/admin/employees/import",
        files={
            "file": (
                "employees.csv",
                b"\xef\xbb\xbf\xe5\xa7\x93\xe5\x90\x8d,\xe5\xb7\xa5\xe5\x8f\xb7,\xe6\x89\x8b\xe6\x9c\xba\xe5\x8f\xb7,\xe9\x83\xa8\xe9\x97\xa8,\xe5\x88\x9d\xe5\xa7\x8b\xe5\xaf\x86\xe7\xa0\x81\n\xe5\xbc\xa0\xe4\xb8\x89,E001,13800000001,\xe8\xa3\x85\xe5\xa4\x87\xe9\x83\xa8,123456\n",
                "text/csv",
            )
        },
        headers=admin_headers,
    )
    token = client.post("/api/auth/login", json={"account": "E001", "password": "123456"}).json()[
        "token"
    ]
    return {"Authorization": f"Bearer {token}"}


def test_single_choice_answer_scoring():
    assert is_answer_correct("A", "A")
    assert is_answer_correct(" a ", "A")
    assert not is_answer_correct("B", "A")


def test_multiple_choice_answer_scoring_is_order_insensitive():
    assert is_answer_correct("B,A,C", "A,B,C")
    assert not is_answer_correct("A,C", "A,B,C")


def test_points_for_answer_uses_rule_values():
    assert points_for_answer(is_correct=True, base_points=1, correct_bonus=2) == 3
    assert points_for_answer(is_correct=False, base_points=1, correct_bonus=2) == 1


def test_practice_session_omits_correct_answer_and_submit_records_feedback(client, admin_headers):
    bank_id = import_bank_with_questions(client, admin_headers)
    headers = login_employee(client, admin_headers)

    session = client.post(
        "/api/practice/sessions",
        json={"bank_id": bank_id, "count": 3},
        headers=headers,
    )

    assert session.status_code == 200
    questions = session.json()["questions"]
    assert len(questions) == 3
    assert "correct_answer" not in questions[0]

    answer = client.post(
        "/api/practice/answers",
        json={"question_id": questions[0]["id"], "selected_answer": "A"},
        headers=headers,
    )

    assert answer.status_code == 200
    payload = answer.json()
    assert {"is_correct", "correct_answer", "explanation", "points_awarded"} <= payload.keys()
