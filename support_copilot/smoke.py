from __future__ import annotations

from support_copilot.brief_risks import extract_risk_flags
from support_copilot.data_store import get_account, tickets_for_account
from support_copilot.prompts import load_prompt, prompt_id
from support_copilot.retriever import retrieve
from support_copilot.routing import recommend_team


def run_smoke() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    hits = retrieve(
        "DataBridge Pro pipeline failed with ERR_CONNECTION_TIMEOUT in production."
    )
    top = hits[0]["path"] if hits else ""
    check("timeout_hits_databridge", "databridge-pro" in top, top)
    check(
        "timeout_skips_other_products",
        all("cloudsync" not in hit["path"].lower() for hit in hits),
        ",".join(hit["path"] for hit in hits),
    )

    check("route_p1", recommend_team("Bug", "P1") == "Tier 2 Incident Response")
    check("route_billing", recommend_team("Billing", "P3") == "Billing Operations")

    account = get_account("ACC-2944")
    check("account_exists", account is not None)
    check("unknown_account", get_account("ACC-0000") is None)

    tickets = tickets_for_account("ACC-2944")
    check("account_has_tickets", len(tickets) > 0, str(len(tickets)))

    flags = extract_risk_flags(account or {}, tickets)
    blob = " ".join(flag.quote.lower() for flag in flags)
    check("churn_quote", "competing vendor" in blob, blob[:200])
    check("flags_quoted", all(flag.quote.strip() for flag in flags))

    check("prompt_triage_id", prompt_id("triage") == "triage_v1")
    check("prompt_brief_loaded", len(load_prompt("brief")) > 40)

    return checks


def main() -> int:
    checks = run_smoke()
    failed = 0
    for name, ok, detail in checks:
        mark = "PASS" if ok else "FAIL"
        extra = f" ({detail})" if detail and not ok else ""
        print(f"{mark}  {name}{extra}")
        if not ok:
            failed += 1
    print(f"{len(checks) - failed}/{len(checks)} passed")
    return 1 if failed else 0
