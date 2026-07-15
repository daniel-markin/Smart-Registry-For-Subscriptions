from unittest.mock import Mock

import pytest
import requests

from src.tools.currency import convert_currency

# Проверяет, что конвертация не выполняется, если исходная и целевая валюты одинаковые.
def test_convert_currency_same_currency():
    assert convert_currency(100, "RUB", "RUB") == 100

# Проверяет, что convert_currency успешно конвертирует сумму по курсу из API.
def test_convert_currency_success(monkeypatch):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"rate": 89.45}

    monkeypatch.setattr("src.tools.currency.requests.get", Mock(return_value=response))

    result = convert_currency(10, "USD", "RUB")

    assert result == pytest.approx(894.5)

# Проверяет, что convert_currency возвращает None, если при обращении к API возникает ошибка.
def test_convert_currency_api_error(monkeypatch):
    monkeypatch.setattr(
        "src.tools.currency.requests.get",
        Mock(side_effect=requests.RequestException("API error")),
    )

    result = convert_currency(10, "USD", "RUB")

    assert result is None
