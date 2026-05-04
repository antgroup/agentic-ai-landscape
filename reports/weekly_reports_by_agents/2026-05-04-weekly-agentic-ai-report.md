# Agentic AI Weekly Report - 2026-05-04

## TL;DR

- 本周发现 **38** 个新的 Agentic AI 候选项目。
- 热门方向集中在：Coding Agent (30), Workflow Orchestration (20), MCP (Model Context Protocol) (16)。
- 优先关注：abhigyanpatwari/GitNexus - OpenRank 增长 1202%, 趋势陡峭, 高关注 (35376 stars)。
- OpenRank 增速最快：abhigyanpatwari/GitNexus，约 1202% 增长。

## Deep Trend Insights

### 1. Coding Agent 正在从“写代码工具”扩展为端到端工作系统

本周 38 个候选项目中，分类最集中的仍是 **Coding Agent：30 个**，但代表项目文本显示，重心已经不只是“在终端里补全/修改代码”，而是向任务分派、上下文管理、执行环境、协作编排延伸。

**badlogic/pi-mono** 是这一变化的典型工程化样本：它不是单一 CLI，而是包含 coding agent CLI、统一 LLM API、TUI 与 Web UI libraries、Slack bot、vLLM pods 的 agent toolkit。其 OpenRank 从 2025-11 的 **7.42** 增长到 2026-03 的 **86.81**，参与者 **43**、stars **44296**，说明它获得的不是单纯收藏热度，而是较强的生态参与信号。

相比之下，**paperclipai/paperclip** 更进一步把 Coding Agent 包装成组织级编排系统，描述为“open-source orchestration for zero-human companies”。它创建于 2026-03-02，短期内已有 **62121 stars**、**62 位参与者**，2026-03 OpenRank 为 **80.83**。由于只有单月 OpenRank，无法判断持续增长趋势，但它的高参与者数说明“agent 作为工作流执行单元”正在成为新的叙事中心。

**multica-ai/multica** 则更明确地提出“Turn coding agents into real teammates — assign tasks, track progress, compound skills”。它创建于 2026-01-13，stars **24213**、参与者 **21**，OpenRank 从 2026-01 的 **1.89** 到 2026-03 的 **3.65**，增速不如 pi-mono 和 GitNexus 爆发，但方向很清楚：Coding Agent 的产品形态正在从个人开发助手，转向可管理、可追踪、可积累技能的团队成员。

这也解释了为什么 **Workflow Orchestration：20 个**、**Observability & Evaluation：10 个**、**Agent Framework：10 个** 同时高频出现：Coding Agent 的竞争焦点正在从“模型能力”迁移到“如何可靠地组织 agent 完成持续任务”。

---

### 2. MCP 与上下文工程成为 Agent 工具链的“连接层”，但项目形态分化明显

本周 **MCP（Model Context Protocol）相关项目有 16 个**，显示协议层正在成为开源 AI 工具链的高频接口。但样本中可以看到两类不同路径：一类是真实工程项目把 MCP 作为能力接入层，另一类则是围绕 Claude Code / Cursor / Codex 的 skills、prompt、上下文资产。

**D4Vinci/Scrapling** 是较扎实的工程项目。它是 Python Web Scraping framework，topics 明确包含 **mcp、mcp-server、playwright、web-scraping**，分类覆盖 MCP、Browser Agent、Workflow Orchestration、Data Processing & ETL。它创建于 2024-10-13，stars **43488**，OpenRank 从 2025-11 的 **4.97** 稳定到 2026-03 的 **5.42**。这类项目说明 MCP 正在进入数据采集、浏览器自动化、ETL 等“agent 可调用工具”场景，而非仅停留在 IDE 插件层。

**Hmbown/DeepSeek-TUI** 和 **1jehuang/jcode** 则代表终端原生 coding agent harness 的方向。DeepSeek-TUI 描述中强调“single binary, no Node/Python runtime required”，并内置 MCP client、sandbox、durable task queue；它创建于 2026-01-19，stars **2827**、参与者 **19**，但缺少 OpenRank 信号，因此只能从文本与参与者判断其工程兴趣。jcode 创建于 2026-01-05，stars **3606**、参与者 **10**，OpenRank 从 2026-02 的 **1.8** 到 2026-03 的 **2.6**，说明 Rust/TUI/MCP 组合开始获得稳定关注。

