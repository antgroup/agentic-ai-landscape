#!/usr/bin/env python3
"""
Weekly Agentic AI Projects Update Workflow

Steps:
1. Query ClickHouse for top 100 projects by star growth in past week
2. Fetch project info (description, topics, readme)
3. Filter for agentic AI projects not in existing CSV
4. Generate one canonical weekly report with LLM trend insights
5. Publish the full report to Yuque, create a review PR, then send DingTalk
6. After the PR is merged, update CSV and regenerate classification

Usage:
    python weekly_update.py --check          # Check new projects, generate reports, create PR
    python weekly_update.py --post-merge     # Process merged PR checklist into CSV
    python weekly_update.py --full           # Legacy: check and add all discovered projects
"""

import os
import csv
import json
import time
import re
import base64
import argparse
import subprocess
import shlex
import requests
import hashlib
import hmac
import urllib.parse
import shutil
from datetime import datetime, timedelta
from collections import Counter
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import clickhouse_connect

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPT_DIR)
ENV_PATH = os.path.join(BASE, "scripts", ".env")
INPUT_CSV = os.path.join(BASE, "data", "agentic-ai-projects.csv")
OUTPUT_CSV = os.path.join(BASE, "data", "agentic-ai-projects.csv")
REPORT_FILE = os.path.join(BASE, "data", "weekly_report.md")
REPORT_ARCHIVE_DIR = os.path.join(BASE, "reports", "weekly_reports_by_agents")

# Target repo for PRs
PR_TARGET_REPO = "antgroup/llm-oss-landscape"

load_dotenv(ENV_PATH)

# ── DingTalk Webhook ─────────────────────────────────────────────────
# Get from environment or use default
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
DINGTALK_SECRET = os.getenv("DINGTALK_SECRET", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "180"))
LLM_REPORT_PROJECT_LIMIT = int(os.getenv("LLM_REPORT_PROJECT_LIMIT", "18"))
ALLOW_LLM_FALLBACK = os.getenv("ALLOW_LLM_FALLBACK", "").strip().lower() in ("1", "true", "yes")
YUQUE_BOOK_ID = os.getenv("YUQUE_BOOK_ID", "211551637").strip()
YUQUE_API_TOKEN = os.getenv("YUQUE_API_TOKEN", "").strip()
YUQUE_API_BASE = os.getenv("YUQUE_API_BASE", "https://www.yuque.com/api/v2").rstrip("/")
YUQUE_PUBLISH_COMMAND = os.getenv("YUQUE_PUBLISH_COMMAND", "").strip()
YUQUE_WEB_BASE = os.getenv("YUQUE_WEB_BASE", "https://yuque.antfin.com").rstrip("/")
YUQUE_NAMESPACE = os.getenv("YUQUE_NAMESPACE", "").strip()
YUQUE_PARENT_URL = os.getenv("YUQUE_PARENT_URL", "").strip()
YUQUE_PARENT_SLUG = os.getenv("YUQUE_PARENT_SLUG", "").strip()
YUQUE_PARENT_TITLE = os.getenv("YUQUE_PARENT_TITLE", "Agentic 每周推送").strip()
YUQUE_PARENT_UUID = os.getenv("YUQUE_PARENT_UUID", "").strip()
YUQUE_PARENT_NODE_UUID = os.getenv("YUQUE_PARENT_NODE_UUID", "").strip()
YUQUE_DOC_PUBLIC = os.getenv("YUQUE_DOC_PUBLIC", "").strip()
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "").strip()
DIRECT_NETWORK_HOSTS = [
    CLICKHOUSE_HOST,
    "api.github.com",
]

def host_from_url(url):
    if not url:
        return ""
    try:
        return urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return ""

# ── Colors ──────────────────────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ── ClickHouse ─────────────────────────────────────────────────────────
_ch_client = None

def ensure_no_proxy(host):
    """Add a host to no_proxy so internal SOCKS settings do not break direct HTTP clients."""
    if not host:
        return
    additions = [host, "127.0.0.1", "localhost"]
    for key in ("no_proxy", "NO_PROXY"):
        existing = [item.strip() for item in os.getenv(key, "").split(",") if item.strip()]
        changed = False
        for item in additions:
            if item not in existing:
                existing.append(item)
                changed = True
        if changed:
            os.environ[key] = ",".join(existing)

def ensure_direct_network_hosts():
    """Bypass inherited SOCKS proxy settings for hosts used by this pipeline."""
    for host in DIRECT_NETWORK_HOSTS:
        ensure_no_proxy(host)

def get_ch_client():
    """Create the ClickHouse client lazily so importing this module has no network side effects."""
    global _ch_client
    if _ch_client is None:
        ensure_direct_network_hosts()
        _ch_client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=8123,
            username=os.getenv("CLICKHOUSE_USER"),
            password=os.getenv("CLICKHOUSE_PASSWORD"),
        )
    return _ch_client

# ── Dynamic date calculation ───────────────────────────────────────────
now = datetime.now()

# OpenRank: latest month (previous month)
openrank_latest_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

# OpenRank trend: last 6 completed months ending with latest OpenRank month
trend_months = []
latest_openrank_date = now.replace(day=1) - timedelta(days=1)
for i in range(5, -1, -1):
    month_date = latest_openrank_date.replace(day=1) - relativedelta(months=i)
    trend_months.append(month_date.strftime("%Y-%m"))

# Participants: current month
participants_start = now.replace(day=1).strftime("%Y-%m-%d")
if now.month == 12:
    participants_end = f"{now.year + 1}-01-01"
else:
    participants_end = f"{now.year}-{now.month + 1:02d}-01"

def print_runtime_context():
    """Print date and API context for CLI runs."""
    print(f"Current date: {now.strftime('%Y-%m-%d')}")
    print(f"OpenRank latest month: {openrank_latest_month}")
    print(f"OpenRank trend months: {trend_months}")
    print(f"Participants month: {now.strftime('%Y-%m')}")
    if github_token:
        print(f"{GREEN}GitHub API: authenticated (rate limit ~5000/hr){RESET}")
    else:
        print(f"{YELLOW}GitHub API: unauthenticated (rate limit 60/hr){RESET}")

# ── GitHub API ─────────────────────────────────────────────────────────
github_token = os.getenv("GITHUB_TOKEN", "").strip()
gh_headers = {"Accept": "application/vnd.github.v3+json"}
if github_token:
    gh_headers["Authorization"] = f"token {github_token}"

# ── ClickHouse batch queries ───────────────────────────────────────────
def fetch_openrank_data(repo_names):
    """Fetch latest OpenRank and 6-month trend for repos."""
    if not repo_names:
        return {}

    def build_in_clause(names):
        return ", ".join([f"'{name.replace(chr(39), chr(39)+chr(39))}'" for name in names])

    repo_placeholders = build_in_clause(repo_names)
    openrank_data = {
        name: {
            "latest": "",
            "latest_month": "",
            "trend": {},
        }
        for name in repo_names
    }
    ch_client = get_ch_client()

    # Query 6-month trend
    for month in trend_months:
        sql_trend = f"""
            SELECT repo_name, openrank
            FROM opensource.global_openrank
            WHERE platform = 'GitHub'
              AND repo_name IN ({repo_placeholders})
              AND type = 'Repo'
              AND created_at = '{month}-01'
        """
        result = ch_client.query(sql_trend)
        for row in result.result_rows:
            name, score = row
            if name in openrank_data:
                score = round(score, 2)
                openrank_data[name]["trend"][month] = score
                openrank_data[name]["latest"] = score
                openrank_data[name]["latest_month"] = month

    return openrank_data

def fetch_participants_data(repo_names):
    """Fetch participant count (unique actors) for repos in current month."""
    if not repo_names:
        return {}

    def build_in_clause(names):
        return ", ".join([f"'{name.replace(chr(39), chr(39)+chr(39))}'" for name in names])

    repo_placeholders = build_in_clause(repo_names)
    participants_data = {}

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
    ch_client = get_ch_client()
    result = ch_client.query(sql)
    for row in result.result_rows:
        name, count = row
        participants_data[name] = count

    return participants_data

