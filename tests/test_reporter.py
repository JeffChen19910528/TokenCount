import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import io
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from token_tracker import storage, reporter
from token_tracker.models import TaskRecord


class TestReporter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._orig_path = storage.DB_PATH
        storage.DB_PATH = Path(self._tmp.name)
        storage.init_db()
        storage.save_task(TaskRecord("claude", 100, 50,  150))
        storage.save_task(TaskRecord("codex",  400, 200, 600))
        storage.save_task(TaskRecord("gemini", 300, 150, 450))

    def tearDown(self):
        storage.DB_PATH = self._orig_path
        self._tmp.close()
        os.unlink(self._tmp.name)

    def test_print_summary_contains_tool_names(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.print_summary()
        output = buf.getvalue()
        self.assertIn("Claude", output)
        self.assertIn("Codex", output)
        self.assertIn("Gemini", output)

    def test_print_summary_shows_token_counts(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.print_summary()
        output = buf.getvalue()
        self.assertIn("150", output)
        self.assertIn("600", output)

    def test_print_tool_report_correct_totals(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.print_tool_report("claude")
        output = buf.getvalue()
        self.assertIn("150", output)
        self.assertIn("1", output)  # task count

    def test_export_csv_valid_format(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.export_data("csv")
        buf.seek(0)
        reader = csv.DictReader(buf)
        rows = list(reader)
        self.assertEqual(len(rows), 3)
        self.assertIn("task_id", reader.fieldnames)
        self.assertIn("total_tokens", reader.fieldnames)

    def test_export_json_valid_format(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.export_data("json")
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertIn("tool", data[0])

    def test_export_csv_filtered_by_tool(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.export_data("csv", tool="claude")
        buf.seek(0)
        rows = list(csv.DictReader(buf))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tool"], "claude")

    def test_export_unknown_format_exits(self):
        with self.assertRaises(SystemExit):
            reporter.export_data("xml")

    def test_print_summary_empty_db(self):
        # Fresh empty DB
        tmp2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        storage.DB_PATH = Path(tmp2.name)
        storage.init_db()
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            reporter.print_summary()
        output = buf.getvalue()
        self.assertIn("No data", output)
        storage.DB_PATH = self._orig_path
        tmp2.close()
        os.unlink(tmp2.name)
