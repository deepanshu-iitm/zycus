from __future__ import annotations

import argparse
import json
import subprocess
import sys

from support_copilot.brief import generate_brief
from support_copilot.config import ROOT_DIR
from support_copilot.triage import triage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="support-copilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage_parser = subparsers.add_parser("triage", help="Triage a support ticket")
    triage_parser.add_argument("--text", default="", help="Raw ticket text")
    triage_parser.add_argument("--subject", default="", help="Ticket subject")
    triage_parser.add_argument("--body", default="", help="Ticket body")
    triage_parser.add_argument("--stream", action="store_true", help="Stream model tokens")

    brief_parser = subparsers.add_parser("brief", help="Generate a TAM account brief")
    brief_parser.add_argument("account_id", help="Account ID, for example ACC-2944")

    subparsers.add_parser("eval", help="Run the evaluation harness")
    subparsers.add_parser("ui", help="Launch the Streamlit demo")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "triage":
        ticket: str | dict
        if args.text.strip():
            ticket = args.text
        else:
            ticket = {"subject": args.subject, "body": args.body}
        if args.stream:
            print("Streaming model output:\n", flush=True)
            result = triage(ticket, on_token=lambda token: print(token, end="", flush=True))
            print("\n")
        else:
            result = triage(ticket)
        print(result.model_dump_json(indent=2))
        return 0

    if args.command == "brief":
        try:
            result = generate_brief(args.account_id)
        except ValueError as exc:
            print(str(exc))
            return 1
        print(result.model_dump_json(indent=2))
        return 0

    if args.command == "eval":
        from support_copilot.evaluate import run_eval

        report = run_eval()
        print(json.dumps(report, indent=2))
        print(f"Passed {report['pass_count']}/{report['case_count']} · quality {report['quality']}")
        return 0 if report["pass_count"] == report["case_count"] else 1

    if args.command == "ui":
        app = ROOT_DIR / "ui" / "app.py"
        return subprocess.call([sys.executable, "-m", "streamlit", "run", str(app)])

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
