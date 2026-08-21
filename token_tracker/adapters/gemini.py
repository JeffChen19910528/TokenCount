from .base import BaseAdapter
from ..models import TaskRecord


class GeminiAdapter(BaseAdapter):
    tool_name = "gemini"

    def parse(self, data: dict) -> TaskRecord:
        meta = data.get("usageMetadata", data.get("usage", {}))
        prompt = self._first(meta, "promptTokenCount", "prompt_tokens")
        completion = self._first(meta, "candidatesTokenCount", "completion_tokens")
        total = meta.get("totalTokenCount", meta.get("total_tokens", 0)) or prompt + completion

        # Fallback: estimate from raw text when no usage metadata present
        if total == 0:
            prompt = self.estimate_tokens(data.get("prompt", ""))
            completion = self.estimate_tokens(data.get("completion", ""))
            total = prompt + completion

        return self._record(prompt, completion, total)
