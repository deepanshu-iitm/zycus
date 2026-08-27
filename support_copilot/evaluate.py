from __future__ import annotations

import json
from pathlib import Path

from support_copilot.brief import generate_brief
from support_copilot.config import ROOT_DIR
from support_copilot.eval_cases import BRIEF_CASES, TRIAGE_CASES
from support_copilot.triage import triage

REPORT_DIR = ROOT_DIR / "reports"


def _score(checks: list[tuple[str, bool]]) -> dict:
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks) or 1
    quality = round(passed / total, 3)
    return {
        "pass": passed == total,
        "quality": quality,
        "checks": [{"name": name, "pass": ok} for name, ok in checks],
    }


def _kb_blob(result) -> str:
    return " ".join(match.path for match in result.knowledge_matches).lower()


def _eval_triage(case: dict) -> dict:
    result = triage(case["ticket"])
    checks = [
        ("has_reasoning", bool(result.reasoning.strip())),
        ("has_first_response", bool(result.first_response.strip())),
        ("has_team", bool(result.responder_team.strip())),
    ]
    if "expect_product" in case:
        checks.append(("product", result.product == case["expect_product"]))
    if "expect_category" in case:
        checks.append(("category", result.category == case["expect_category"]))
    if "expect_categories" in case:
        checks.append(("category", result.category in case["expect_categories"]))
    if "kb_contains" in case:
        checks.append(("kb_match", case["kb_contains"] in _kb_blob(result)))
    if "allowed_products" in case:
        checks.append(("product_allowed", result.product in case["allowed_products"]))
    row = _score(checks)
    row.update({"id": case["id"], "task": "triage", "adversarial": bool(case.get("adversarial"))})
    return row


def _eval_brief(case: dict) -> dict:
    if case.get("expect_error"):
        try:
            generate_brief(case["account_id"])
            checks = [("raises_for_unknown_account", False)]
        except ValueError:
            checks = [("raises_for_unknown_account", True)]
        row = _score(checks)
        row.update({"id": case["id"], "task": "brief", "adversarial": True})
        return row

    result = generate_brief(case["account_id"])
    summary = result.executive_summary.lower()
    flag_text = " ".join(flag.quote.lower() for flag in result.open_risks)
    sentences = [part for part in result.executive_summary.replace("!", ".").split(".") if part.strip()]
    checks = [
        ("has_summary", bool(result.executive_summary.strip())),
        ("summary_length", 3 <= len(sentences) <= 6),
        ("has_talking_points", len(result.talking_points) >= 3),
        ("flags_have_quotes", all(flag.quote.strip() for flag in result.open_risks)),
    ]
    if "expect_company" in case:
        checks.append(("company", result.company == case["expect_company"]))
    if "summary_must_include" in case:
        checks.append(("summary_includes", case["summary_must_include"] in summary))
    if "summary_must_not_include" in case:
        checks.append(("summary_excludes", case["summary_must_not_include"] not in summary))
    if "flag_quote_must_include" in case:
        checks.append(("flag_quote", case["flag_quote_must_include"] in flag_text))
    row = _score(checks)
    row.update({"id": case["id"], "task": "brief", "adversarial": bool(case.get("adversarial"))})
    return row


def run_eval() -> dict:
    results = []
    for case in TRIAGE_CASES:
        try:
            results.append(_eval_triage(case))
        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "task": "triage",
                    "pass": False,
                    "quality": 0.0,
                    "checks": [{"name": "ran_without_error", "pass": False}],
                    "error": str(exc),
                    "adversarial": bool(case.get("adversarial")),
                }
            )
    for case in BRIEF_CASES:
        try:
            results.append(_eval_brief(case))
        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "task": "brief",
                    "pass": False,
                    "quality": 0.0,
                    "checks": [{"name": "ran_without_error", "pass": False}],
                    "error": str(exc),
                    "adversarial": bool(case.get("adversarial")),
                }
            )

    quality = round(sum(item["quality"] for item in results) / len(results), 3)
    report = {
        "pass_count": sum(1 for item in results if item["pass"]),
        "case_count": len(results),
        "quality": quality,
        "results": results,
    }
    _write_reports(report)
    return report


def _write_reports(report: dict) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    json_path = REPORT_DIR / "eval_report.json"
    md_path = REPORT_DIR / "eval_report.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Eval report",
        "",
        f"Passed **{report['pass_count']}/{report['case_count']}** · quality **{report['quality']}**",
        "",
        "| Case | Task | Pass | Quality |",
        "|---|---|---|---|",
    ]
    for item in report["results"]:
        lines.append(
            f"| {item['id']} | {item['task']} | {'yes' if item['pass'] else 'no'} | {item['quality']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
