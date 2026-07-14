import requests

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | None:
    if from_currency == to_currency:
        return amount

    url = f"https://api.frankfurter.dev/v2/rate/{from_currency}/{to_currency}"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        rate = float(response.json()["rate"])
        return amount * rate
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None