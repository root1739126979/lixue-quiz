from io import BytesIO


def _import_employee(client, admin_headers) -> int:
    csv_bytes = (
        "姓名,工号,手机号,部门,初始密码\n"
        "张三,E001,13800000001,装备部,123456\n"
    ).encode("utf-8-sig")
    response = client.post(
        "/api/admin/employees/import",
        files={"file": ("employees.csv", BytesIO(csv_bytes), "text/csv")},
        headers=admin_headers,
    )
    assert response.status_code == 200
    return response.json()["users"][0]["id"]


def _import_question_bank(client, admin_headers) -> int:
    bank = client.post(
        "/api/admin/banks",
        json={"name": "设备知识题库", "description": "岗位练习"},
        headers=admin_headers,
    )
    assert bank.status_code == 201
    bank_id = bank.json()["id"]
    question_csv = (
        "题号,题型,题干,选项A,选项B,选项C,选项D,选项E,正确答案,正确答案文本,解析\n"
        "1,单选题,第一题,A项,B项,,,,A,A项正确,第一题解析\n"
        "2,单选题,第二题,A项,B项,,,,B,B项正确,第二题解析\n"
    ).encode("utf-8-sig")
    response = client.post(
        f"/api/admin/banks/{bank_id}/questions/import",
        files={"file": ("questions.csv", BytesIO(question_csv), "text/csv")},
        headers=admin_headers,
    )
    assert response.status_code == 200
    return bank_id


def _employee_headers(client) -> dict[str, str]:
    login = client.post("/api/auth/login", json={"account": "E001", "password": "123456"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['token']}"}


def test_admin_can_view_single_employee_learning_summary(client, admin_headers):
    employee_id = _import_employee(client, admin_headers)
    bank_id = _import_question_bank(client, admin_headers)
    employee_headers = _employee_headers(client)
    session = client.post(
        "/api/practice/sessions",
        json={"bank_id": bank_id, "count": 2},
        headers=employee_headers,
    )
    assert session.status_code == 200
    questions = {question["stem"]: question for question in session.json()["questions"]}

    correct = client.post(
        "/api/practice/answers",
        json={"question_id": questions["第一题"]["id"], "selected_answer": "A"},
        headers=employee_headers,
    )
    wrong = client.post(
        "/api/practice/answers",
        json={"question_id": questions["第二题"]["id"], "selected_answer": "A"},
        headers=employee_headers,
    )
    assert correct.status_code == 200
    assert wrong.status_code == 200

    response = client.get(f"/api/admin/employees/{employee_id}/summary", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == employee_id
    assert payload["name"] == "张三"
    assert payload["answer_count"] == 2
    assert payload["accuracy"] == 50
    assert payload["total_points"] == 3
    assert payload["open_wrong_count"] == 1


def test_admin_employee_summary_returns_404_for_missing_employee(client, admin_headers):
    response = client.get("/api/admin/employees/999/summary", headers=admin_headers)

    assert response.status_code == 404
