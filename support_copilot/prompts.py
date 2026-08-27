from __future__ import annotations

from support_copilot.config import ROOT_DIR

CURRENT = {
    "triage": "v1",
    "brief": "v1",
}


def prompt_id(name: str) -> str:
    return f"{name}_{CURRENT[name]}"


def load_prompt(name: str) -> str:
    path = ROOT_DIR / "prompts" / f"{prompt_id(name)}.txt"
    return path.read_text(encoding="utf-8").strip()