# ── Load existing projects ─────────────────────────────────────────────
def load_existing_projects():
    """Load existing project repo_names from CSV."""
    existing = set()
    if os.path.exists(INPUT_CSV):
        with open(INPUT_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("repo_name"):
                    existing.add(row["repo_name"].strip())
    print(f"Loaded {len(existing)} existing projects")
    return existing

# ── Query ClickHouse for star growth ──────────────────────────────────
def query_top_star_growth_projects(limit=100):
    """Query top projects by star growth in the past week."""
    # Calculate date range - last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Query for most starred repos in past week (WatchEvent = GitHub star)
    sql = f"""
        SELECT repo_name, count() as stars_received
        FROM opensource.events
        WHERE platform = 'GitHub'
          AND type = 'WatchEvent'
          AND created_at >= '{start_date.strftime('%Y-%m-%d')}'
          AND created_at < '{end_date.strftime('%Y-%m-%d')}'
        GROUP BY repo_name
        ORDER BY stars_received DESC
        LIMIT {limit}
    """
    
    result = get_ch_client().query(sql)
    projects = [row[0] for row in result.result_rows]
    print(f"Found {len(projects)} projects with star events in past week")
    return projects

# ── Fetch GitHub info ─────────────────────────────────────────────────
def fetch_github_info(repo_name):
    """Fetch repo info from GitHub API."""
    ensure_direct_network_hosts()
    url = f"https://api.github.com/repos/{repo_name}"
    try:
        resp = requests.get(url, headers=gh_headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "repo_id": data.get("id", 0),
                "description": data.get("description") or "",
                "stars": data.get("stargazers_count", 0),
                "language": data.get("language") or "",
                "created_at": data.get("created_at", "").split("T")[0] if data.get("created_at") else "",
                "topics": ",".join(data.get("topics", [])),
            }
        elif resp.status_code == 404:
            return None
        else:
            print(f"  HTTP {resp.status_code} for {repo_name}")
    except Exception as e:
        if "Missing dependencies for SOCKS support" in str(e):
            raise
        print(f"  Error for {repo_name}: {e}")
    return None

def fetch_github_readme(repo_name):
    """Fetch README content from GitHub API."""
    ensure_direct_network_hosts()
    url = f"https://api.github.com/repos/{repo_name}/readme"
    try:
        resp = requests.get(url, headers=gh_headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return content[:50000]
    except Exception as e:
        if "Missing dependencies for SOCKS support" in str(e):
            raise
    return ""

# ── Filter agentic AI projects ────────────────────────────────────────

def _word_match(keyword, text):
    """Match keyword with word boundaries to prevent substring false positives."""
    return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))

AGENTIC_CORE_KEYWORDS = [
    "agent", "agents", "agentic", "autonomous", "multi-agent", "multi agent",
    "ai agent", "coding agent", "dev agent", "llm agent", "gpt agent",
    "agent framework", "agent sdk", "agent toolkit", "agent builder",
    "agentic workflow", "agent workflow", "agent orchestration",
    "mcp", "model context protocol", "mcp server", "mcp client",
    "tool calling", "function calling", "tool integration",
    "browser agent", "web agent", "robot agent", "voice agent",
    "autogpt", "crewai", "langchain", "langgraph", "autogen", "agno", "camel",
    "metagpt", "openmanus", "claude agent", "gpt builder",
    "agent tools", "agent communication", "agent protocol", "a2a",
    "self-driving agent", "autonomous system", "agent autonomy",
]

ML_GENERAL_KEYWORDS = [
    "rag", "retrieval augmented", "vector database", "embedding",
    "fine-tuning", "model training", "inference", "llm inference", "vllm", "ollama",
    "workflow", "orchestration", "automation", "dify", "n8n", "flowise",
    "memory", "mem0", "memgpt", "letta", "context management",
    "evaluation", "observability", "tracing", "langfuse", "wandb",
    "code generation", "code completion", "ai coding", "program synthesis",
    "chatbot", "ai assistant", "knowledge base",
    "graphrag", "knowledge graph",
    "speech", "voice", "tts", "stt",
]

COLLECTION_KEYWORDS = [
    "awesome", "awesome list", "collection", "curated list",
    "papers", "tutorial", "course", "book", "blog", "newsletter",
    "reading list", "resources",
]

EXCLUSION_KEYWORDS = [
    "best practice", "best-practice", "cheat sheet", "cheatsheet",
    "design spec", "specification", "handbook",
    "skill file", "claude.md",
    "prompt template", "system prompt",
]

# Repo-name patterns that indicate non-project repos (skill files, CLAUDE.md repos)
SKILL_REPO_PATTERNS = [
    r'-skills?$',           # ends with -skill or -skills
    r'-best-practices?$',   # ends with -best-practice(s)
    r'claude[.-]code[.-]skill',  # contains claude-code-skill pattern
]

def is_agentic_project(project_info, readme_content, repo_name=""):
    """Check if project is agentic AI related using tiered keyword matching."""
    text = f"{project_info.get('description', '')} {project_info.get('topics', '')} {readme_content[:5000]}".lower()

    # Check repo-name patterns for skill-file / non-project repos
    name_part = repo_name.split("/")[-1] if "/" in repo_name else repo_name
    for pattern in SKILL_REPO_PATTERNS:
        if re.search(pattern, name_part, re.IGNORECASE):
            return False

    # Check exclusion keywords — reject unless strong agentic signal (≥5 core matches)
    core_count = sum(1 for kw in AGENTIC_CORE_KEYWORDS if _word_match(kw, text))
    for kw in EXCLUSION_KEYWORDS:
        if _word_match(kw, text):
            if core_count < 5:
                return False
            break

    # Check collection keywords — reject unless strong agentic signal (≥5 core matches)
    for kw in COLLECTION_KEYWORDS:
        if _word_match(kw, text):
            if core_count < 5:
                return False
            break

    # Require at least 1 agentic core keyword AND ≥2 total matches (core + general)
    if core_count < 1:
        return False

    general_count = sum(1 for kw in ML_GENERAL_KEYWORDS if _word_match(kw, text))
    total_count = core_count + general_count

    return total_count >= 2

