from __future__ import annotations

from langchain_core.callbacks import BaseCallbackHandler


class ConsoleTraceCallbackHandler(BaseCallbackHandler):
    def on_chain_start(self, serialized, inputs, **kwargs):
        question = inputs.get("input") if isinstance(inputs, dict) else None
        print("\n=== СТАРТ РАБОТЫ АГЕНТА ===", flush=True)
        print(f"Вопрос: {question}", flush=True)

    def on_agent_action(self, action, **kwargs):
        tool = getattr(action, "tool", None)
        tool_input = getattr(action, "tool_input", None)

        print("\nThought:", flush=True)
        print("Нужно вызвать инструмент для следующего шага.", flush=True)

        print("\nAction:", flush=True)
        print(tool, flush=True)

        print("\nAction Input:", flush=True)
        print(tool_input, flush=True)

    def on_chain_end(self, outputs, **kwargs):
        print("\n=== КОНЕЦ РАБОТЫ АГЕНТА ===", flush=True)
        if isinstance(outputs, dict) and "output" in outputs:
            print("Итоговый ответ:", flush=True)
            print(outputs["output"], flush=True)