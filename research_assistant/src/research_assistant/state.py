from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    company: str
    clarity_status: str
    clarification_question: str
    research_findings: dict
    confidence_score: int
    validation_result: str
    validation_attempts: int
    response: str
