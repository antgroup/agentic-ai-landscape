## ADDED Requirements

### Requirement: Script-native LLM trend generation
The `--check` workflow SHALL call an LLM from inside the script to generate deep trend insight content from structured weekly project context.

#### Scenario: LLM generates deep insights
- **WHEN** candidate project data has been enriched and LLM configuration is available
- **THEN** the system SHALL call the configured LLM and include generated deep trend insights in the canonical weekly report

#### Scenario: LLM input is structured project context
- **WHEN** the system calls the LLM
- **THEN** the prompt/input SHALL be based on structured project context including category distribution, highlighted projects, OpenRank growth, participants, stars, and project descriptions

### Requirement: LLM configuration
The LLM generator SHALL be configured through environment variables and SHALL support a default model when only an API key is provided.

#### Scenario: API key and model configured
- **WHEN** `OPENAI_API_KEY` and `OPENAI_MODEL` are set
- **THEN** the system SHALL use those values for LLM generation

#### Scenario: API key configured without model
- **WHEN** `OPENAI_API_KEY` is set and `OPENAI_MODEL` is unset
- **THEN** the system SHALL use the repository's default LLM model for report generation

### Requirement: LLM fallback behavior
The `--check` workflow SHALL continue when LLM generation is unavailable and SHALL clearly mark the trend content as fallback-generated.

#### Scenario: Missing LLM configuration
- **WHEN** no LLM API key is configured
- **THEN** the system SHALL generate a template-based fallback trend section and mark it as fallback-generated in the canonical report

#### Scenario: LLM call fails
- **WHEN** the configured LLM call fails
- **THEN** the system SHALL log the failure, generate a template-based fallback trend section, and continue the publishing workflow
