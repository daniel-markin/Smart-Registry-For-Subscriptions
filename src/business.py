from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from src.tools.currency import convert_currency


def filter_obligations_by_date(
    obligations: list[dict],
    date_from: str,
    date_to: str,
) -> list[dict]:
    try:
        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)
    except ValueError as exc:
        raise ValueError("date_from and date_to must be in YYYY-MM-DD format") from exc

    if start > end:
        raise ValueError("date_from must be <= date_to")

    result = []
    for obligation in obligations:
        payment_date = date.fromisoformat(obligation["next_payment_date"])
        if start <= payment_date <= end:
            result.append(obligation)
    return result


def convert_dataset_currency(
    obligations: list[dict],
    to_currency: str,
) -> list[dict[str, Any]] | None:
    converted: list[dict[str, Any]] = []

    for obligation in obligations:
        amount = float(obligation["amount"])
        from_currency = obligation["currency"]

        if from_currency == to_currency:
            new_obligation = dict(obligation)
            new_obligation["amount"] = amount
            new_obligation["currency"] = to_currency
            converted.append(new_obligation)
            continue

        converted_amount = convert_currency(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
        )
        if converted_amount is None:
            return None

        new_obligation = dict(obligation)
        new_obligation["amount"] = float(converted_amount)
        new_obligation["currency"] = to_currency
        converted.append(new_obligation)

    return converted


def aggregate_total(obligations: list[dict]) -> float:
    return sum(float(obligation["amount"]) for obligation in obligations)


def aggregate_by_category(
    obligations: list[dict],
    to_currency: str = "RUB",
) -> dict[str, float] | None:
    totals = defaultdict(float)

    for obligation in obligations:
        amount = float(obligation["amount"])
        from_currency = obligation["currency"]

        if from_currency == to_currency:
            converted_amount = amount
        else:
            converted_amount = convert_currency(
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
            )
            if converted_amount is None:
                return None

        totals[obligation["category"]] += float(converted_amount)

    return dict(totals)


def get_top_category(category_totals: dict[str, float]) -> dict[str, Any] | None:
    if not category_totals:
        return None

    category = max(category_totals, key=category_totals.get)
    return {"category": category, "total": category_totals[category]}


def get_min_category(category_totals: dict[str, float]) -> dict[str, Any] | None:
    if not category_totals:
        return None

    category = min(category_totals, key=category_totals.get)
    return {"category": category, "total": category_totals[category]}


def has_items(obligations: list[dict]) -> bool:
    return len(obligations) > 0