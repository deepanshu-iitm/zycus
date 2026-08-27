from __future__ import annotations

import re

from support_copilot.brief_schema import RiskFlag

_PATTERNS = (
    (
        "Competitor evaluation",
        re.compile(r"competitor|another vendor|switching to|evaluating .{0,40}vendor", re.I),
    ),
    (
        "Cancellation / non-renewal",
        re.compile(r"\bcancel(?:lation)?\b|not renew|won't renew|will not renew|\bchurn", re.I),
    ),
    (
        "Escalation / frustration",
        re.compile(r"frustrat|unacceptable|escalate|outraged|legal team|lawyer", re.I),
    ),
    (
        "Data loss",
        re.compile(r"data loss|lost data|missing data|corrupt(?:ed)? data", re.I),
    ),
)


def _quote_around(text: str, match: re.Match) -> str:
    start = text.rfind(".", 0, match.start()) + 1
    end = text.find(".", match.end())
    snippet = text[start : end if end != -1 else match.end() + 120].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet[:280]


def extract_risk_flags(account: dict, tickets: list[dict]) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    seen: set[tuple[str, str]] = set()

    def add(label: str, quote: str, source: str) -> None:
        key = (label, quote)
        if not quote or key in seen:
            return
        seen.add(key)
        flags.append(RiskFlag(label=label, quote=quote, source=source))

    for note in account.get("escalation_notes") or []:
        cleaned = str(note).strip()
        if cleaned:
            add("Account escalation note", cleaned, "escalation_notes")

    for ticket in tickets:
        ticket_id = ticket.get("ticket_id", "unknown")
        blob = f"{ticket.get('subject', '')}\n{ticket.get('body', '')}"
        if ticket.get("urgency") == "P1":
            subject = str(ticket.get("subject") or "").strip()
            add("P1 incident", subject or blob[:180].strip(), ticket_id)
        for label, pattern in _PATTERNS:
            match = pattern.search(blob)
            if match:
                add(label, _quote_around(blob, match), ticket_id)

    return flags
