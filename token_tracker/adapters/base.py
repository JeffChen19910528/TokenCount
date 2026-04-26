from abc import ABC, abstractmethod
from ..models import TaskRecord


class BaseAdapter(ABC):
    tool_name: str = ""

    @abstractmethod
    def parse(self, data: dict) -> TaskRecord:
        pass

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4
