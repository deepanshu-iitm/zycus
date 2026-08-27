from __future__ import annotations

from pydantic import BaseModel, Field


class RiskFlag(BaseModel):
    label: str
    quote: str
    source: str


class AccountBrief(BaseModel):
    account_id: str
    company: str
    executive_summary: str
    open_risks: list[RiskFlag] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)
