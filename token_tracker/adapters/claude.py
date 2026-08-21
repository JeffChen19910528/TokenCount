from .base import BaseAdapter
from ..models import TaskRecord


class ClaudeAdapter(BaseAdapter):
    tool_name = "claude"

    def parse(self, data: dict) -> TaskRecord:
        usage = data.get("usage", data)
        prompt = self._first(usage, "input_tokens", "prompt_tokens")
        completion = self._first(usage, "output_tokens", "completion_tokens")
        total = usage.get("total_tokens")
        return self._record(prompt, completion, total)
