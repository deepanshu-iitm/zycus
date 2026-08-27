from __future__ import annotations

import argparse

from support_copilot.triage import triage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="support-copilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage_parser = subparsers.add_parser("triage", help="Triage a support ticket")
    triage_parser.add_argument("--text", default="", help="Raw ticket text")
    triage_parser.add_argument("--subject", default="", help="Ticket subject")
    triage_parser.add_argument("--body", default="", help="Ticket body")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "triage":
        ticket: str | dict
        if args.text.strip():
            ticket = args.text
        else:
            ticket = {"subject": args.subject, "body": args.body}
        result = triage(ticket)
        print(result.model_dump_json(indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
