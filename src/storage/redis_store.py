from __future__ import annotations

import json
import os
import uuid
from typing import Any

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def make_dataset_id() -> str:
    return f"ds_{uuid.uuid4().hex}"


def dataset_key(dataset_id: str) -> str:
    return f"agent:dataset:{dataset_id}"


def conversation_key(conversation_id: str) -> str:
    return f"agent:{conversation_id}"


def save_dataset(dataset_id: str, payload: dict[str, Any], ttl_seconds: int = 1800) -> None:
    redis_client.set(dataset_key(dataset_id), json.dumps(payload), ex=ttl_seconds)


def load_dataset(dataset_id: str) -> dict[str, Any] | None:
    raw = redis_client.get(dataset_key(dataset_id))
    if raw is None:
        return None
    return json.loads(raw)


def delete_dataset(dataset_id: str) -> None:
    redis_client.delete(dataset_key(dataset_id))


def set_current_dataset_id(conversation_id: str, dataset_id: str, ttl_seconds: int = 1800) -> None:
    redis_client.set(conversation_key(conversation_id), dataset_id, ex=ttl_seconds)


def get_current_dataset_id(conversation_id: str) -> str | None:
    return redis_client.get(conversation_key(conversation_id))