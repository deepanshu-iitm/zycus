from __future__ import annotations

from functools import lru_cache

from support_copilot.config import ROOT_DIR

KB_DIR = ROOT_DIR / "knowledge-base"


@lru_cache(maxsize=1)
def load_documents() -> list[dict]:
    documents = []
    for path in sorted(KB_DIR.rglob("*.md")):
        documents.append(
            {
                "path": path.relative_to(ROOT_DIR).as_posix(),
                "title": path.stem,
                "text": path.read_text(encoding="utf-8"),
            }
        )
    return documents
