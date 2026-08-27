from __future__ import annotations

from collections.abc import Callable

from support_copilot.llm import complete_json
from support_copilot.prompts import load_prompt
from support_copilot.retriever import retrieve
from support_copilot.routing import recommend_team
from support_copilot.triage_schema import KnowledgeMatch, TriageResult

_PRODUCTS = {
    "DataBridge Pro",
    "CloudSync",
    "AnalyticsHub",
    "SecureVault",
    "WorkflowEngine",
    "Unknown",
}
_CATEGORIES = {
    "Bug",
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
}
_URGENCIES = {"P1", "P2", "P3", "P4"}


def _normalize(ticket: str | dict) -> tuple[str, str]:
    if isinstance(ticket, str):
        return "", ticket.strip()
    subject = str(ticket.get("subject") or "").strip()
    body = str(ticket.get("body") or ticket.get("text") or "").strip()
    return subject, body


def triage(ticket: str | dict, on_token: Callable[[str], None] | None = None) -> TriageResult:
    subject, body = _normalize(ticket)
    query = f"{subject}\n{body}".strip()
    hits = retrieve(query, top_k=4)

    excerpts = "\n\n".join(
        f"[{hit['path']} | {hit['heading']}]\n{hit['text'][:900]}" for hit in hits
    ) or "None"

    payload = complete_json(
        [
            {"role": "system", "content": load_prompt("triage")},
            {
                "role": "user",
                "content": (
                    f"Subject: {subject or '(none)'}\n\n"
                    f"Body:\n{body or '(empty)'}\n\n"
                    f"Knowledge-base excerpts:\n{excerpts}"
                ),
            },
        ],
        on_token=on_token,
    )

    product = payload.get("product", "Unknown")
    if product not in _PRODUCTS:
        product = "Unknown"
    category = payload.get("category", "How-To")
    if category not in _CATEGORIES:
        category = "How-To"
    urgency = payload.get("urgency", "P3")
    if urgency not in _URGENCIES:
        urgency = "P3"

    matches = [
        KnowledgeMatch(
            path=hit["path"],
            heading=hit["heading"],
            snippet=hit["text"][:400],
            score=hit["score"],
        )
        for hit in hits
    ]

    return TriageResult(
        product=product,
        product_area=str(payload.get("product_area") or ""),
        category=category,
        urgency=urgency,
        reasoning=str(payload.get("reasoning") or ""),
        responder_team=recommend_team(category, urgency),
        first_response=str(payload.get("first_response") or ""),
        knowledge_matches=matches,
    )
