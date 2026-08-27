from __future__ import annotations

import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from support_copilot.knowledge_base import load_chunks

_TOKEN = re.compile(r"[A-Za-z0-9_]+")
_ERROR_CODE = re.compile(r"\b[A-Z][A-Z0-9_]{4,}\b")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text)]


def _error_codes(text: str) -> set[str]:
    return set(_ERROR_CODE.findall(text))


@lru_cache(maxsize=1)
def _bm25_index() -> tuple[list[dict], BM25Okapi]:
    chunks = load_chunks()
    corpus = [tokenize(f"{chunk['heading']} {chunk['text']}") for chunk in chunks]
    return chunks, BM25Okapi(corpus)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    chunks, bm25 = _bm25_index()
    scores = bm25.get_scores(tokenize(query))
    codes = _error_codes(query)

    ranked = []
    for score, chunk in zip(scores, chunks):
        blob = f"{chunk['heading']}\n{chunk['text']}"
        exact = 1 if any(code in blob for code in codes) else 0
        if score <= 0 and not exact:
            continue
        ranked.append((exact, float(score), chunk))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)

    results = []
    for exact, score, chunk in ranked[:top_k]:
        match = dict(chunk)
        match["score"] = score + (100.0 if exact else 0.0)
        results.append(match)
    return results
