from __future__ import annotations

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
