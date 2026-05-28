from pathlib import Path


def test_exam_attempt_uses_snapshot_and_scores_percentage(client, admin_headers):
    bank_id = client.post(
        "/api/admin/banks",
        json={"name": "设备知识题库", "exam_question_count": 5, "exam_time_limit_minutes": 15},
        headers=admin_headers,
    ).json()["id"]
    with Path("../question/questions.csv").open("rb") as file:
        client.post(
            f"/api/admin/banks/{bank_id}/questions/import",
            files={"file": ("questions.csv", file, "text/csv")},
            headers=admin_headers,
        )
    client.post(
        "/api/admin/employees/import",
        files={
            "file": (
                "employees.csv",
                "姓名,工号,手机号,部门,初始密码\n张三,E001,13800000001,装备部,123456\n".encode(
                    "utf-8-sig"
                ),
                "text/csv",
            )
        },
        headers=admin_headers,
    )
    token = client.post("/api/auth/login", json={"account": "E001", "password": "123456"}).json()[
        "token"
    ]
    headers = {"Authorization": f"Bearer {token}"}

    attempt = client.post("/api/exams/attempts", json={"bank_id": bank_id}, headers=headers)

    assert attempt.status_code == 200
    payload = attempt.json()
    assert payload["time_limit_minutes"] == 15
    assert len(payload["questions"]) == 5

    answers = [
        {
            "question_id": item["id"],
            "selected_answer": client.get(
                f"/api/admin/questions/{item['id']}", headers=admin_headers
            ).json()["correct_answer"],
        }
        for item in payload["questions"]
    ]
    result = client.post(
        f"/api/exams/attempts/{payload['attempt_id']}/submit",
        json={"answers": answers},
        headers=headers,
    )

    assert result.status_code == 200
    assert result.json()["score"] == 100
    assert result.json()["correct_count"] == 5
