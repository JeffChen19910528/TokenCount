from abc import ABC, abstractmethod
from ..models import TaskRecord


class BaseAdapter(ABC):
    tool_name: str = ""

    @abstractmethod
    def parse(self, data: dict) -> TaskRecord:
        pass

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    @staticmethod
    def _first(usage: dict, *keys: str, default: int = 0) -> int:
        """Return the value of the first key present in usage, else default."""
        for key in keys:
            if key in usage:
                return usage[key]
        return default

    def _record(self, prompt: int, completion: int, total: int | None = None) -> TaskRecord:
        return TaskRecord(
            tool=self.tool_name,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total if total is not None else prompt + completion,
        )
