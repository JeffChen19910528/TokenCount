#!/usr/bin/env python3
"""Seed demo data into the tracker database."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from token_tracker import registry, storage

storage.init_db()

samples = [
    ("claude", {"usage": {"input_tokens": 1240, "output_tokens": 580}}),
    ("claude", {"usage": {"input_tokens": 890,  "output_tokens": 340}}),
    ("claude", {"usage": {"input_tokens": 2100, "output_tokens": 950}}),
    ("codex",  {"usage": {"prompt_tokens": 890,  "completion_tokens": 310, "total_tokens": 1200}}),
    ("codex",  {"usage": {"prompt_tokens": 560,  "completion_tokens": 180, "total_tokens": 740}}),
    ("gemini", {"usageMetadata": {"promptTokenCount": 750, "candidatesTokenCount": 420, "totalTokenCount": 1170}}),
    ("gemini", {"prompt": "Explain recursion.", "completion": "Recursion is a technique where a function calls itself."}),
]

for tool, data in samples:
    adapter = registry.get_adapter(tool)
    record = adapter.parse(data)
    storage.save_task(record)
    print(f"  {tool:<8} prompt={record.prompt_tokens:>5}  completion={record.completion_tokens:>5}  total={record.total_tokens:>6}")

print(f"\nSeeded {len(samples)} tasks. Run: python tracker.py summary")
