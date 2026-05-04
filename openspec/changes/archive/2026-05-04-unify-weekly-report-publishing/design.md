## Context

`scripts/weekly_update.py --check` currently discovers candidate projects, generates `data/weekly_report.md`, saves a separate `data/yuque_report.md`, prints manual instructions for trend analysis/Yuque/DingTalk, and creates a PR checklist. This splits one weekly narrative across multiple files and manual steps. The desired flow is that one complete weekly report is generated first, then each publishing channel derives from that same content.

The pipeline depends on ClickHouse for star growth, OpenRank, and participant data; GitHub API for repository metadata and README content; Yuque/DWS tooling for internal document publishing; DingTalk webhook for notification; and `gh` CLI for PR creation.

## Goals / Non-Goals

**Goals:**

- Make `weekly_report.md` the single source of truth for weekly content.
- Archive dated reports under `reports/weekly_reports_by_agents/` so historical reports are not overwritten.
- Generate deep trend insights automatically inside the script using an LLM.
- Publish full report content to Yuque.
- Create a PR whose body contains an independent review checklist and the full weekly report.
- Send DingTalk last, with concise content and both Yuque and PR URLs.
- Keep the checklist structurally stable for later `--post-merge` work.

**Non-Goals:**

- Redesign `--post-merge` selection ingestion or CSV update semantics.
- Build a web UI or scheduler.
- Replace ClickHouse/GitHub data collection.
- Require Yuque content to be publicly accessible.

## Decisions

### One Canonical Report

Generate one complete markdown report and save it to:

```text
reports/weekly_reports_by_agents/YYYY-MM-DD-weekly-agentic-ai-report.md
```

Also update `data/weekly_report.md` as a latest compatibility copy. Stop generating `data/yuque_report.md`.

Rationale: a dated archive prevents losing history, while the latest copy avoids breaking scripts or habits that still inspect `data/weekly_report.md`.

### Report Composition

The canonical report should include:

- TL;DR
- Deep trend insights
- Highlighted projects
- Review candidates table
- Candidate details with evidence

The report generator should construct structured context from the enriched project data first, then ask the LLM to produce the narrative sections. Deterministic table/detail sections can still be assembled by code to keep review data complete and parseable.

### Script-Native LLM Generation

Add an LLM client layer controlled by environment variables:

```text
OPENAI_API_KEY
OPENAI_MODEL
```

If LLM configuration is missing or the call fails, `--check` should continue with a template fallback report and clearly mark the trend section as fallback-generated.

Rationale: scheduled and repeatable reporting requires the script to generate trend insights without relying on Codex/Claude manual intervention.

### Publishing Order

Use a strict order:

```text
generate canonical report
publish Yuque full report
create GitHub PR
send DingTalk concise message
```

DingTalk sends last because it should include both the Yuque URL and PR URL.

### Channel Views

Yuque receives full report markdown.

GitHub PR body receives:

```markdown
## Review Checklist

<!-- agentic-review-checklist:start -->
- [ ] owner/repo-a
- [ ] owner/repo-b
<!-- agentic-review-checklist:end -->

---

## Full Weekly Report

<canonical weekly report>
```

The PR body must not depend on a Yuque link because Yuque may not be visible to external reviewers.

DingTalk receives a concise message containing:

- report date and candidate count
- at most 3 highlighted projects
- Yuque URL
- PR URL

## Risks / Trade-offs

- **[LLM hallucination or unsupported claims]** -> Build the prompt from structured project data only, require project/data citations in every insight, and keep deterministic candidate tables in code.
- **[LLM unavailable]** -> Continue with fallback report and make the fallback explicit.
- **[Report too long for PR body]** -> Prefer full PR body as required; if GitHub body limits are hit, fail with a clear error and keep the archived report available for retry.
- **[Yuque publish succeeds but PR creation fails]** -> Do not send DingTalk without both links; print the Yuque URL and failure reason so the user can retry PR creation.
- **[PR succeeds but DingTalk fails]** -> Keep Yuque/PR outputs and log DingTalk failure; rerun notification manually if needed.
- **[Duplicated latest/archive report paths]** -> Treat `reports/weekly_reports_by_agents/...` as canonical and `data/weekly_report.md` as a compatibility copy only.

## Migration Plan

1. Add canonical report path helpers and create `reports/weekly_reports_by_agents/` on demand.
2. Replace separate internal/Yuque report generation with one canonical report generator.
3. Add LLM generation with fallback.
4. Publish canonical report to Yuque.
5. Update PR body generation to include independent checklist plus full canonical report.
6. Update DingTalk to send last with Yuque and PR URLs.
7. Remove `yuque_report.md` writes from `--check`.

## Open Questions

- Which exact LLM model should be the default when `OPENAI_MODEL` is unset?
- Should DingTalk include a short trend summary from TL;DR, or only top projects and links?
- Should `data/weekly_report.md` remain long-term or be removed after downstream callers migrate to the dated archive?
