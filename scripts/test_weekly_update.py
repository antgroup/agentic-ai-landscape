#!/usr/bin/env python3
"""Unit tests for weekly_update.py — run with: .venv/bin/python3 scripts/test_weekly_update.py"""

import sys
import os

# Ensure we can import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Stub heavy imports before importing weekly_update
import types
from unittest.mock import MagicMock, patch

# Mock clickhouse_connect before import
mock_cc = MagicMock()
sys.modules["clickhouse_connect"] = mock_cc

# Set env vars so load_dotenv doesn't fail
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_USER", "test")
os.environ.setdefault("CLICKHOUSE_PASSWORD", "test")
os.environ["OPENAI_API_KEY"] = ""
os.environ["ALLOW_LLM_FALLBACK"] = "1"

import weekly_update as wu

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✓ {name}")
        passed += 1
    else:
        print(f"  ✗ {name} — {detail}")
        failed += 1

# ── 1. Path resolution ────────────────────────────────────────────────
print("\n1. Path resolution")
test("BASE ends with llm-oss-landscape", wu.BASE.endswith("llm-oss-landscape"), wu.BASE)
test("SCRIPT_DIR ends with scripts", wu.SCRIPT_DIR.endswith("scripts"), wu.SCRIPT_DIR)
test("ENV_PATH points to scripts/.env", wu.ENV_PATH.endswith("scripts/.env"), wu.ENV_PATH)
test("PR_TARGET_REPO is antgroup", wu.PR_TARGET_REPO == "antgroup/llm-oss-landscape", wu.PR_TARGET_REPO)
test("OPENAI_BASE_URL has v1 endpoint", wu.OPENAI_BASE_URL.endswith("/v1"), wu.OPENAI_BASE_URL)
test("ClickHouse client is lazy", wu._ch_client is None, "client should not initialize at import")
test("trend ends at latest OpenRank month", wu.trend_months[-1] == wu.openrank_latest_month, str(wu.trend_months))
# Check source code doesn't contain hardcoded path
with open(os.path.join(wu.SCRIPT_DIR, "weekly_update.py"), "r") as f:
    src = f.read()
test("no hardcoded paths", "xiaoyawork" not in src and "/Users/" not in src.split("SCRIPT_DIR")[0], "check source")

# ── 2. md_cell pipe escaping ──────────────────────────────────────────
print("\n2. md_cell pipe escaping")
test("escapes pipe", wu.md_cell("Browser Harness | Self-healing") == "Browser Harness │ Self-healing")
test("truncates long text", wu.md_cell("x" * 100, 50) == "x" * 50 + "...")
test("handles None", wu.md_cell(None) == "")
test("handles empty", wu.md_cell("") == "")
test("short text unchanged", wu.md_cell("hello", 50) == "hello")

# ── 3. canonical weekly report ────────────────────────────────────────
print("\n3. canonical weekly report")
fake_projects = [
    {
        "repo_name": "test/repo",
        "description": "A test | project with pipe",
        "stars": 1500,
        "language": "Python",
        "created_at": "2026-01-01",
        "topics": "agent,tool-calling",
        "openrank_latest": 12.5,
        "openrank_month": "2026-01",
        "openrank_trend": {"2025-11": 2.0, "2025-12": 4.0, "2026-01": 12.5},
        "participants": 42,
        "reason": "agent, tool calling",
        "categories": ["Coding Agent", "Browser Agent"],
    },
    {
        "repo_name": "foo/bar",
        "description": "Another project",
        "stars": 500,
        "language": "Rust",
        "created_at": "2026-02-01",
        "topics": "mcp",
        "openrank_latest": 3.0,
        "openrank_month": "",
        "openrank_trend": {},
        "participants": 7,
        "reason": "mcp",
        "categories": ["Agent Framework"],
    },
]
fake_recs = [
    (fake_projects[0], 0.9, "OpenRank 增长 200%"),
]
existing_latest_report = None
if os.path.exists(wu.REPORT_FILE):
    with open(wu.REPORT_FILE, "r", encoding="utf-8") as f:
        existing_latest_report = f.read()
yuque_before = None
yuque_path = os.path.join(wu.BASE, "data", "yuque_report.md")
if os.path.exists(yuque_path):
    with open(yuque_path, "r", encoding="utf-8") as f:
        yuque_before = f.read()
