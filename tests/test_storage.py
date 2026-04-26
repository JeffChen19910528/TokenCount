import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
from pathlib import Path
from token_tracker import storage
from token_tracker.models import TaskRecord


class TestStorage(unittest.TestCase):
    def setUp(self):
        # Redirect DB to a temp file so tests don't pollute the real DB
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._orig_path = storage.DB_PATH
        storage.DB_PATH = Path(self._tmp.name)
        storage.init_db()

    def tearDown(self):
        storage.DB_PATH = self._orig_path
        self._tmp.close()
        os.unlink(self._tmp.name)

    def _make_record(self, tool="claude", prompt=100, completion=50):
        return TaskRecord(
            tool=tool,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=prompt + completion,
        )

    # --- save_task / get_tasks ---

    def test_save_and_retrieve_task(self):
        r = self._make_record()
        storage.save_task(r)
        tasks = storage.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_id"], r.task_id)
        self.assertEqual(tasks[0]["tool"], "claude")
        self.assertEqual(tasks[0]["total_tokens"], 150)

    def test_multiple_tools_stored_separately(self):
        storage.save_task(self._make_record("claude"))
        storage.save_task(self._make_record("codex"))
        storage.save_task(self._make_record("gemini"))
        self.assertEqual(len(storage.get_tasks()), 3)
        self.assertEqual(len(storage.get_tasks("claude")), 1)
        self.assertEqual(len(storage.get_tasks("codex")), 1)

    def test_filter_by_tool(self):
        for _ in range(3):
            storage.save_task(self._make_record("claude"))
        storage.save_task(self._make_record("codex"))
        self.assertEqual(len(storage.get_tasks("claude")), 3)
        self.assertEqual(len(storage.get_tasks("codex")), 1)

    def test_get_tasks_empty_db(self):
        self.assertEqual(storage.get_tasks(), [])
        self.assertEqual(storage.get_tasks("claude"), [])

    # --- tool_stats ---

    def test_tool_stats_accumulate(self):
        storage.save_task(self._make_record("claude", 100, 50))   # total 150
        storage.save_task(self._make_record("claude", 200, 100))  # total 300
        stats = {s["tool"]: s for s in storage.get_tool_stats()}
        self.assertEqual(stats["claude"]["total_tokens"], 450)
        self.assertEqual(stats["claude"]["task_count"], 2)

    def test_tool_stats_per_tool(self):
        storage.save_task(self._make_record("claude", 100, 50))
        storage.save_task(self._make_record("codex", 200, 100))
        stats = {s["tool"]: s for s in storage.get_tool_stats()}
        self.assertEqual(stats["claude"]["total_tokens"], 150)
        self.assertEqual(stats["codex"]["total_tokens"], 300)

    # --- daily_stats ---

    def test_daily_stats_groups_by_date(self):
        storage.save_task(self._make_record("claude", 100, 50))
        storage.save_task(self._make_record("claude", 200, 100))
        daily = storage.get_daily_stats()
        self.assertGreater(len(daily), 0)
        claude_rows = [d for d in daily if d["tool"] == "claude"]
        self.assertEqual(sum(d["total_tokens"] for d in claude_rows), 450)

    # --- idempotency (same task_id replaced) ---

    def test_duplicate_task_id_replaced(self):
        r = self._make_record()
        storage.save_task(r)
        storage.save_task(r)  # same task_id
        self.assertEqual(len(storage.get_tasks()), 1)
