#!/usr/bin/env python3
"""Generate SVG figures and summary tables for the agentic landscape report."""

import ast
import html
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
DATA_FILE = BASE / "data" / "agentic-ai-projects.csv"
OUT_DIR = BASE / "reports" / "260601-agentic_landscape"
FIG_DIR = OUT_DIR / "figures"
SUMMARY_FILE = OUT_DIR / "agentic-summary.json"

MONTHS = [
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
]

COLORS = {
    "blue": "#2563eb",
    "cyan": "#0891b2",
    "green": "#16a34a",
    "orange": "#ea580c",
    "purple": "#7c3aed",
    "pink": "#db2777",
    "gray": "#64748b",
    "dark": "#0f172a",
    "grid": "#e2e8f0",
    "muted": "#475569",
    "bg": "#ffffff",
}


def parse_trend(value):
    try:
        values = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []
    return [None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v) for v in values]


def escape(value):
    return html.escape(str(value), quote=True)


def svg_text(x, y, text, size=12, weight=400, fill=None, anchor="start"):
    fill = fill or COLORS["dark"]
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{escape(text)}</text>'
    )


def save_svg(name, width, height, body):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f'<rect width="{width}" height="{height}" fill="{COLORS["bg"]}"/>'
        f"{body}</svg>\n"
    )
    (FIG_DIR / name).write_text(content, encoding="utf-8")


def category_counts(df):
    counts = Counter()
    openrank = defaultdict(float)
    stars = defaultdict(int)
    for _, row in df.iterrows():
        cats = [c.strip() for c in str(row["categories"]).split("|") if c.strip()]
        score = row["openrank_current"]
        score = 0 if pd.isna(score) else float(score)
        for cat in cats:
            counts[cat] += 1
            openrank[cat] += score
            stars[cat] += int(row["stars"] or 0)
    rows = [
        {
            "category": cat,
            "projects": count,
            "openrank": round(openrank[cat], 2),
            "stars": stars[cat],
        }
        for cat, count in counts.items()
    ]
    return sorted(rows, key=lambda x: (x["projects"], x["openrank"]), reverse=True)


def trend_change(row):
    values = [v for v in row["trend"] if v is not None]
    if len(values) < 2:
        return None
    start = values[0]
    end = values[-1]
    pct = None if start == 0 else (end - start) / start * 100
    return {
        "start": start,
        "end": end,
        "absolute": end - start,
        "pct": pct,
    }


def draw_bar_chart(rows, name, title, label_key, value_key, width=1100, height=650):
    left = 275
    right = 80
    top = 82
    row_h = 36
    chart_w = width - left - right
    max_value = max(r[value_key] for r in rows) or 1
    parts = [svg_text(32, 42, title, 24, 700)]
    for i, row in enumerate(rows):
        y = top + i * row_h
        value = row[value_key]
        bar_w = chart_w * value / max_value
        parts.append(svg_text(left - 14, y + 20, row[label_key], 13, 500, COLORS["dark"], "end"))
        parts.append(
            f'<rect x="{left}" y="{y}" width="{bar_w:.1f}" height="22" rx="4" fill="{COLORS["blue"]}"/>'
        )
        parts.append(svg_text(left + bar_w + 8, y + 17, f"{value:,.0f}", 12, 600, COLORS["muted"]))
    save_svg(name, width, height, "".join(parts))


def draw_line_chart(df, repos, name, title, width=1100, height=650):
    left = 78
    right = 190
    top = 78
    bottom = 78
    chart_w = width - left - right
    chart_h = height - top - bottom
    colors = [COLORS["blue"], COLORS["orange"], COLORS["green"], COLORS["purple"], COLORS["pink"], COLORS["cyan"]]
    max_y = 1
    for repo in repos:
        trend = df.loc[df["repo_name"] == repo, "trend"].iloc[0]
        max_y = max(max_y, max([v for v in trend if v is not None] or [0]))
    max_y = math.ceil(max_y / 100) * 100 if max_y > 100 else math.ceil(max_y / 10) * 10
    parts = [svg_text(32, 42, title, 24, 700)]
    for i in range(5):
        y = top + chart_h * i / 4
        value = max_y * (4 - i) / 4
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}" stroke="{COLORS["grid"]}"/>')
        parts.append(svg_text(left - 12, y + 4, f"{value:.0f}", 11, 400, COLORS["muted"], "end"))
    for i, month in enumerate(MONTHS):
        if i % 2 == 0 or i == len(MONTHS) - 1:
            x = left + chart_w * i / (len(MONTHS) - 1)
            parts.append(svg_text(x, height - 34, month[2:], 11, 400, COLORS["muted"], "middle"))
    for idx, repo in enumerate(repos):
        trend = df.loc[df["repo_name"] == repo, "trend"].iloc[0]
        pts = []
        for i, value in enumerate(trend):
            if value is None:
                continue
            x = left + chart_w * i / (len(MONTHS) - 1)
            y = top + chart_h * (1 - value / max_y)
            pts.append((x, y))
        if len(pts) < 2:
            continue
        color = colors[idx % len(colors)]
        path = " ".join([f"{x:.1f},{y:.1f}" for x, y in pts])
        parts.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="3"/>')
        for x, y in pts[-1:]:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        legend_y = top + 26 + idx * 26
        parts.append(f'<rect x="{width - right + 26}" y="{legend_y - 10}" width="14" height="14" rx="3" fill="{color}"/>')
        parts.append(svg_text(width - right + 48, legend_y + 2, repo, 12, 600, COLORS["dark"]))
    save_svg(name, width, height, "".join(parts))


