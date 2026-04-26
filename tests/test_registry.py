import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from token_tracker import registry
from token_tracker.adapters.claude import ClaudeAdapter
from token_tracker.adapters.codex import CodexAdapter
from token_tracker.adapters.gemini import GeminiAdapter


class TestRegistry(unittest.TestCase):
    def test_default_tools_registered(self):
        tools = registry.available_tools()
        self.assertIn("claude", tools)
        self.assertIn("codex", tools)
        self.assertIn("gemini", tools)

    def test_get_adapter_returns_correct_type(self):
        self.assertIsInstance(registry.get_adapter("claude"), ClaudeAdapter)
        self.assertIsInstance(registry.get_adapter("codex"), CodexAdapter)
        self.assertIsInstance(registry.get_adapter("gemini"), GeminiAdapter)

    def test_get_adapter_unknown_tool_raises(self):
        with self.assertRaises(ValueError):
            registry.get_adapter("unknown_tool_xyz")

    def test_register_custom_adapter(self):
        from token_tracker.adapters.base import BaseAdapter
        from token_tracker.models import TaskRecord

        class DummyAdapter(BaseAdapter):
            tool_name = "dummy_test_tool"
            def parse(self, data: dict) -> TaskRecord:
                return TaskRecord(tool=self.tool_name, prompt_tokens=1, completion_tokens=1, total_tokens=2)

        registry.register(DummyAdapter())
        self.assertIn("dummy_test_tool", registry.available_tools())
        r = registry.get_adapter("dummy_test_tool").parse({})
        self.assertEqual(r.tool, "dummy_test_tool")
