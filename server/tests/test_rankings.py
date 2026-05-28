from collections import defaultdict


def build_ranking(transactions, bank_id=None):
    totals = defaultdict(int)
    for item in transactions:
        if bank_id is None or item["bank_id"] == bank_id:
            totals[item["user"]] += item["points"]
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)


def test_global_and_bank_ranking_contracts_are_separate():
    transactions = [
        {"user": "张三", "bank_id": 1, "points": 10},
        {"user": "李四", "bank_id": 1, "points": 8},
        {"user": "李四", "bank_id": 2, "points": 20},
    ]

    assert build_ranking(transactions)[0] == ("李四", 28)
    assert build_ranking(transactions, bank_id=1)[0] == ("张三", 10)


def test_point_rules_can_be_updated(client, admin_headers):
    response = client.put(
        "/api/admin/point-rules",
        json={
            "answer_base_points": 2,
            "correct_bonus_points": 3,
            "wrong_retry_correct_points": 4,
            "exam_complete_points": 5,
            "daily_point_limit": 6,
        },
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert client.get("/api/admin/point-rules", headers=admin_headers).json()["daily_point_limit"] == 6
