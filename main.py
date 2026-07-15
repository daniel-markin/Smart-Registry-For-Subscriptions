from __future__ import annotations

import sys
import uuid

from src.agent import build_agent_executor
from src.runtime import set_current_conversation_id


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not user_input:
        user_input = input("Введите вопрос: ").strip()

    conversation_id = f"conv_{uuid.uuid4().hex}"
    set_current_conversation_id(conversation_id)

    executor = build_agent_executor(user_input)
    result = executor.invoke({"input": user_input})