archive_path = wu.get_report_archive_path("2099-01-02")
if os.path.exists(archive_path):
    os.remove(archive_path)
report, written_path, report_context = wu.generate_canonical_report(
    fake_projects,
    ["2025-11", "2025-12", "2026-01"],
    fake_recs,
    date_str="2099-01-02",
)
test("archive path uses date", written_path.endswith("reports/weekly_reports_by_agents/2099-01-02-weekly-agentic-ai-report.md"), written_path)
test("archive report exists", os.path.exists(written_path), written_path)
with open(wu.REPORT_FILE, "r", encoding="utf-8") as f:
    latest_report = f.read()
test("latest copy matches archive", latest_report == report)
test("has fallback marker", "fallback" in report.lower())
test("has TLDR section", "## TL;DR" in report)
test("has deep trend section", "## Deep Trend Insights" in report)
test("has highlighted projects", "## Highlighted Projects" in report and "OpenRank 增长 200%" in report)
test("has review candidates", "## Review Candidates" in report and "test/repo" in report)
test("has openrank month column", "Latest OpenRank | OpenRank Month" in report and "| 12.5 | 2026-01 |" in report)
test("does not duplicate candidate details", "## Candidate Details" not in report)
if yuque_before is not None:
    with open(yuque_path, "r", encoding="utf-8") as f:
        yuque_after = f.read()
    test("does not rewrite yuque_report", yuque_after == yuque_before)
