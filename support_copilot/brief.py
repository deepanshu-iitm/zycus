from __future__ import annotations

from support_copilot.brief_risks import extract_risk_flags
from support_copilot.brief_schema import AccountBrief
from support_copilot.data_store import get_account, tickets_for_account
from support_copilot.llm import complete_json
from support_copilot.prompts import load_prompt


def _ticket_lines(tickets: list[dict]) -> str:
    if not tickets:
        return "No tickets in the last 90 days."
    lines = []
    for ticket in tickets[:20]:
        lines.append(
            f"- {ticket.get('ticket_id')} | {ticket.get('urgency')} | "
            f"{ticket.get('status')} | {ticket.get('product')} | {ticket.get('subject')}"
        )
    extra = len(tickets) - 20
    if extra > 0:
        lines.append(f"- … {extra} more tickets omitted")
    return "\n".join(lines)


def generate_brief(account_id: str) -> AccountBrief:
    account = get_account(account_id)
    if account is None:
        raise ValueError(f"Unknown account_id: {account_id}")

    tickets = tickets_for_account(account_id)
    flags = extract_risk_flags(account, tickets)
    contact = account.get("primary_contact") or {}

    facts = (
        f"account_id: {account['account_id']}\n"
        f"company: {account.get('company')}\n"
        f"plan_tier: {account.get('plan_tier')}\n"
        f"arr_usd: {account.get('arr_usd')}\n"
        f"health_status: {account.get('health_status')}\n"
        f"usage_trend: {account.get('usage_trend')}\n"
        f"open_tickets: {account.get('open_tickets')}\n"
        f"p1_tickets_last_30d: {account.get('p1_tickets_last_30d')}\n"
        f"nps_score: {account.get('nps_score')}\n"
        f"renewal_date: {account.get('renewal_date')}\n"
        f"last_qbr_date: {account.get('last_qbr_date')}\n"
        f"products: {', '.join(account.get('products') or [])}\n"
        f"primary_contact: {contact.get('name')} ({contact.get('title')})\n"
        f"ticket_count_90d: {len(tickets)}\n"
    )
    flag_lines = (
        "\n".join(f"- {flag.label} [{flag.source}]: \"{flag.quote}\"" for flag in flags)
        or "None"
    )

    payload = complete_json(
        [
            {"role": "system", "content": load_prompt("brief")},
            {
                "role": "user",
                "content": (
                    f"Account facts:\n{facts}\n"
                    f"Tickets (last 90 days):\n{_ticket_lines(tickets)}\n\n"
                    f"Risk flags (already verified; do not invent more):\n{flag_lines}"
                ),
            },
        ],
        temperature=0.0,
    )

    talking_points = payload.get("talking_points") or []
    if isinstance(talking_points, str):
        talking_points = [talking_points]
    talking_points = [str(item).strip() for item in talking_points if str(item).strip()]

    return AccountBrief(
        account_id=account["account_id"],
        company=str(account.get("company") or ""),
        executive_summary=str(payload.get("executive_summary") or "").strip(),
        open_risks=flags,
        talking_points=talking_points,
    )
