from __future__ import annotations

from support_copilot.llm import complete_json
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

_SYSTEM = """You classify internal support tickets. Return a JSON object with keys:
product, product_area, category, urgency, reasoning, first_response.

product must be one of: DataBridge Pro, CloudSync, AnalyticsHub, SecureVault, WorkflowEngine, Unknown.
category must be one of: Bug, Feature Request, How-To, Performance, Billing, Integration, Onboarding, Data Loss.
urgency must be one of: P1, P2, P3, P4.
P1 = business stopped. P2 = major impact, workaround is painful. P3 = moderate, workaround exists. P4 = low or cosmetic.
If the ticket is ambiguous, set product to Unknown and explain in reasoning.
first_response is a short draft the support agent can send to the customer.
Use the knowledge-base excerpts for troubleshooting steps when they are relevant.
Do not invent error codes or product names that are not in the ticket or excerpts.
"""


def _normalize(ticket: str | dict) -> tuple[str, str]:
    if isinstance(ticket, str):
        return "", ticket.strip()
    subject = str(ticket.get("subject") or "").strip()
    body = str(ticket.get("body") or ticket.get("text") or "").strip()
    return subject, body


def triage(ticket: str | dict) -> TriageResult:
    subject, body = _normalize(ticket)
    query = f"{subject}\n{body}".strip()
    hits = retrieve(query, top_k=4)

    excerpts = "\n\n".join(
        f"[{hit['path']} | {hit['heading']}]\n{hit['text'][:900]}" for hit in hits
    ) or "None"

    payload = complete_json(
        [
            {"role": "system", "content": _SYSTEM},
            {
                "role": "user",
                "content": (
                    f"Subject: {subject or '(none)'}\n\n"
                    f"Body:\n{body or '(empty)'}\n\n"
                    f"Knowledge-base excerpts:\n{excerpts}"
                ),
            },
        ]
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
