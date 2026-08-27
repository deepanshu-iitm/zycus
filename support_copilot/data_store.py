from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from support_copilot.config import ROOT_DIR

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
