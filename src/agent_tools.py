from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from src.business import (
    aggregate_by_category,
    aggregate_total,
    convert_dataset_currency,
    filter_obligations_by_date,
    get_min_category,
    get_top_category,
    has_items,
)
from src.runtime import get_current_conversation_id
from src.storage.redis_store import (
    delete_dataset,
    get_current_dataset_id,
    load_dataset,
    make_dataset_id,
    save_dataset,
    set_current_dataset_id,
)
from src.tools.obligations import get_obligations


def _require_conversation_id() -> str:
    conversation_id = get_current_conversation_id()
    if not conversation_id:
        raise RuntimeError("conversation_id is not set")
    return conversation_id


def _require_current_dataset_id(conversation_id: str) -> str:
    dataset_id = get_current_dataset_id(conversation_id)
    if not dataset_id:
        raise RuntimeError("current dataset_id is not set. Call tool_get_obligations first.")
    return dataset_id


@tool
def tool_get_obligations(status: str | None = None, category: str | None = None) -> str:
    """
    Загружает список обязательств из локального JSON-файла и при необходимости
    фильтрует их по статусу и/или категории.

    Возвращает dataset_id.
    """
    conversation_id = _require_conversation_id()

    obligations = get_obligations(status=status, category=category)
    dataset_id = make_dataset_id()

    save_dataset(
        dataset_id,
        {
            "type": "records",
            "source": "obligations.json",
            "record_ids": [obligation["id"] for obligation in obligations],
            "records": obligations,
            "filters_applied": {
                "status": status,
                "category": category,
            },
        },
    )
    set_current_dataset_id(conversation_id, dataset_id)

    print("\nObservation:", flush=True)
    print(f"dataset_id={dataset_id}", flush=True)
    print(f"records={len(obligations)}", flush=True)
    return dataset_id


@tool
def tool_filter_by_date(date_from: str, date_to: str) -> str:
    """
    Фильтрует список обязательств по полю next_payment_date
    в диапазоне [date_from, date_to].

    Возвращает новый dataset_id.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_filter_by_date.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "records":
        return "ERROR: dataset type must be records"

    filtered_obligations = filter_obligations_by_date(
        payload["records"],
        date_from=date_from,
        date_to=date_to,
    )

    new_dataset_id = make_dataset_id()
    save_dataset(
        new_dataset_id,
        {
            "type": "records",
            "source": payload.get("source", "obligations.json"),
            "record_ids": [obligation["id"] for obligation in filtered_obligations],
            "records": filtered_obligations,
            "filters_applied": {
                **payload.get("filters_applied", {}),
                "date_from": date_from,
                "date_to": date_to,
            },
        },
    )
    set_current_dataset_id(conversation_id, new_dataset_id)
    delete_dataset(dataset_id)

    print("\nObservation:", flush=True)
    print(f"filtered_dataset_id={new_dataset_id}", flush=True)
    print(f"records={len(filtered_obligations)}", flush=True)

    return new_dataset_id


@tool
def tool_convert_dataset_currency(to_currency: str) -> str:
    """
    Конвертирует суммы обязательств в целевую валюту.
    Вызывает convert_currency для каждого обязательства, валюта суммы которого отличается от целевой валюты.

    Возвращает новый dataset_id.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_convert_dataset_currency.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "records":
        return "ERROR: dataset type must be records"

    converted_obligations = convert_dataset_currency(
        payload["records"],
        to_currency=to_currency,
    )
    if converted_obligations is None:
        return "ERROR: currency conversion failed"

    new_dataset_id = make_dataset_id()
    save_dataset(
        new_dataset_id,
        {
            "type": "records",
            "source": payload.get("source", "obligations.json"),
            "record_ids": [obligation["id"] for obligation in converted_obligations],
            "records": converted_obligations,
            "filters_applied": {
                **payload.get("filters_applied", {}),
                "converted_to": to_currency,
            },
        },
    )
    set_current_dataset_id(conversation_id, new_dataset_id)
    delete_dataset(dataset_id)

    print("\nObservation:", flush=True)
    print(f"converted_dataset_id={new_dataset_id}", flush=True)
    print(f"records={len(converted_obligations)}", flush=True)

    return new_dataset_id


@tool
def tool_aggregate_total() -> float | str:
    """
    Вычисляет и возвращает сумму стоимостей всех обязательств.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_aggregate_total.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "records":
        return "ERROR: dataset type must be records"

    total = aggregate_total(payload["records"])

    print("\nObservation:", flush=True)
    print(f"Sum of all the obligations={total}", flush=True)

    return total


@tool
def tool_aggregate_by_category(to_currency: str = "RUB") -> str:
    """
    Суммирует расходы по категориям с конвертацией в единую валюту.

    Возвращает новый dataset_id.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_aggregate_by_category.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "records":
        return "ERROR: dataset type must be records"

    totals = aggregate_by_category(payload["records"], to_currency=to_currency)
    if totals is None:
        return "ERROR: currency conversion failed"

    new_dataset_id = make_dataset_id()
    save_dataset(
        new_dataset_id,
        {
            "type": "aggregates",
            "group_by": "category",
            "currency": to_currency,
            "data": totals,
            "source_dataset_id": dataset_id,
        },
    )
    set_current_dataset_id(conversation_id, new_dataset_id)
    delete_dataset(dataset_id)

    print("\nObservation:", flush=True)
    print(f"aggregated_dataset_id={new_dataset_id}", flush=True)
    
    return new_dataset_id


@tool
def tool_get_top_category() -> dict[str, Any] | str:
    """
    Возвращает словарь, в котором хранится пара ключ-значение.
    Ключ: название категории, расход по которой максимален.
    Значение: сумма расхода.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_get_top_category.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "aggregates":
        return "ERROR: dataset must be aggregated"

    result = get_top_category(payload["data"])

    print("\nObservation:", flush=True)
    print(f"result={result}", flush=True)

    return result if result is not None else "ERROR: empty dataset"


@tool
def tool_get_min_category() -> dict[str, Any] | str:
    """
    Возвращает словарь, в котором хранится пара ключ-значение.
    Ключ: название категории, расход по которой минимален.
    Значение: сумма расхода.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_get_min_category.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "aggregates":
        return "ERROR: dataset must be aggregated"

    result = get_min_category(payload["data"])

    print("\nObservation:", flush=True)
    print(f"result={result}", flush=True)

    return result if result is not None else "ERROR: empty dataset"


@tool
def tool_has_items() -> bool | str:
    """
    Проверяет, содержит ли список обязательств хотя бы одно обязательство,
    и возвращает True, если содержит, и False, если не содержит.

    Требует, чтобы tool_get_obligations уже был вызван до вызова tool_has_items.
    """
    conversation_id = _require_conversation_id()
    dataset_id = _require_current_dataset_id(conversation_id)

    payload = load_dataset(dataset_id)
    if payload is None:
        return "ERROR: dataset not found"

    if payload.get("type") != "records":
        return "ERROR: dataset type must be records"

    result = has_items(payload["records"])
    print("\nObservation:", flush=True)
    print(f"result={result}", flush=True)

    return result