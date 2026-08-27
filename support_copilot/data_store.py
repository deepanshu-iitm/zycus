from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

from support_copilot.config import ROOT_DIR, get_settings

DATA_DIR = ROOT_DIR / "data"


def _read_json(path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_tickets() -> list[dict]:
    return _read_json(DATA_DIR / "tickets.json")


@lru_cache(maxsize=1)
def load_accounts() -> list[dict]:
    return _read_json(DATA_DIR / "accounts.json")


def get_ticket(ticket_id: str) -> dict | None:
    for ticket in load_tickets():
        if ticket["ticket_id"] == ticket_id:
            return ticket
    return None


def get_account(account_id: str) -> dict | None:
    for account in load_accounts():
        if account["account_id"] == account_id:
            return account
    return None


def dataset_as_of() -> datetime:
    raw = get_settings().dataset_as_of
    return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def tickets_for_account(account_id: str, days: int = 90) -> list[dict]:
    """Tickets for an account in the last `days`, using the frozen dataset date.

    Most ticket `account_id` values do not match `accounts.json`. When the
    account exists, join by company name first, then fall back to account_id.
    """
    account = get_account(account_id)
    tickets = load_tickets()

    if account is not None:
        matched = [ticket for ticket in tickets if ticket.get("company") == account["company"]]
        if not matched:
            matched = [ticket for ticket in tickets if ticket["account_id"] == account_id]
    else:
        matched = [ticket for ticket in tickets if ticket["account_id"] == account_id]

    cutoff = dataset_as_of() - timedelta(days=days)
    return [
        ticket
        for ticket in matched
        if datetime.fromisoformat(ticket["created_at"].replace("Z", "+00:00")) > cutoff
    ]
