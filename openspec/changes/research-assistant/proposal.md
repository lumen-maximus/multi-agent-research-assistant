## Why

We need a multi-agent research assistant that demonstrates LangGraph's core capabilities: conditional routing, human-in-the-loop interrupts, and multi-turn conversation. The system helps users gather company information through four specialized agents working together, using local LLM inference via Ollama (`qwen2.5:3b`) with no external API dependencies.

## What Changes

- Add a Python package `research_assistant` with 4 LangGraph agent nodes: Clarity, Research, Validator, Synthesis
- Clarity and Synthesis agents use Ollama (`qwen2.5:3b`) for natural language understanding and generation
- Research and Validator agents are deterministic (mock data lookup + threshold logic)
- CLI conversation loop with multi-turn history via LangGraph's MemorySaver checkpointer
- Human-in-the-loop via LangGraph `interrupt()` when queries are ambiguous
- Conditional routing: Clarity→Research/Interrupt, Research→Validator/Synthesis (confidence threshold), Validator→Research (retry loop, max 3)/Synthesis
- Mock company data for Apple Inc. and Tesla (no external APIs)
- Virtual environment setup via `python -m venv` with `pyproject.toml`
- Demo test suite (`test_demo.py`) exercising all three routing paths

## Capabilities

### New Capabilities

- `agent-graph`: LangGraph StateGraph wiring 4 agents with conditional edges and interrupt support
- `clarity-agent`: LLM-powered query classification (clear vs needs_clarification) with company extraction
- `research-agent`: Deterministic mock data lookup with confidence scoring
- `validator-agent`: Research quality validation with retry loop (max 3 attempts)
- `synthesis-agent`: LLM-powered conversational summary generation from research findings
- `conversation-loop`: CLI multi-turn conversation with MemorySaver state persistence

### Modified Capabilities

## Impact

- **New files**: ~8 source files + 1 test file under `research_assistant/`
- **Dependencies**: `langgraph>=0.3,<1.0`, `langchain-core`, `langchain-ollama`, `pytest`
- **Runtime requirement**: Ollama running locally with `qwen2.5:3b` model pulled
- **No external APIs**: Fully local execution, no API keys needed