另一类则是资源与 skills 型项目，例如 **affaan-m/everything-claude-code** 和 **JuliusBrussee/caveman**。前者描述为“Skills, instincts, memory, security, and research-first development for Claude Code, Codex, Opencode, Cursor and beyond”，stars 高达 **172908**，OpenRank 从 2026-01 的 **7.82** 到 2026-03 的 **20.73**，参与者 **11**。它更像围绕 Agent Harness 的知识库/方法论/skills 集合，而不是单一基础设施。后者 caveman 是 Claude Code skill，主打“cuts 65% of tokens”，创建于 2026-04-04，stars **53252**、参与者 **4**，但缺少 OpenRank 信号。它的热度更接近 meme 化 skill 与提示工程技巧的传播，而非成熟工程采用。

因此，MCP 的结构性意义不在于某个协议标签本身，而在于它正在把 **数据源、终端执行器、浏览器工具、skills、memory、sandbox** 串成 Agent Runtime 的连接层。

---

### 3. Memory、Knowledge Graph 与 RAG 正在进入代码理解场景，而非只服务问答

本周 **Memory & Knowledge：14 个**、**Vector Database & RAG** 在多个代表项目中出现，表明 AI 开源生态正在把长期记忆和知识结构嵌入 Agent 工作流，尤其是代码理解和任务延续。

**abhigyanpatwari/GitNexus** 是最强信号之一。它将 GitHub repo 或 ZIP 在浏览器中转成交互式知识图谱，并内置 Graph RAG Agent，定位为“Zero-Server Code Intelligence Engine”。它创建于 2025-08-02，stars **35376**、参与者 **30**，OpenRank 从 2025-12 的 **0.45** 飙升到 2026-03 的 **17.88**，是 fastest_growing 第一名。这里的重点不是“又一个代码阅读器”，而是代码库正在被转译为 agent 可检索、可推理、可导航的知识图谱。

**1jehuang/jcode** 也把 Coding Agent、Memory & Knowledge、Vector Database & RAG、MCP 放在一起，说明轻量终端 agent 也开始内置记忆与检索能力。虽然它 stars 只有 **3606**，但 OpenRank 从 **1.8** 到 **2.6**，说明小型工程项目也在形成活跃度，而不只是被大型明星项目吸走注意力。

**affaan-m/everything-claude-code** 进一步把 memory 变成“agent harness performance optimization system”的一部分，强调 skills、instincts、memory、security。它的 stars **172908** 与 OpenRank **20.73** 表示社区对“如何让 Claude Code / Codex / Cursor 长期稳定工作”的方法论需求极强。与 GitNexus 这类真实工具相比，它更偏资源/skills/方法论层，但其热度说明：记忆不是单独产品，而是 Agent Harness 的核心组成。

这意味着 RAG 的应用场景正在发生变化：从“面向文档问答的检索增强”，转向“面向代码库、任务状态、团队知识、设计规范的操作记忆”。

---

### 4. 资源、Awesome、Skills 项目获得巨大 star，但需要与工程采用信号区分

本周 star 信号非常强，但并不都代表同一种价值。部分项目是可运行工程系统，部分是资源集合、skills、prompt 或设计规范资产。分析时必须区分“传播热度”与“工程采用”。

**VoltAgent/awesome-design-md** 是典型资源型项目。它描述为“A collection of DESIGN.md files inspired by popular brand design systems”，用于让 coding agents 生成匹配 UI。它创建于 2026-03-31，stars **70616**、参与者 **2**，但缺少 OpenRank 信号。其价值在于把设计系统转化为 agent 可消费的文本规范，而不是提供完整运行时。它被归入 Coding Agent、Tool & Integration Platform、LLM Inference、Workflow Orchestration 等多个分类，但从文本看，更接近 awesome/design assets collection。

