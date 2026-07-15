from __future__ import annotations

import os
import re
from datetime import date, timedelta

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_gigachat import GigaChat

from src.agent_tools import (
    tool_aggregate_by_category,
    tool_aggregate_total,
    tool_convert_dataset_currency,
    tool_filter_by_date,
    tool_get_min_category,
    tool_get_obligations,
    tool_get_top_category,
    tool_has_items,
)
from src.logging_callbacks import ConsoleTraceCallbackHandler


def _get_today() -> date:
    return date.today()


def _extract_period_days(text: str) -> int | None:
    match = re.search(r"(\d+)\s*(дн|дня|дней)", text.lower())
    if match:
        return int(match.group(1))
    return None


def _build_date_bounds(user_input: str) -> tuple[str | None, str | None]:
    today = _get_today()
    period_days = _extract_period_days(user_input)
    if period_days is None:
        return None, None
    return today.isoformat(), (today + timedelta(days=period_days)).isoformat()


def build_agent_executor(user_input: str | None = None) -> AgentExecutor:
    llm = GigaChat(
        credentials=os.getenv("GIGACHAT_CREDENTIALS"),
        scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
        model=os.getenv("GIGACHAT_MODEL", "GigaChat"),
        verify_ssl_certs=False,
        temperature=0,
    )

    tools = [
        tool_get_obligations,
        tool_filter_by_date,
        tool_convert_dataset_currency,
        tool_aggregate_total,
        tool_aggregate_by_category,
        tool_get_top_category,
        tool_get_min_category,
        tool_has_items,
    ]

    today = _get_today()
    date_from, date_to = _build_date_bounds(user_input or "")
    target_currency = "RUB"

    date_block = ""
    if date_from and date_to:
        date_block = f"""
Если пользователь спрашивает про сумму в ближайшие N дней, используйте диапазон:
date_from = {date_from}
date_to = {date_to}
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""
Вы — Платформа «Умный реестр подписок» для автоматизации учёта, 
расчёта дат списаний и контроля статуса подписок пользователя

Текущая дата: {today.isoformat()}.
{date_block}

Если пользователь явно просит итог в валюте, используйте целевую валюту:
target_currency = {target_currency}

Правила:
1) Сначала всегда вызывайте tool_get_obligations.
2) Никогда не выдумывайте суммы, курсы, даты и категории.
3) Если данных недостаточно или конвертация не удалась — скажите об этом прямо.

Возможные сценарии использования:
а) Пользователь просит ответить, сколько он потратит за период n в валюте k. 
Вы должны выполнить такую последовательность шагов:
1) Обязательно вызывайте tool_get_obligations
2) Обязательно фильтруйте полученные обязательства по next_payment_date
3) Обязательно конвертируйте суммы обязательств в целевую валюту.
4) Обязательно считайте сумму всех обязательств
5) Обязательно возвращайте ответ

б) Пользователь просит ответить, какая категория обязательств является самой дорогой. 
Вы должны выполнить такую последовательность шагов:
1) Обязательно вызывайте tool_get_obligations
2) Обязательно сгруппируйте обязательства по категориям
3) Обязательно вычислите самую дорогую категорию обязательств из полученного набора

в) Пользователь просит, ответить если ли у него платежи на протяжении временного промежутка n.
Вы должны выполнить такую последовательность шагов:
1) Обязательно вызывайте tool_get_obligations
2) Обязательно фильтруйте полученные обязательства по next_payment_date
3) Обязательно проверьте, содержит ли полученный список обязательств хотя бы одно обязательство

Внимание!!! Помните, что необходимо строго придерживаться каждой последовательности, выполнять все шаги и не менять шаги местами.
Если Вы пропустите какой-либо шаг, то ваш ответ будет неверным.

Каждый шаг выполняйте лишь один раз.

Отвечайте кратко и по существу.
""".strip(),
            ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        callbacks=[ConsoleTraceCallbackHandler()],
        handle_parsing_errors=True,
    )