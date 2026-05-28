from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook


def _employee_workbook_bytes(rows: list[tuple]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["姓名", "工号", "手机号", "部门", "状态", "初始密码"])
    for row in rows:
        sheet.append(row)
    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def test_admin_imports_employee_and_employee_logs_in(client, admin_headers):
    csv_bytes = "姓名,工号,手机号,部门,初始密码\n张三,E001,13800000001,装备部,123456\n".encode(
        "utf-8-sig"
    )

    import_response = client.post(
        "/api/admin/employees/import",
        files={"file": ("employees.csv", BytesIO(csv_bytes), "text/csv")},
        headers=admin_headers,
    )
    assert import_response.status_code == 200
    assert import_response.json()["imported_count"] == 1

    login_response = client.post(
        "/api/auth/login",
        json={"account": "E001", "password": "123456"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["token"]
    assert login_response.json()["user"]["name"] == "张三"


def test_employee_import_rejects_duplicate_work_numbers_in_file(client, admin_headers):
    csv_bytes = (
        "姓名,工号,手机号,部门,初始密码\n"
        "张三,E001,13800000001,装备部,123456\n"
        "李四,E001,13800000002,装备部,123456\n"
    ).encode("utf-8-sig")

    response = client.post(
        "/api/admin/employees/import",
        files={"file": ("employees.csv", BytesIO(csv_bytes), "text/csv")},
        headers=admin_headers,
    )

    assert response.status_code == 400
    assert "重复" in response.json()["detail"]


def test_admin_imports_xlsx_employee_with_numeric_cells(client, admin_headers):
    workbook_bytes = _employee_workbook_bytes(
        [("裴宸豪", 89500071, 18842117754, "装备与创新部", "启用", 123456)]
    )

    with TestClient(client.app, raise_server_exceptions=False) as safe_client:
        import_response = safe_client.post(
            "/api/admin/employees/import",
            files={"file": ("employees.xlsx", BytesIO(workbook_bytes), "application/vnd.ms-excel")},
            headers=admin_headers,
        )

    assert import_response.status_code == 200
    payload = import_response.json()
    assert payload["imported_count"] == 1
    assert payload["users"][0]["work_no"] == "89500071"
    assert payload["users"][0]["phone"] == "18842117754"

    login_response = client.post(
        "/api/auth/login",
        json={"account": "89500071", "password": "123456"},
    )

    assert login_response.status_code == 200


def test_admin_import_detects_xlsx_content_with_csv_filename(client, admin_headers):
    workbook_bytes = _employee_workbook_bytes(
        [("李四", 1002, 13800000002, "生产部", "启用", 123456)]
    )

    with TestClient(client.app, raise_server_exceptions=False) as safe_client:
        response = safe_client.post(
            "/api/admin/employees/import",
            files={"file": ("employees.csv", BytesIO(workbook_bytes), "text/csv")},
            headers=admin_headers,
        )

    assert response.status_code == 200
    assert response.json()["imported_count"] == 1
