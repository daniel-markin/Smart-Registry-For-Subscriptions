import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BASE_DIR / "data" / "obligations.json"


def load_obligations() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def filter_obligations(
    obligations: list[dict],
    status: str | None = None,
    category: str | None = None,
) -> list[dict]:
    filtered_obligations = obligations

    if status is not None:
        filtered_obligations = [
            obligation
            for obligation in filtered_obligations
            if obligation["status"] == status
        ]

    if category is not None:
        filtered_obligations = [
            obligation
            for obligation in filtered_obligations
            if obligation["category"] == category
        ]

    return filtered_obligations


def get_obligations(
    status: str | None = None,
    category: str | None = None,
) -> list[dict]:
    obligations = load_obligations()
    return filter_obligations(obligations=obligations, status=status, category=category)