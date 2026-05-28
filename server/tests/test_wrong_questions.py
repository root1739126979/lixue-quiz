from pathlib import Path


def setup_wrong_question(client, admin_headers):
    bank_id = client.post(
        "/api/admin/banks", json={"name": "设备知识题库"}, headers=admin_headers
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
    question = client.post(
        "/api/practice/sessions",
        json={"bank_id": bank_id, "count": 1},
        headers=headers,
    ).json()["questions"][0]
    correct = client.get(
        f"/api/admin/questions/{question['id']}", headers=admin_headers
    ).json()["correct_answer"]
    selected = "B" if correct != "B" else "A"
    client.post(
        "/api/practice/answers",
        json={"question_id": question["id"], "selected_answer": selected},
        headers=headers,
    )
    return headers, question["id"]


def test_wrong_question_lifecycle(client, admin_headers):
    headers, question_id = setup_wrong_question(client, admin_headers)

    listing = client.get("/api/wrong-questions", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["items"][0]["question_id"] == question_id
    assert listing.json()["items"][0]["status"] == "open"

    mastered = client.post(f"/api/wrong-questions/{question_id}/master", headers=headers)
    assert mastered.status_code == 200
    assert mastered.json()["status"] == "mastered"

    listing = client.get("/api/wrong-questions", headers=headers)
    assert listing.json()["items"] == []