def draw_scatter(df, name, title, width=1100, height=700):
    left = 92
    right = 72
    top = 88
    bottom = 78
    chart_w = width - left - right
    chart_h = height - top - bottom
    rows = df[df["openrank_current"] > 0].copy()
    rows["log_stars"] = rows["stars"].apply(lambda v: math.log10(max(v, 1)))
    rows["log_openrank"] = rows["openrank_current"].apply(lambda v: math.log10(max(v, 0.01)))
    min_x, max_x = rows["log_stars"].min(), rows["log_stars"].max()
    min_y, max_y = rows["log_openrank"].min(), rows["log_openrank"].max()
    parts = [svg_text(32, 42, title, 24, 700)]
    for i in range(5):
        x = left + chart_w * i / 4
        y = top + chart_h * i / 4
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart_h}" stroke="{COLORS["grid"]}"/>')
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}" stroke="{COLORS["grid"]}"/>')
    for _, row in rows.iterrows():
        x = left + chart_w * (row["log_stars"] - min_x) / (max_x - min_x)
        y = top + chart_h * (1 - (row["log_openrank"] - min_y) / (max_y - min_y))
        r = 3.5 + min(9, math.sqrt(row["stars"]) / 95)
        color = COLORS["blue"] if "Coding Agent" in row["categories"] else COLORS["cyan"]
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" opacity="0.58"/>')
    labels = ["openclaw/openclaw", "anthropics/claude-code", "anomalyco/opencode", "openai/codex", "google-gemini/gemini-cli"]
    for repo in labels:
        row = rows[rows["repo_name"] == repo]
        if row.empty:
            continue
        row = row.iloc[0]
        x = left + chart_w * (row["log_stars"] - min_x) / (max_x - min_x)
        y = top + chart_h * (1 - (row["log_openrank"] - min_y) / (max_y - min_y))
        parts.append(svg_text(x + 10, y - 8, repo, 12, 700, COLORS["dark"]))
    parts.append(svg_text(left + chart_w / 2, height - 28, "Stars, log scale", 13, 600, COLORS["muted"], "middle"))
    parts.append(svg_text(26, top + chart_h / 2, "OpenRank, log scale", 13, 600, COLORS["muted"], "middle"))
    save_svg(name, width, height, "".join(parts))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_FILE)
    openrank_columns = sorted([col for col in df.columns if col.startswith("openrank_") and col != "openrank_trend"])
    openrank_col = openrank_columns[-1] if openrank_columns else "openrank_latest"
    df["openrank_current"] = pd.to_numeric(df[openrank_col], errors="coerce")
    df["trend"] = df["openrank_trend"].fillna("[]").apply(parse_trend)
    df["change"] = df.apply(trend_change, axis=1)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    cats = category_counts(df)
    lang_counts = df["language"].fillna("Unknown").replace("", "Unknown").value_counts().head(10)
    ranked_df = df[df["openrank_current"].notna()].copy()
    top_openrank = ranked_df.sort_values("openrank_current", ascending=False).head(15)
    top_growth = []
    top_decline = []
    for _, row in df.iterrows():
        change = row["change"]
        if not change:
            continue
        latest = row["openrank_current"]
        latest = None if pd.isna(latest) else float(latest)
        item = {
            "repo_name": row["repo_name"],
            "stars": int(row["stars"]),
            "openrank_current": latest,
            "start": round(change["start"], 2),
            "end": round(change["end"], 2),
            "absolute": round(change["absolute"], 2),
            "pct": None if change["pct"] is None else round(change["pct"], 1),
            "categories": row["categories"],
        }
        top_growth.append(item)
        top_decline.append(item)
    top_growth = sorted(top_growth, key=lambda x: x["absolute"], reverse=True)[:15]
    top_decline = sorted(top_decline, key=lambda x: x["absolute"])[:15]

    draw_bar_chart(cats[:15], "category-distribution.svg", "Agentic AI Categories by Project Count", "category", "projects")
    draw_bar_chart(
        top_openrank[["repo_name", "openrank_current"]].rename(columns={"openrank_current": "openrank"}).to_dict("records"),
        "top-openrank-projects.svg",
        "Top Projects by Latest OpenRank",
        "repo_name",
        "openrank",
    )
    draw_bar_chart(
        [{"language": k, "projects": int(v)} for k, v in lang_counts.items()],
        "language-mix.svg",
        "Language Mix by Project Count",
        "language",
        "projects",
        height=520,
    )
    draw_line_chart(
        df,
        ["openclaw/openclaw", "anthropics/claude-code", "anomalyco/opencode", "openai/codex", "google-gemini/gemini-cli", "n8n-io/n8n"],
        "openrank-trends-leading-projects.svg",
        "OpenRank Trends for Leading Agentic Projects",
    )
    draw_scatter(df, "stars-vs-openrank.svg", "Stars vs OpenRank: Attention and Community Activity")

    summary = {
        "project_count": int(len(df)),
        "total_stars": int(df["stars"].sum()),
        "openrank_field": openrank_col,
        "total_openrank": round(float(df["openrank_current"].sum()), 2),
        "median_openrank": round(float(df["openrank_current"].median()), 2),
        "categories": cats,
        "languages": [{"language": k, "projects": int(v)} for k, v in lang_counts.items()],
        "top_openrank": top_openrank[["repo_name", "stars", "openrank_current", "language", "created_at", "categories"]].assign(
            created_at=lambda x: x["created_at"].dt.strftime("%Y-%m-%d")
        ).to_dict("records"),
        "top_growth": top_growth,
        "top_decline": top_decline,
        "new_since_2025": int((df["created_at"] >= "2025-01-01").sum()),
        "new_since_2026": int((df["created_at"] >= "2026-01-01").sum()),
    }
    SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Wrote {SUMMARY_FILE}")
    print(f"Wrote figures to {FIG_DIR}")


if __name__ == "__main__":
    main()
