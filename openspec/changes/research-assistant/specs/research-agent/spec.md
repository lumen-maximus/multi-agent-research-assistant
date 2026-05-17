## ADDED Requirements

### Requirement: Look up company in mock data

The research agent SHALL look up `state.company` in the mock data dictionary and return matching research findings.

#### Scenario: Exact match found

- **WHEN** `company` is `"Apple Inc."` and mock data contains `"Apple Inc."`
- **THEN** `research_findings` SHALL contain the Apple Inc. data and `confidence_score` SHALL be 8

#### Scenario: No match found

- **WHEN** `company` is `"Microsoft"` and mock data does not contain `"Microsoft"`
- **THEN** `research_findings` SHALL be empty and `confidence_score` SHALL be 2

### Requirement: Fuzzy company name matching

The research agent SHALL perform case-insensitive substring matching of `state.company` (the raw name extracted by the clarity agent) against mock data keys (e.g., "apple" matches "Apple Inc."). The research agent is solely responsible for name-to-key resolution; the clarity agent passes the name as-is from the LLM.

#### Scenario: Partial name matches

- **WHEN** `company` is `"Apple"` (without "Inc.")
- **THEN** `research_findings` SHALL contain the `"Apple Inc."` data and `confidence_score` SHALL be 8

### Requirement: Assign confidence score based on match quality

The research agent SHALL assign `confidence_score`: 8 when a mock data entry is found (exact key match or case-insensitive substring match), 2 when no entry matches.

#### Scenario: Confidence score for known company

- **WHEN** `company` matches a mock data entry (exact or fuzzy)
- **THEN** `confidence_score` SHALL be 8

#### Scenario: Confidence score for unknown company

- **WHEN** `company` does not match any mock data entry
- **THEN** `confidence_score` SHALL be 2

### Requirement: Include mock data for Apple Inc. and Tesla

The mock data SHALL contain entries for `"Apple Inc."` and `"Tesla"`, each with `recent_news`, `stock_info`, and `key_developments` fields.

#### Scenario: Mock data is complete

- **WHEN** mock data is loaded
- **THEN** it SHALL contain exactly the keys `"Apple Inc."` and `"Tesla"` with all three subfields populated
