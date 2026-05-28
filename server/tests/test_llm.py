from app.services.llm import build_explanation_prompt


def test_build_explanation_prompt_contains_question_and_original_explanation():
    prompt = build_explanation_prompt(
        stem="三联件的组成及顺序正确的是",
        options={"A": "油雾器、电磁阀、过滤器", "C": "过滤器、减压阀、油雾器"},
        correct_answer="C",
        original_explanation="安装正确顺序：过滤器、减压阀、油污器。",
    )

    assert "三联件" in prompt
    assert "正确答案：C" in prompt
    assert "不要编造" in prompt


def test_ai_explanation_disabled_returns_409(client, admin_headers):
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

    response = client.post(
        "/api/questions/1/ai-explanation",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "AI讲解未启用"
