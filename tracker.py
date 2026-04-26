#!/usr/bin/env python3
"""Multi-LLM Token Usage Tracker CLI."""
import argparse
import json
import sys

from token_tracker import registry, storage, reporter


def cmd_add(args: argparse.Namespace) -> None:
    adapter = registry.get_adapter(args.tool)
    data = json.loads(args.data) if args.data else {}
    record = adapter.parse(data)
    storage.save_task(record)
    print(f"Saved  task_id={record.task_id}  tool={record.tool}  tokens={record.total_tokens:,}")


def cmd_summary(args: argparse.Namespace) -> None:
    reporter.print_summary()


def cmd_report(args: argparse.Namespace) -> None:
    reporter.print_tool_report(args.tool)


def cmd_export(args: argparse.Namespace) -> None:
    reporter.export_data(args.format, getattr(args, "tool", None))


def build_parser() -> argparse.ArgumentParser:
    tools = registry.available_tools()
    parser = argparse.ArgumentParser(
        prog="tracker",
        description="Multi-LLM Token Usage Tracker",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # add
    p = sub.add_parser("add", help="Record a token usage entry")
    p.add_argument("--tool", required=True, choices=tools, help="LLM tool name")
    p.add_argument("--data", help='JSON string with usage data (e.g. \'{"usage":{"input_tokens":100,"output_tokens":50}}\')')
    p.set_defaults(func=cmd_add)

    # summary
    p = sub.add_parser("summary", help="Show overall token usage summary")
    p.set_defaults(func=cmd_summary)

    # report
    p = sub.add_parser("report", help="Show detailed report for a specific tool")
    p.add_argument("--tool", required=True, choices=tools)
    p.set_defaults(func=cmd_report)

    # export
    p = sub.add_parser("export", help="Export all data to CSV or JSON")
    p.add_argument("--format", required=True, choices=["csv", "json"])
    p.add_argument("--tool", choices=tools, help="Filter by tool (optional)")
    p.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    storage.init_db()
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
