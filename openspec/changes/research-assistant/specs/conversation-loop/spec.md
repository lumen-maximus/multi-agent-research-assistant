## ADDED Requirements

### Requirement: Interactive CLI conversation loop

The system SHALL provide a `main()` function that runs a `while True` loop accepting user input, invoking the graph, and printing responses.

#### Scenario: User submits a query and gets a response

- **WHEN** user types "Tell me about Apple" at the prompt
- **THEN** the system SHALL invoke the full graph pipeline and print the synthesized response

#### Scenario: User quits the loop

- **WHEN** user types "quit" or "exit"
- **THEN** the loop SHALL terminate gracefully

### Requirement: Multi-turn state persistence via MemorySaver

The system SHALL use LangGraph's `MemorySaver` checkpointer with a consistent `thread_id` so conversation state persists across turns within a session.

#### Scenario: Follow-up query accesses prior history

- **WHEN** user asks "Tell me about Apple" then asks "What about their stock?"
- **THEN** the second invocation SHALL have access to the first query and response in `messages`

### Requirement: Handle interrupt and resume in CLI

The system SHALL detect when the graph is interrupted, print the clarification question, collect user input, and resume the graph with `Command(resume=...)`.

#### Scenario: Unclear query triggers clarification prompt

- **WHEN** the graph interrupts with a clarification question
- **THEN** the CLI SHALL print the question, collect user input, and resume the graph

### Requirement: Virtual environment and pyproject.toml setup

The project SHALL include a `pyproject.toml` with dependencies (`langgraph>=0.3,<1.0`, `langchain-core`, `langchain-ollama`) and a dev extra for `pytest`. The `pyproject.toml` SHALL configure `[tool.setuptools.packages.find] where = ["src"]` to support the `src/` layout. Setup SHALL work via `python -m venv .venv && pip install -e ".[dev]"`.

#### Scenario: Fresh setup from clean state

- **WHEN** a developer clones the repo and runs `python -m venv .venv && .venv/bin/pip install -e ".[dev]"`
- **THEN** all dependencies SHALL be installed and `python -m research_assistant.main` SHALL start the CLI

### Requirement: Demo test suite covering all routing paths

The project SHALL include `tests/test_demo.py` with tests exercising: (1) clear query full pipeline, (2) unclear query interrupt, (3) low confidence retry loop.

#### Scenario: Demo tests pass

- **WHEN** `pytest tests/test_demo.py -v` is run
- **THEN** all three tests SHALL pass and demonstrate the three routing paths
