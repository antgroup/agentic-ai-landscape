"""
Enrich agentic-ai-projects.csv with data from GitHub API and ClickHouse.

Columns added:
  - description, stars, language, created_at, topics  (GitHub API)
  - readme  (GitHub API - base64 decoded)
  - openrank_latest, openrank_trend  (ClickHouse - dynamic based on current month)
  - participants_latest  (ClickHouse - participants in issues/PRs in recent month)
"""

import os
import csv
import json
import time
import base64
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import clickhouse_connect

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(BASE, "scripts", ".env")
INPUT_CSV = os.path.join(BASE, "data", "agentic-ai-projects.csv")
OUTPUT_CSV = os.path.join(BASE, "data", "agentic-ai-projects.csv")
OUTPUT_READMES = os.path.join(BASE, "data", "project_readmes.json")

load_dotenv(ENV_PATH)

# ── Dynamic date calculation ───────────────────────────────────────────
now = datetime.now()
# OpenRank data is updated monthly, use previous month as latest
# If current month is April 2026, latest openrank is March 2026
openrank_latest_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
openrank_latest_date = f"{openrank_latest_month}-01"

# Participants: use current month data (events are real-time)
participants_latest_month = now.strftime("%Y-%m")
participants_start = now.replace(day=1).strftime("%Y-%m-%d")
# Calculate end of current month
if now.month == 12:
    participants_end = f"{now.year + 1}-01-01"
else:
    participants_end = f"{now.year}-{now.month + 1:02d}-01"

# OpenRank trend: last 12 completed months ending with latest OpenRank month
trend_months = []
latest_openrank_date = now.replace(day=1) - timedelta(days=1)
for i in range(11, -1, -1):
    month_date = latest_openrank_date.replace(day=1) - relativedelta(months=i)
    trend_months.append(month_date.strftime("%Y-%m"))

print(f"Current date: {now.strftime('%Y-%m-%d')}")
print(f"OpenRank latest month: {openrank_latest_month}")
print(f"Participants month: {participants_latest_month}")
print(f"Trend months: {trend_months}")

# ── ClickHouse ─────────────────────────────────────────────────────────
ch_client = clickhouse_connect.get_client(
    host=os.getenv("CLICKHOUSE_HOST"),
    port=8123,
    username=os.getenv("CLICKHOUSE_USER"),
    password=os.getenv("CLICKHOUSE_PASSWORD"),
)

# ── GitHub API ─────────────────────────────────────────────────────────
github_token = os.getenv("GITHUB_TOKEN", "").strip()
gh_headers = {"Accept": "application/vnd.github.v3+json"}
if github_token:
    gh_headers["Authorization"] = f"token {github_token}"
    print(f"GitHub API: authenticated (rate limit ~5000/hr)")
else:
    print("GitHub API: unauthenticated (rate limit 60/hr) — set GITHUB_TOKEN in .env for faster runs")