**JuliusBrussee/caveman** 同样属于 skill/prompt/meme 边界项目。它创建于 2026-04-04，stars **53252**、参与者 **4**，缺少 OpenRank 信号。它提出用“caveman”风格减少 Claude Code token 消耗，可能有实用启发，但更应视为 Claude Code skill 与提示压缩技巧，而非基础设施项目。

与之形成对比的是 **badlogic/pi-mono** 和 **paperclipai/paperclip**。pi-mono 有多组件工程栈、**43 位参与者**、OpenRank **86.81**；paperclip 有 **62 位参与者**、OpenRank **80.83**。这类项目的信号更接近真实工程生态，而不只是 README 传播。

**ultraworkers/claw-code** 则处在中间地带：它 stars 高达 **189916**，描述中强调“fastest repo in history to surpass 100K stars”，创建于 2026-03-31，参与者 **5**，但缺少 OpenRank 信号。它声称用 Rust、oh-my-codex 构建，并提供 Rust workspace、Roadmap 等入口；不过在没有 OpenRank 序列的情况下，更应谨慎看待其爆发式 star，把它视为强传播信号，而不是已验证的持续生态活跃度。

因此，本周一个重要判断是：**star 正在更强地奖励“可被 Agent 使用的文本资产、skills、规范和 meme”，但 OpenRank 与参与者数更能帮助区分真实工程项目与传播型资源项目。**

---

### 5. 垂直应用层开始从“演示 Agent”走向高价值任务：金融、设计、办公、网页数据

除了底层工具链，应用层也出现了更明确的垂直化趋势。它们不是泛泛地“做一个 agent”，而是围绕金融研究、交易、多模态设计、PPT 生成、网页数据采集等高价值任务构建。

金融方向有两个样本值得对照。**virattt/dexter** 是 autonomous financial research agent，强调 task planning、self-reflection、real-time market data，创建于 2025-10-14，stars **22758**，但参与者为 **0**。其 OpenRank 从 2025-11 的 **2.68** 升至 2026-02 的 **8.43**，2026-03 回落到 **5.49**，说明关注度有过明显峰值但近期降温。**TauricResearch/TradingAgents** 则是 Multi-Agents LLM Financial Trading Framework，创建于 2024-12-28，stars **65970**、参与者 **22**，OpenRank 在 2026-02 低至 **1.7** 后于 2026-03 回升到 **8.57**。两者都说明金融 Agent 仍有吸引力，但 OpenRank 波动提示其生态活跃度受市场叙事、研究传播或版本节奏影响较大。

办公与设计方向也在快速抬头。**hugohe3/ppt-master** 聚焦“AI generates natively editable PPTX”，强调真实 PowerPoint shapes 与 native animations，而不是图片导出。它创建于 2025-12-10，stars **11068**、参与者 **5**，OpenRank 从 **1.33** 到 **2.74**，显示缓慢但持续增长。**nexu-io/open-design** 则更激进，定位为本地优先的 Claude Design 替代品，提供 19 Skills、71 brand-grade Design Systems，并支持 web、desktop、mobile prototypes、slides、images、videos、HTML/PDF/PPTX/MP4 export。它创建于 2026-04-28，stars **21062**、参与者 **66**，但缺少 OpenRank 信号。其参与者数很高，说明设计 agent / 多格式生成工具正在吸引协作，但仍需后续 OpenRank 验证持续性。

网页数据层则由 **firecrawl/firecrawl** 和 **D4Vinci/Scrapling** 代表。firecrawl 创建于 2024-04-15，stars **114828**，是“search, scrape, and interact with the web for AI”的 API，但 OpenRank 从 2025-11 的 **39.04** 下降到 2026-03 的 **23.81**，参与者 **4**，显示成熟项目可能进入增长放缓阶段。Scrapling stars **43488**，OpenRank 稳定小幅上升至 **5.42**，说明开源网页采集能力仍是 Agent 应用基础，但竞争正在从“能抓网页”转向“能否作为 MCP/Browser Agent/ETL 工具稳定接入工作流”。

---

### 6. OpenRank 显示生态进入“双峰结构”：少数平台型项目强吸附，大量新项目靠叙事爆发

