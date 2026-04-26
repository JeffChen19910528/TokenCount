import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import tempfile
from pathlib import Path
from token_tracker import storage, aggregator
from token_tracker.models import TaskRecord


class TestAggregator(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._orig_path = storage.DB_PATH
        storage.DB_PATH = Path(self._tmp.name)
        storage.init_db()
        self._seed()

    def tearDown(self):
        storage.DB_PATH = self._orig_path
        self._tmp.close()
        os.unlink(self._tmp.name)

    def _seed(self):
        records = [
            TaskRecord("claude", 100, 50,  150),
            TaskRecord("claude", 200, 100, 300),
            TaskRecord("codex",  400, 200, 600),
            TaskRecord("gemini", 300, 150, 450),
        ]
        for r in records:
            storage.save_task(r)

    def test_summarize_returns_tool_stats(self):
        data = aggregator.summarize()
        tools = {s["tool"] for s in data["tool_stats"]}
        self.assertIn("claude", tools)
        self.assertIn("codex", tools)
        self.assertIn("gemini", tools)

    def test_claude_total_correct(self):
        data = aggregator.summarize()
        stats = {s["tool"]: s for s in data["tool_stats"]}
        self.assertEqual(stats["claude"]["total_tokens"], 450)
        self.assertEqual(stats["claude"]["task_count"], 2)

    def test_tool_report_structure(self):
        report = aggregator.tool_report("codex")
        self.assertEqual(report["tool"], "codex")
        self.assertEqual(report["task_count"], 1)
        self.assertEqual(report["total_tokens"], 600)
        self.assertEqual(len(report["tasks"]), 1)

    def test_tool_report_empty_tool(self):
        report = aggregator.tool_report("nonexistent")
        self.assertEqual(report["task_count"], 0)
        self.assertEqual(report["total_tokens"], 0)
        self.assertEqual(report["tasks"], [])

    def test_summarize_daily_stats_present(self):
        data = aggregator.summarize()
        self.assertIn("daily_stats", data)
        self.assertGreater(len(data["daily_stats"]), 0)