# ── Taxonomy & Classification ──────────────────────────────────────────
TAXONOMY = {
    "Coding Agent": {
        "keywords": [
            "coding agent", "code agent", "coding assistant", "ai coding", "code generation",
            "autonomous coding", "developer agent", "programming agent", "code completion",
            "ide agent", "terminal agent", "cli agent", "code editor", "copilot",
            "aider", "cline", "continue", "tabby", "codex", "opencode", "goose",
            "cursor", "code assistant", "autonomous developer",
        ],
        "weight": 1.0,
    },
    "Agent Framework": {
        "keywords": [
            "agent framework", "build agents", "create agents", "agent development",
            "agent sdk", "agent library", "multi-agent", "agent orchestration",
            "langchain", "langgraph", "crewai", "autogen", "semantic kernel",
            "agent toolkit", "agent builder", "agentic framework", "llm agent",
            "agent workflow", "agno", "camel", "openai agents",
        ],
        "weight": 1.0,
    },
    "Workflow Orchestration": {
        "keywords": [
            "workflow", "orchestration", "automation platform", "low-code", "no-code",
            "dify", "n8n", "flowise", "langflow", "activepieces", "workflow automation",
            "visual builder", "drag and drop", "flow builder", "pipeline orchestration",
            "workflow engine", "process automation",
        ],
        "weight": 0.9,
    },
    "LLM Inference": {
        "keywords": [
            "llm inference", "model serving", "inference server", "vllm", "ollama",
            "llama.cpp", "tensorrt", "text generation inference", "tgi", "inference engine",
            "model deployment", "llm serving", "gpu inference", "optimized inference",
            "inference optimization", "sglang", "triton inference", "bentoml",
            "ramalama", "dynamo", "gpustack", "xinference",
        ],
        "weight": 1.0,
    },
    "Model Training & Fine-tuning": {
        "keywords": [
            "fine-tuning", "model training", "training framework", "llm training",
            "deep learning framework", "pytorch", "tensorflow", "jax", "paddle",
            "deepspeed", "megatron", "nemo", "colossalai", "unsloth", "swift",
            "llama factory", "openrlhf", "verl", "areal", "flash attention",
            "model optimization", "quantization", "distillation",
        ],
        "weight": 0.9,
    },
    "Vector Database & RAG": {
        "keywords": [
            "vector database", "vector search", "embedding", "rag", "retrieval augmented",
            "milvus", "chroma", "weaviate", "qdrant", "lancedb", "pgvector",
            "semantic search", "document retrieval", "knowledge retrieval",
            "ragflow", "anything-llm", "fastgpt", "docling",
        ],
        "weight": 0.9,
    },
    "Memory & Knowledge": {
        "keywords": [
            "memory", "knowledge base", "memory system", "agent memory",
            "mem0", "memgpt", "letta", "second-me", "claude-mem",
            "long-term memory", "conversation memory", "context management",
            "knowledge management", "memory layer",
        ],
        "weight": 0.9,
    },
    "MCP (Model Context Protocol)": {
        "keywords": [
            "mcp", "model context protocol", "mcp server", "mcp client",
            "context protocol", "mcp tools", "mcp integration",
        ],
        "weight": 1.0,
    },
    "Browser Agent": {
        "keywords": [
            "browser agent", "web agent", "browser automation", "web browsing",
            "browser-use", "playwright", "selenium", "puppeteer", "web interaction",
            "browser control", "web scraping agent", "omniparser",
        ],
        "weight": 1.0,
    },
    "Chat UI & Frontend": {
        "keywords": [
            "chat ui", "chat interface", "chatbot ui", "web ui", "frontend",
            "open-webui", "chatbox", "nextchat", "cherry studio", "lobe chat",
            "siyuan", "silly tavern", "text-generation-webui", "chat frontend",
            "conversation ui",
        ],
        "weight": 0.8,
    },
    "Observability & Evaluation": {
        "keywords": [
            "observability", "monitoring", "evaluation", "llm evaluation", "tracing",
            "langfuse", "wandb", "phoenix", "opik", "mlflow", "promptfoo",
            "opencompass", "model evaluation", "prompt evaluation", "llm monitoring",
            "agent evaluation", "benchmark",
        ],
        "weight": 0.9,
    },
    "LLM Gateway & Proxy": {
        "keywords": [
            "llm gateway", "api gateway", "proxy", "litellm", "one-api",
            "ai gateway", "model proxy", "api proxy", "unified api",
            "llm api", "model routing", "load balancing",
        ],
        "weight": 1.0,
    },
    "Data Processing & ETL": {
        "keywords": [
            "data processing", "etl", "data pipeline", "airflow", "dagster",
            "prefect", "airbyte", "dbt", "data orchestration", "data integration",
            "unstructured", "document processing", "data extraction",
            "apache spark", "dask", "datachain",
        ],
        "weight": 0.7,
    },
    "Data Lake & Storage": {
        "keywords": [
            "data lake", "data warehouse", "iceberg", "delta lake", "hudi",
            "paimon", "gravitino", "openmetadata", "datahub", "data catalog",
            "table format", "apache iceberg",
        ],
        "weight": 0.7,
    },
    "Robotics & Embodied AI": {
        "keywords": [
            "robotics", "embodied ai", "robot", "lerobot", "genesis",
            "robot learning", "manipulation", "robotic arm", "embodied agent",
        ],
        "weight": 1.0,
    },
    "Multi-Agent System": {
        "keywords": [
            "multi-agent", "multi agent", "agent team", "agent collaboration",
            "crewai", "autogen", "metagpt", "openmanus", "agent swarm",
            "hierarchical agent", "agent coordination",
        ],
        "weight": 1.0,
    },
    "Search & Information Retrieval": {
        "keywords": [
            "search engine", "information retrieval", "perplexica", "searxng",
            "web search", "search api", "knowledge search",
        ],
        "weight": 0.9,
    },
    "Tool & Integration Platform": {
        "keywords": [
            "tool integration", "api integration", "composio", "daytona",
            "integration platform", "tool calling", "function calling",
            "agent tools", "mcp servers",
        ],
        "weight": 0.9,
    },
    "Speech & Voice AI": {
        "keywords": [
            "speech", "voice", "audio", "tts", "stt", "speech recognition",
            "livekit", "pipecat", "voice agent", "audio processing",
        ],
        "weight": 1.0,
    },
    "Image & Video Generation": {
        "keywords": [
            "image generation", "video generation", "stable diffusion", "comfyui",
            "diffusion model", "image synthesis", "generative art",
            "automatic1111", "sdxl", "flux",
        ],
        "weight": 1.0,
    },
    "Notebook & Development Environment": {
        "keywords": [
            "notebook", "jupyter", "marimo", "development environment",
            "ide", "code environment", "interactive computing",
        ],
        "weight": 0.8,
    },
    "AI Infrastructure & Platform": {
        "keywords": [
            "ai infrastructure", "ml platform", "kubernetes", "ray", "spark",
            "distributed computing", "gpu management", "volcano", "1panel",
            "coder", "dev environment", "cloud native",
        ],
        "weight": 0.7,
    },
    "LLM SDK & Library": {
        "keywords": [
            "sdk", "library", "client library", "llm sdk", "python sdk",
            "typescript sdk", "api client", "vercel ai", "llamaindex",
            "haystack", "dspy",
        ],
        "weight": 0.8,
    },
    "GraphRAG & Knowledge Graph": {
        "keywords": [
            "graphrag", "knowledge graph", "graph rag", "neo4j", "graph database",
            "entity extraction", "relationship extraction",
        ],
        "weight": 1.0,
    },
    "Deep Learning Core": {
        "keywords": [
            "deep learning", "neural network", "pytorch", "tensorflow", "jax",
            "paddle", "keras", "onnx", "mlx", "triton", "cuda", "nccl",
            "flashinfer", "cutlass", "transformer engine",
        ],
        "weight": 0.6,
    },
    "Hardware & Edge AI": {
        "keywords": [
            "edge ai", "embedded ai", "esp32", "xiaozhi", "on-device",
            "mobile ai", "iot ai", "edge computing",
        ],
        "weight": 1.0,
    },
    "A2A Protocol": {
        "keywords": [
            "a2a", "agent-to-agent", "agent communication", "agent protocol",
        ],
        "weight": 1.0,
    },
    "Autonomous Agent": {
        "keywords": [
            "autonomous agent", "autogpt", "autonomous ai", "self-driving agent",
            "autonomous system", "agent autonomy",
        ],
        "weight": 1.0,
    },
    "API & Backend Service": {
        "keywords": [
            "api server", "backend", "rest api", "graphql", "fastapi",
            "supabase", "elasticsearch", "opensearch", "vespa",
        ],
        "weight": 0.6,
    },
}

def classify_project(proj):
    """Classify a project based on its content against TAXONOMY."""
    text = f"{proj.get('description', '')} {proj.get('topics', '')} {proj.get('readme', '')[:10000]}".lower()

    scores = {}
    for category, config in TAXONOMY.items():
        score = 0
        for keyword in config["keywords"]:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text))
            if matches > 0:
                score += matches * config["weight"]
        if score > 0:
            scores[category] = score

    sorted_categories = sorted(scores.items(), key=lambda x: -x[1])
    return [cat for cat, score in sorted_categories if score > 0.5]

# ── Markdown helpers ────────────────────────────────────────────────────
def md_cell(text, max_len=50):
    """Sanitize text for a markdown table cell: escape pipes, truncate."""
    s = str(text) if text else ""
    s = s.replace("|", "│")
    if len(s) > max_len:
        s = s[:max_len] + "..."
    return s

# ── OpenRank Sparkline ─────────────────────────────────────────────────
def generate_sparkline(trend_dict, trend_months):
    """Generate ASCII sparkline from OpenRank trend data."""
    if not trend_dict or not trend_months:
        return "—"

    # Get values in order, handle missing months
    values = []
    for month in trend_months:
        if month in trend_dict:
            values.append(trend_dict[month])

    if len(values) < 2:
        return "—"

    # Map values to sparkline characters
    chars = "▁▂▃▄▅▆▇█"
    min_val, max_val = min(values), max(values)

    if min_val == max_val:
        return chars[4] * len(values)

    sparkline = ""
    for v in values:
        idx = int((v - min_val) / (max_val - min_val) * (len(chars) - 1))
        sparkline += chars[idx]

    return sparkline

# ── Recommendation Algorithm ────────────────────────────────────────────
def compute_recommendation_score(project, trend_months):
    """
    Compute a recommendation score for a project.
    OpenRank-dominant weighting:
    - OpenRank growth rate: 50%
    - OpenRank trend slope: 20%
    - Participants (log scaled): 15%
    - Stars (log scaled, with novelty bonus for new projects): 15%
    """
    import math
    from datetime import datetime

    trend = project.get("openrank_trend", {})
    stars = project.get("stars", 0) or 0
    participants = project.get("participants", 0) or 0
    created_at = project.get("created_at", "")

    # Get OpenRank values in order
    values = [trend.get(m, 0) for m in trend_months if m in trend]

    if len(values) < 2 or max(values) == 0:
        # Not enough data, use default score
        return 0.5, {"reason": "数据不足"}

    # OpenRank growth rate (50%)
    or_growth = (values[-1] - values[0]) / (values[0] + 1)

    # OpenRank trend slope (20%) - linear regression slope normalized
    n = len(values)
    if n > 1:
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        or_slope = numerator / denominator if denominator != 0 else 0
        # Normalize slope by average OpenRank
        avg_or = sum(values) / n
        or_slope_normalized = or_slope / (avg_or + 1)
    else:
        or_slope_normalized = 0

    # Participants score (15%) - log scaled
    participants_score = math.log(participants + 1) / math.log(1000 + 1)

    # Stars score with novelty bonus (15%)
    stars_score = math.log(stars + 1) / math.log(100000 + 1)

    # Novelty bonus: projects created within 6 months get 1.5x bonus
    novelty_bonus = 1.0
    if created_at:
        try:
            created_date = datetime.strptime(created_at, "%Y-%m-%d")
            age_months = (datetime.now() - created_date).days / 30
            if age_months < 6:
                novelty_bonus = 1.5
        except:
            pass

    # Compute total score
    score = (
        0.50 * or_growth +
        0.20 * or_slope_normalized +
        0.15 * participants_score +
        0.15 * novelty_bonus * stars_score
    )

    # Build reason
    reasons = []
    if or_growth > 0.5:
        reasons.append(f"OpenRank 增长 {or_growth*100:.0f}%")
    if or_slope_normalized > 0.1:
        reasons.append("趋势陡峭")
    if participants > 100:
        reasons.append(f"社区活跃 ({participants} 参与者)")
    if novelty_bonus > 1:
        reasons.append("新项目")
    if stars > 5000:
        reasons.append(f"高关注 ({stars} stars)")

    reason = ", ".join(reasons[:3]) if reasons else "综合表现良好"

    return score, {"reason": reason}

def generate_recommendations(new_projects, trend_months, top_n=None):
    """
    Generate recommendation list sorted by comprehensive score.
    Returns list of (project, score, reason) tuples.
    """
    scored = []
    for p in new_projects:
        score, meta = compute_recommendation_score(p, trend_months)
        scored.append((p, score, meta["reason"]))

    # Sort by score descending
    scored.sort(key=lambda x: -x[1])

    # Return top N when a report explicitly needs highlighted projects.
    if top_n:
        return scored[:top_n]

    # Dynamic: include all projects with score > 0.5
    return [(p, s, r) for p, s, r in scored if s > 0.5]

