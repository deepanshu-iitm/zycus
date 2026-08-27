from __future__ import annotations

import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from support_copilot.knowledge_base import load_chunks

_TOKEN = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text)]


@lru_cache(maxsize=1)
def _bm25_index() -> tuple[list[dict], BM25Okapi]:
    chunks = load_chunks()
    corpus = [tokenize(f"{chunk['heading']} {chunk['text']}") for chunk in chunks]
    return chunks, BM25Okapi(corpus)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    chunks, bm25 = _bm25_index()
    scores = bm25.get_scores(tokenize(query))
    ranked = sorted(zip(scores, chunks), key=lambda item: item[0], reverse=True)

    results = []
    for score, chunk in ranked[:top_k]:
        if score <= 0:
            continue
        match = dict(chunk)
        match["score"] = float(score)
        results.append(match)
    return results
