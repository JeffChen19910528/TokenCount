from .base import BaseAdapter
from ..models import TaskRecord


class GeminiAdapter(BaseAdapter):
    tool_name = "gemini"

    def parse(self, data: dict) -> TaskRecord:
        meta = data.get("usageMetadata", data.get("usage", {}))
        prompt = meta.get("promptTokenCount", meta.get("prompt_tokens", 0))
        completion = meta.get("candidatesTokenCount", meta.get("completion_tokens", 0))
        total = meta.get("totalTokenCount", meta.get("total_tokens", 0)) or prompt + completion

        # Fallback: estimate from raw text when no usage metadata present
        if total == 0:
            prompt_text = data.get("prompt", "")
            completion_text = data.get("completion", "")
            prompt = self.estimate_tokens(prompt_text)
            completion = self.estimate_tokens(completion_text)
            total = prompt + completion

        return TaskRecord(
            tool=self.tool_name,
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=total,
        )
