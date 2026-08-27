from __future__ import annotations

import re
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


def _first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return fallback


def _chunk_document(document: dict) -> list[dict]:
    parts = [part.strip() for part in re.split(r"(?m)^---\s*$", document["text"]) if part.strip()]
    chunks = []
    for index, part in enumerate(parts):
        chunks.append(
            {
                "chunk_id": f"{document['path']}#{index}",
                "path": document["path"],
                "title": document["title"],
                "heading": _first_heading(part, document["title"]),
                "text": part,
            }
        )
    return chunks


@lru_cache(maxsize=1)
def load_chunks() -> list[dict]:
    chunks: list[dict] = []
    for document in load_documents():
        chunks.extend(_chunk_document(document))
    return chunks
