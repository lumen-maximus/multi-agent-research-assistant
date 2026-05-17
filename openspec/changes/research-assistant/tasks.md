<!-- Targets: targets.json | Patch log: patches.json -->

## 1. Project Setup (sequential)

- [x] 1.1 Create `research_assistant/pyproject.toml` → target: `research_assistant/pyproject.toml` [create]
- [x] 1.2 Create `src/research_assistant/__init__.py` and `src/research_assistant/agents/__init__.py` → targets: `research_assistant/src/research_assistant/__init__.py`, `research_assistant/src/research_assistant/agents/__init__.py` [create]
- [x] 1.3 Create `research_assistant/Makefile` with `setup`, `run`, `test`, `demo` targets → target: `research_assistant/Makefile` [create]
- [x] 1.4 Verify virtual environment setup: `python -m venv .venv && .venv/bin/pip install -e ".[dev]"` completes without errors [verify]

## 2. State & Mock Data (parallel — no dependencies between 2.1 and 2.2)

- [x] 2.1 Create `src/research_assistant/state.py` with `ResearchState` TypedDict — `messages: Annotated[list[BaseMessage], add_messages]` for auto-accumulation; all other fields: `query: str`, `company: str`, `clarity_status: str`, `clarification_question: str`, `research_findings: dict`, `confidence_score: int`, `validation_result: str`, `validation_attempts: int`, `response: str` → target: `research_assistant/src/research_assistant/state.py` [create]
- [x] 2.2 Create `src/research_assistant/mock_data.py` with mock research dict for Apple Inc. and Tesla (recent_news, stock_info, key_developments) → target: `research_assistant/src/research_assistant/mock_data.py` [create]

## 3. Agent Nodes (parallel — 3.1, 3.2, 3.3, 3.4 are independent; each imports only state.py and/or mock_data.py)

- [x] 3.1 Create `src/research_assistant/agents/clarity.py` — LLM agent using `ChatOllama(model="qwen2.5:3b")` with system prompt for query classification and company extraction; parses LLM output as `CLEAR|<company>` or `NEEDS_CLARIFICATION|<question>` (defaults to needs_clarification on unparseable output); reads `messages` for follow-up resolution; calls `interrupt(clarification_question)` when needs_clarification, and on resume reads the return value as new query and re-runs LLM classification → target: `research_assistant/src/research_assistant/agents/clarity.py` [create]
- [x] 3.2 Create `src/research_assistant/agents/research.py` — deterministic mock data lookup with case-insensitive substring matching; assigns confidence_score (8=match found, 2=no match) → target: `research_assistant/src/research_assistant/agents/research.py` [create]
- [x] 3.3 Create `src/research_assistant/agents/validator.py` — deterministic key-presence check on research_findings; increments validation_attempts; sets validation_result → target: `research_assistant/src/research_assistant/agents/validator.py` [create]
- [x] 3.4 Create `src/research_assistant/agents/synthesis.py` — LLM agent using `ChatOllama(model="qwen2.5:3b")` with system prompt to summarize findings; appends AI message to messages → target: `research_assistant/src/research_assistant/agents/synthesis.py` [create]

## 4. Graph Assembly (sequential — single file, tasks depend on each other)

- [x] 4.1 Create `src/research_assistant/graph.py` — build StateGraph with 4 nodes, conditional edges (clarity→research/interrupt, research→validator/synthesis, validator→research/synthesis), and MemorySaver checkpointer → target: `research_assistant/src/research_assistant/graph.py` [create]
- [x] 4.2 Implement routing functions: `route_after_clarity`, `route_after_research`, `route_after_validator` → target: `research_assistant/src/research_assistant/graph.py` [modify]

## 5. CLI & Tests (parallel — 5.1 and 5.2 are independent; both import graph.py, not each other)

- [x] 5.1 Create `src/research_assistant/main.py` with `main()` function: while-loop, graph invocation, interrupt detection, `Command(resume=...)` handling, quit command → target: `research_assistant/src/research_assistant/main.py` [create]
- [x] 5.2 Create `tests/test_demo.py` with three test functions: `test_clear_query_full_pipeline` (invoke with "Tell me about Apple", assert response contains Apple data), `test_unclear_query_interrupts` (invoke with "Tell me about stocks", assert graph interrupts with clarification question), `test_low_confidence_retry_loop` (invoke with "Tell me about Microsoft", assert validation_attempts > 0 and response acknowledges limited data) → target: `research_assistant/tests/test_demo.py` [create]

## 6. Verification (sequential)

- [x] 6.1 Run `pytest tests/test_demo.py -v` and verify all 3 tests pass [verify]
- [x] 6.2 Verify interactive conversation works: clear query, follow-up query, unclear query with clarification [verify]
