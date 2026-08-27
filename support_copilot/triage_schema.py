from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Product = Literal[
    "DataBridge Pro",
    "CloudSync",
    "AnalyticsHub",
    "SecureVault",
    "WorkflowEngine",
    "Unknown",
]

Category = Literal[
    "Bug",
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
]

Urgency = Literal["P1", "P2", "P3", "P4"]


class KnowledgeMatch(BaseModel):
    path: str
    heading: str
    snippet: str
    score: float = 0.0


class TriageResult(BaseModel):
    product: Product
    product_area: str = ""
    category: Category
    urgency: Urgency
    reasoning: str
    responder_team: str
    first_response: str
    knowledge_matches: list[KnowledgeMatch] = Field(default_factory=list)