# ── Read input CSV ─────────────────────────────────────────────────────
with open(INPUT_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    input_rows = list(reader)

print(f"Input: {len(input_rows)} repos to enrich")

# ── Collect all repo_names ─────────────────────────────────────────────
repo_names = [r["repo_name"].strip() for r in input_rows if r["repo_name"].strip()]

# ── Batch query ClickHouse for OpenRank data ───────────────────────────
openrank_data = {}
print("Querying ClickHouse for OpenRank data...")

# Build IN clause for repo names
def build_in_clause(names):
    return ", ".join([f"'{name.replace(chr(39), chr(39)+chr(39))}'" for name in names])

repo_placeholders = build_in_clause(repo_names)

# Query openrank for last 12 months
for month in trend_months:
    sql = f"""
        SELECT repo_name, openrank
        FROM opensource.global_openrank
        WHERE platform = 'GitHub'
          AND repo_name IN ({repo_placeholders})
          AND type = 'Repo'
          AND created_at = '{month}-01'
    """
    result = ch_client.query(sql)
    for row in result.result_rows:
        name, score = row
        if name not in openrank_data:
            openrank_data[name] = {}
        openrank_data[name][month] = round(score, 2)

print(f"ClickHouse OpenRank: got data for {len(openrank_data)} repos")

# ── Batch query ClickHouse for Participants data ───────────────────────
participants_data = {}
print("Querying ClickHouse for Participants data...")

# Query participants for current month
sql = f"""
    SELECT repo_name, count(DISTINCT actor_id) as participants
    FROM opensource.events
    WHERE platform = 'GitHub'
      AND repo_name IN ({repo_placeholders})
      AND type IN ('IssuesEvent', 'IssueCommentEvent', 'PullRequestEvent',
                   'PullRequestReviewEvent', 'PullRequestReviewCommentEvent')
      AND created_at >= '{participants_start}'
      AND created_at < '{participants_end}'
    GROUP BY repo_name
"""
result = ch_client.query(sql)
for row in result.result_rows:
    name, count = row
    participants_data[name] = count

print(f"ClickHouse Participants: got data for {len(participants_data)} repos")

# ── GitHub API fetch with retry & rate-limit handling ─────────────────
def fetch_github_info(repo_name, max_retries=3):
    """Fetch repo info from GitHub API with retry on rate limit."""
    url = f"https://api.github.com/repos/{repo_name}"
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=gh_headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "description": data.get("description") or "",
                    "stars": data.get("stargazers_count", 0),
                    "language": data.get("language") or "",
                    "created_at": data.get("created_at", "").split("T")[0] if data.get("created_at") else "",
                    "topics": ",".join(data.get("topics", [])),
                }
            elif resp.status_code == 403 and "rate limit" in resp.text.lower():
                reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - int(time.time()), 60)
                print(f"  Rate limit hit for {repo_name}, waiting {wait}s...")
                time.sleep(wait)
                continue
            elif resp.status_code == 404:
                print(f"  404 for {repo_name}")
                return None
            else:
                print(f"  HTTP {resp.status_code} for {repo_name}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        except Exception as e:
            print(f"  Error for {repo_name}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return None

def fetch_github_readme(repo_name, max_retries=3):
    """Fetch README content from GitHub API."""
    url = f"https://api.github.com/repos/{repo_name}/readme"
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=gh_headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                return content[:50000]  # Limit to 50KB per README
            elif resp.status_code == 404:
                return ""
            elif resp.status_code == 403 and "rate limit" in resp.text.lower():
                reset_time = int(resp.headers.get("X-RateLimit-Reset", 0))
                wait = max(reset_time - int(time.time()), 60)
                print(f"  Rate limit hit for {repo_name} readme, waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    return ""

# ── Main loop ─────────────────────────────────────────────────────────
FIELDNAMES = [
    "repo_id", "repo_name", "description", "stars",
    "openrank_latest", "openrank_trend",
    "participants_latest",
    "language", "created_at", "topics", "categories"
]

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_progress(idx, total, repo_name, gh_info, or_data, participants, readme_len):
    """Print a live row showing data fetched for each repo."""
    stars = gh_info.get("stars", 0) if gh_info else 0
    lang = (gh_info.get("language") or "—")[:12]
    created = gh_info.get("created_at") or "—"

    # Latest openrank
    rank = or_data.get(openrank_latest_month, None)
    rank_str = f"{rank:.1f}" if rank else "—"

    color = GREEN if stars > 0 and rank else (YELLOW if stars > 0 else RED)
    print(f"{BOLD}[{idx+1:>3}/{total}]{RESET} {color}{repo_name:<40}{RESET}  "
          f"stars={stars:>8}  rank={rank_str:>6}  part={participants:>5}  "
          f"readme={readme_len:>5}  lang={lang:<12}")

enriched_rows = []
readmes = {}
skipped = 0

for i, row in enumerate(input_rows):
    repo_name = row["repo_name"].strip()
    repo_id = row["repo_id"].strip()

    if not repo_name:
        skipped += 1
        continue

    # GitHub API - fetch info and readme in parallel
    gh_info = fetch_github_info(repo_name)
    if gh_info is None:
        gh_info = {
            "description": "", "stars": 0, "language": "",
            "created_at": "", "topics": ""
        }

    readme = fetch_github_readme(repo_name)
    readmes[repo_name] = readme

    # ClickHouse data
    or_data = openrank_data.get(repo_name, {})
    participants = participants_data.get(repo_name, 0)

    # Show live progress
    print_progress(i, len(input_rows), repo_name, gh_info, or_data, participants, len(readme))

    # Build openrank trend list
    trend_list = [or_data.get(m, None) for m in trend_months]
    # Trim trailing None values
    while trend_list and trend_list[-1] is None:
        trend_list.pop()

    # Get latest openrank
    openrank_latest = or_data.get(openrank_latest_month, None)

    # Preserve existing categories if present
    existing_categories = row.get("categories", "")

    enriched_rows.append({
        "repo_id": repo_id,
        "repo_name": repo_name,
        "description": gh_info["description"],
        "stars": gh_info["stars"],
        "openrank_latest": openrank_latest if openrank_latest else "",
        "openrank_trend": json.dumps(trend_list),
        "participants_latest": participants,
        "language": gh_info["language"],
        "created_at": gh_info["created_at"],
        "topics": gh_info["topics"],
        "categories": existing_categories,
    })

    # Respect rate limits
    if not github_token:
        time.sleep(1.5)
    else:
        time.sleep(0.3)

# ── Write output CSV ───────────────────────────────────────────────────
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(enriched_rows)

print(f"\nDone! Wrote {len(enriched_rows)} enriched rows to {OUTPUT_CSV}")
print(f"Skipped {skipped} rows with empty repo_name")

# ── Write READMEs JSON ─────────────────────────────────────────────────
readme_output = []
for row in enriched_rows:
    readme_output.append({
        "repo_id": row["repo_id"],
        "repo_name": row["repo_name"],
        "description": row["description"],
        "stars": row["stars"],
        "language": row["language"],
        "created_at": row["created_at"],
        "topics": row["topics"],
        "readme": readmes.get(row["repo_name"], "")
    })

with open(OUTPUT_READMES, "w", encoding="utf-8") as f:
    json.dump(readme_output, f, ensure_ascii=False, indent=2)

print(f"Saved READMEs to {OUTPUT_READMES}")

# Summary
has_openrank = sum(1 for r in enriched_rows if r["openrank_latest"])
has_stars = sum(1 for r in enriched_rows if r["stars"] and r["stars"] > 0)
has_participants = sum(1 for r in enriched_rows if r["participants_latest"] > 0)
has_readme = sum(1 for r in readme_output if r["readme"])
print(f"  - Repos with openrank_latest: {has_openrank}")
print(f"  - Repos with stars: {has_stars}")
print(f"  - Repos with participants: {has_participants}")
print(f"  - Repos with readme: {has_readme}")
