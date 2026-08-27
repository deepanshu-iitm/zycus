from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    dataset_as_of: str = Field(default="2026-05-22", alias="DATASET_AS_OF")


def _merge_streamlit_secrets() -> None:
    try:
        import streamlit as st

        secrets = st.secrets
    except Exception:
        return
    for key in ("OPENAI_API_KEY", "OPENAI_MODEL", "DATASET_AS_OF"):
        if os.environ.get(key, "").strip():
            continue
        try:
            value = secrets[key]
        except Exception:
            continue
        if value:
            os.environ[key] = str(value)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _merge_streamlit_secrets()
    return Settings()
