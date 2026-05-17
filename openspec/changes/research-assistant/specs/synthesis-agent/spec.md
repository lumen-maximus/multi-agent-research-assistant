## ADDED Requirements

### Requirement: Generate natural language summary from research findings

The synthesis agent SHALL take `research_findings`, `query`, `company`, and `messages` and produce a coherent natural language summary stored in `response`.

#### Scenario: Summarize known company research

- **WHEN** `research_findings` contains Apple Inc. data and `query` is "Tell me about Apple"
- **THEN** `response` SHALL contain a readable summary mentioning Apple's stock, news, and developments

#### Scenario: Summarize with limited data

- **WHEN** `research_findings` is empty and `company` is "Microsoft"
- **THEN** `response` SHALL acknowledge that limited information was found

### Requirement: Incorporate conversation history

The synthesis agent SHALL reference conversation history from `messages` to provide contextually relevant responses to follow-up queries.

#### Scenario: Follow-up response references prior context

- **WHEN** conversation history contains a prior Apple summary and user asks "What about their competitors?"
- **THEN** `response` SHALL reference Apple as the context company

### Requirement: Use Ollama qwen2.5:3b for generation

The synthesis agent SHALL use `ChatOllama(model="qwen2.5:3b")` for response generation.

#### Scenario: LLM invocation for synthesis

- **WHEN** the synthesis agent generates a response
- **THEN** it SHALL invoke Ollama with research findings and conversation context

### Requirement: Append response to message history

The synthesis agent SHALL append an AI message with the generated response to `messages` so future turns have context.

#### Scenario: Message history grows after synthesis

- **WHEN** synthesis completes with a response
- **THEN** `messages` SHALL contain a new AI message with the response content
