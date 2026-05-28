from pathlib import Path


def test_admin_can_create_bank_and_import_questions(client, admin_headers):
    bank_response = client.post(
        "/api/admin/banks",
        json={"name": "设备知识题库", "description": "首批设备岗位知识题库"},
        headers=admin_headers,
    )
    assert bank_response.status_code == 201
    bank_id = bank_response.json()["id"]

    csv_path = Path("../question/questions.csv")
    with csv_path.open("rb") as file:
        response = client.post(
            f"/api/admin/banks/{bank_id}/questions/import",
            files={"file": ("questions.csv", file, "text/csv")},
            headers=admin_headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_rows"] == 169
    assert payload["imported_count"] == 168
    assert payload["type_counts"]["single"] == 112


def test_employee_banks_hide_inactive_banks(client, admin_headers):
    active = client.post("/api/admin/banks", json={"name": "启用题库"}, headers=admin_headers).json()
    inactive = client.post("/api/admin/banks", json={"name": "停用题库"}, headers=admin_headers).json()
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

    client.patch(f"/api/admin/banks/{inactive['id']}", json={"is_active": False}, headers=admin_headers)

    response = client.get("/api/banks", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert active["id"] in ids
    assert inactive["id"] not in ids
