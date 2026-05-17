from research_assistant.state import ResearchState

REQUIRED_KEYS = {"recent_news", "stock_info", "key_developments"}


def validator_node(state: ResearchState) -> dict:
    findings = state.get("research_findings", {})
    attempts = state.get("validation_attempts", 0) + 1

    present_keys = set(findings.keys()) & REQUIRED_KEYS
    if present_keys == REQUIRED_KEYS:
        validation_result = "sufficient"
    else:
        validation_result = "insufficient"

    return {
        "validation_result": validation_result,
        "validation_attempts": attempts,
    }
