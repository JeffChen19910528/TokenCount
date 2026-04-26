import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .models import TaskRecord

DB_PATH = Path("token_usage.db")


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id           TEXT PRIMARY KEY,
                tool              TEXT NOT NULL,
                prompt_tokens     INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens      INTEGER NOT NULL,
                timestamp         TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tool_stats (
                tool        TEXT PRIMARY KEY,
                total_tokens INTEGER NOT NULL DEFAULT 0,
                task_count   INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_tool ON tasks(tool)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(substr(timestamp,1,10))")


def save_task(record: TaskRecord) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO tasks VALUES (?,?,?,?,?,?)",
            (record.task_id, record.tool, record.prompt_tokens,
             record.completion_tokens, record.total_tokens, record.timestamp),
        )
        conn.execute(
            """
            INSERT INTO tool_stats (tool, total_tokens, task_count) VALUES (?,?,1)
            ON CONFLICT(tool) DO UPDATE SET
                total_tokens = total_tokens + excluded.total_tokens,
                task_count   = task_count + 1
            """,
            (record.tool, record.total_tokens),
        )


def get_tasks(tool: str | None = None) -> list[dict]:
    with _conn() as conn:
        if tool:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE tool=? ORDER BY timestamp DESC", (tool,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks ORDER BY timestamp DESC").fetchall()
        return [dict(r) for r in rows]


def get_tool_stats() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM tool_stats ORDER BY total_tokens DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_daily_stats() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT tool,
                   substr(timestamp,1,10) AS date,
                   SUM(total_tokens)      AS total_tokens,
                   COUNT(*)               AS task_count
            FROM tasks
            GROUP BY tool, date
            ORDER BY date DESC, tool
        """).fetchall()
        return [dict(r) for r in rows]
