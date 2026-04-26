from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class TaskRecord:
    tool: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
