## ADDED Requirements

### Requirement: Publish full report to Yuque
After generating the canonical weekly report, the system SHALL publish the full report content to Yuque and capture the resulting document URL.

#### Scenario: Yuque receives full report
- **WHEN** a canonical weekly report has been generated
- **THEN** the system SHALL publish the full markdown report content to Yuque with title `Agentic 每周推送 YYYY-MM-DD`

#### Scenario: Yuque publish fails
- **WHEN** Yuque publishing fails
- **THEN** the system SHALL log the failure and SHALL NOT send DingTalk as if both publishing links are available

### Requirement: Create PR with independent checklist and full report
After Yuque publishing, the system SHALL create a GitHub PR whose body contains an independent review checklist and the full canonical weekly report content.

#### Scenario: PR body contains checklist block
- **WHEN** a PR is created for candidate project review
- **THEN** the PR body SHALL contain a checklist wrapped in `<!-- agentic-review-checklist:start -->` and `<!-- agentic-review-checklist:end -->`

#### Scenario: PR body contains full report
- **WHEN** a PR is created for candidate project review
- **THEN** the PR body SHALL include the full canonical weekly report content after the checklist section

#### Scenario: PR does not depend on Yuque visibility
- **WHEN** a PR is created
- **THEN** the PR body SHALL NOT require reviewers to open Yuque to read the report because Yuque may not be accessible externally

### Requirement: Send concise DingTalk notification last
The system SHALL send DingTalk only after Yuque publishing and PR creation have both completed, and the message SHALL stay concise.

#### Scenario: DingTalk includes both links
- **WHEN** Yuque publishing and PR creation both succeed
- **THEN** the DingTalk message SHALL include the Yuque URL and GitHub PR URL

#### Scenario: DingTalk highlights at most three projects
- **WHEN** DingTalk content is generated from highlighted projects
- **THEN** the message SHALL include no more than three highlighted projects

#### Scenario: DingTalk is sent last
- **WHEN** the `--check` workflow publishes weekly results
- **THEN** DingTalk SHALL be sent after both the Yuque URL and GitHub PR URL are known