# ── Canonical weekly report ────────────────────────────────────────────
def format_stars(stars):
    stars = int(stars or 0)
    return f"{stars/1000:.1f}k" if stars >= 1000 else str(stars)

def format_openrank(project):
    openrank = project.get("openrank_latest", "")
    if isinstance(openrank, (int, float)):
        return f"{openrank:.1f}"
    return str(openrank) if openrank else "-"

def format_openrank_month(project):
    return project.get("openrank_month", "") or "-"

def get_report_archive_path(date_str=None):
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    os.makedirs(REPORT_ARCHIVE_DIR, exist_ok=True)
    return os.path.join(REPORT_ARCHIVE_DIR, f"{date_str}-weekly-agentic-ai-report.md")

def get_project_categories(project):
    categories = project.get("categories", [])
    if isinstance(categories, str):
        categories = [c.strip() for c in categories.split("|") if c.strip()]
    if not categories:
        categories = classify_project(project)
    return categories or ["Other"]

def build_report_context(new_projects, trend_months, recommendations=None):
    """Build structured context used by the canonical report and LLM prompt."""
    recommendations = recommendations or []
    category_counter = Counter()
    for p in new_projects:
        p["categories"] = get_project_categories(p)
        for category in p["categories"]:
            category_counter[category] += 1

    growth_projects = []
    for p in new_projects:
        trend = p.get("openrank_trend", {})
        values = [trend.get(m) for m in trend_months if m in trend]
        valid = [v for v in values if v is not None and v > 0]
        if len(valid) >= 2:
            growth = (valid[-1] - valid[0]) / (valid[0] + 1)
            growth_projects.append({
                "repo_name": p["repo_name"],
                "growth": growth,
                "from": valid[0],
                "to": valid[-1],
            })
    growth_projects.sort(key=lambda item: -item["growth"])

    highlighted = [
        {"project": project, "score": score, "reason": reason}
        for project, score, reason in recommendations[:10]
    ]

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "project_count": len(new_projects),
        "projects": new_projects,
        "trend_months": trend_months,
        "category_counts": category_counter,
        "highlighted": highlighted,
        "fastest_growing": growth_projects[:5],
    }

def project_text_excerpt(project, max_len=500):
    parts = [
        project.get("description", ""),
        project.get("topics", ""),
        project.get("readme", ""),
    ]
    text = "\n".join(part for part in parts if part).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:max_len]

def summarize_trend(project, trend_months):
    trend = project.get("openrank_trend", {})
    values = [
        {"month": month, "openrank": trend[month]}
        for month in trend_months
        if trend.get(month) is not None
    ]
    if len(values) >= 2:
        first = values[0]["openrank"]
        last = values[-1]["openrank"]
        growth = (last - first) / (first + 1)
    else:
        growth = None
    return {
        "latest_month": project.get("openrank_month", ""),
        "latest": project.get("openrank_latest", ""),
        "series": values,
        "growth": growth,
    }

def generate_fallback_trend_insights(context):
    """Generate deterministic trend insight text when LLM generation is unavailable."""
    lines = [
        "> LLM trend analysis unavailable; generated from template fallback.",
        "",
    ]
    top_categories = context["category_counts"].most_common(3)
    if top_categories:
        categories = "、".join(f"{cat}（{count} 个）" for cat, count in top_categories)
        lines.append(f"**项目分布显示 Agentic AI 工程化工具链仍是主线。** 本周 {context['project_count']} 个候选项目中，{categories} 最为集中，说明开发者关注点继续围绕可落地的 agent 开发、编排和工具接入能力展开。")
        lines.append("")

    if context["fastest_growing"]:
        top = context["fastest_growing"][0]
        growth_pct = top["growth"] * 100
        lines.append(f"**OpenRank 增长突出的项目值得优先 review。** {top['repo_name']} 的 OpenRank 从 {top['from']:.1f} 增至 {top['to']:.1f}，增长约 {growth_pct:.0f}%，体现出近期社区互动显著升温。")
        lines.append("")

    if context["highlighted"]:
        names = "、".join(item["project"]["repo_name"] for item in context["highlighted"][:3])
        lines.append(f"**精选项目可作为本周趋势案例。** {names} 在 OpenRank、参与者、star 或新项目信号上表现突出，适合在报告和后续人工 review 中优先关注。")
        lines.append("")

    return "\n".join(lines).strip()

def build_llm_prompt(context):
    """Create an evidence-rich prompt for the trend insight LLM call."""
    top_by_stars = sorted(context["projects"], key=lambda p: p.get("stars", 0) or 0, reverse=True)[:10]
    top_by_participants = sorted(context["projects"], key=lambda p: p.get("participants", 0) or 0, reverse=True)[:10]
    projects_by_name = {p["repo_name"]: p for p in context["projects"]}
    selected_names = []
    for item in context["highlighted"]:
        selected_names.append(item["project"]["repo_name"])
    for item in context["fastest_growing"]:
        selected_names.append(item["repo_name"])
    selected_names.extend(p["repo_name"] for p in top_by_stars)
    selected_names.extend(p["repo_name"] for p in top_by_participants)

    seen = set()
    selected_projects = []
    for name in selected_names:
        if name in seen or name not in projects_by_name:
            continue
        seen.add(name)
        selected_projects.append(projects_by_name[name])
        if len(selected_projects) >= LLM_REPORT_PROJECT_LIMIT:
            break

    payload = {
        "date": context["date"],
        "project_count": context["project_count"],
        "category_counts": dict(context["category_counts"].most_common(12)),
        "fastest_growing": context["fastest_growing"],
        "top_by_stars": [p["repo_name"] for p in top_by_stars],
        "top_by_participants": [p["repo_name"] for p in top_by_participants],
        "projects": [
            {
                "repo_name": p["repo_name"],
                "description": p.get("description", ""),
                "topics": p.get("topics", ""),
                "stars": p.get("stars", 0),
                "language": p.get("language", ""),
                "created_at": p.get("created_at", ""),
                "participants": p.get("participants", 0),
                "categories": p.get("categories", []),
                "openrank": summarize_trend(p, context["trend_months"]),
                "text_excerpt": project_text_excerpt(p),
            }
            for p in selected_projects
        ],
    }
    return (
        "你是开源 AI 生态分析师。请基于下面 JSON 数据生成一份中文深度趋势洞察，"
        "重点不是罗列项目，而是从项目文本、分类分布、OpenRank 趋势、参与者和 star 信号中提炼结构性变化。"
        f"本周共有 {context['project_count']} 个候选项目，JSON 中 projects 是用于深入分析的代表性项目样本。"
        "要求：\n"
        "1. 输出 4-6 个有观点的小节，每节使用 Markdown 三级标题；\n"
        "2. 每节必须引用至少 2 个具体项目名，并尽量引用 OpenRank、参与者、star、创建时间等证据；\n"
        "3. 明确区分真实工程项目、资源/skills/awesome 类项目、协议/工具链/应用层趋势；\n"
        "4. 不要编造未提供的数据；缺失 OpenRank 时直接说明该项目缺少 OpenRank 信号，但可以结合项目文本和 GitHub 信号分析；\n"
        "5. 不要输出候选清单或表格，避免重复 Review Candidates 表。\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
    )

def generate_llm_trend_insights(context):
    """Generate deep trend insights using OpenAI Chat Completions with fallback."""
    if not OPENAI_API_KEY:
        if ALLOW_LLM_FALLBACK:
            return generate_fallback_trend_insights(context), True
        raise RuntimeError("OPENAI_API_KEY is required for weekly trend insights. Set ALLOW_LLM_FALLBACK=1 to allow template fallback.")

    try:
        ensure_no_proxy(host_from_url(OPENAI_BASE_URL))
        resp = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You write concise, evidence-grounded open-source ecosystem analysis in Chinese."},
                    {"role": "user", "content": build_llm_prompt(context)},
                ],
                "temperature": 0.4,
            },
            timeout=OPENAI_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        if not content:
            raise ValueError("empty LLM response")
        return content, False
    except Exception as e:
        print(f"{YELLOW}LLM trend generation failed: {e}{RESET}")
        if ALLOW_LLM_FALLBACK:
            return generate_fallback_trend_insights(context), True
        raise

def generate_tldr(context):
    lines = [
        f"本周发现 **{context['project_count']}** 个新的 Agentic AI 候选项目。",
    ]
    if context["category_counts"]:
        top_categories = ", ".join(f"{cat} ({count})" for cat, count in context["category_counts"].most_common(3))
        lines.append(f"热门方向集中在：{top_categories}。")
    if context["highlighted"]:
        top = context["highlighted"][0]
        lines.append(f"优先关注：{top['project']['repo_name']} - {top['reason']}。")
    if context["fastest_growing"]:
        fastest = context["fastest_growing"][0]
        lines.append(f"OpenRank 增速最快：{fastest['repo_name']}，约 {fastest['growth']*100:.0f}% 增长。")
    return lines

