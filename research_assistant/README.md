# Research Assistant — Project Report

## Overview
Multi-agent research assistant built with LangGraph, running locally via Ollama (`qwen2.5:3b`). Four specialized agents collaborate through a StateGraph with conditional routing, human-in-the-loop interrupts, and multi-turn conversation memory.

## Architecture

```
User Query
    │
    ▼
┌──────────┐   clear    ┌──────────┐  confidence≥6  ┌───────────┐
│ Clarity  │ ──────────▶│ Research │ ──────────────▶│ Synthesis │──▶ END
│ (LLM)   │            │ (determ) │                │  (LLM)    │
└──────────┘            └──────────┘                └───────────┘
    │                       ▲  │                        ▲
    │ needs_clarification   │  │ confidence<6            │
    ▼                       │  ▼                        │
 interrupt()             ┌──────────┐  sufficient OR    │
 ◄─ resume ─┘            │Validator │  max retries ─────┘
                         │ (determ) │
                         └──────────┘
                          insufficient
                          & attempts<3 ──▶ loop back to Research
```

## Agent Summary

| Agent | Type | Role |
|-------|------|------|
| Clarity | LLM (`qwen2.5:3b`) | Classifies query, extracts company, triggers interrupt if vague |
| Research | Deterministic | Mock data lookup with fuzzy matching, confidence scoring (8/2) |
| Validator | Deterministic | Key-presence validation, retry loop (max 3 attempts) |
| Synthesis | LLM (`qwen2.5:3b`) | Summarizes findings using conversation context |

## Key Features Implemented
- **Conditional routing**: 3 distinct paths (clear→synthesis, low confidence→validator loop, vague→interrupt)
- **Human-in-the-loop**: `interrupt()` pauses graph; `Command(resume=...)` re-enters clarity with clarification
- **Multi-turn memory**: `MemorySaver` checkpointer with `thread_id` preserves state across turns
- **Message accumulation**: `Annotated[list[BaseMessage], add_messages]` auto-appends across invocations

## File Structure
```
research_assistant/
├── pyproject.toml              # Dependencies: langgraph>=0.3,<1.0, langchain-core, langchain-ollama
├── Makefile                    # setup, run, test, demo targets
├── src/research_assistant/
│   ├── state.py                # ResearchState TypedDict (10 fields)
│   ├── mock_data.py            # Apple Inc. + Tesla mock data
│   ├── graph.py                # StateGraph assembly, routing functions, MemorySaver
│   ├── main.py                 # CLI conversation loop with interrupt handling
│   └── agents/
│       ├── clarity.py          # LLM query classification + interrupt
│       ├── research.py         # Mock data lookup, confidence scoring
│       ├── validator.py        # Key-presence check, attempt tracking
│       └── synthesis.py        # LLM summarization, AIMessage append
└── tests/
    └── test_demo.py            # 4 tests (3 isolated + 1 full conversation demo)
```

## Test Results
```
tests/test_demo.py::test_clear_query_full_pipeline      PASSED
tests/test_demo.py::test_unclear_query_interrupts        PASSED
tests/test_demo.py::test_low_confidence_retry_loop       PASSED
tests/test_demo.py::test_full_conversation_demo          PASSED

4 passed in 43.16s
```

## Spec Coverage

| Requirement | Covered By |
|-------------|-----------|
| 4 specialized agents | clarity.py, research.py, validator.py, synthesis.py |
| Conditional routing (all 3 paths) | graph.py + test_clear, test_low_confidence, test_unclear |
| Human-in-the-loop interrupt + resume | clarity.py `interrupt()` + test_full_conversation Turn 3 |
| Multi-turn conversation with history | MemorySaver + test_full_conversation Turns 1-5 |
| Follow-up question resolution | test_full_conversation Turn 5 (soft assert) |
| Mock data (Apple Inc. + Tesla) | mock_data.py + test_full_conversation Turns 1-2 |
| State management (TypedDict) | state.py ResearchState |

## Setup & Run
```bash
cd research_assistant
make setup    # creates venv, installs deps
make test     # runs pytest
make run      # interactive CLI
```
Requires: Python ≥3.11, Ollama running with `qwen2.5:3b` pulled.
