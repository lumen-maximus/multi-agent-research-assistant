# Multi-Agent Research Assistant

A **multi-agent company research assistant** built with **LangGraph**. Four specialized agents collaborate through a `StateGraph` with conditional routing, **human-in-the-loop interrupts**, and multi-turn conversation memory.

Runs **locally** via Ollama (`qwen2.5:3b`) — no cloud LLM keys required.

---

## Architecture

```
User Query
    │
    ▼
┌──────────┐   clear    ┌──────────┐  confidence≥6  ┌───────────┐
│ Clarity  │ ──────────▶│ Research │ ──────────────▶│ Synthesis │──▶ END
│ (LLM)    │            │ (determ) │                │  (LLM)    │
└──────────┘            └──────────┘                └───────────┘
    │                       ▲  │                        ▲
    │ needs_clarification   │  │ confidence<6           │
    ▼                       │  ▼                        │
 interrupt()             ┌──────────┐  sufficient OR    │
 ◄─ resume ──┘           │Validator │  max retries ─────┘
                         │ (determ) │
                         └──────────┘
                          insufficient
                          & attempts<3 ──▶ loop back to Research
```

### Agents

| Agent | Type | Role |
|---|---|---|
| **Clarity** | LLM | Classifies query, extracts company name, triggers `interrupt()` if vague |
| **Research** | Deterministic | Mock-data lookup with fuzzy matching, confidence scoring (0–10) |
| **Validator** | Deterministic | Key-presence validation with bounded retry loop (max 3 attempts) |
| **Synthesis** | LLM | Summarizes findings using full conversation context |

### Key features

- **Conditional routing** — 3 distinct paths (clear → synthesis, low-confidence → validator loop, vague → interrupt)
- **Human-in-the-loop** — `interrupt()` pauses the graph; `Command(resume=...)` re-enters the clarity node with the user's clarification
- **Multi-turn memory** — `MemorySaver` checkpointer keyed by `thread_id` preserves state across turns
- **Message accumulation** — `Annotated[list[BaseMessage], add_messages]` auto-appends across invocations
- **Bounded retries** — hard ceiling on the validator loop prevents runaway execution
- **Pluggable search** — Tavily MCP backend or local mock data for offline runs

## Project layout

```
research_assistant/
├── pyproject.toml              # deps: langgraph>=0.3,<1.0, langchain-core, langchain-ollama
├── Makefile                    # setup, run, test, demo targets
├── src/research_assistant/
│   ├── state.py                # ResearchState TypedDict
│   ├── mock_data.py            # Apple Inc. + Tesla mock data
│   ├── graph.py                # StateGraph assembly, routing, MemorySaver
│   ├── main.py                 # CLI conversation loop with interrupt handling
│   └── agents/
│       ├── clarity.py          # LLM query classification + interrupt
│       ├── research.py         # Mock lookup + confidence scoring
│       ├── validator.py        # Key-presence check + attempt tracking
│       └── synthesis.py        # LLM summarization
└── tests/
    └── test_demo.py            # 4 tests (3 isolated + 1 full conversation)
openspec/                       # change-tracking specs
spec.md                         # original problem statement
```

## Test results

```
tests/test_demo.py::test_clear_query_full_pipeline      PASSED
tests/test_demo.py::test_unclear_query_interrupts       PASSED
tests/test_demo.py::test_low_confidence_retry_loop      PASSED
tests/test_demo.py::test_full_conversation_demo         PASSED

4 passed in 43.16s
```

## Spec coverage

| Requirement | Covered by |
|---|---|
| 4 specialized agents | `clarity.py`, `research.py`, `validator.py`, `synthesis.py` |
| Conditional routing (all 3 paths) | `graph.py` + `test_clear`, `test_low_confidence`, `test_unclear` |
| Human-in-the-loop interrupt + resume | `clarity.py` `interrupt()` + `test_full_conversation` Turn 3 |
| Multi-turn conversation with history | `MemorySaver` + `test_full_conversation` Turns 1–5 |
| Follow-up question resolution | `test_full_conversation` Turn 5 |
| Mock data (Apple Inc. + Tesla) | `mock_data.py` + `test_full_conversation` Turns 1–2 |
| State management (TypedDict) | `state.py` `ResearchState` |

## Quick start

```bash
cd research_assistant
make setup    # creates venv, installs deps
make test     # runs pytest
make run      # interactive CLI
```

Requires: **Python ≥ 3.11**, **Ollama** running with `qwen2.5:3b` pulled.

## Tech

- **LangGraph** — multi-agent state machine + interrupts + checkpointing
- **LangChain Core** — message types and tool abstractions
- **Ollama** (`qwen2.5:3b`) — local LLM inference
- **pytest** — full graph + per-agent tests
- **Tavily** (optional) — web search MCP

## License

MIT — see [LICENSE](LICENSE).
