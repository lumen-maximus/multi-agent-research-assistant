## ADDED Requirements

### Requirement: Validate research completeness

The validator agent SHALL check if `research_findings` contains all expected keys (`recent_news`, `stock_info`, `key_developments`) and set `validation_result` accordingly.

#### Scenario: Complete findings are sufficient

- **WHEN** `research_findings` contains all three expected keys
- **THEN** `validation_result` SHALL be `"sufficient"`

#### Scenario: Empty findings are insufficient

- **WHEN** `research_findings` is empty
- **THEN** `validation_result` SHALL be `"insufficient"`

### Requirement: Track validation attempts

The validator agent SHALL increment `validation_attempts` by 1 each time it runs.

#### Scenario: Attempt counter increments

- **WHEN** validator runs with `validation_attempts` at 1
- **THEN** `validation_attempts` SHALL be 2 after execution

### Requirement: Enforce maximum 3 retry attempts

The validator agent SHALL allow the retry loop to execute at most 3 times. After 3 attempts, the graph SHALL proceed to synthesis regardless of validation result.

#### Scenario: Third attempt forces synthesis

- **WHEN** `validation_attempts` reaches 3 and `validation_result` is `"insufficient"`
- **THEN** the graph SHALL route to `synthesis` (not back to `research`)

### Requirement: Deterministic validation logic

The validator agent SHALL use deterministic logic (key presence checks) without invoking any LLM.

#### Scenario: No LLM call during validation

- **WHEN** the validator agent processes research findings
- **THEN** it SHALL complete without making any Ollama API calls
