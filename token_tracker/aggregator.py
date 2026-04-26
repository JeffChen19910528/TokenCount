from .storage import get_tool_stats, get_tasks, get_daily_stats


def summarize() -> dict:
    return {
        "tool_stats": get_tool_stats(),
        "daily_stats": get_daily_stats(),
    }


def tool_report(tool: str) -> dict:
    tasks = get_tasks(tool)
    return {
        "tool": tool,
        "task_count": len(tasks),
        "total_tokens": sum(t["total_tokens"] for t in tasks),
        "tasks": tasks,
    }
