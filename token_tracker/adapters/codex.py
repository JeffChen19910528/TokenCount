from .base import BaseAdapter
from ..models import TaskRecord


class CodexAdapter(BaseAdapter):
    tool_name = "codex"

    def parse(self, data: dict) -> TaskRecord:
        usage = data.get("usage", data)
        prompt = self._first(usage, "prompt_tokens")
        completion = self._first(usage, "completion_tokens")
        total = usage.get("total_tokens")
        return self._record(prompt, completion, total)
