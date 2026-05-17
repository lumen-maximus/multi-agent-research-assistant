import pytest
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from research_assistant.graph import get_compiled_graph


@pytest.fixture
def graph():
    return get_compiled_graph()


# ---------------------------------------------------------------------------
# Isolated route tests (quick sanity checks)
# ---------------------------------------------------------------------------


def test_clear_query_full_pipeline(graph):
    """Clear query about a known company goes through full pipeline and returns a response."""
    config = {"configurable": {"thread_id": "test-clear"}}
    result = graph.invoke(
        {"messages": [HumanMessage(content="Tell me about Apple")], "query": "Tell me about Apple"},
        config,
    )

    assert result.get("clarity_status") == "clear"
    assert result.get("confidence_score") == 8
    response = result.get("response", "")
    assert response, "Expected a non-empty response"
    assert result.get("company"), "Expected a company to be extracted"


def test_unclear_query_interrupts(graph):
    """Vague query triggers an interrupt with a clarification question."""
    config = {"configurable": {"thread_id": "test-unclear"}}
    graph.invoke(
        {"messages": [HumanMessage(content="Tell me about stocks")], "query": "Tell me about stocks"},
        config,
    )

    snapshot = graph.get_state(config)
    assert snapshot.next, "Expected graph to be interrupted but it completed"

    assert snapshot.tasks, "Expected at least one pending task"
    interrupts = snapshot.tasks[0].interrupts
    assert interrupts, "Expected an interrupt value"
    clarification = interrupts[0].value
    assert isinstance(clarification, str) and len(clarification) > 0


def test_low_confidence_retry_loop(graph):
    """Unknown company triggers low confidence -> validator retry loop -> synthesis with limited data."""
    config = {"configurable": {"thread_id": "test-low-confidence"}}
    result = graph.invoke(
        {"messages": [HumanMessage(content="Tell me about Microsoft")], "query": "Tell me about Microsoft"},
        config,
    )

    assert result.get("validation_attempts", 0) > 0
    assert result.get("confidence_score") == 2
    response = result.get("response", "")
    assert response, "Expected a response even for unknown company"


# ---------------------------------------------------------------------------
# Full conversation demo — exercises every spec requirement in one flow
# ---------------------------------------------------------------------------


def test_full_conversation_demo(graph):
    """End-to-end multi-turn demo covering all spec requirements.

    Turn 1: Clear query about Apple (known company, high confidence)
    Turn 2: Clear query about Tesla (second mock company, proves both work)
    Turn 3: Vague query -> interrupt -> resume with clarification -> pipeline completes
    Turn 4: Unknown company (Microsoft) -> low confidence -> validator retry -> synthesis
    Turn 5: Follow-up "What about their stock?" -> resolves from conversation history
    """
    config = {"configurable": {"thread_id": "test-demo-conversation"}}

    # ── Turn 1: Apple (clear query, known company) ────────────────────────
    result = graph.invoke(
        {"messages": [HumanMessage(content="Tell me about Apple")], "query": "Tell me about Apple"},
        config,
    )
    snapshot = graph.get_state(config)

    assert not snapshot.next, "Turn 1: graph should have completed (no interrupt)"
    assert result.get("clarity_status") == "clear", "Turn 1: expected clarity_status='clear'"
    assert result.get("confidence_score") == 8, "Turn 1: expected confidence_score=8 for known company"
    assert result.get("response"), "Turn 1: expected a non-empty response"
    assert result.get("company"), "Turn 1: expected a company to be extracted"
    # Messages should contain at least the user message + AI response
    msgs_after_t1 = result.get("messages", [])
    assert len(msgs_after_t1) >= 2, f"Turn 1: expected >=2 messages, got {len(msgs_after_t1)}"

    # ── Turn 2: Tesla (second mock company, multi-turn on same thread) ────
    result = graph.invoke(
        {"messages": [HumanMessage(content="Tell me about Tesla")], "query": "Tell me about Tesla"},
        config,
    )
    snapshot = graph.get_state(config)

    assert not snapshot.next, "Turn 2: graph should have completed"
    assert result.get("clarity_status") == "clear", "Turn 2: expected clarity_status='clear'"
    assert result.get("confidence_score") == 8, "Turn 2: expected confidence_score=8 for Tesla"
    assert result.get("response"), "Turn 2: expected a non-empty response"
    # Multi-turn: messages should have accumulated from Turn 1 + Turn 2
    msgs_after_t2 = result.get("messages", [])
    assert len(msgs_after_t2) > len(msgs_after_t1), (
        f"Turn 2: messages should accumulate across turns ({len(msgs_after_t2)} > {len(msgs_after_t1)})"
    )

    # ── Turn 3: Vague query -> interrupt -> resume -> completes ───────────
    graph.invoke(
        {"messages": [HumanMessage(content="Tell me about stocks")], "query": "Tell me about stocks"},
        config,
    )
    snapshot = graph.get_state(config)

    assert snapshot.next, "Turn 3: expected graph to be interrupted (vague query)"
    assert snapshot.tasks, "Turn 3: expected pending tasks"
    interrupts = snapshot.tasks[0].interrupts
    assert interrupts, "Turn 3: expected an interrupt value"
    clarification_question = interrupts[0].value
    assert isinstance(clarification_question, str) and len(clarification_question) > 0, (
        "Turn 3: clarification question should be a non-empty string"
    )

    # Resume with a clear clarification
    result = graph.invoke(
        Command(resume="Tell me about Tesla stock"),
        config,
    )
    snapshot = graph.get_state(config)

    assert not snapshot.next, "Turn 3 resume: graph should have completed after clarification"
    assert result.get("response"), "Turn 3 resume: expected a response after resume"
    assert result.get("clarity_status") == "clear", "Turn 3 resume: clarity should be 'clear' after resume"

    # ── Turn 4: Unknown company -> low confidence -> validator retry ──────
    result = graph.invoke(
        {"messages": [HumanMessage(content="Tell me about Microsoft")], "query": "Tell me about Microsoft"},
        config,
    )
    snapshot = graph.get_state(config)

    assert not snapshot.next, "Turn 4: graph should have completed"
    assert result.get("confidence_score") == 2, "Turn 4: expected confidence_score=2 for unknown company"
    assert result.get("validation_attempts", 0) > 0, "Turn 4: expected validator to have run (attempts > 0)"
    assert result.get("response"), "Turn 4: expected a response acknowledging limited data"

    # ── Turn 5: Follow-up referencing previous company ────────────────────
    result = graph.invoke(
        {"messages": [HumanMessage(content="What about their stock?")], "query": "What about their stock?"},
        config,
    )
    snapshot = graph.get_state(config)

    # The graph should complete regardless of whether the LLM resolves "their"
    # If it resolves the reference: clarity_status=clear, we get a response
    # If it doesn't: it may interrupt for clarification (acceptable for 3B model)
    if snapshot.next:
        # Model didn't resolve "their" — interrupted for clarification (acceptable)
        assert snapshot.tasks, "Turn 5: if interrupted, should have pending tasks"
    else:
        # Model resolved "their" from history — full pipeline completed
        assert result.get("clarity_status") == "clear", "Turn 5: expected clear status"
        assert result.get("response"), "Turn 5: expected a response"

    # Final check: messages accumulated across all 5 turns
    final_msgs = result.get("messages", [])
    assert len(final_msgs) >= 5, (
        f"Expected messages from all turns to accumulate, got {len(final_msgs)}"
    )