os.remove(written_path)
if existing_latest_report is not None:
    with open(wu.REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(existing_latest_report)
else:
    os.remove(wu.REPORT_FILE)

# ── 4. PR body and DingTalk format ────────────────────────────────────
print("\n4. PR body and DingTalk format")
body = wu.build_pr_body(fake_projects, "# Full Report\n\nBody", date_str="2099-01-02")
test("has checklist start marker", "agentic-review-checklist:start" in body)
test("has checklist end marker", "agentic-review-checklist:end" in body)
test("has plain checklist item", "- [ ] test/repo" in body)
test("has full report section", "## Full Weekly Report" in body and "# Full Report" in body)
test("does not require Yuque link", "yuque" not in body.lower())
test("review table omits match reason", "Match Reason" not in report)
test("parses existing report candidates", wu.parse_report_candidates(report) == [{"repo_name": "test/repo"}, {"repo_name": "foo/bar"}])
parsed_highlights = wu.parse_report_highlights(report)
test("parses existing report highlights", parsed_highlights and parsed_highlights[0][0]["repo_name"] == "test/repo")

dingtalk_md = wu.build_dingtalk_markdown(
    fake_projects,
    fake_recs + [(fake_projects[1], 0.8, "第二个"), (fake_projects[0], 0.7, "第三个"), (fake_projects[1], 0.6, "第四个"), (fake_projects[0], 0.5, "第五个")],
    "/go/doc/123",
    "https://github.com/antgroup/llm-oss-landscape/pull/1",
    date_str="2099-01-02",
    report_markdown=report,
)
test("DingTalk title omits date", "## Agentic AI Weekly Update - 2099-01-02" not in dingtalk_md)
test("DingTalk includes trend opinions", "**趋势观点**" in dingtalk_md)
test("DingTalk uses Yuque markdown link", "[完整报告](https://yuque.antfin.com/go/doc/123)" in dingtalk_md)
test("DingTalk uses PR markdown link", "[待筛选 PR](https://github.com/antgroup/llm-oss-landscape/pull/1)" in dingtalk_md)
test("DingTalk lists five highlighted projects", dingtalk_md.count("- **") == 5, dingtalk_md)
tldr_only_report = "# Agentic AI Weekly Report - 2099-01-02\n\n## TL;DR\n\n- 本周发现 **2** 个候选项目。\n- 热门方向集中在 Coding Agent。\n\n## Review Candidates\n"
test("DingTalk trend opinions fall back to TLDR", wu.extract_trend_opinions(tldr_only_report) == ["本周发现 2 个候选项目。", "热门方向集中在 Coding Agent。"])

# ── 5. parse_pr_checklist ─────────────────────────────────────────────
print("\n5. parse_pr_checklist")
# Table-style
pr_body_table = """## Weekly Update
| ✓ | Repo | Description | Stars | Language | Created |
|---|------|-------------|-------|----------|---------|
| - [x] | **test/repo** | A test project | 1.5k | Python | 2026-01 |
| - [ ] | **foo/bar** | Another project | 0.5k | Rust | 2026-02 |
"""
items = wu.parse_pr_checklist(pr_body_table)
test("parses table rows", len(items) == 2, f"got {len(items)}")
test("detects checked item", items[0] == ("test/repo", True), str(items[0]))
test("detects unchecked item", items[1] == ("foo/bar", False), str(items[1]))

# List-style fallback
pr_body_list = "- [x] **test/repo** — desc\n- [ ] **foo/bar** — desc\n"
items2 = wu.parse_pr_checklist(pr_body_list)
test("parses list style", len(items2) == 2, f"got {len(items2)}")
test("list checked correct", items2[0] == ("test/repo", True))
plain_items = wu.parse_pr_checklist("- [x] test/repo\n- [ ] foo/bar\n")
test("parses plain checklist", plain_items == [("test/repo", True), ("foo/bar", False)], str(plain_items))

with patch("weekly_update.subprocess.run") as mock_run:
    mock_run.return_value = types.SimpleNamespace(stdout='{"number":16,"mergedAt":"2026-05-04T00:00:00Z","body":"- [x] test/repo"}', stderr="")
    pr = wu.fetch_upstream_pr(16)
    called_args = mock_run.call_args[0][0]
    test("fetch_upstream_pr uses explicit upstream repo", "--repo" in called_args and wu.PR_TARGET_REPO in called_args and "16" in called_args, str(called_args))
    test("fetch_upstream_pr parses JSON", pr["number"] == 16 and bool(pr["mergedAt"]), str(pr))

# ── 6. generate_trend_context ─────────────────────────────────────────
print("\n6. generate_trend_context")
existing_trend_context = None
if os.path.exists(wu.TREND_CONTEXT_FILE):
    with open(wu.TREND_CONTEXT_FILE, "r", encoding="utf-8") as f:
        existing_trend_context = f.read()
fake_projects_trend = [
    {
        "repo_name": "fast/grower",
        "description": "Fast growing project",
        "stars": 50000,
        "language": "Python",
        "created_at": "2026-01-15",
        "categories": ["Coding Agent"],
        "openrank_latest": 80.0,
        "openrank_month": "2026-02",
        "openrank_trend": {"2025-11": 10.0, "2025-12": 20.0, "2026-01": 40.0, "2026-02": 80.0},
        "participants": 200,
    },
    {
        "repo_name": "new/hot",
        "description": "Brand new project",
        "stars": 10000,
        "language": "Rust",
        "created_at": "2026-03-01",
        "categories": ["Browser Agent", "Coding Agent"],
        "openrank_latest": 5.0,
        "openrank_month": "",
        "openrank_trend": {},
        "participants": 50,
    },
]
trend_months = ["2025-11", "2025-12", "2026-01", "2026-02"]
fake_recs_trend = [(fake_projects_trend[0], 0.95, "增速 700%")]
wu.generate_trend_context(fake_projects_trend, trend_months, fake_recs_trend)

test("trend context file created", os.path.exists(wu.TREND_CONTEXT_FILE))
with open(wu.TREND_CONTEXT_FILE, "r") as f:
    ctx = f.read()
test("has category distribution", "Coding Agent" in ctx and "Browser Agent" in ctx)
test("has data highlights", "增速最快" in ctx)
test("has top recommendations", "fast/grower" in ctx)
test("has growth percentage", "700%" in ctx)
test("has participant count", "200" in ctx)

# Cleanup: preserve the checked-in trend context if it existed before the test.
if existing_trend_context is not None:
    with open(wu.TREND_CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(existing_trend_context)
else:
    os.remove(wu.TREND_CONTEXT_FILE)

# ── 7. CSV path correctness ───────────────────────────────────────────
print("\n7. File paths")
test("INPUT_CSV points to data/", wu.INPUT_CSV.endswith("data/agentic-ai-projects.csv"), wu.INPUT_CSV)
test("REPORT_FILE points to data/", wu.REPORT_FILE.endswith("data/weekly_report.md"), wu.REPORT_FILE)
test("CSV file exists", os.path.exists(wu.INPUT_CSV))

# ── Summary ────────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed")
if failed:
    print("Some tests failed!")
    sys.exit(1)
else:
    print("All tests passed!")
