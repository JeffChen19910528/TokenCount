from .base import BaseAdapter
from ..models import TaskRecord


class CodexAdapter(BaseAdapter):
    tool_name = "codex"

    def parse(self, data: dict) -> TaskRecord:
        usage = data.get("usage", data)
        prompt = usage.get("prompt_tokens", 0)
        completion = usage.get("completion_tokens", 0)
        total = usage.get("total_tokens", prompt + completion)
        return TaskRecord(
            tool=self.tool_name,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
        )
