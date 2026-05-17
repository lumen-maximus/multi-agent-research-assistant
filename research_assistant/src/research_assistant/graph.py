from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from research_assistant.agents.clarity import clarity_node
from research_assistant.agents.research import research_node
from research_assistant.agents.synthesis import synthesis_node
from research_assistant.agents.validator import validator_node
from research_assistant.state import ResearchState


def route_after_clarity(state: ResearchState) -> str:
    if state.get("clarity_status") == "clear":
        return "research"
    return END


def route_after_research(state: ResearchState) -> str:
    if state.get("confidence_score", 0) >= 6:
        return "synthesis"
    return "validator"


def route_after_validator(state: ResearchState) -> str:
    if state.get("validation_result") == "sufficient":
        return "synthesis"
    if state.get("validation_attempts", 0) >= 3:
        return "synthesis"
    return "research"


def build_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    graph.add_node("clarity", clarity_node)
    graph.add_node("research", research_node)
    graph.add_node("validator", validator_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("clarity")

    graph.add_conditional_edges("clarity", route_after_clarity, ["research", END])
    graph.add_conditional_edges("research", route_after_research, ["synthesis", "validator"])
    graph.add_conditional_edges("validator", route_after_validator, ["synthesis", "research"])
    graph.add_edge("synthesis", END)

    return graph


def get_compiled_graph():
    memory = MemorySaver()
    graph = build_graph()
    return graph.compile(checkpointer=memory)
