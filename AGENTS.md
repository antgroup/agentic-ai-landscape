# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

This repository analyzes the **Open Source LLM Development Landscape** by tracking project vitality, trends, and community engagement metrics. The project uses [OpenRank](https://open-digger.cn/en/docs/user_docs/metrics/openrank) to assess repository health and identifies emerging trends in the LLM ecosystem. Reports are published on Medium and WeChat, with an interactive version on Canva.

## Environment Setup

### Prerequisites
- Python 3.12
- pip or conda for package management
- Access to ClickHouse database (credentials in `.env`)
- GitHub API token (for GitHub API calls)

### Initial Setup

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or: .venv\Scripts\activate  # On Windows
   ```

2. **Configure environment variables** (`.env` file in `notebooks/` directory):
   ```
   GITHUB_TOKEN=your_github_token
   CLICKHOUSE_HOST=your_clickhouse_host
   CLICKHOUSE_USER=your_username
   CLICKHOUSE_PASSWORD=your_password
   HF_TOKEN=your_huggingface_token  # Optional, for some analyses
   ```

3. **Install dependencies**:
   Dependencies are managed via Jupyter notebooks' import statements. Key packages include:
   - `pandas` - Data manipulation and analysis
   - `requests` - API calls (GitHub, Open-Digger)
   - `clickhouse_connect` - ClickHouse database access
   - `matplotlib` - Basic plotting
   - `scipy` - Interpolation and scientific computing
   - `python-dotenv` - Environment variable management
   - `wordcloud` - Word cloud generation

## Project Architecture

### Directory Structure

```
├── notebooks/              # Jupyter notebooks for data analysis and visualization
│   ├── src/               # Font files (e.g., RacingSansOne-Regular.ttf)
│   ├── get_projects_info.ipynb          # Query OpenRank data and fetch project info
│   ├── contruct_network_from_seed.ipynb # Build project relationship networks
│   ├── draw_figures.ipynb               # Create all report visualizations
│   └── .env               # Local environment variables (not in git)
├── data/                  # CSV datasets with landscape data
│   ├── landscape_250913.csv             # Current landscape snapshot
│   └── landscape_full_250913.csv        # Full project data
├── reports/               # Generated report outputs
│   ├── 250913_llm_landscape/           # Latest report (figures, data)
│   └── 250527_llm_landscape/           # Previous reports
├── data_stories/          # Community-contributed project insights (markdown files)
├── .cursor/               # Cursor IDE configuration (empty - available for rules)
└── README.md             # Project overview and links
```

### Data Processing Pipeline

The workflow follows this sequence:

1. **Data Collection** (`get_projects_info.ipynb`):
   - Query ClickHouse for repositories with OpenRank ≥ 50 in specified month
   - Fetch project metadata from GitHub API (stars, forks, language, topics, description)
   - Retrieve OpenRank trend data from Open-Digger API
   - Save results as CSV in `data/` directory

2. **Network Analysis** (`contruct_network_from_seed.ipynb`):
   - Build dependency/relationship networks from seed projects
   - Identify project clusters and connections

3. **Visualization Generation** (`draw_figures.ipynb`):
   - Create OpenRank trend charts with smooth spline interpolation
   - Generate comparative OpenRank curves (e.g., PyTorch vs TensorFlow)
   - Produce word clouds from project descriptions
   - Export figures to PNG/SVG for reports

4. **Report Assembly**:
   - Figures from step 3 are manually organized into reports in `reports/` directory
   - Data stories collected from `data_stories/` are compiled

### Key Concepts

**OpenRank Score**: A metric maintained by OpenRank measuring repository vitality based on:
- Commit frequency
- Star growth
- Contributor activity
- Issue/PR engagement

Selection criterion: Projects with OpenRank ≥ 50 in the analyzed month are included (adjustable per report).

**Landscape Categories**: Projects are categorized by domain:
- Large Models (foundational LLMs)
- AI Coding/Development Tools
- RAG/Knowledge Systems
- Agent Frameworks
- Infrastructure/Serving
- And others based on analysis focus

## Running Notebooks

### Execute Entire Notebook
```bash
cd notebooks
jupyter notebook get_projects_info.ipynb
# Select "Run All" or "Restart & Run All" from the Kernel menu
```

### Run Individual Cells
- Open notebook in Jupyter
- Click on a cell and press `Shift+Enter` to run it
- Cells typically include section headers (markdown cells) for organization

### Important Notes
- All notebooks use `.env` in the `notebooks/` directory for configuration
- Database connection established once at notebook start (see first code cell)
- Modify month/date parameters in queries to analyze different time periods
- Font file (`RacingSansOne-Regular.ttf`) must be in `notebooks/src/` for word clouds

## Data Access & APIs

### GitHub API
- Endpoint: `https://api.github.com/repos/{owner}/{repo}`
- Rate limit: 60 requests/minute (unauthenticated), 5000/hour (authenticated with token)
- Required for fetching: stars, forks, language, topics, description, creation date

### ClickHouse (Open-Digger)
- Hosts global repository metrics including OpenRank
- Query examples in notebooks filter by `platform = 'GitHub'` and date ranges
- Default table: `opensource.global_openrank`

### Open-Digger OpenRank Trends
- Endpoint: `https://oss.open-digger.cn/github/{repo_name}/openrank.json`
- Returns monthly OpenRank values (e.g., "2025-07": 150)
- Used for trend analysis and historical comparison

## Contribution Guidelines

### Adding Data Stories
1. Create `.md` file in `data_stories/` named after project (e.g., `DeepSeek.md`)
2. Include analysis, insights, and metrics from the landscape
3. Submit via pull request
4. See `data_stories/README.md` for format details

### Updating Analysis
- Modify notebook parameters (date, OpenRank threshold, project list)
- Re-run affected cells to regenerate data
- Save outputs and commit alongside updated notebooks

## Common Development Tasks

### Add a New Analysis Report
1. Create date-named subdirectory in `reports/` (e.g., `reports/260301_llm_landscape/`)
2. Update notebook parameters for new date range/criteria
3. Run `get_projects_info.ipynb` to refresh data CSV
4. Run `draw_figures.ipynb` to generate all visualizations
5. Save figures to report directory
6. Document selection criteria and findings

### Query Specific Project Data
- Modify `repo_names` list in `get_projects_info.ipynb` with GitHub full names (e.g., `openai/gpt-4`)
- Run fetch section to get stats, or query ClickHouse directly for trends
- Data formatted as CSV for import into reports

### Customize Visualizations
- Edit chart parameters in `draw_figures.ipynb` (colors, fonts, axes labels)
- Use custom fonts from `notebooks/src/` directory
- Matplotlib/Wordcloud libraries used; refer to cell examples for common patterns

## Security & Credentials

- **Never commit `.env` file** - contains API tokens and database credentials
- `.gitignore` excludes `.env` and `.venv/`
- Use Ant Group's ClickHouse instance or configure own for development
- Rotate GitHub tokens regularly; use fine-grained personal access tokens when possible
