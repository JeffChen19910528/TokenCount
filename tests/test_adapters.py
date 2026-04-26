import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from token_tracker.adapters.claude import ClaudeAdapter
from token_tracker.adapters.codex import CodexAdapter
from token_tracker.adapters.gemini import GeminiAdapter
from token_tracker.models import TaskRecord


class TestClaudeAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ClaudeAdapter()

    def test_tool_name(self):
        self.assertEqual(self.adapter.tool_name, "claude")

    def test_standard_anthropic_format(self):
        data = {"usage": {"input_tokens": 100, "output_tokens": 50}}
        r = self.adapter.parse(data)
        self.assertIsInstance(r, TaskRecord)
        self.assertEqual(r.tool, "claude")
        self.assertEqual(r.prompt_tokens, 100)
        self.assertEqual(r.completion_tokens, 50)
        self.assertEqual(r.total_tokens, 150)

    def test_flat_prompt_tokens_key(self):
        data = {"prompt_tokens": 200, "completion_tokens": 80, "total_tokens": 280}
        r = self.adapter.parse(data)
        self.assertEqual(r.prompt_tokens, 200)
        self.assertEqual(r.completion_tokens, 80)
        self.assertEqual(r.total_tokens, 280)

    def test_zero_usage(self):
        r = self.adapter.parse({})
        self.assertEqual(r.total_tokens, 0)

    def test_returns_unique_task_ids(self):
        r1 = self.adapter.parse({"usage": {"input_tokens": 10, "output_tokens": 5}})
        r2 = self.adapter.parse({"usage": {"input_tokens": 10, "output_tokens": 5}})
        self.assertNotEqual(r1.task_id, r2.task_id)


class TestCodexAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = CodexAdapter()

    def test_tool_name(self):
        self.assertEqual(self.adapter.tool_name, "codex")

    def test_openai_response_format(self):
        data = {
            "usage": {
                "prompt_tokens": 800,
                "completion_tokens": 300,
                "total_tokens": 1100,
            }
        }
        r = self.adapter.parse(data)
        self.assertEqual(r.prompt_tokens, 800)
        self.assertEqual(r.completion_tokens, 300)
        self.assertEqual(r.total_tokens, 1100)

    def test_total_computed_when_missing(self):
        data = {"usage": {"prompt_tokens": 400, "completion_tokens": 100}}
        r = self.adapter.parse(data)
        self.assertEqual(r.total_tokens, 500)

    def test_zero_usage(self):
        r = self.adapter.parse({})
        self.assertEqual(r.total_tokens, 0)


class TestGeminiAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = GeminiAdapter()

    def test_tool_name(self):
        self.assertEqual(self.adapter.tool_name, "gemini")

    def test_usage_metadata_format(self):
        data = {
            "usageMetadata": {
                "promptTokenCount": 600,
                "candidatesTokenCount": 200,
                "totalTokenCount": 800,
            }
        }
        r = self.adapter.parse(data)
        self.assertEqual(r.prompt_tokens, 600)
        self.assertEqual(r.completion_tokens, 200)
        self.assertEqual(r.total_tokens, 800)

    def test_fallback_estimation_from_text(self):
        prompt_text = "A" * 40   # 40 chars → 10 tokens
        completion_text = "B" * 80  # 80 chars → 20 tokens
        data = {"prompt": prompt_text, "completion": completion_text}
        r = self.adapter.parse(data)
        self.assertEqual(r.prompt_tokens, 10)
        self.assertEqual(r.completion_tokens, 20)
        self.assertEqual(r.total_tokens, 30)

    def test_empty_fallback(self):
        r = self.adapter.parse({})
        self.assertEqual(r.total_tokens, 0)

    def test_total_computed_from_counts_when_total_missing(self):
        data = {
            "usageMetadata": {
                "promptTokenCount": 300,
                "candidatesTokenCount": 150,
            }
        }
        r = self.adapter.parse(data)
        self.assertEqual(r.total_tokens, 450)


class TestBaseEstimation(unittest.TestCase):
    def test_estimate_tokens(self):
        adapter = ClaudeAdapter()
        self.assertEqual(adapter.estimate_tokens("A" * 100), 25)
        self.assertEqual(adapter.estimate_tokens(""), 0)
        self.assertEqual(adapter.estimate_tokens("abcd"), 1)
