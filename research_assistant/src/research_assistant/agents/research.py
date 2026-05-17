from research_assistant.mock_data import MOCK_DATA
from research_assistant.state import ResearchState


def research_node(state: ResearchState) -> dict:
    company = state.get("company", "")
    company_lower = company.lower()

    # Try exact key match first, then case-insensitive substring
    for key, data in MOCK_DATA.items():
        if company_lower == key.lower() or company_lower in key.lower():
            return {
                "research_findings": data,
                "confidence_score": 8,
            }

    return {
        "research_findings": {},
        "confidence_score": 2,
    }
