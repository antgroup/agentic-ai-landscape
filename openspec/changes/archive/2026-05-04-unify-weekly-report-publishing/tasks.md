## 1. Canonical Report Artifact

- [x] 1.1 Add report path helpers for `reports/weekly_reports_by_agents/YYYY-MM-DD-weekly-agentic-ai-report.md` and ensure the archive directory is created on demand.
- [x] 1.2 Replace separate `generate_report()` and Yuque draft generation with one canonical report generation path.
- [x] 1.3 Keep `data/weekly_report.md` as a latest compatibility copy with the exact same content as the dated archived report.
- [x] 1.4 Stop writing `data/yuque_report.md` during `--check`.

## 2. Report Content

- [x] 2.1 Build structured report context from enriched candidates, recommendations, category distribution, OpenRank trends, participants, stars, descriptions, topics, and agentic match reasons.
- [x] 2.2 Generate deterministic review candidate table and candidate detail sections from structured project data.
- [x] 2.3 Compose the final report with TL;DR, deep trend insights, highlighted projects, review candidates, and candidate details.

## 3. LLM Trend Generation

- [x] 3.1 Add LLM configuration loading for `OPENAI_API_KEY` and optional `OPENAI_MODEL`.
- [x] 3.2 Implement script-native LLM call for deep trend insights using structured weekly project context.
- [x] 3.3 Add template fallback generation when LLM config is missing or the LLM call fails.
- [x] 3.4 Mark fallback-generated trend content clearly in the canonical report.

## 4. Yuque Publishing

- [x] 4.1 Publish the full canonical weekly report markdown to Yuque with title `Agentic 每周推送 YYYY-MM-DD`.
- [x] 4.2 Return and log the Yuque document URL for downstream notification.
- [x] 4.3 Handle Yuque publish failures without sending DingTalk as if publishing fully succeeded.

## 5. GitHub PR Publishing

- [x] 5.1 Update PR creation to use the canonical report content instead of a separate report view.
- [x] 5.2 Add an independent review checklist block wrapped by `agentic-review-checklist:start` and `agentic-review-checklist:end` markers.
- [x] 5.3 Append the full canonical weekly report content to the PR body after the checklist.
- [x] 5.4 Avoid relying on Yuque links for PR review content.

## 6. DingTalk Notification

- [x] 6.1 Send DingTalk only after both Yuque publishing and PR creation have completed.
- [x] 6.2 Keep DingTalk content concise and include no more than 3 highlighted projects.
- [x] 6.3 Include both Yuque URL and GitHub PR URL prominently in the DingTalk message.
- [x] 6.4 Log DingTalk failure without invalidating the already-created Yuque document or PR.

## 7. Tests and Validation

- [x] 7.1 Add unit tests for dated report path generation and latest-copy behavior.
- [x] 7.2 Add unit tests for canonical report structure and absence of `yuque_report.md` writes.
- [x] 7.3 Add unit tests for LLM fallback behavior.
- [x] 7.4 Add unit tests for PR body checklist markers and full-report inclusion.
- [x] 7.5 Add unit tests for DingTalk summary limiting highlighted projects to 3 and requiring both links.
- [x] 7.6 Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 scripts/test_weekly_update.py`.
