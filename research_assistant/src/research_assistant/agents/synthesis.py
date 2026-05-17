from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama

from research_assistant.state import ResearchState

SYSTEM_PROMPT = """You are a research synthesis agent. Given company research findings and conversation context, produce a clear, conversational summary.

Include key highlights from the research data provided. If the findings are empty or limited, acknowledge that and share what you can.

Be concise but informative. Write in a natural, helpful tone."""


def synthesis_node(state: ResearchState) -> dict:
    llm = ChatOllama(model="qwen2.5:3b")

    query = state.get("query", "")
    company = state.get("company", "")
    findings = state.get("research_findings", {})
    messages = state.get("messages", [])

    conversation_context = ""
    if messages:
        recent = messages[-6:]
        conversation_context = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in recent
        )

    findings_text = ""
    if findings:
        for section, data in findings.items():
            findings_text += f"\n{section}:\n"
            if isinstance(data, list):
                for item in data:
                    findings_text += f"  - {item}\n"
            elif isinstance(data, dict):
                for k, v in data.items():
                    findings_text += f"  {k}: {v}\n"
    else:
        findings_text = "No research data found for this company."

    user_message = (
        f"Company: {company}\n"
        f"Query: {query}\n"
        f"Research findings:\n{findings_text}\n"
        f"Conversation history:\n{conversation_context}"
    )

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])

    response_text = str(response.content).strip()

    return {
        "response": response_text,
        "messages": [AIMessage(content=response_text)],
    }
