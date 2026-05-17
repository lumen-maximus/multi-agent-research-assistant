## Context

This is a greenfield Python project. No existing codebase. The system is a multi-agent research assistant built on LangGraph that runs entirely locally using Ollama for LLM inference. Target environment is WSL2 with a GTX 1070 GPU and `qwen2.5:3b` (1.9GB) already pulled.

## Goals / Non-Goals

**Goals:**

- Demonstrate LangGraph's StateGraph with 4 agent nodes and conditional routing
- Implement human-in-the-loop via LangGraph `interrupt()` / `Command(resume=...)`
- Support multi-turn conversation with history preservation via MemorySaver checkpointer
- Run fully locally with Ollama — no API keys, no cloud dependency
- Provide a demo test suite that exercises all routing paths without user interaction
- One-command setup via virtual environment + `pyproject.toml`

**Non-Goals:**

- Real API integrations (Tavily, financial APIs) — mock data only
- Web UI or REST API — CLI only
- Production error handling, logging, or observability
- Token windowing or RAG for conversation history
- Streaming responses
- Multiple LLM model support (single model: `qwen2.5:3b`)

## Decisions

### 1. Hybrid LLM + Deterministic agents

**Decision**: Clarity and Synthesis agents use Ollama LLM; Research and Validator are deterministic.
**Alternatives considered**:

- All 4 agents use LLM → wastes tokens on dict lookups and threshold checks, slower
- All deterministic → doesn't demonstrate real agent behavior, reduces spec value
  **Rationale**: LLM where language understanding matters (classification, summarization), deterministic where logic is sufficient (data lookup, threshold check). Minimizes latency and keeps single model in VRAM.

### 2. `qwen2.5:3b` as the sole LLM

**Decision**: Use `qwen2.5:3b` (general-purpose) for both LLM agents.
**Alternatives considered**:

- `qwen2.5-coder:3b` → code-tuned, worse at natural language classification and summarization
- `llama3.2` (2.0GB) → slightly larger, would work but `qwen2.5:3b` is already loaded and proven
- `qwen2.5:7b` (4.7GB) → higher quality but 2.5x memory, slower on GTX 1070
  **Rationale**: Same size as coder variant, better at natural language tasks. Single model avoids VRAM swapping.

### 3. LangGraph `interrupt()` for human-in-the-loop

**Decision**: Use LangGraph's built-in `interrupt()` function (v0.3+) instead of custom pause logic.
**Alternatives considered**:

- Custom node that reads stdin → breaks graph execution model, can't resume cleanly
- Callback-based interrupts → more complex, non-standard
  **Rationale**: Idiomatic LangGraph pattern. Graph pauses, CLI collects input, resumes with `Command(resume=...)`. Clean separation between graph logic and I/O.

### 4. MemorySaver for conversation persistence

**Decision**: Use LangGraph's `MemorySaver` (in-memory checkpointer) with `thread_id` for multi-turn state.
**Alternatives considered**:

- Manual message list management → error-prone, doesn't integrate with graph state
- SQLite checkpointer → overkill for CLI MVP
  **Rationale**: Zero-config, built into LangGraph. Messages accumulate automatically across invocations with same `thread_id`.

### 5. Flat package layout with agents/ subpackage

**Decision**: `src/research_assistant/` with `agents/` subpackage containing one module per agent.
**Rationale**: Each agent is independently testable. Clear mapping from spec concepts to code. Easy to swap mock→real research later by replacing one file.

### 6. Confidence score as match-quality metric

**Decision**: Research agent assigns confidence as a binary: 8 (match found via exact key or case-insensitive substring) or 2 (no match). No intermediate scores.
**Alternatives considered**:

- Three-tier scoring (8/5/2 with "partial match") → ambiguous definition of partial vs fuzzy, complicates logic for no demonstrable benefit with only 2 mock entries
  **Rationale**: Binary scoring is unambiguous. Known companies go straight to synthesis (8 >= 6), unknown ones trigger the validator retry loop (2 < 6). Demonstrates all three routing paths with simple test inputs.

## Risks / Trade-offs

- **[3b model quality]** `qwen2.5:3b` may misclassify edge-case queries in Clarity Agent → Mitigation: tight system prompt with few-shot examples; fallback to asking for clarification (safe default)
- **[Cold start latency]** First Ollama call takes ~5s to load model → Mitigation: acceptable for CLI MVP; could pre-warm at startup
- **[Follow-up resolution]** "What about their competitors?" requires context from history → Mitigation: Clarity Agent receives full message history; worst case it asks for clarification
- **[LangGraph API stability]** API has evolved rapidly → Mitigation: pin `langgraph>=0.3,<1.0`; use only documented patterns (interrupt, Command, MemorySaver)
- **[Mock data limitations]** Only 2 companies in mock data → Mitigation: validator retry loop handles unknown companies gracefully; synthesis acknowledges limited data
