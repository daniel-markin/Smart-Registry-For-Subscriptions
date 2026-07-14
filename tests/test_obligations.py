import json
import pytest
from src.tools.obligations import get_obligations


@pytest.fixture
def obligations_data():
    return [
        {
            "id": "c608c6ba-45a7-4361-b469-e503c206cb73",
            "title": "Video Streaming Plus",
            "amount": 449.55,
            "currency": "RUB",
            "category": "entertainment",
            "next_payment_date": "2026-08-10",
            "status": "active",
        },
        {
            "id": "d046ef34-96eb-49b4-850a-732f539c81bf",
            "title": "Music Premium",
            "amount": 11.27,
            "currency": "USD",
            "category": "entertainment",
            "next_payment_date": "2026-07-14",
            "status": "active",
        },
        {
            "id": "9fc08e91-f164-46de-b2f9-ccb808a27db9",
            "title": "Photo Editor Plus",
            "amount": 9.99,
            "currency": "USD",
            "category": "work",
            "next_payment_date": "2026-08-15",
            "status": "canceled",
        },
    ]


def test_get_obligations_returns_all_records(monkeypatch, tmp_path, obligations_data):
    data_file = tmp_path / "obligations.json"
    data_file.write_text(json.dumps(obligations_data), encoding="utf-8")
    monkeypatch.setattr("src.tools.obligations.DATA_PATH", data_file)

    result = get_obligations()

    assert len(result) == 3
    assert result[0]["title"] == "Video Streaming Plus"
    assert result[1]["title"] == "Music Premium"
    assert result[2]["title"] == "Photo Editor Plus"


def test_get_obligations_filters_by_status(monkeypatch, tmp_path, obligations_data):
    data_file = tmp_path / "obligations.json"
    data_file.write_text(json.dumps(obligations_data), encoding="utf-8")
    monkeypatch.setattr("src.tools.obligations.DATA_PATH", data_file)

    result = get_obligations(status="active")

    assert len(result) == 2
    assert all(item["status"] == "active" for item in result)


def test_get_obligations_filters_by_status_and_category(monkeypatch, tmp_path, obligations_data):
    data_file = tmp_path / "obligations.json"
    data_file.write_text(json.dumps(obligations_data), encoding="utf-8")
    monkeypatch.setattr("src.tools.obligations.DATA_PATH", data_file)

    result = get_obligations(status="active", category="entertainment")

    assert len(result) == 2
    assert {item["title"] for item in result} == {
        "Video Streaming Plus",
        "Music Premium",
    }