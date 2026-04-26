from .adapters.base import BaseAdapter
from .adapters.claude import ClaudeAdapter
from .adapters.codex import CodexAdapter
from .adapters.gemini import GeminiAdapter

_registry: dict[str, BaseAdapter] = {}


def register(adapter: BaseAdapter) -> None:
    _registry[adapter.tool_name] = adapter


def get_adapter(tool_name: str) -> BaseAdapter:
    if tool_name not in _registry:
        raise ValueError(f"Unknown tool '{tool_name}'. Available: {available_tools()}")
    return _registry[tool_name]


def available_tools() -> list[str]:
    return list(_registry.keys())


register(ClaudeAdapter())
register(CodexAdapter())
register(GeminiAdapter())
