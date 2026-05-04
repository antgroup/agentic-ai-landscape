## ADDED Requirements

### Requirement: Canonical weekly report generation
The `--check` workflow SHALL generate one canonical weekly report that combines deep trend insights, highlighted projects, review candidates, and candidate details.

#### Scenario: Check creates one complete report
- **WHEN** `python scripts/weekly_update.py --check` finds candidate projects
- **THEN** the system SHALL generate a markdown report containing TL;DR, deep trend insights, highlighted projects, a review candidates table, and candidate detail sections

#### Scenario: Report includes review evidence
- **WHEN** a candidate project is included in the weekly report
- **THEN** the report SHALL include enough review evidence for that project, including repo URL, description, topics when available, stars, OpenRank latest/trend, participants, language, created date, and agentic match reason

### Requirement: Dated report archive
The system SHALL save each canonical weekly report under `reports/weekly_reports_by_agents/` using a date-based filename and SHALL NOT rely only on overwriting `data/weekly_report.md`.

#### Scenario: Report is archived by date
- **WHEN** a canonical report is generated for `2026-05-04`
- **THEN** the system SHALL write `reports/weekly_reports_by_agents/2026-05-04-weekly-agentic-ai-report.md`

#### Scenario: Latest compatibility copy is updated
- **WHEN** a canonical report is archived successfully
- **THEN** the system SHALL also update `data/weekly_report.md` with the same content as the latest compatibility copy

### Requirement: Remove duplicate Yuque report artifact
The `--check` workflow SHALL stop generating `data/yuque_report.md`; Yuque publishing SHALL use the canonical weekly report content directly.

#### Scenario: Check does not write Yuque duplicate
- **WHEN** `python scripts/weekly_update.py --check` completes report generation
- **THEN** the system SHALL NOT write a new `data/yuque_report.md` file as a separate report artifact
