from __future__ import annotations

CURRENT_CONVERSATION_ID: str | None = None


def set_current_conversation_id(conversation_id: str) -> None:
    global CURRENT_CONVERSATION_ID
    CURRENT_CONVERSATION_ID = conversation_id


def get_current_conversation_id() -> str | None:
    return CURRENT_CONVERSATION_ID