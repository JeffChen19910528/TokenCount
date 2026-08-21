# Token Usage Tracker

A unified CLI tool for tracking token usage across multiple LLM tools: **Claude Code**, **OpenAI Codex**, and **Gemini CLI**.

## Project Structure

```
TokenCount/
├── tracker.py                   # CLI entry point (add / summary / report / export)
├── requirements.txt
├── token_tracker/
│   ├── __init__.py
│   ├── models.py                # TaskRecord dataclass
│   ├── registry.py              # Adapter registry (register / get_adapter)
│   ├── storage.py               # SQLite backend  →  token_usage.db
│   ├── aggregator.py            # Per-tool and daily aggregation (only layer that touches storage)
│   ├── reporter.py              # CLI output, CSV / JSON export (goes through aggregator only)
│   └── adapters/
│       ├── __init__.py
│       ├── base.py              # BaseAdapter ABC + estimate_tokens() / _first() / _record() helpers
│       ├── claude.py            # Anthropic  (input_tokens / output_tokens)
│       ├── codex.py             # OpenAI     (prompt_tokens / completion_tokens)
│       └── gemini.py            # Google     (usageMetadata, fallback estimation)
├── examples/
│   ├── seed_demo.py             # Insert sample records for all three tools
│   ├── claude_response.json
│   ├── codex_response.json
│   ├── gemini_response.json
│   └── gemini_no_usage.json     # Gemini without usageMetadata (triggers estimation)
└── tests/                       # 40 unit tests — pytest
    ├── test_adapters.py         # 15 tests: parse logic, fallback, unique IDs
    ├── test_storage.py          #  9 tests: CRUD, filtering, stats accumulation
    ├── test_aggregator.py       #  5 tests: tool totals, daily grouping
    ├── test_registry.py         #  4 tests: lookup, unknown tool, custom adapter
    └── test_reporter.py         #  8 tests: output format, CSV/JSON, empty DB
```

## Requirements

- Python 3.10+
- No third-party packages (stdlib only: `sqlite3`, `argparse`, `dataclasses`, `csv`, `json`)
- `pytest` for running tests

## Quick Start

```bash
# Seed demo data
python examples/seed_demo.py

# Show summary across all tools
python tracker.py summary

# Detailed report for one tool
python tracker.py report --tool claude

# Add a record manually
python tracker.py add --tool claude --data '{"usage":{"input_tokens":1200,"output_tokens":400}}'
python tracker.py add --tool codex  --data '{"usage":{"prompt_tokens":800,"completion_tokens":300}}'
python tracker.py add --tool gemini --data '{"usageMetadata":{"promptTokenCount":600,"candidatesTokenCount":200}}'

# Export data
python tracker.py export --format csv
python tracker.py export --format json --tool gemini

# Run all tests
python -m pytest tests/ -v
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `tracker.py add --tool <name> --data <json>` | Record a token usage entry |
| `tracker.py summary` | Overall totals per tool + daily breakdown |
| `tracker.py report --tool <name>` | Per-task detail for one tool |
| `tracker.py export --format csv\|json [--tool <name>]` | Export all or filtered data |

## Input Formats

### Claude (Anthropic API)
```json
{"usage": {"input_tokens": 1240, "output_tokens": 580}}
```

### Codex (OpenAI API)
```json
{"usage": {"prompt_tokens": 890, "completion_tokens": 310, "total_tokens": 1200}}
```

### Gemini (Google API)
```json
{"usageMetadata": {"promptTokenCount": 750, "candidatesTokenCount": 420, "totalTokenCount": 1170}}
```

If `usageMetadata` is absent, the Gemini adapter estimates tokens using `len(text) / 4` from `prompt` and `completion` text fields.

## Storage

Data is persisted in `token_usage.db` (SQLite) with two tables:

| Table | Contents |
|-------|---------|
| `tasks` | One row per recorded task (task_id, tool, prompt/completion/total tokens, timestamp) |
| `tool_stats` | Running totals per tool (total_tokens, task_count) — updated on every insert |

## Layering

Each module only depends on the layer directly beneath it:

```
reporter.py  →  aggregator.py  →  storage.py
```

`reporter.py` never imports `storage` directly — it calls `aggregator.list_tasks()` / `summarize()` / `tool_report()`. This keeps the CLI output layer decoupled from the persistence layer, so storage can change without touching reporting.

## Adding a New Tool

1. Create `token_tracker/adapters/mytool.py` extending `BaseAdapter`
2. Set `tool_name = "mytool"` and implement `parse(data: dict) -> TaskRecord`
   - Use `self._first(usage, "key_a", "key_b")` to read a field under multiple possible key names
   - Use `self._record(prompt, completion, total)` to build the `TaskRecord` (computes `total` from `prompt + completion` when `total` is `None`)
3. Register it in `token_tracker/registry.py`:
   ```python
   from .adapters.mytool import MyToolAdapter
   register(MyToolAdapter())
   ```
4. Add tests in `tests/test_adapters.py`
