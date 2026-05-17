# Multi-Agent Research Assistant

A **multi-agent company research assistant** built with **LangGraph**. Orchestrates four specialized agents to answer research questions about companies, supports multi-turn conversation, follow-up questions, and human-in-the-loop clarification when queries are ambiguous.

## Architecture

Four specialized agents wired through a LangGraph state machine:

| Agent | Role | Routes to |
|---|---|---|
| **Clarity Agent** | Detects vague/ambiguous queries; checks for company name | `Interrupt` (ask user) → resume → `Research Agent` |
| **Research Agent** | Gathers company info (news, financials, recent developments) via search tool (Tavily) or mock data; assigns a confidence score (0–10) | `Validator` if confidence < 6, else `Synthesis` |
| **Validator Agent** | Reviews completeness and quality of findings | Loops back to `Research` if insufficient (max 3 attempts), else `Synthesis` |
| **Synthesis Agent** | Produces a coherent, user-friendly summary using full conversation context | `END` |

### Key features

- **Multi-turn conversation** — agents share message history across turns
- **Human-in-the-loop** — LangGraph `interrupt` pauses the workflow for user clarification
- **Adaptive routing** — confidence-gated branching between research / validation / synthesis
- **Bounded retries** — validator loop has a hard ceiling to prevent runaway execution
- **Pluggable search** — Tavily MCP backend or local mock data for offline runs

## Project layout

```
research_assistant/   # graph definition, agent nodes, prompts, state
openspec/             # change-tracking specs
spec.md               # original problem statement / requirements
```

## Quick start

```bash
# Python side
cd research_assistant
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Run the graph
python -m research_assistant
```

Configure a `.env` with `TAVILY_API_KEY` (optional — falls back to mock data) and any LLM provider keys.

## Tech

- **LangGraph** — multi-agent state machine + interrupts
- **Python 3.10+**
- **Tavily** (optional) — web search MCP
- **pytest** for tests

## License

MIT