def generate_review_candidates_table(projects, trend_months):
    rows = [
        "| # | Repo | Description | Topics | Stars | Created | Latest OpenRank | OpenRank Month | Trend | Participants | Language | Categories |",
        "|---|------|-------------|--------|-------|---------|-----------------|----------------|-------|--------------|----------|------------|",
    ]
    for i, p in enumerate(projects, 1):
        desc = md_cell(p.get("description", ""), 70)
        topics = md_cell(p.get("topics", ""), 50)
        created = p.get("created_at", "-")[:10] if p.get("created_at") else "-"
        trend = generate_sparkline(p.get("openrank_trend", {}), trend_months)
        participants = p.get("participants", 0)
        lang = p.get("language", "-") or "-"
        categories = md_cell(", ".join(get_project_categories(p)[:3]), 70)
        rows.append(
            f"| {i} | [{p['repo_name']}](https://github.com/{p['repo_name']}) | {desc} | {topics} | {format_stars(p.get('stars', 0))} | {created} | {format_openrank(p)} | {format_openrank_month(p)} | {trend} | {participants} | {lang} | {categories} |"
        )
    return "\n".join(rows)

def compose_canonical_report(context, trend_insights, fallback_used=False):
    date_str = context["date"]
    lines = [
        f"# Agentic AI Weekly Report - {date_str}",
        "",
        "## TL;DR",
        "",
    ]
    lines.extend(f"- {item}" for item in generate_tldr(context))
    lines.extend(["", "## Deep Trend Insights", "", trend_insights, ""])

    if fallback_used:
        lines.extend(["", "_Trend insights were generated by deterministic fallback because LLM generation was unavailable._", ""])

    lines.extend([
        "## Highlighted Projects",
        "",
    ])
    if context["highlighted"]:
        for i, item in enumerate(context["highlighted"][:10], 1):
            p = item["project"]
            lines.extend([
                f"### {i}. [{p['repo_name']}](https://github.com/{p['repo_name']})",
                "",
                f"- Stars: {format_stars(p.get('stars', 0))}",
                f"- Language: {p.get('language', '-') or '-'}",
                f"- Latest OpenRank: {format_openrank(p)} ({format_openrank_month(p)})",
                f"- OpenRank trend: {generate_sparkline(p.get('openrank_trend', {}), context['trend_months'])}",
                f"- Participants: {p.get('participants', 0)}",
                f"- Reason: {item['reason']}",
                "",
            ])
    else:
        lines.extend(["No highlighted projects met the recommendation threshold.", ""])

    lines.extend([
        "## Review Candidates",
        "",
        generate_review_candidates_table(context["projects"], context["trend_months"]),
        "",
        "---",
        "*Generated by weekly_update.py*",
        "",
    ])
    return "\n".join(lines)

def generate_canonical_report(new_projects, trend_months=None, recommendations=None, date_str=None):
    """Generate, archive, and latest-copy the single weekly report source of truth."""
    trend_months = trend_months or []
    context = build_report_context(new_projects, trend_months, recommendations)
    if date_str:
        context["date"] = date_str
    trend_insights, fallback_used = generate_llm_trend_insights(context)
    report = compose_canonical_report(context, trend_insights, fallback_used=fallback_used)

    archive_path = get_report_archive_path(context["date"])
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(report)
    shutil.copyfile(archive_path, REPORT_FILE)

    print(f"{CYAN}Weekly report archived to {archive_path}{RESET}")
    print(f"{CYAN}Latest weekly report copied to {REPORT_FILE}{RESET}")
    return report, archive_path, context

# ── Trend context for LLM analysis ─────────────────────────────────────
TREND_CONTEXT_FILE = os.path.join(BASE, "data", "trend_context.md")

