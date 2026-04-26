You are a senior software engineer. Help me build a token usage tracking system for multiple AI CLI tools.

## 🎯 Goal

Build a Python-based tool that tracks and reports token usage for:

* Claude Code CLI
* OpenAI Codex CLI
* Gemini CLI

> **Status: ✅ Fully implemented** — see `tracker.py`, `token_tracker/`, `tests/`

---

## 🧱 Requirements

### 1. Multi-source parsing ✅

Adapters implemented in `token_tracker/adapters/`:

#### Claude Adapter (`adapters/claude.py`) ✅

* Parses Anthropic API response format
* Extracts `input_tokens` → `prompt_tokens`, `output_tokens` → `completion_tokens`
* Also accepts flat `prompt_tokens` / `completion_tokens` keys

#### Codex Adapter (`adapters/codex.py`) ✅

* Parses OpenAI API response format
* Extracts `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`

#### Gemini Adapter (`adapters/gemini.py`) ✅

* Parses `usageMetadata.promptTokenCount` / `candidatesTokenCount` / `totalTokenCount`
* Fallback estimation when `usageMetadata` absent:
  ```
  tokens ≈ len(text) / 4
  ```

---

### 2. Unified Data Format ✅

Implemented as `TaskRecord` dataclass in `token_tracker/models.py`:

```json
{
  "tool": "claude | codex | gemini",
  "task_id": "string (auto UUID)",
  "prompt_tokens": number,
  "completion_tokens": number,
  "total_tokens": number,
  "timestamp": "ISO8601 (auto UTC)"
}
```

---

### 3. Storage ✅

SQLite backend in `token_tracker/storage.py` → `token_usage.db`

Tables:

* `tasks` — one row per recorded task
* `tool_stats` — running totals per tool (updated on every insert via upsert)

---

### 4. Aggregation ✅

Implemented in `token_tracker/aggregator.py`:

* Total tokens per tool
* Tokens per task
* Daily usage grouped by tool + date

---

### 5. Reporting ✅

Implemented in `token_tracker/reporter.py`:

```bash
python tracker.py summary
python tracker.py report --tool claude
python tracker.py export --format csv
python tracker.py export --format json --tool gemini
```

Output example:

```
=== Token Usage Summary ===

Claude:
  Total Tokens: 6,100
  Tasks:        3

Codex:
  Total Tokens: 1,940
  Tasks:        2

Gemini:
  Total Tokens: 1,187
  Tasks:        2
```

---

### 6. Extensibility ✅

Adapter pattern via `token_tracker/registry.py`:

```python
# register a new tool in registry.py
from .adapters.mytool import MyToolAdapter
register(MyToolAdapter())
```

---

### 7. Optional (Advanced)

* [ ] Live monitoring via subprocess wrapper
* [ ] Hook into CLI calls

---

## ⚙️ Tech stack ✅

* Python 3.13 (compatible with 3.10+)
* SQLite (stdlib `sqlite3`)
* `argparse`
* `dataclasses`
* No third-party runtime dependencies

---

## 📦 Deliverables ✅

* [x] Full project structure
* [x] Working code (`tracker.py` + `token_tracker/`)
* [x] Example logs (`examples/`)
* [x] README (`README.md`)
* [x] Test suite — 40 tests, 100% passing (`tests/`)