从 OpenRank 趋势看，本周生态并不是均匀增长，而是出现“双峰结构”：一端是平台型、工程型项目快速吸附贡献与关注；另一端是新创建的 skills、awesome、meme、应用项目依靠 star 快速出圈，但缺少持续活跃度验证。

平台型项目中，**badlogic/pi-mono** 的 OpenRank **86.81**、参与者 **43**，以及 **paperclipai/paperclip** 的 OpenRank **80.83**、参与者 **62**，明显高于多数样本。它们共同指向“agent platform / orchestration / runtime”成为生态中心。**abhigyanpatwari/GitNexus** 虽然 OpenRank 最新为 **17.88**，低于前两者，但从 **0.45** 到 **17.88** 的增长速度极快，说明代码知识图谱与 GraphRAG Agent 可能是下一类平台能力。

另一端，**ultraworkers/claw-code**、**VoltAgent/awesome-design-md**、**JuliusBrussee/caveman** 都拥有极高 stars，分别为 **189916**、**70616**、**53252**，但均缺少 OpenRank 信号。它们代表 GitHub star 传播机制对“Claude Code 生态周边”“设计规范资产”“token 节省 skill”的强烈奖励。这里不能简单否定其价值，但应把它们归为资源/skills/传播型信号，而不是直接等同于工程生态领导者。

成熟基础项目则表现出另一种状态。**firecrawl/firecrawl** stars **114828**，但 OpenRank 连续从 **41.31**、**33.05**、**28.99** 到 **23.81** 下滑；**D4Vinci/Scrapling** OpenRank 则从 **4.97** 到 **5.42** 小幅稳定增长。前者可能已经从爆发期进入平台化维护期，后者仍在垂直工具位稳步积累。

综合来看，本周开源 AI 生态的结构性变化可以概括为：**Coding Agent 仍是最大入口，但真正的竞争正在迁移到 Agent Runtime、MCP 工具链、上下文/记忆层、工作流编排与垂直任务系统；同时，skills 与 awesome 类文本资产正在成为新的 star 放大器，需要用 OpenRank 和参与者信号进行二次过滤。**

## Highlighted Projects

### 1. [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus)

- Stars: 35.4k
- Language: TypeScript
- Latest OpenRank: 17.9 (2026-03)
- OpenRank trend: ▁▁▃█
- Participants: 30
- Reason: OpenRank 增长 1202%, 趋势陡峭, 高关注 (35376 stars)

### 2. [badlogic/pi-mono](https://github.com/badlogic/pi-mono)

- Stars: 44.3k
- Language: TypeScript
- Latest OpenRank: 86.8 (2026-03)
- OpenRank trend: ▁▃▅▆█
- Participants: 43
- Reason: OpenRank 增长 943%, 趋势陡峭, 高关注 (44296 stars)

### 3. [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)

- Stars: 172.9k
- Language: JavaScript
- Latest OpenRank: 20.7 (2026-03)
- OpenRank trend: ▁▃█
- Participants: 11
- Reason: OpenRank 增长 146%, 趋势陡峭, 新项目

### 4. [multica-ai/multica](https://github.com/multica-ai/multica)

- Stars: 24.2k
- Language: TypeScript
- Latest OpenRank: 3.6 (2026-03)
- OpenRank trend: ▁▁█
- Participants: 21
- Reason: OpenRank 增长 61%, 趋势陡峭, 新项目

### 5. [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)

- Stars: 11.1k
- Language: Python
- Latest OpenRank: 2.7 (2026-03)
- OpenRank trend: ▁▄▅█
- Participants: 5
- Reason: OpenRank 增长 61%, 趋势陡峭, 新项目

## Review Candidates

