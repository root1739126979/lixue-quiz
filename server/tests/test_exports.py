def test_rows_to_csv_includes_utf8_bom_and_headers():
    from app.services.exports import rows_to_csv

    content = rows_to_csv(
        headers=["姓名", "累计答题数"],
        rows=[["张三", 12]],
    )

    assert content.startswith("\ufeff")
    assert "姓名,累计答题数" in content
    assert "张三,12" in content


def test_export_user_summary_returns_csv(client, admin_headers):
    response = client.get("/api/admin/exports/users", headers=admin_headers)

    assert response.status_code == 200
    assert response.text.startswith("\ufeff")
    assert "姓名" in response.text
