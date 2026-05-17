## ADDED Requirements

### Requirement: Graph assembles four agent nodes with conditional edges

The system SHALL define a LangGraph StateGraph with exactly four nodes: `clarity`, `research`, `validator`, and `synthesis`, connected by conditional edges based on state values.

#### Scenario: Graph builds successfully

- **WHEN** the graph is compiled
- **THEN** it SHALL contain nodes `clarity`, `research`, `validator`, `synthesis` and compile without errors

#### Scenario: Entry point is clarity agent

- **WHEN** a new query enters the graph
- **THEN** the first node executed SHALL be `clarity`

### Requirement: Conditional routing from clarity agent

The system SHALL route from the clarity node to either `research` (when `clarity_status == "clear"`) or trigger an interrupt (when `clarity_status == "needs_clarification"`).

#### Scenario: Clear query routes to research

- **WHEN** clarity agent sets `clarity_status` to `"clear"`
- **THEN** the graph SHALL route to the `research` node

#### Scenario: Unclear query triggers interrupt

- **WHEN** clarity agent sets `clarity_status` to `"needs_clarification"`
- **THEN** the clarity node SHALL call `interrupt(clarification_question)` to pause graph execution

### Requirement: Conditional routing from research agent

The system SHALL route from the research node to `synthesis` (when `confidence_score >= 6`) or `validator` (when `confidence_score < 6`).

#### Scenario: High confidence skips validation

- **WHEN** research agent sets `confidence_score` to 8
- **THEN** the graph SHALL route directly to `synthesis`

#### Scenario: Low confidence triggers validation

- **WHEN** research agent sets `confidence_score` to 2
- **THEN** the graph SHALL route to `validator`

### Requirement: Conditional routing from validator agent

The system SHALL route from the validator node back to `research` (when `validation_result == "insufficient"` and `validation_attempts < 3`) or to `synthesis` (when sufficient or max attempts reached).

#### Scenario: Insufficient with retries remaining loops back

- **WHEN** validator sets `validation_result` to `"insufficient"` and `validation_attempts` is 1
- **THEN** the graph SHALL route back to `research`

#### Scenario: Max attempts reached proceeds to synthesis

- **WHEN** validator sets `validation_result` to `"insufficient"` and `validation_attempts` is 3
- **THEN** the graph SHALL route to `synthesis`

#### Scenario: Sufficient validation proceeds to synthesis

- **WHEN** validator sets `validation_result` to `"sufficient"`
- **THEN** the graph SHALL route to `synthesis`

### Requirement: Interrupt resumes into clarity agent

The system SHALL resume graph execution into the clarity node after a human provides clarification via `Command(resume=...)`. In LangGraph, `interrupt(value)` pauses the graph on first call; on resume, the node re-executes from the top and `interrupt()` returns the resume payload. The clarity node SHALL detect the resume (non-None return from `interrupt()`), set it as `state.query`, and run the full LLM classification flow on the new query.

#### Scenario: User provides clarification after interrupt

- **WHEN** the graph is interrupted and user provides a clarification string via `Command(resume="Tell me about Tesla")`
- **THEN** the clarity node SHALL re-execute, receive `"Tell me about Tesla"` from `interrupt()`, set `state.query` to it, call the LLM to classify the new query, and set `clarity_status` and `company` based on the LLM response

### Requirement: State schema includes all required fields

The system SHALL use a TypedDict state schema with fields: `messages` (typed as `Annotated[list[BaseMessage], add_messages]` for automatic message accumulation), `query: str`, `company: str`, `clarity_status: str`, `clarification_question: str`, `research_findings: dict`, `confidence_score: int`, `validation_result: str`, `validation_attempts: int`, `response: str`.

#### Scenario: State schema validates

- **WHEN** the state is initialized
- **THEN** all fields SHALL be present with appropriate default values

#### Scenario: Messages accumulate across graph invocations

- **WHEN** the graph is invoked twice with the same `thread_id`
- **THEN** `messages` SHALL contain messages from both invocations due to the `add_messages` reducer
