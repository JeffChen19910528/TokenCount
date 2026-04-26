import csv
import json
import sys

from .aggregator import summarize, tool_report
from .storage import get_tasks


def print_summary() -> None:
    data = summarize()

    print("\n=== Token Usage Summary ===\n")
    if not data["tool_stats"]:
        print("  No data recorded yet.\n")
        return

    for stat in data["tool_stats"]:
        print(f"{stat['tool'].capitalize()}:")
        print(f"  Total Tokens: {stat['total_tokens']:,}")
        print(f"  Tasks:        {stat['task_count']}")
        print()

    if data["daily_stats"]:
        print("=== Daily Usage ===\n")
        current_date = None
        for row in data["daily_stats"]:
            if row["date"] != current_date:
                current_date = row["date"]
                print(f"  {current_date}:")
            print(f"    {row['tool']:<10} {row['total_tokens']:>10,} tokens  ({row['task_count']} tasks)")
        print()


def print_tool_report(tool: str) -> None:
    data = tool_report(tool)
    print(f"\n=== Report: {data['tool'].capitalize()} ===\n")
    print(f"Total Tasks:  {data['task_count']:,}")
    print(f"Total Tokens: {data['total_tokens']:,}\n")

    if not data["tasks"]:
        print("  No tasks recorded.\n")
        return

    header = f"{'Task ID':<38}  {'Prompt':>10}  {'Completion':>12}  {'Total':>10}  Timestamp"
    print(header)
    print("-" * len(header))
    for t in data["tasks"]:
        print(
            f"{t['task_id']:<38}  {t['prompt_tokens']:>10,}  "
            f"{t['completion_tokens']:>12,}  {t['total_tokens']:>10,}  {t['timestamp']}"
        )
    print()


def export_data(fmt: str, tool: str | None = None) -> None:
    tasks = get_tasks(tool)
    fields = ["task_id", "tool", "prompt_tokens", "completion_tokens", "total_tokens", "timestamp"]

    if fmt == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(tasks)
    elif fmt == "json":
        print(json.dumps(tasks, indent=2))
    else:
        print(f"Unknown format '{fmt}'. Use 'csv' or 'json'.", file=sys.stderr)
        sys.exit(1)
