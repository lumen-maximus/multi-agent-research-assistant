from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.types import interrupt

from research_assistant.state import ResearchState

SYSTEM_PROMPT = """You are a query classification agent. Analyze the user's query and conversation history.

Your job:
1. Determine if the query clearly asks about a specific company
2. Extract the company name if present

Respond in EXACTLY one of these two formats (no extra text):
CLEAR|<company_name>
NEEDS_CLARIFICATION|<question to ask the user>

Examples:
- "Tell me about Apple" → CLEAR|Apple
- "What's Tesla's stock price?" → CLEAR|Tesla
- "Tell me about stocks" → NEEDS_CLARIFICATION|Which company are you asking about?
- "What about their competitors?" (after discussing Apple) → CLEAR|Apple

If the user references a previously discussed company (e.g., "their", "that company"), use conversation history to resolve it."""


def clarity_node(state: ResearchState) -> dict:
    llm = ChatOllama(model="qwen2.5:3b")

    query = state.get("query", "")
    messages = state.get("messages", [])

    conversation_context = ""
    if messages:
        recent = messages[-6:]
        conversation_context = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        )

    user_message = f"Conversation history:\n{conversation_context}\n\nCurrent query: {query}"

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    raw = str(response.content).strip()

    if "|" in raw:
        parts = raw.split("|", 1)
        prefix = parts[0].strip().upper()
        payload = parts[1].strip()

        if prefix == "CLEAR" and payload:
            return {
                "clarity_status": "clear",
                "company": payload,
            }
        elif prefix == "NEEDS_CLARIFICATION" and payload:
            clarification_question = payload
            resume_value = interrupt(clarification_question)
            return {
                "query": resume_value,
                **clarity_node({**state, "query": resume_value}),
            }

    # Unparseable — default to needs_clarification
    clarification_question = "Could you be more specific about which company you're asking about?"
    resume_value = interrupt(clarification_question)
    return {
        "query": resume_value,
        **clarity_node({**state, "query": resume_value}),
    }
