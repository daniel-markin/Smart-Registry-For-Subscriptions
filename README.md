# Платформа «Умный реестр подписок» для автоматизации учёта, расчёта дат списаний и контроля статуса подписок пользователя

## 1. Как запустить:
0. Сначала необходимо склонировать репозиторий и перейти в папку проекта:
```bash
git clone https://github.com/daniel-markin/Smart-Registry-For-Subscriptions.git && cd Smart-Registry-For-Subscriptions
```
1. Переменные для LLM задаются в файле .env, который необходимо создать в корне проекта:
```bash
GIGACHAT_CREDENTIALS=
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_VERIFY_SSL_CERTS=False
GIGACHAT_MODEL=GigaChat-Max
```
Необходимо указать значение для переменной GIGACHAT_CREDENTIALS, которая хранит ключ для доступа к GigaChat API.
Документация для получения ключа: https://developers.sber.ru/docs/ru/gigachat/quickstart/ind-create-project

2. Затем необходимо загрузить переменные из .env:
```bash
set -a
source .env
set +a
```
2. Затем необходимо запустить команду для первого вопроса:
```bash
docker compose run --rm app python main.py "Сколько я потрачу в ближайшие 30 дней? Покажи итог в рублях."
```
3. Для второго вопроса:
```bash
docker compose run --rm app python main.py "Какая категория обходится мне дороже всего?"
```
4. Для третьего вопроса:
```bash
docker compose run --rm app python main.py "Есть ли у меня платежи на этой неделе?"
```

## 2. Выбранная LLM:
GigaChat Max. Именно эта модель была выбрана, поскольку она является одной из самых передовых российских LLM и отлично работает с текстами на русском языке.

## 3. Пример полного ReAct-трейса для запроса: "Сколько я потрачу в ближайшие 30 дней? Покажи итог в рублях.":
```text
=== СТАРТ РАБОТЫ АГЕНТА ===
Вопрос: Сколько я потрачу в ближайшие 30 дней? Покажи итог в рублях.

Thought:
Нужно вызвать инструмент для следующего шага.

Action:
tool_get_obligations

Action Input:
{}

Observation:
dataset_id=ds_57ce8b95af3d46419e1a812e54db7ca5
records=14

Thought:
Нужно вызвать инструмент для следующего шага.

Action:
tool_filter_by_date

Action Input:
{'date_from': '2026-07-15', 'date_to': '2026-08-14'}

Observation:
filtered_dataset_id=ds_15711244bada4f75869f94a52b2b7e80
records=5

Thought:
Нужно вызвать инструмент для следующего шага.

Action:
tool_convert_dataset_currency

Action Input:
{'to_currency': 'RUB'}

Observation:
converted_dataset_id=ds_e4c93cd75ffb4e8080e022a8a6195542
records=5

Thought:
Нужно вызвать инструмент для следующего шага.

Action:
tool_aggregate_total

Action Input:
{}

Observation:
Sum of all the obligations=5907.471500000001

=== КОНЕЦ РАБОТЫ АГЕНТА ===
Итоговый ответ:
За следующие 30 дней вы потратите 5907 рублей.
```