| # | Repo | Description | Topics | Stars | Created | Latest OpenRank | OpenRank Month | Trend | Participants | Language | Categories |
|---|------|-------------|--------|-------|---------|-----------------|----------------|-------|--------------|----------|------------|
| 1 | [nexu-io/open-design](https://github.com/nexu-io/open-design) | 🎨 Local-first, open-source alternative to Anthropic's Claude Design. ⚡... | agent-skills,ai-agents,ai-design,byok,claude,claud... | 21.1k | 2026-04-28 | - | - | — | 66 | TypeScript | Coding Agent, LLM Gateway & Proxy, Workflow Orchestration |
| 2 | [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | TradingAgents: Multi-Agents LLM Financial Trading Framework | agent,finance,llm,multiagent,trading | 66.0k | 2024-12-28 | 8.6 | 2026-03 | ▄▃▂▁█ | 22 | Python | LLM Inference, Agent Framework, LLM Gateway & Proxy |
| 3 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 🌊 The leading agent orchestration platform for Claude. Deploy intellig... | agentic-ai,agentic-engineering,agentic-framework,a... | 39.8k | 2025-06-02 | 14.1 | 2026-03 | █▁ | 3 | TypeScript | MCP (Model Context Protocol), Memory & Knowledge, Agent Framework |
| 4 | [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | 🕷️ An adaptive Web Scraping framework that handles everything from a s... | ai,ai-scraping,automation,crawler,crawling,crawlin... | 43.5k | 2024-10-13 | 5.4 | 2026-03 | ▄▁▂▆█ | 3 | Python | MCP (Model Context Protocol), LLM Gateway & Proxy, Browser Agent |
| 5 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | The agent harness performance optimization system. Skills, instincts, ... | ai-agents,anthropic,claude,claude-code,developer-t... | 172.9k | 2026-01-18 | 20.7 | 2026-03 | ▁▃█ | 11 | JavaScript | Coding Agent, Memory & Knowledge, Workflow Orchestration |
| 6 | [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) | GitNexus: The Zero-Server Code Intelligence Engine -       GitNexus is... |  | 35.4k | 2025-08-02 | 17.9 | 2026-03 | ▁▁▃█ | 30 | TypeScript | MCP (Model Context Protocol), Coding Agent, GraphRAG & Knowledge Graph |
| 7 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 🪨 why use many token when few token do trick — Claude Code skill that ... | ai,anthropic,caveman,claude,claude-code,llm,meme,p... | 53.3k | 2026-04-04 | - | - | — | 4 | Python | Coding Agent, MCP (Model Context Protocol), LLM Gateway & Proxy |
| 8 | [openai/symphony](https://github.com/openai/symphony) | Symphony turns project work into isolated, autonomous implementation r... |  | 21.1k | 2026-02-26 | 0.1 | 2026-03 | — | 0 | Elixir | Coding Agent |
| 9 | [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | A collection of DESIGN.md files inspired by popular brand design syste... | awesome-list,design-md,design-system,design-tokens... | 70.6k | 2026-03-31 | - | - | — | 2 | - | Coding Agent, Tool & Integration Platform, LLM Inference |
| 10 | [Fincept-Corporation/FinceptTerminal](https://github.com/Fincept-Corporation/FinceptTerminal) | FinceptTerminal is a modern finance application offering advanced mark... | ai-agents,algorithmic-trading,bloomberg-terminal,c... | 19.6k | 2024-08-29 | 3.1 | 2026-03 | ▅▄█▁▂ | 5 | Python | LLM SDK & Library, LLM Inference, MCP (Model Context Protocol) |
| 11 | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | Huashu Design · HTML-native design skill for Claude Code · Claude Code... |  | 11.7k | 2026-04-19 | - | - | — | 1 | HTML | Coding Agent, Browser Agent, Workflow Orchestration |
| 12 | [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura) | The headless browser for AI agents and web scraping |  | 9.9k | 2026-04-13 | - | - | — | 5 | Rust | Browser Agent, LLM Gateway & Proxy, Speech & Voice AI |
| 13 | [badlogic/pi-mono](https://github.com/badlogic/pi-mono) | AI agent toolkit: coding agent CLI, unified LLM API, TUI & web UI libr... |  | 44.3k | 2025-08-09 | 86.8 | 2026-03 | ▁▃▅▆█ | 43 | TypeScript | Coding Agent, LLM Gateway & Proxy, Agent Framework |
| 14 | [1jehuang/jcode](https://github.com/1jehuang/jcode) | Coding Agent Harness | ai,claude,cli,coding-agent,llm,mcp,openai,rust,ter... | 3.6k | 2026-01-05 | 2.6 | 2026-03 | ▁█ | 10 | Rust | Coding Agent, Memory & Knowledge, Vector Database & RAG |
| 15 | [withastro/flue](https://github.com/withastro/flue) | The sandbox agent framework. |  | 2.2k | 2026-02-07 | 0.8 | 2026-03 | ▁█ | 8 | TypeScript | Tool & Integration Platform, LLM SDK & Library, Coding Agent |
| 16 | [Hmbown/DeepSeek-TUI](https://github.com/Hmbown/DeepSeek-TUI) | Coding agent for DeepSeek models that runs in your terminal | cli,deepseek,llm,rust,terminal,tui | 2.8k | 2026-01-19 | - | - | — | 19 | Rust | MCP (Model Context Protocol), Coding Agent, LLM Inference |
| 17 | [cursor/cookbook](https://github.com/cursor/cookbook) |  |  | 3.3k | 2026-04-27 | - | - | — | 3 | TypeScript | Coding Agent, LLM SDK & Library |
| 18 | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 🔥 The API to search, scrape, and interact with the web for AI | ai,ai-agents,ai-crawler,ai-scraping,ai-search,craw... | 114.8k | 2024-04-15 | 23.8 | 2026-03 | ▇█▄▃▁ | 4 | TypeScript | MCP (Model Context Protocol), Coding Agent, LLM Gateway & Proxy |
| 19 | [multica-ai/multica](https://github.com/multica-ai/multica) | The open-source managed agents platform. Turn coding agents into real ... |  | 24.2k | 2026-01-13 | 3.6 | 2026-03 | ▁▁█ | 21 | TypeScript | Coding Agent, Vector Database & RAG, Observability & Evaluation |
| 20 | [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | Open-source orchestration for zero-human companies |  | 62.1k | 2026-03-02 | 80.8 | 2026-03 | — | 62 | TypeScript | Coding Agent, Workflow Orchestration, Multi-Agent System |
| 21 | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | AI generates natively editable PPTX from any document — real PowerPoin... | ai-agent,aippt,office,powerpoint,powerpoint-genera... | 11.1k | 2025-12-10 | 2.7 | 2026-03 | ▁▄▅█ | 5 | Python | Speech & Voice AI, Coding Agent, Workflow Orchestration |
| 22 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Write HTML. Render video. Built for agents. | ai,animation,ffmpeg,framework,gsap,html,mcp,puppet... | 14.2k | 2026-03-10 | 1.9 | 2026-03 | — | 5 | TypeScript | Coding Agent, Speech & Voice AI, Browser Agent |
| 23 | [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) | Uncensored, open-source alternative to Higgsfield AI, Freepik AI, Krea... | ai-art-generator,ai-image-generation,ai-video-gene... | 11.2k | 2023-05-09 | - | - | — | 3 | JavaScript | Image & Video Generation, Deep Learning Core, Coding Agent |
| 24 | [santifer/career-ops](https://github.com/santifer/career-ops) | AI-powered job search system built on Claude Code. 14 skill modes, Go ... | ai-agent,anthropic,automation,career,claude,claude... | 42.3k | 2026-04-04 | - | - | — | 7 | JavaScript | Coding Agent, Browser Agent, Observability & Evaluation |
| 25 | [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything) | Graphs that teach > graphs that impress. Turn any code, or knowledge b... | antigravity-skills,business-knowledge,claude-code,... | 11.1k | 2026-03-15 | 5.0 | 2026-03 | — | 3 | TypeScript | Coding Agent, GraphRAG & Knowledge Graph, Memory & Knowledge |
| 26 | [google/skills](https://github.com/google/skills) | Agent Skills for Google products and technologies | google,googlecloud,skills | 6.5k | 2026-03-31 | - | - | — | 0 | - | Observability & Evaluation, AI Infrastructure & Platform |
| 27 | [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | Local knowledge graph for Claude Code. Builds a persistent map of your... | ai-coding,claude,claude-code,code-review,graphrag,... | 15.2k | 2026-02-26 | 2.5 | 2026-03 | — | 1 | Python | Coding Agent, MCP (Model Context Protocol), Notebook & Development Env... |
| 28 | [mksglu/context-mode](https://github.com/mksglu/context-mode) | Context window optimization for AI coding agents. Sandboxes tool outpu... | antigravity,claude,claude-code,claude-code-hooks,c... | 12.4k | 2026-02-23 | 9.3 | 2026-03 | — | 8 | TypeScript | MCP (Model Context Protocol), Coding Agent, API & Backend Service |
| 29 | [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | LLM驱动的 A/H/美股智能分析器：多数据源行情 + 实时新闻 + LLM决策仪表盘 + 多渠道推送，零成本定时运行，纯白嫖. LLM-p... | agent,ai,aigc,gemini,llm,quant,quantitative-tradin... | 33.9k | 2026-01-10 | 25.2 | 2026-03 | ▁▄█ | 10 | Python | LLM Inference, Workflow Orchestration, Search & Information Retrieval |
| 30 | [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) | A light-weight and powerful meta-prompting, context engineering and sp... | claude-code,context-engineering,meta-prompting,spe... | 59.8k | 2025-12-14 | 30.5 | 2026-03 | █▁ | 19 | JavaScript | Coding Agent, Workflow Orchestration, LLM SDK & Library |
| 31 | [mattpocock/sandcastle](https://github.com/mattpocock/sandcastle) | Orchestrate sandboxed coding agents in TypeScript with sandcastle.run(... |  | 3.3k | 2026-03-17 | 0.3 | 2026-03 | — | 10 | TypeScript | Coding Agent, Observability & Evaluation, LLM SDK & Library |
| 32 | [holaboss-ai/holaOS](https://github.com/holaboss-ai/holaOS) | An Open Agent Computer for ANY digital work. | agent,agent-harness,agent-os,agentic,ai,ai-agent,a... | 4.6k | 2026-03-22 | - | - | — | 2 | TypeScript | Memory & Knowledge, Coding Agent, MCP (Model Context Protocol) |
| 33 | [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | "Vibe-Trading: Your Personal Trading Agent" | ai-agent,algorithmic-trading,backtesting,fintech,l... | 4.9k | 2026-04-01 | - | - | — | 3 | Python | MCP (Model Context Protocol), Chat UI & Frontend, Coding Agent |
| 34 | [virattt/dexter](https://github.com/virattt/dexter) | An autonomous agent for deep financial research |  | 22.8k | 2025-10-14 | 5.5 | 2026-03 | ▁▁▆█▄ | 0 | TypeScript | Search & Information Retrieval, LLM Inference, Autonomous Agent |
| 35 | [OpenCoworkAI/open-codesign](https://github.com/OpenCoworkAI/open-codesign) | Open-source Claude Design alternative. One-click import your Claude Co... | ai-design,anthropic,byok,claude,claude-code,claude... | 4.5k | 2026-04-18 | - | - | — | 8 | TypeScript | LLM Inference, Coding Agent, Workflow Orchestration |
| 36 | [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | LLM Wiki is a cross-platform desktop application that turns your docum... |  | 5.7k | 2026-04-08 | - | - | — | 2 | TypeScript | Vector Database & RAG, GraphRAG & Knowledge Graph, Memory & Knowledge |
| 37 | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) | The repo is finally unlocked. enjoy the party! The fastest repo in his... |  | 189.9k | 2026-03-31 | - | - | — | 5 | Rust | Coding Agent, Workflow Orchestration |
| 38 | [lsdefine/GenericAgent](https://github.com/lsdefine/GenericAgent) | Self-evolving agent: grows skill tree from 3.3K-line seed, achieving f... | ai-agent,automation,autonomous-agent,browser-autom... | 9.0k | 2026-01-16 | 2.5 | 2026-03 | — | 6 | Python | Memory & Knowledge, Agent Framework, Workflow Orchestration |

---
*Generated by weekly_update.py*
