## ADDED Requirements

### Requirement: Classify query clarity

The clarity agent SHALL analyze the user's query and set `clarity_status` to `"clear"` when a specific company is mentioned and the query is researchable, or `"needs_clarification"` when the query is too vague.

#### Scenario: Query with explicit company name

- **WHEN** user submits "Tell me about Apple"
- **THEN** `clarity_status` SHALL be `"clear"` and `company` SHALL be `"Apple Inc."`

#### Scenario: Vague query without company

- **WHEN** user submits "Tell me about stocks"
- **THEN** `clarity_status` SHALL be `"needs_clarification"` and `clarification_question` SHALL ask which company

#### Scenario: Very short ambiguous query

- **WHEN** user submits "Tell me something"
- **THEN** `clarity_status` SHALL be `"needs_clarification"`

### Requirement: Extract company name from query

The clarity agent SHALL extract the company name from the user's query as returned by the LLM (e.g., "Apple", "Tesla", "TESLA"). The research agent is solely responsible for matching this raw name against mock data keys.

#### Scenario: Company name extraction

- **WHEN** user submits "tell me about TESLA"
- **THEN** `company` SHALL be the LLM-extracted name (e.g., `"Tesla"` or `"TESLA"`); the research agent handles matching against mock data keys

### Requirement: Resolve follow-up queries from conversation history

The clarity agent SHALL use the conversation history in `messages` to resolve ambiguous follow-up queries that reference a previously mentioned company.

#### Scenario: Follow-up references previous company

- **WHEN** conversation history contains a query about Apple and user submits "What about their competitors?"
- **THEN** `clarity_status` SHALL be `"clear"` and `company` SHALL be `"Apple Inc."`

### Requirement: Use Ollama qwen2.5:3b for classification

The clarity agent SHALL use `ChatOllama(model="qwen2.5:3b")` for query analysis and company extraction.

#### Scenario: LLM invocation

- **WHEN** the clarity agent processes a query
- **THEN** it SHALL invoke Ollama with a system prompt and return structured output

### Requirement: Structured LLM output format

The clarity agent SHALL instruct the LLM to respond in one of two text-prefix formats and parse accordingly:

- `CLEAR|<company_name>` — query is researchable, company extracted
- `NEEDS_CLARIFICATION|<question>` — query is ambiguous, clarification question provided

The agent SHALL split the LLM response on `|` to extract status and payload. If the LLM response does not match either format, the agent SHALL default to `NEEDS_CLARIFICATION` with a generic "Could you be more specific about which company you're asking about?" question.

#### Scenario: LLM returns clear format

- **WHEN** LLM responds with `CLEAR|Apple Inc.`
- **THEN** `clarity_status` SHALL be `"clear"` and `company` SHALL be `"Apple Inc."`

#### Scenario: LLM returns clarification format

- **WHEN** LLM responds with `NEEDS_CLARIFICATION|Which company are you asking about?`
- **THEN** `clarity_status` SHALL be `"needs_clarification"` and `clarification_question` SHALL be `"Which company are you asking about?"`

#### Scenario: LLM returns unparseable response

- **WHEN** LLM responds with text that doesn't contain `|` or match either prefix
- **THEN** `clarity_status` SHALL default to `"needs_clarification"` with a generic clarification question

### Requirement: Handle interrupt and resume

The clarity node SHALL call `interrupt(clarification_question)` when `clarity_status` is `"needs_clarification"`. In LangGraph, `interrupt(value)` pauses the graph on first call; on resume via `Command(resume=...)`, the node re-executes from the top and `interrupt()` returns the resume payload instead of raising. The clarity node SHALL:

1. Run LLM classification on the current query
2. If `NEEDS_CLARIFICATION`: call `resume_value = interrupt(clarification_question)`
3. After interrupt returns (resume path only): set `state.query` to `resume_value` and re-run the full LLM classification on the new query

#### Scenario: Resume value triggers re-classification

- **WHEN** the graph resumes with `Command(resume="Tell me about Tesla stock")`
- **THEN** the clarity node SHALL set `query` to `"Tell me about Tesla stock"`, call the LLM to classify the new query, and set `clarity_status` and `company` based on the LLM response
