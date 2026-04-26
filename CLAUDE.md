# Token Usage Tracker for Multi-LLM CLI Tools

## 📌 Project Overview

This project provides a unified token usage tracking system for multiple LLM CLI tools, including:

* Claude Code (Anthropic)
* Codex CLI (OpenAI)
* Gemini CLI (Google)

The system is designed to **monitor, aggregate, and report token consumption** across different tools while keeping their usage **separated and independently analyzable**.

> **Status:** Fully implemented. Run `python -m pytest tests/ -v` to verify (40/40 tests pass).

---

## 🎯 Objectives

* Track token usage per task
* Maintain separate statistics for each LLM tool
* Provide aggregated reports (per tool, per day, per task)
* Support both **exact usage extraction** and **fallback estimation**
* Enable future extensibility for additional LLM providers

---

## 🧱 System Architecture

The system follows a modular architecture:

```
                +----------------------+
                |   CLI / Log Sources  |
                +----------+-----------+
                           |
        +------------------+------------------+
        |        Source Adapters              |
        |------------------------------------|
        | ClaudeAdapter  (adapters/claude.py) |
        | CodexAdapter   (adapters/codex.py)  |
        | GeminiAdapter  (adapters/gemini.py) |
        +------------------+------------------+
                           |
                           v
                +----------------------+
                | Token Normalizer     |  ← TaskRecord dataclass (models.py)
                +----------------------+
                           |
                           v
                +----------------------+
                | Aggregator           |  ← aggregator.py
                +----------------------+
                           |
                           v
                +----------------------+
                | Storage (SQLite)     |  ← storage.py → token_usage.db
                +----------------------+
                           |
                           v
                +----------------------+
                | Reporter (CLI/Export)|  ← reporter.py
                +----------------------+
```

### Key files

| File | Role |
|------|------|
| `tracker.py` | CLI entry point — `add`, `summary`, `report`, `export` subcommands |
| `token_tracker/models.py` | `TaskRecord` dataclass with auto-generated `task_id` and `timestamp` |
| `token_tracker/registry.py` | Adapter registry; call `register()` to add new tools |
| `token_tracker/storage.py` | SQLite CRUD — `init_db`, `save_task`, `get_tasks`, `get_tool_stats`, `get_daily_stats` |
| `token_tracker/aggregator.py` | `summarize()` and `tool_report()` — thin layer over storage |
| `token_tracker/reporter.py` | Formatted terminal output + CSV/JSON export |
| `token_tracker/adapters/base.py` | `BaseAdapter` ABC + `estimate_tokens(text)` helper |

---

## 🔌 Supported Tools

### Claude Code

* Provider: Anthropic
* Token source: API response / CLI logs
* Accuracy: High (native token usage available)

### Codex CLI

* Provider: OpenAI
* Token source: API response / logs
* Accuracy: High

### Gemini CLI

* Provider: Google
* Token source: Not always available
* Strategy:

  * Use native usage if available
  * Otherwise fallback to estimation:

    ```
    tokens ≈ len(text) / 4
    ```

---

## 📊 Data Model

Each task is recorded as:

```json
{
  "tool": "claude | codex | gemini",
  "task_id": "string",
  "prompt_tokens": number,
  "completion_tokens": number,
  "total_tokens": number,
  "timestamp": "ISO8601"
}
```

---

## 📈 Aggregation Strategy

Token usage is **NOT merged across tools**.

Instead, the system maintains:

* Per-tool total tokens
* Per-task token usage
* Time-based summaries (daily / session)

Example:

```
Claude:
  Total Tokens: 50,000
  Tasks: 25

Codex:
  Total Tokens: 30,000

Gemini:
  Total Tokens: 20,000
```

---

## 💾 Storage

Two supported storage backends:

### Option A: SQLite (Recommended)

Tables:

* `tasks`
* `tool_stats`

### Option B: JSON

* Simple file-based storage
* Easier debugging

---

## 🧪 Task Definition

A "task" is defined as:

* One CLI invocation OR
* One request-response cycle

Each task must include:

* Unique ID
* Timestamp
* Tool identifier

---

## 📤 Reporting Features

CLI commands:

```bash
python tracker.py summary                          # totals per tool + daily breakdown
python tracker.py report --tool claude             # per-task detail
python tracker.py export --format csv              # all data as CSV
python tracker.py export --format json --tool codex  # filtered JSON export
```

Outputs include:

* Total tokens per tool
* Token usage per task
* Daily usage breakdown
* Exportable reports (CSV / JSON)

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

40 unit tests across 5 modules:

| Test file | Coverage |
|-----------|---------|
| `tests/test_adapters.py` | parse logic, field fallbacks, fallback estimation, unique IDs |
| `tests/test_storage.py` | save/retrieve, tool filtering, stats accumulation, duplicate handling |
| `tests/test_aggregator.py` | tool totals, empty tool, daily grouping |
| `tests/test_registry.py` | default adapters, unknown tool error, custom adapter registration |
| `tests/test_reporter.py` | terminal output, CSV/JSON format, tool filter, unknown format exit |

---

## ⚠️ Limitations

1. Not all tools expose token usage (e.g., Gemini CLI)
2. Estimation may introduce inaccuracies
3. Requires consistent log format or API access

---

## 🔧 Extensibility

The system uses an Adapter Pattern:

To add a new tool:

1. Create `token_tracker/adapters/<toolname>.py` extending `BaseAdapter`
2. Set `tool_name` and implement `parse(data: dict) -> TaskRecord`
3. Register in `token_tracker/registry.py` with `register(MyAdapter())`
4. Add tests in `tests/test_adapters.py`

---

## 💡 Future Improvements

* Real-time monitoring via CLI wrapper
* Cost calculation (USD per token)
* Dashboard visualization (Streamlit / Grafana)
* Integration with experiment pipelines (e.g., ERC-4337 simulations)

---

## 📚 Use Cases

* LLM cost tracking
* Experiment analysis (token efficiency)
* Multi-model comparison
* Research and academic reporting

---

## 🧾 License

MIT License (or specify as needed)

---

## 👨‍💻 Author Notes

This project is designed for developers and researchers who frequently use multiple LLM tools and need a **clear, structured, and auditable view of token consumption**.

The separation of token statistics across tools ensures:

* Better cost control
* Accurate benchmarking
* Transparent analysis

---
