from __future__ import annotations


def recommend_team(category: str, urgency: str) -> str:
    if urgency == "P1":
        return "Tier 2 Incident Response"
    if category == "Billing":
        return "Billing Operations"
    if category in {"How-To", "Onboarding"}:
        return "Tier 1 Support"
    if category in {"Bug", "Performance", "Integration", "Data Loss"}:
        return "Tier 2 Product Support"
    if category == "Feature Request":
        return "Product Specialist"
    return "Tier 1 Support"
