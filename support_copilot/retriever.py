from __future__ import annotations

import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from support_copilot.knowledge_base import load_chunks

_TOKEN = re.compile(r"[A-Za-z0-9_]+")
_ERROR_CODE = re.compile(r"\b[A-Z][A-Z0-9_]{4,}\b")
_PRODUCT_HINTS = (
    ("databridge", "databridge-pro"),
    ("cloudsync", "cloudsync"),
    ("analyticshub", "analyticshub"),
    ("securevault", "securevault"),
    ("workflowengine", "workflowengine"),
)


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text)]


def _error_codes(text: str) -> set[str]:
    return set(_ERROR_CODE.findall(text))


def _mentioned_products(query: str) -> set[str]:
    compact = re.sub(r"[^a-z0-9]", "", query.lower())
    return {slug for hint, slug in _PRODUCT_HINTS if hint in compact}


def _product_fit(query_products: set[str], chunk: dict) -> int:
    if not query_products:
        return 0
    path = chunk["path"].lower()
    slugs = {slug for _, slug in _PRODUCT_HINTS}
    for slug in slugs:
        if slug in path:
            return 2 if slug in query_products else 0
    if any(part in path for part in ("/troubleshooting/", "/billing/", "/onboarding/")):
        return 1
    return 0


@lru_cache(maxsize=1)
def _bm25_index() -> tuple[list[dict], BM25Okapi]:
    chunks = load_chunks()
    corpus = [tokenize(f"{chunk['heading']} {chunk['text']}") for chunk in chunks]
    return chunks, BM25Okapi(corpus)


def retrieve(query: str, top_k: int = 4) -> list[dict]:
    chunks, bm25 = _bm25_index()
    scores = bm25.get_scores(tokenize(query))
    codes = _error_codes(query)
    products = _mentioned_products(query)

    ranked = []
    for score, chunk in zip(scores, chunks):
        blob = f"{chunk['heading']}\n{chunk['text']}"
        exact = 1 if any(code in blob for code in codes) else 0
        fit = _product_fit(products, chunk)
        if products and fit == 0:
            continue
        if score <= 0 and not exact:
            continue
        ranked.append((exact, fit, float(score), chunk))

    ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)

    results = []
    for exact, fit, score, chunk in ranked[:top_k]:
        match = dict(chunk)
        match["score"] = score + (100.0 if exact else 0.0) + (10.0 * fit)
        results.append(match)
    return results
