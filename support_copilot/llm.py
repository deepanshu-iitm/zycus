from __future__ import annotations

import json
from collections.abc import Callable

from openai import OpenAI

from support_copilot.config import get_settings


def get_client() -> OpenAI:
    settings = get_settings()
    key = settings.openai_api_key.strip()
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return OpenAI(api_key=key)


def complete(messages: list[dict], temperature: float = 0.1) -> str:
    settings = get_settings()
    response = get_client().chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=temperature,
    )
    return (response.choices[0].message.content or "").strip()


def complete_json(
    messages: list[dict],
    temperature: float = 0.1,
    on_token: Callable[[str], None] | None = None,
) -> dict:
    settings = get_settings()
    request = {
        "model": settings.openai_model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    if on_token is None:
        response = get_client().chat.completions.create(**request)
        return json.loads(response.choices[0].message.content or "{}")

    request["stream"] = True
    parts: list[str] = []
    for event in get_client().chat.completions.create(**request):
        if not event.choices:
            continue
        text = event.choices[0].delta.content or ""
        if text:
            parts.append(text)
            on_token(text)
    return json.loads("".join(parts) or "{}")