def generate_trend_context(new_projects, trend_months, recommendations=None):
    """Generate a structured data summary for Claude session to produce trend analysis."""
    from collections import Counter

    ctx = "# 本周趋势分析数据\n\n"
    ctx += f"## 概览\n\n"
    ctx += f"- 新增项目：{len(new_projects)} 个\n"

    # Category distribution
    cat_counter = Counter()
    cat_projects = {}  # category -> list of (stars, repo_name, desc)
    for p in new_projects:
        cats = p.get("categories", [])
        if isinstance(cats, str):
            cats = [c.strip() for c in cats.split("|") if c.strip()]
        if not cats:
            cats = classify_project(p)
        for c in cats:
            cat_counter[c] += 1
            if c not in cat_projects:
                cat_projects[c] = []
            stars = p.get("stars", 0) or 0
            cat_projects[c].append((stars, p["repo_name"], p.get("description", "") or ""))

    ctx += f"- 覆盖分类：{len(cat_counter)} 个\n\n"

    ctx += "## 分类分布\n\n"
    ctx += "| 分类 | 项目数 | 代表项目 |\n"
    ctx += "|------|--------|----------|\n"
    for cat, count in cat_counter.most_common():
        top_in_cat = sorted(cat_projects.get(cat, []), key=lambda x: -x[0])[:2]
        reps = ", ".join(r[1] for r in top_in_cat)
        ctx += f"| {cat} | {count} | {reps} |\n"
    ctx += "\n"

    # Top recommendations with full detail
    if recommendations:
        ctx += "## Top 5 推荐（用于案例引用）\n\n"
        for i, (p, score, reason) in enumerate(recommendations[:5], 1):
            stars = p.get("stars", 0) or 0
            stars_str = f"{stars/1000:.1f}k" if stars >= 1000 else str(stars)
            cats = p.get("categories", [])
            if isinstance(cats, str):
                cats = [c.strip() for c in cats.split("|") if c.strip()]
            cats_str = ", ".join(cats[:3]) if cats else "未分类"

            ctx += f"### {i}. [{p['repo_name']}](https://github.com/{p['repo_name']}) ⭐{stars_str}\n"
            ctx += f"- 描述：{p.get('description', '')}\n"
            ctx += f"- 分类：{cats_str}\n"

            trend = p.get("openrank_trend", {})
            or_latest = p.get("openrank_latest", "")
            if trend:
                values = [trend.get(m) for m in trend_months if m in trend]
                valid = [v for v in values if v is not None and v > 0]
                if len(valid) >= 2:
                    growth_pct = (valid[-1] - valid[0]) / (valid[0] + 1) * 100
                    ctx += f"- OpenRank 趋势：{valid[0]:.1f} → {valid[-1]:.1f} (增长 {growth_pct:.0f}%)\n"
                elif or_latest:
                    ctx += f"- OpenRank：{or_latest:.1f}\n"
            elif or_latest:
                ctx += f"- OpenRank：{or_latest:.1f}\n"

            participants = p.get("participants", 0)
            if participants:
                ctx += f"- 参与者：{participants}\n"
            ctx += f"- 推荐理由：{reason}\n\n"

    # Data highlights
    ctx += "## 数据亮点\n\n"

    # Fastest growing
    growth_list = []
    for p in new_projects:
        trend = p.get("openrank_trend", {})
        values = [trend.get(m) for m in trend_months if m in trend]
        valid = [v for v in values if v is not None and v > 0]
        if len(valid) >= 2:
            growth = (valid[-1] - valid[0]) / (valid[0] + 1)
            growth_list.append((p["repo_name"], growth, valid[0], valid[-1]))
    if growth_list:
        growth_list.sort(key=lambda x: -x[1])
        ctx += "### 增速最快\n\n"
        for name, g, v0, v1 in growth_list[:3]:
            ctx += f"- **{name}**：OpenRank {v0:.1f} → {v1:.1f} (增长 {g*100:.0f}%)\n"
        ctx += "\n"

    # Most participants
    part_list = [(p["repo_name"], p.get("participants", 0) or 0) for p in new_projects]
    part_list.sort(key=lambda x: -x[1])
    if part_list and part_list[0][1] > 0:
        ctx += "### 参与者最多\n\n"
        for name, cnt in part_list[:3]:
            ctx += f"- **{name}**：{cnt} 位参与者\n"
        ctx += "\n"

    # Highest stars among young projects (< 6 months)
    from datetime import datetime
    young = []
    for p in new_projects:
        created = p.get("created_at", "")
        stars = p.get("stars", 0) or 0
        if created and stars >= 1000:
            try:
                age_days = (datetime.now() - datetime.strptime(created, "%Y-%m-%d")).days
                if age_days < 180:
                    young.append((p["repo_name"], stars, created[:7]))
            except ValueError:
                pass
    if young:
        young.sort(key=lambda x: -x[1])
        ctx += "### 新锐高星项目（6 个月内创建）\n\n"
        for name, s, c in young[:3]:
            s_str = f"{s/1000:.1f}k" if s >= 1000 else str(s)
            ctx += f"- **{name}** ⭐{s_str} (创建于 {c})\n"
        ctx += "\n"

    # Write to file
    with open(TREND_CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(ctx)
    print(f"{CYAN}Trend context saved to {TREND_CONTEXT_FILE}{RESET}")

# ── Yuque / DingTalk / PR publishing ───────────────────────────────────
def publish_to_yuque(report_markdown, date_str=None):
    """Publish full canonical report to Yuque. Returns the document URL, or None on failure."""
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    title = f"Agentic 每周推送 {date_str}"
    slug = f"agentic-weekly-{date_str}"
    payload = {
        "book_id": YUQUE_BOOK_ID,
        "namespace": YUQUE_NAMESPACE,
        "parent_url": YUQUE_PARENT_URL,
        "parent_slug": YUQUE_PARENT_SLUG,
        "parent_title": YUQUE_PARENT_TITLE,
        "parent_uuid": YUQUE_PARENT_UUID,
        "parent_node_uuid": YUQUE_PARENT_NODE_UUID,
        "public": YUQUE_DOC_PUBLIC,
        "title": title,
        "slug": slug,
        "date": date_str,
        "body": report_markdown,
    }

    if YUQUE_PUBLISH_COMMAND:
        try:
            result = subprocess.run(
                shlex.split(YUQUE_PUBLISH_COMMAND),
                input=json.dumps(payload, ensure_ascii=False),
                capture_output=True,
                text=True,
                check=True,
            )
            output = result.stdout.strip()
            try:
                data = json.loads(output)
                url = data.get("url") or data.get("doc_url") or data.get("web_url")
            except json.JSONDecodeError:
                url = output
            if url:
                url = normalize_yuque_url(url)
                print(f"{GREEN}Yuque published: {url}{RESET}")
                return url
        except Exception as e:
            print(f"{RED}Yuque publish command failed: {e}{RESET}")
            return None

    if not YUQUE_API_TOKEN:
        print(f"{YELLOW}No Yuque publisher configured; skipping Yuque publish{RESET}")
        return None

    try:
        resp = requests.post(
            f"{YUQUE_API_BASE}/repos/{YUQUE_BOOK_ID}/docs",
            headers={
                "X-Auth-Token": YUQUE_API_TOKEN,
                "Content-Type": "application/json",
            },
            json={
                "title": title,
                "slug": slug,
                "body": report_markdown,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json().get("data", resp.json())
        url = data.get("url") or data.get("web_url") or data.get("link")
        if not url and data.get("slug"):
            url = f"https://www.yuque.com/{YUQUE_BOOK_ID}/{data['slug']}"
        url = normalize_yuque_url(url) if url else url
        print(f"{GREEN}Yuque published: {url or title}{RESET}")
        return url
    except Exception as e:
        print(f"{RED}Yuque publish failed: {e}{RESET}")
        return None

def normalize_yuque_url(url):
    """Normalize Yuque MCP relative paths into clickable absolute URLs."""
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return f"{YUQUE_WEB_BASE}{url}"
    return url

def extract_trend_opinions(report_markdown, max_sentences=3):
    """Extract two to three concise trend sentences from the generated report."""
    if not report_markdown:
        return []
    def tldr_fallback():
        tldr = re.search(r"## TL;DR\n\n(.+?)(?:\n## |\Z)", report_markdown, re.S)
        if not tldr:
            return []
        fallback = []
        for line in tldr.group(1).splitlines():
            line = line.strip()
            if not line.startswith("- "):
                continue
            sentence = re.sub(r"\*\*([^*]+)\*\*", r"\1", line[2:]).strip()
            if sentence:
                fallback.append(sentence)
            if len(fallback) >= max_sentences:
                break
        return fallback

    match = re.search(r"## Deep Trend Insights\n\n(.+?)(?:\n## |\Z)", report_markdown, re.S)
    if not match:
        return tldr_fallback()
    text = match.group(1)
    text = re.sub(r"^### .*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[。！？])\s*", text)
    opinions = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 24:
            continue
        opinions.append(sentence)
        if len(opinions) >= max_sentences:
            break
    if opinions:
        return opinions

    return tldr_fallback()

def build_dingtalk_markdown(projects, recommendations, yuque_url, pr_url, date_str=None, report_markdown=None):
    """Build concise DingTalk markdown. Requires Yuque and PR URLs."""
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    trend_opinions = extract_trend_opinions(report_markdown)
    lines = [
        "## Agentic AI Weekly Update",
        "",
        f"**{date_str}** 本周发现 **{len(projects)}** 个候选项目。",
        "",
    ]
    if trend_opinions:
        lines.append("**趋势观点**")
        for opinion in trend_opinions[:3]:
            lines.append(f"- {opinion}")
        lines.append("")
    if recommendations:
        lines.append("**值得关注的项目**")
        for p, score, reason in recommendations[:5]:
            lines.append(f"- **{p['repo_name']}** - {reason}")
        lines.append("")
    lines.extend([
        f"[完整报告]({normalize_yuque_url(yuque_url)})",
        "",
        f"[待筛选 PR]({pr_url})",
    ])
    return "\n".join(lines)

def send_dingtalk(projects, recommendations, yuque_url, pr_url, report_markdown=None):
    """Send DingTalk notification after both Yuque and PR URLs are available."""
    if not yuque_url or not pr_url:
        print(f"{YELLOW}Skipping DingTalk: Yuque URL and PR URL are both required{RESET}")
        return False
    if not DINGTALK_WEBHOOK:
        print(f"{YELLOW}No DingTalk webhook configured, skipping notification{RESET}")
        return False

    md_msg = build_dingtalk_markdown(projects, recommendations, yuque_url, pr_url, report_markdown=report_markdown)
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "Weekly Agentic AI Update",
            "text": md_msg,
        },
    }

    url = DINGTALK_WEBHOOK
    ensure_no_proxy(host_from_url(url))
    if DINGTALK_SECRET:
        timestamp = str(round(time.time() * 1000))
        secret_enc = DINGTALK_SECRET.encode("utf-8")
        string_to_sign = f"{timestamp}\n{DINGTALK_SECRET}"
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = f"{DINGTALK_WEBHOOK}&timestamp={timestamp}&sign={sign}"

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("errcode") == 0:
                print(f"{GREEN}DingTalk notification sent!{RESET}")
                return True
            print(f"{RED}DingTalk error: {result.get('errmsg')}{RESET}")
        else:
            print(f"{RED}DingTalk HTTP error: {resp.status_code}{RESET}")
    except Exception as e:
        print(f"{RED}Failed to send DingTalk: {e}{RESET}")
    return False

def parse_report_date(report_markdown):
    match = re.search(r"^# Agentic AI Weekly Report - ([0-9]{4}-[0-9]{2}-[0-9]{2})", report_markdown, re.MULTILINE)
    return match.group(1) if match else datetime.now().strftime("%Y-%m-%d")

def parse_report_candidates(report_markdown):
    """Parse repo names from the Review Candidates table in a generated report."""
    projects = []
    for line in report_markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        match = re.search(r"\|\s*\d+\s*\|\s*\[([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]\(", line)
        if match:
            projects.append({"repo_name": match.group(1)})
    return projects

def parse_report_highlights(report_markdown):
    """Parse highlighted projects and reasons for concise DingTalk content."""
    highlights = []
    current = None
    in_section = False
    for line in report_markdown.splitlines():
        if line.startswith("## Highlighted Projects"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        heading = re.match(r"^###\s+\d+\.\s+\[([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]\(", line)
        if heading:
            current = {"repo_name": heading.group(1)}
            highlights.append((current, 0, "重点推荐"))
            continue
        if current and line.startswith("- Reason:"):
            highlights[-1] = (current, 0, line.replace("- Reason:", "", 1).strip() or "重点推荐")
    return highlights

def build_pr_body(projects, report_markdown, date_str=None):
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    checklist = "\n".join(f"- [ ] {p['repo_name']}" for p in projects)
    return "\n".join([
        f"# Weekly Agentic AI Review - {date_str}",
        "",
        "## Review Checklist",
        "",
        "<!-- agentic-review-checklist:start -->",
        checklist,
        "<!-- agentic-review-checklist:end -->",
        "",
        "---",
        "",
        "## Full Weekly Report",
        "",
        report_markdown,
    ])

# ── GitHub PR creation ────────────────────────────────────────────────
def create_pr(projects, report_markdown, report_path):
    """Create a GitHub PR with checklist for project selection."""
    date_str = datetime.now().strftime('%Y-%m-%d')
    branch_name = f"weekly/{date_str}"
    existing_branch = subprocess.run(
        ["git", "branch", "--list", branch_name],
        capture_output=True, text=True
    ).stdout.strip()
    if existing_branch:
        branch_name = f"weekly/{date_str}-{datetime.now().strftime('%H%M%S')}"
    body = build_pr_body(projects, report_markdown, date_str=date_str)
    if len(body) > 60000:
        print(f"{RED}PR body is too long ({len(body)} chars). Shorten report before creating PR.{RESET}")
        return None

    try:
        # Create branch and commit report
        subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
        add_paths = [REPORT_FILE]
        if report_path and os.path.abspath(report_path) != os.path.abspath(REPORT_FILE):
            add_paths.append(report_path)
        subprocess.run(["git", "add", *add_paths], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Weekly update {date_str}: {len(projects)} new projects"],
                       check=True, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, capture_output=True)

        # Determine fork owner from origin remote
        remote_url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        # Extract owner from git@github.com:owner/repo.git or https://github.com/owner/repo.git
        owner_match = re.search(r'[:/]([^/]+)/', remote_url)
        fork_owner = owner_match.group(1) if owner_match else "xiaoya-yaya"

        result = subprocess.run(
            ["gh", "pr", "create",
             "--repo", PR_TARGET_REPO,
             "--head", f"{fork_owner}:{branch_name}",
             "--title", f"Weekly update {date_str}: {len(projects)} new projects",
             "--body", body],
            capture_output=True, text=True, check=True
        )
        pr_url = result.stdout.strip()
        print(f"{GREEN}PR created: {pr_url}{RESET}")

        # Switch back to main
        subprocess.run(["git", "checkout", "main"], capture_output=True)

        return pr_url
    except FileNotFoundError:
        print(f"{YELLOW}gh CLI not found. Skipping PR creation.{RESET}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"{YELLOW}PR creation failed: {e.stderr[:200] if e.stderr else e}{RESET}")
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        return None

def publish_existing_report(report_path=None):
    """Publish an already generated report without re-running data collection or LLM generation."""
    report_path = report_path or REPORT_FILE
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Report not found: {report_path}")
    with open(report_path, "r", encoding="utf-8") as f:
        report_markdown = f.read()

    projects = parse_report_candidates(report_markdown)
    if not projects:
        raise ValueError(f"No Review Candidates table rows found in {report_path}")
    recommendations = parse_report_highlights(report_markdown)
    date_str = parse_report_date(report_markdown)

    print(f"{CYAN}Publishing existing report: {report_path}{RESET}")
    print(f"{CYAN}Parsed {len(projects)} review candidates and {len(recommendations)} highlighted projects{RESET}")

    print(f"\n{BOLD}=== Publish existing: Yuque ==={RESET}")
    yuque_url = publish_to_yuque(report_markdown, date_str=date_str)

    print(f"\n{BOLD}=== Publish existing: GitHub review PR ==={RESET}")
    pr_url = create_pr(projects, report_markdown, report_path)

    print(f"\n{BOLD}=== Publish existing: DingTalk summary ==={RESET}")
    send_dingtalk(projects, recommendations, yuque_url, pr_url, report_markdown=report_markdown)

    print(f"\n{GREEN}Publish existing complete!{RESET}")

# ── Post-merge: parse PR and update CSV ────────────────────────────────

def parse_pr_checklist(pr_body):
    """Parse checked/unchecked items from PR body (table-embedded or list checkboxes).
    Returns list of (repo_name, checked)."""
    items = []
    for line in pr_body.split("\n"):
        line = line.strip()
        # Table row with checkbox: | - [x] | **repo** | ... | or | - [ ] | **repo** | ... |
        if line.startswith("|") and ("- [x]" in line or "- [ ]" in line):
            checked = "- [x]" in line
            match = re.search(r'\*\*([^*]+)\*\*', line)
            if match:
                items.append((match.group(1), checked))
            continue
        # Fallback: list-style checkbox: - [x] **repo** or - [ ] **repo**
        if line.startswith("- [x]") or line.startswith("- [ ]"):
            checked = line.startswith("- [x]")
            match = re.search(r'\*\*([^*]+)\*\*', line)
            if match:
                items.append((match.group(1), checked))
                continue
            match = re.search(r'- \[[x ]\]\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)', line)
            if match:
                items.append((match.group(1), checked))
    return items

def find_merged_pr():
    """Find the most recently merged weekly PR."""
    try:
        # List all merged PRs and filter for weekly/ branches
        result = subprocess.run(
            ["gh", "pr", "list", "--state", "merged",
             "--json", "number,title,body,url,headRefName", "--limit", "10"],
            capture_output=True, text=True, check=True
        )
        prs = json.loads(result.stdout)
        # Filter for weekly/ branch prefix
        weekly_prs = [p for p in prs if p.get("headRefName", "").startswith("weekly/")]
        if not weekly_prs:
            return None
        return weekly_prs[0]
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None

def fetch_upstream_pr(pr_number):
    """Fetch one explicit upstream PR. Post-merge intentionally does not auto-discover PRs."""
    try:
        result = subprocess.run(
            [
                "gh", "pr", "view", str(pr_number),
                "--repo", PR_TARGET_REPO,
                "--json", "number,title,body,url,headRefName,state,mergedAt",
            ],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        print(f"{RED}gh CLI not found. Cannot fetch upstream PR.{RESET}")
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"{RED}Could not fetch upstream PR #{pr_number}: {e}{RESET}")
        return None

def update_csv_with_projects(selected_projects):
    """Add selected projects to CSV."""
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        existing_rows = list(reader)

    added = 0
    for p in selected_projects:
        if any(r.get("repo_name") == p["repo_name"] for r in existing_rows):
            continue
        row = {
            "repo_id": p.get("repo_id", ""),
            "repo_name": p["repo_name"],
            "description": p.get("description", ""),
            "stars": p.get("stars", 0),
            "openrank_latest": p.get("openrank_latest", ""),
            "openrank_trend": (
                "|".join(f"{month}:{value}" for month, value in p.get("openrank_trend", {}).items())
                if isinstance(p.get("openrank_trend"), dict)
                else p.get("openrank_trend", "")
            ),
            "language": p.get("language", ""),
            "created_at": p.get("created_at", ""),
            "topics": p.get("topics", ""),
            "categories": "|".join(p.get("categories", [])) if isinstance(p.get("categories"), list) else "",
        }
        # Set openrank fields from whichever columns exist
        for fn in fieldnames:
            if fn not in row:
                row[fn] = ""
        existing_rows.append(row)
        added += 1

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(existing_rows)

    return added

def fetch_project_records_for_repos(repo_names):
    """Build CSV-ready project records from explicit repo names."""
    records = []
    for i, repo_name in enumerate(repo_names, 1):
        print(f"  [{i}/{len(repo_names)}] Fetching {repo_name}...", end=" ")
        info = fetch_github_info(repo_name)
        if not info:
            print(f"{YELLOW}skip: GitHub info unavailable{RESET}")
            continue
        readme = fetch_github_readme(repo_name)
        project = {**info, "repo_name": repo_name, "readme": readme}
        project["categories"] = classify_project(project) or ["Other"]
        records.append(project)
        print(f"{GREEN}{'|'.join(project['categories'])[:50]}{RESET}")

    openrank_data = fetch_openrank_data([p["repo_name"] for p in records])
    for project in records:
        or_data = openrank_data.get(project["repo_name"], {})
        project["openrank_latest"] = or_data.get("latest", "")
        project["openrank_trend"] = or_data.get("trend", {})

    return records

# ── Taxonomy evolution ─────────────────────────────────────────────────
def reclassify_projects(project_list):
    """Reclassify a list of projects using current TAXONOMY. Updates categories in-place."""
    for p in project_list:
        categories = classify_project(p)
        p["categories"] = categories if categories else ["Other"]
    return project_list

def analyze_taxonomy_coverage(all_projects):
    """Analyze keyword coverage and suggest new taxonomy categories."""
    # Collect keywords from unclassified/Other projects
    other_projects = [p for p in all_projects if "Other" in p.get("categories", [])]

    if not other_projects:
        total = len(all_projects)
        covered = total - len(other_projects)
        pct = (covered / total * 100) if total > 0 else 100
        print(f"\n{GREEN}Taxonomy coverage: {pct:.1f}% — no new category suggestions{RESET}")
        return

    # Extract potential keywords from Other projects
    from collections import Counter
    keyword_counter = Counter()
    for p in other_projects:
        text = f"{p.get('description', '')} {p.get('topics', '')}".lower()
        words = re.findall(r'\b[a-z][a-z-]+[a-z]\b', text)
        keyword_counter.update(words)

    # Check which high-frequency words are NOT covered by existing taxonomy
    existing_kw = set()
    for config in TAXONOMY.values():
        existing_kw.update(kw.lower() for kw in config["keywords"])

    uncovered = {kw: count for kw, count in keyword_counter.most_common(50)
                 if kw not in existing_kw and count >= 2 and len(kw) > 3}

    total = len(all_projects)
    covered = total - len(other_projects)
    pct = (covered / total * 100) if total > 0 else 100
    print(f"\n{CYAN}=== Taxonomy Coverage ==={RESET}")
    print(f"Coverage: {pct:.1f}% ({covered}/{total} projects classified)")
    print(f"Unclassified projects: {len(other_projects)}")

    if uncovered:
        print(f"\n{YELLOW}Suggested new keywords to consider for taxonomy:{RESET}")
        for kw, count in sorted(uncovered.items(), key=lambda x: -x[1])[:10]:
            print(f"  - \"{kw}\" (appears in {count} unclassified projects)")

def fetch_and_reclassify_top100(new_repo_names):
    """Fetch fresh data for top 100 projects + new ones, reclassify all."""
    print(f"\n{BOLD}=== Reclassifying top projects ==={RESET}")

    # Read all projects from CSV
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    # Sort by openrank to get top 100
    def sort_key(row):
        try:
            return float(row.get("openrank_latest", 0) or 0)
        except (ValueError, TypeError):
            return 0

    all_rows.sort(key=sort_key, reverse=True)
    top_rows = all_rows[:100]

    # Add new projects not yet in CSV
    new_rows = []
    for name in new_repo_names:
        if not any(r.get("repo_name") == name for r in all_rows):
            new_rows.append({"repo_name": name})

    to_classify = top_rows + new_rows
    print(f"Reclassifying {len(to_classify)} projects ({len(top_rows)} top + {len(new_rows)} new)")

    # Fetch fresh info for each
    classified_count = 0
    for i, row in enumerate(to_classify):
        repo_name = row.get("repo_name", "")
        if not repo_name:
            continue
        print(f"  [{i+1}/{len(to_classify)}] {repo_name}...", end=" ")
        info = fetch_github_info(repo_name)
        if info:
            readme = fetch_github_readme(repo_name)
            proj = {**row, **info, "readme": readme}
            categories = classify_project(proj)
            row["categories"] = "|".join(categories) if categories else "Other"
            row["description"] = info.get("description", row.get("description", ""))
            row["stars"] = info.get("stars", row.get("stars", 0))
            row["topics"] = info.get("topics", row.get("topics", ""))
            row["language"] = info.get("language", row.get("language", ""))
            classified_count += 1
            print(f"{GREEN}{row['categories'][:40]}{RESET}")
        else:
            print(f"{YELLOW}skip{RESET}")
        time.sleep(0.3)

    # Write updated CSV using existing fieldnames
    fieldnames = list(all_rows[0].keys()) if all_rows else ["repo_id", "repo_name", "description", "stars",
                  "openrank_latest", "openrank_trend", "language",
                  "created_at", "topics", "categories"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"{GREEN}Reclassified {classified_count} projects{RESET}")

    # Taxonomy coverage analysis
    analyze_taxonomy_coverage(all_rows)

# ── Orchestrators ──────────────────────────────────────────────────────
def run_check(full_mode=False, report_only=False):
    """Main --check flow: query, filter, canonical report, Yuque, PR, DingTalk."""
    print(f"\n{BOLD}=== Step 1: Query ClickHouse for top star growth projects ==={RESET}")
    try:
        top_projects = query_top_star_growth_projects(100)
    except Exception as e:
        print(f"{RED}ClickHouse query failed; aborting weekly check: {e}{RESET}")
        raise

    print(f"\n{BOLD}=== Step 2: Fetch GitHub info and filter for agentic projects ==={RESET}")
    existing_projects = load_existing_projects()

    candidate_projects = []
    for i, repo_name in enumerate(top_projects):
        if repo_name in existing_projects:
            continue

        print(f"[{i+1}/{len(top_projects)}] Checking {repo_name}...", end=" ")
        info = fetch_github_info(repo_name)
        if not info:
            print("not found")
            continue

        readme = fetch_github_readme(repo_name)
        if is_agentic_project(info, readme, repo_name):
            text = f"{info.get('description', '')} {info.get('topics', '')} {readme[:5000]}".lower()
            core_matches = [kw for kw in AGENTIC_CORE_KEYWORDS if _word_match(kw, text)]
            general_matches = [kw for kw in ML_GENERAL_KEYWORDS if _word_match(kw, text)]
            info["repo_name"] = repo_name
            info["reason"] = ", ".join((core_matches + general_matches)[:3])
            info["readme"] = readme
            candidate_projects.append(info)
            print(f"{GREEN}✓ Agentic!{RESET}")
        else:
            print(f"{YELLOW}✗ Not agentic{RESET}")

        if not github_token:
            time.sleep(1.5)
        else:
            time.sleep(0.3)

    # Enrich with ClickHouse data
    print(f"\n{BOLD}=== Step 3: Enrich with OpenRank and Participants data ==={RESET}")
    repo_names = [p["repo_name"] for p in candidate_projects]
    openrank_data = fetch_openrank_data(repo_names)
    participants_data = fetch_participants_data(repo_names)

    new_agentic_projects = []
    for p in candidate_projects:
        or_data = openrank_data.get(p["repo_name"], {})
        p["openrank_latest"] = or_data.get("latest", "")
        p["openrank_month"] = or_data.get("latest_month", "")
        p["openrank_trend"] = or_data.get("trend", {})
        p["participants"] = participants_data.get(p["repo_name"], 0)
        new_agentic_projects.append(p)

    print(f"Enriched {len(new_agentic_projects)} projects")

    if not new_agentic_projects:
        print(f"{YELLOW}No new agentic projects this week{RESET}")
        return

    # Generate recommendations
    recommendations = generate_recommendations(new_agentic_projects, trend_months, top_n=5) if len(new_agentic_projects) >= 3 else []

    print(f"\n{BOLD}=== Step 4: Generate canonical weekly report ==={RESET}")
    report_markdown, report_path, report_context = generate_canonical_report(
        new_agentic_projects,
        trend_months,
        recommendations,
    )

    # Keep the structured trend context for debugging and prompt inspection.
    generate_trend_context(new_agentic_projects, trend_months, recommendations)

    if report_only:
        print(f"\n{BOLD}=== Report-only mode: skipping Yuque, GitHub PR, and DingTalk ==={RESET}")
        print(f"{GREEN}Report generated for review: {report_path}{RESET}")
    elif full_mode:
        # Legacy: add all projects directly
        print(f"\n{BOLD}=== Full mode: adding all projects ==={RESET}")
        added = update_csv_with_projects(new_agentic_projects)
        print(f"{GREEN}Added {added} projects to CSV{RESET}")
    else:
        print(f"\n{BOLD}=== Step 5: Publish full report to Yuque ==={RESET}")
        yuque_url = publish_to_yuque(report_markdown, date_str=report_context["date"])

        print(f"\n{BOLD}=== Step 6: Create GitHub review PR ==={RESET}")
        pr_url = create_pr(new_agentic_projects, report_markdown, report_path)

        print(f"\n{BOLD}=== Step 7: Send DingTalk summary ==={RESET}")
        send_dingtalk(new_agentic_projects, recommendations, yuque_url, pr_url, report_markdown=report_markdown)

    print(f"\n{GREEN}Check complete!{RESET}")

def run_post_merge(pr_number):
    """Process a merged PR: update CSV with checked items, reclassify, evolve taxonomy."""
    print(f"\n{BOLD}=== Post-merge: Fetching upstream PR #{pr_number} ==={RESET}")
    pr = fetch_upstream_pr(pr_number)
    if not pr:
        return

    if pr.get("state") != "MERGED" and not pr.get("mergedAt"):
        print(f"{RED}Upstream PR #{pr_number} is not merged yet. Merge it before running --post-merge.{RESET}")
        return

    print(f"Found upstream merged PR: {pr.get('title', '')} — {pr.get('url', '')}")

    # Parse checklist from PR body
    body = pr.get("body", "")
    items = parse_pr_checklist(body)
    if not items:
        print(f"{YELLOW}No checklist items found in PR body{RESET}")
        return

    checked_repos = [name for name, checked in items if checked]
    print(f"Checked: {len(checked_repos)} / {len(items)} projects")

    if not checked_repos:
        print(f"{YELLOW}No projects selected{RESET}")
        return

    selected = fetch_project_records_for_repos(checked_repos)
    print(f"Selected {len(selected)} projects to add")
    if not selected:
        print(f"{YELLOW}No project records could be fetched{RESET}")
        return

    # Update CSV
    added = update_csv_with_projects(selected)
    print(f"{GREEN}Added {added} projects to CSV{RESET}")
    if added == 0:
        print(f"{YELLOW}No new rows were added; skipping top project reclassification{RESET}")
        return

    # Reclassify top 100 + new projects
    new_repo_names = [p["repo_name"] for p in selected]
    fetch_and_reclassify_top100(new_repo_names)

# ── Main workflow ─────────────────────────────────────────────────────
def main():
    print_runtime_context()
    parser = argparse.ArgumentParser(description="Weekly Agentic AI Projects Update")
    parser.add_argument("--check", action="store_true", help="Check new projects, generate report drafts, create PR")
    parser.add_argument("--report-only", action="store_true", help="Generate the weekly report only; do not publish to Yuque, create PR, or send DingTalk")
    parser.add_argument("--no-publish", action="store_true", help="Alias for --report-only")
    parser.add_argument("--publish-existing", action="store_true", help="Publish an existing generated report to Yuque, GitHub PR, and DingTalk without re-running data collection")
    parser.add_argument("--report-path", default=REPORT_FILE, help="Report path for --publish-existing")
    parser.add_argument("--confirm", action="store_true", help="(DEPRECATED) Use PR-based confirmation instead")
    parser.add_argument("--post-merge", action="store_true", help="Process a specified upstream merged PR: update CSV, reclassify, evolve taxonomy")
    parser.add_argument("--pr", type=int, help="Required with --post-merge: upstream PR number in antgroup/llm-oss-landscape")
    parser.add_argument("--full", action="store_true", help="Full pipeline (check + confirm all without PR)")
    args = parser.parse_args()

    if args.confirm:
        print(f"{YELLOW}--confirm is deprecated. Use PR-based confirmation:{RESET}")
        print(f"  1. Review the PR created by --check")
        print(f"  2. Check items you want to include")
        print(f"  3. Merge the PR")
        print(f"  4. Run --post-merge --pr <number> to update CSV")
        return

    if args.publish_existing:
        publish_existing_report(args.report_path)
        return

    if args.check or args.full:
        run_check(full_mode=args.full, report_only=args.report_only or args.no_publish)

    if args.post_merge:
        if not args.pr:
            parser.error("--post-merge requires --pr <upstream-pr-number>")
        run_post_merge(args.pr)

if __name__ == "__main__":
    main()
