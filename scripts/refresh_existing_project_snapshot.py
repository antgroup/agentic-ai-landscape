#!/usr/bin/env python3
"""Refresh metrics for the existing canonical project pool without adding repos.

The script updates GitHub repository metadata and contributor counts for every
row already present in ``data/agentic-ai-projects.csv``. It also appends the
August 2026 OpenRank point and a rolling 12-month trend from OpenDigger's
published repository JSON. Landscape selection and taxonomy columns are never
changed.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / "data" / "agentic-ai-projects.csv"
DERIVED_PATHS = (
    ROOT / "data" / "agent_infra_landscape_projects.csv",
    ROOT / "data" / "model_infra_landscape_projects.csv",
)
OPENRANK_MONTH = "2026-08"
OPENRANK_FIELD = "openrank_2608"
TREND_MONTHS = [
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
    "2026-06",
    "2026-07",
    "2026-08",
]
TREND_FIELD = "openrank_trend_2509_2608"
GITHUB_API_VERSION = "2026-03-10"
PRESERVED_FIELDS = {
    "repo_id",
    "repo_name",
    "landscape_action",
    "landscape_layer",
    "landscape_section",
    "selection_reason",
    "selection_caveat",
    "trend_signal",
    "trend_signal_reason",
}
GITHUB_FIELDS = (
    "description",
    "stars",
    "contributors",
    "forks",
    "open_issues",
    "license",
    "archived",
    "pushed_at",
    "language",
    "created_at",
    "topics",
    "github_status",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "").strip() or os.getenv("GH_TOKEN", "").strip()
    result = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "agentic-ai-landscape-existing-pool-refresh",
    }
    if token:
        result["Authorization"] = f"Bearer {token}"
    return result


def request_json(
    url: str,
    request_headers: dict[str, str] | None = None,
    params: dict[str, object] | None = None,
) -> tuple[int, object, requests.Response]:
    last_response: requests.Response | None = None
    for attempt in range(5):
        try:
            response = requests.get(
                url,
                headers=request_headers,
                params=params,
                timeout=30,
            )
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2**attempt)
            continue
        last_response = response
        if response.status_code in {200, 204, 404, 451}:
            payload: object = None
            if response.status_code == 200:
                payload = response.json()
            return response.status_code, payload, response
        if response.status_code not in {403, 429, 500, 502, 503, 504}:
            break
        retry_after = int(response.headers.get("Retry-After", "0") or 0)
        time.sleep(max(retry_after, 2**attempt))
    assert last_response is not None
    raise RuntimeError(
        f"HTTP {last_response.status_code} for {url}: {last_response.text[:180]}"
    )


def contributor_count(repo: str, request_headers: dict[str, str]) -> int | None:
    status, payload, response = request_json(
        f"https://api.github.com/repos/{repo}/contributors",
        request_headers,
        {"per_page": 1},
    )
    if status in {404, 451}:
        return None
    if status == 204:
        return 0
    last_url = response.links.get("last", {}).get("url")
    if last_url:
        pages = parse_qs(urlparse(last_url).query).get("page", [])
        if pages:
            return int(pages[0])
    return len(payload) if isinstance(payload, list) else 0


def github_snapshot(repo: str, request_headers: dict[str, str]) -> dict[str, object]:
    status, payload, _ = request_json(
        f"https://api.github.com/repos/{repo}", request_headers
    )
    if status in {404, 451} or not isinstance(payload, dict):
        return {"github_status": "missing" if status == 404 else "blocked"}
    contributors = contributor_count(repo, request_headers)
    license_payload = payload.get("license")
    return {
        "description": payload.get("description") or "",
        "stars": payload.get("stargazers_count") or 0,
        "contributors": contributors if contributors is not None else "",
        "forks": payload.get("forks_count") or 0,
        "open_issues": payload.get("open_issues_count") or 0,
        "license": (
            license_payload.get("spdx_id")
            if isinstance(license_payload, dict)
            else ""
        )
        or "",
        "archived": str(bool(payload.get("archived"))).lower(),
        "pushed_at": str(payload.get("pushed_at") or "").split("T")[0],
        "language": payload.get("language") or "",
        "created_at": str(payload.get("created_at") or "").split("T")[0],
        "topics": ",".join(payload.get("topics") or []),
        "github_status": "ok",
    }


def openrank_snapshot(repo: str) -> dict[str, object]:
    status, payload, _ = request_json(
        f"https://oss.open-digger.cn/github/{repo}/openrank.json"
    )
    if status == 404 or not isinstance(payload, dict):
        return {OPENRANK_FIELD: "", TREND_FIELD: json.dumps([None] * 12)}
    trend = [payload.get(month) for month in TREND_MONTHS]
    latest = payload.get(OPENRANK_MONTH)
    return {
        OPENRANK_FIELD: round(float(latest), 2) if latest is not None else "",
        TREND_FIELD: json.dumps(
            [round(float(value), 2) if value is not None else None for value in trend]
        ),
    }


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def with_snapshot_fields(fields: list[str]) -> list[str]:
    output = list(fields)
    if OPENRANK_FIELD not in output:
        output.insert(output.index("openrank_2607") + 1, OPENRANK_FIELD)
    if TREND_FIELD not in output:
        anchor = output.index("openrank_trend_2508_2607") + 1
        output.insert(anchor, TREND_FIELD)
    return output


def validate(
    before: list[dict[str, str]], after: list[dict[str, object]]
) -> None:
    if len(before) != len(after):
        raise RuntimeError("Project row count changed during refresh")
    for old, new in zip(before, after, strict=True):
        for field in PRESERVED_FIELDS:
            if old.get(field, "") != str(new.get(field, "")):
                raise RuntimeError(f"Preserved field changed: {old['repo_name']} {field}")


def main() -> None:
    args = parse_args()
    if args.workers < 1 or args.workers > 8:
        raise SystemExit("--workers must be between 1 and 8")
    load_dotenv(ROOT / ".env")
    request_headers = headers()
    fields, rows = read_csv(CANONICAL_PATH)
    snapshots: dict[str, dict[str, object]] = {}

    print(f"Refreshing {len(rows)} existing repositories; project pool is fixed.")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                lambda repo: {
                    **github_snapshot(repo, request_headers),
                    **openrank_snapshot(repo),
                },
                row["repo_name"],
            ): row["repo_name"]
            for row in rows
        }
        for index, future in enumerate(as_completed(futures), 1):
            repo = futures[future]
            snapshots[repo.lower()] = future.result()
            if index % 25 == 0 or index == len(futures):
                print(f"  {index}/{len(futures)}")

    refreshed: list[dict[str, object]] = []
    for row in rows:
        updated: dict[str, object] = dict(row)
        snapshot = snapshots[row["repo_name"].lower()]
        previous_trend = json.loads(row.get("openrank_trend_2508_2607") or "[]")
        refreshed_trend = json.loads(str(snapshot[TREND_FIELD]))
        for index in range(min(11, len(refreshed_trend))):
            if refreshed_trend[index] is None and len(previous_trend) > index + 1:
                refreshed_trend[index] = previous_trend[index + 1]
        snapshot[TREND_FIELD] = json.dumps(refreshed_trend)
        for field in (*GITHUB_FIELDS, OPENRANK_FIELD, TREND_FIELD):
            if field in snapshot:
                updated[field] = snapshot[field]
        refreshed.append(updated)
    validate(rows, refreshed)

    coverage = sum(bool(row.get(OPENRANK_FIELD, "")) for row in refreshed)
    github_ok = sum(row.get("github_status") == "ok" for row in refreshed)
    selected = [
        row
        for row in refreshed
        if str(row.get("landscape_action", "")).lower() in {"keep", "add"}
    ]
    selected_coverage = sum(bool(row.get(OPENRANK_FIELD, "")) for row in selected)
    print(
        f"GitHub ok: {github_ok}/{len(refreshed)}; "
        f"August OpenRank: {coverage}/{len(refreshed)}; "
        f"selected coverage: {selected_coverage}/{len(selected)}"
    )
    if args.dry_run:
        print("Dry run complete; no files written.")
        return

    output_fields = with_snapshot_fields(fields)
    write_csv(CANONICAL_PATH, output_fields, refreshed)
    by_repo = {str(row["repo_name"]).lower(): row for row in refreshed}
    for path in DERIVED_PATHS:
        derived_fields, derived_rows = read_csv(path)
        output_rows: list[dict[str, object]] = []
        for row in derived_rows:
            source = by_repo[row["repo_name"].lower()]
            updated: dict[str, object] = dict(row)
            for field in (*GITHUB_FIELDS, OPENRANK_FIELD, TREND_FIELD):
                updated[field] = source.get(field, "")
            output_rows.append(updated)
        write_csv(path, with_snapshot_fields(derived_fields), output_rows)
    print(f"Updated {CANONICAL_PATH.relative_to(ROOT)} and derived landscape CSVs")


if __name__ == "__main__":
    main()
