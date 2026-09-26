import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

import type {
  LandscapeProject,
  StageId,
  TrendSignal,
} from "./landscape-types";

type SectionDefinition = {
  layer: "Agent Infra" | "Model Infra";
  stage: StageId;
  zone: string;
};

const LANDSCAPE_SECTIONS: SectionDefinition[] = [
  { layer: "Agent Infra", stage: "application", zone: "Agentic coding" },
  {
    layer: "Agent Infra",
    stage: "application",
    zone: "Coding workflows & harnesses",
  },
  {
    layer: "Agent Infra",
    stage: "application",
    zone: "Personal AI assistants",
  },
  {
    layer: "Agent Infra",
    stage: "application",
    zone: "Chatbot workspaces",
  },
  {
    layer: "Agent Infra",
    stage: "framework",
    zone: "Multi-agent orchestration",
  },
  {
    layer: "Agent Infra",
    stage: "framework",
    zone: "Workflow & agent builders",
  },
  {
    layer: "Agent Infra",
    stage: "framework",
    zone: "Code-first frameworks",
  },
  {
    layer: "Agent Infra",
    stage: "runtime",
    zone: "Memory, knowledge & context",
  },
  {
    layer: "Agent Infra",
    stage: "runtime",
    zone: "Protocols & interoperability",
  },
  {
    layer: "Agent Infra",
    stage: "runtime",
    zone: "Tools, web & computer use",
  },
  {
    layer: "Agent Infra",
    stage: "runtime",
    zone: "Observability & evaluation",
  },
  {
    layer: "Agent Infra",
    stage: "runtime",
    zone: "Development sandboxes",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Model API gateways",
  },
  { layer: "Model Infra", stage: "model", zone: "Serving · Deploy" },
  { layer: "Model Infra", stage: "model", zone: "Serving · Inference" },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Post-Train · RL & environments",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Post-Train · Supervised fine-tuning",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Pre-Train · Framework & parallel",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Pre-Train · Evaluation & observability",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Pre-Train · Robotics infra",
  },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Pre-Train · Compiler & accelerator",
  },
  { layer: "Model Infra", stage: "model", zone: "Data · Labeling" },
  { layer: "Model Infra", stage: "model", zone: "Data · Integration" },
  { layer: "Model Infra", stage: "model", zone: "Data · Governance" },
  {
    layer: "Model Infra",
    stage: "model",
    zone: "Compute & scheduling",
  },
];

const PROJECT_NAME_OVERRIDES: Record<string, string> = {
  "aaif-goose/goose": "Goose",
  "a2aproject/a2a": "A2A",
  "a2ui-project/a2ui": "A2UI",
  "affaan-m/ecc": "Everything Claude Code",
  "ag-ui-protocol/ag-ui": "AG-UI",
  "agentscope-ai/qwenpaw": "QwenPaw",
  "agentgateway/agentgateway": "AgentGateway",
  "ai-dynamo/dynamo": "NVIDIA Dynamo",
  "alibaba/page-agent": "page-agent",
  "anthropics/claude-code": "Claude Code",
  "anthropics/skills": "Agent Skills",
  "anomalyco/opencode": "OpenCode",
  "apache/airflow": "Apache Airflow",
  "apache/gravitino": "Apache Gravitino",
  "apache/hudi": "Apache Hudi",
  "apache/iceberg": "Apache Iceberg",
  "apache/paimon": "Apache Paimon",
  "apache/spark": "Apache Spark",
  "areal-project/areal": "AReaL",
  "arize-ai/phoenix": "Arize Phoenix",
  "astrbotdevs/astrbot": "AstrBot",
  "berriai/litellm": "LiteLLM",
  "browser-use/browser-use": "Browser Use",
  "cherryhq/cherry-studio": "Cherry Studio",
  "code-yeongyu/oh-my-openagent": "Oh My OpenAgent",
  "comet-ml/opik": "Opik",
  "copilotkit/copilotkit": "CopilotKit",
  "crewaiinc/crewai": "crewAI",
  "cvat-ai/cvat": "CVAT",
  "danny-avila/librechat": "LibreChat",
  "dao-ailab/flash-attention": "FlashAttention",
  "datahub-project/datahub": "DataHub",
  "deepspeedai/deepspeed": "DeepSpeed",
  "deepseek-ai/deepep": "DeepEP",
  "deepseek-ai/deepseek-harness": "DeepSeek Harness",
  "minimax-ai/minimax-code": "MiniMax Code",
  "deusdata/codebase-memory-mcp": "Codebase Memory MCP",
  "delta-io/delta": "Delta Lake",
  "earendil-works/pi": "Pi",
  "farion1231/cc-switch": "cc-switch",
  "flowiseai/flowise": "Flowise",
  "github/copilot-cli": "Copilot CLI",
  "google/adk-python": "Google ADK",
  "google-gemini/gemini-cli": "Gemini CLI",
  "ggml-org/llama.cpp": "llama.cpp",
  "hiyouga/llamafactory": "LLaMA Factory",
  "hkuds/nanobot": "nanobot",
  "huggingface/lerobot": "LeRobot",
  "huggingface/trl": "TRL",
  "humansignal/label-studio": "Label Studio",
  "ibm/mcp-context-forge": "MCP Context Forge",
  "infiniflow/ragflow": "RAGFlow",
  "jax-ml/jax": "JAX",
  "jetbrains/koog": "Koog",
  "kilo-org/kilocode": "Kilo Code",
  "langchain-ai/langchain": "LangChain",
  "langflow-ai/langflow": "Langflow",
  "langfuse/langfuse": "Langfuse",
  "langgenius/dify": "Dify",
  "larksuite/cli": "Lark CLI",
  "livekit/agents": "LiveKit Agents",
  "llm-d/llm-d": "llm-d",
  "lobehub/lobehub": "LobeHub",
  "mastra-ai/mastra": "Mastra",
  "mem0ai/mem0": "mem0",
  "microsoft/agent-framework": "Microsoft Agent Framework",
  "microsoft/onnxruntime": "ONNX Runtime",
  "milvus-io/milvus": "Milvus",
  "mlflow/mlflow": "MLflow",
  "modelcontextprotocol/servers": "MCP",
  "modelscope/ms-swift": "ms-swift",
  "n8n-io/n8n": "n8n",
  "nousresearch/hermes-agent": "Hermes Agent",
  "nvidia/cutlass": "CUTLASS",
  "nvidia/megatron-lm": "Megatron-LM",
  "nvidia/model-optimizer": "NVIDIA Model Optimizer",
  "nvidia-nemo/rl": "NeMo RL",
  "nvidia/tensorrt-llm": "TensorRT-LLM",
  "nvidia/transformerengine": "Transformer Engine",
  "oceanbase/seekdb": "seekdb",
  "open-metadata/openmetadata": "OpenMetadata",
  "open-webui/open-webui": "Open WebUI",
  "openai/codex": "Codex",
  "openclaw/openclaw": "OpenClaw",
  "openmind/om1": "OpenMind OM1",
  "opensandbox-group/opensandbox": "OpenSandbox",
  "openvinotoolkit/openvino": "OpenVINO",
  "openxla/xla": "OpenXLA",
  "paddlepaddle/paddle": "PaddlePaddle",
  "paperclipai/paperclip": "Paperclip",
  "pipecat-ai/pipecat": "Pipecat",
  "pingdotgg/t3code": "T3 Code",
  "promptfoo/promptfoo": "promptfoo",
  "pydantic/pydantic-ai": "Pydantic AI",
  "pytorch/pytorch": "PyTorch",
  "qwenlm/qwen-code": "Qwen Code",
  "quantumnous/new-api": "New API",
  "rlinf/rlinf": "RLinf",
  "sgl-project/sglang": "SGLang",
  "stacklok/toolhive": "ToolHive",
  "topoteretes/cognee": "Cognee",
  "trycua/cua": "CUA",
  "unslothai/unsloth": "Unsloth",
  "vercel/ai": "Vercel AI SDK",
  "vercel-labs/agent-browser": "Agent Browser",
  "vllm-project/vllm": "vLLM",
  "vllm-project/vllm-omni": "vLLM Omni",
  "volcengine/openviking": "OpenViking",
  "wandb/wandb": "Weights & Biases",
  "warpdotdev/warp": "Warp",
  "zeroclaw-labs/zeroclaw": "ZeroClaw",
};

function latestOpenrank(record: Record<string, string>) {
  return nullableNumber(record.openrank_2608) ?? nullableNumber(record.openrank_2607);
}

function latestOpenrankTrend(record: Record<string, string>) {
  return parseTrend(
    record.openrank_trend_2509_2608 || record.openrank_trend_2508_2607,
  );
}

function parseCsv(source: string) {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;

  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    const next = source[index + 1];

    if (character === '"') {
      if (quoted && next === '"') {
        cell += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === "," && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && next === "\n") index += 1;
      row.push(cell);
      if (row.some(Boolean)) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += character;
    }
  }

  if (cell || row.length) {
    row.push(cell);
    rows.push(row);
  }

  const [headers, ...records] = rows;
  return records.map((record) =>
    Object.fromEntries(
      headers.map((header, index) => [header, record[index] ?? ""]),
    ),
  );
}

function resolveLandscapeDataPath() {
  const candidates = [
    process.env.LANDSCAPE_DATA_PATH,
    path.join(process.cwd(), "data", "agentic-ai-projects.csv"),
    path.resolve(process.cwd(), "../../data/agentic-ai-projects.csv"),
    path.resolve(process.cwd(), "../../../../data/agentic-ai-projects.csv"),
  ].filter((candidate): candidate is string => Boolean(candidate));
  const resolved = candidates.find((candidate) => existsSync(candidate));

  if (!resolved) {
    throw new Error(
      `Landscape data not found. Checked: ${candidates.join(", ")}`,
    );
  }

  return resolved;
}

function readCsvRecords(filePath: string) {
  return parseCsv(
    readFileSync(filePath, "utf8").replace(/^\uFEFF/, ""),
  );
}

function resolveMay2026SnapshotPath() {
  const currentDataPath = resolveLandscapeDataPath();
  const candidates = [
    path.join(
      path.dirname(currentDataPath),
      "history_snapshot",
      "2605_agentic_projects.csv",
    ),
    path.join(
      process.cwd(),
      "data",
      "history_snapshot",
      "2605_agentic_projects.csv",
    ),
    path.resolve(
      process.cwd(),
      "../../data/history_snapshot/2605_agentic_projects.csv",
    ),
  ];
  const resolved = candidates.find((candidate) => existsSync(candidate));

  if (!resolved) {
    throw new Error(
      `May 2026 landscape snapshot not found. Checked: ${candidates.join(", ")}`,
    );
  }

  return resolved;
}

function numberOrZero(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function nullableNumber(value: string) {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseTrendSignals(value: string): TrendSignal[] {
  const supported = new Set<TrendSignal>(["new", "rising"]);
  return [
    ...new Set(
      value
        .toLowerCase()
        .split(/[+,]/)
        .map((signal) => signal.trim()),
    ),
  ].filter((signal): signal is TrendSignal =>
      supported.has(signal as TrendSignal),
  );
}

function parseTrend(value: string): Array<number | null> {
  try {
    const parsed = JSON.parse(value) as unknown[];
    return parsed.map((item) => (typeof item === "number" ? item : null));
  } catch {
    return [];
  }
}

function displayName(repo: string) {
  const override = PROJECT_NAME_OVERRIDES[repo.toLowerCase()];
  if (override) return override;

  const repoName = repo.split("/").at(-1) ?? repo;
  const spaced = repoName.replaceAll(/[-_]+/g, " ");
  if (/[A-Z]/.test(spaced)) return spaced;

  return spaced.replaceAll(/\b[a-z]/g, (letter) => letter.toUpperCase());
}

function readSelectedRecords() {
  const records = readCsvRecords(resolveLandscapeDataPath());
  const selected = records.filter((record) =>
    ["keep", "add"].includes(record.landscape_action.trim().toLowerCase()),
  );
  const sectionByZone = new Map(
    LANDSCAPE_SECTIONS.map((section, index) => [
      section.zone,
      { ...section, index },
    ]),
  );
  const unknownSections = [
    ...new Set(
      selected
        .filter(
          (record) =>
            !sectionByZone.has(record.landscape_section) ||
            sectionByZone.get(record.landscape_section)?.layer !==
              record.landscape_layer,
        )
        .map(
          (record) =>
            `${record.landscape_layer || "missing layer"} / ${
              record.landscape_section || "missing section"
            }`,
        ),
    ),
  ];

  if (unknownSections.length) {
    throw new Error(
      `Selected landscape projects use unknown sections: ${unknownSections.join(
        ", ",
      )}`,
    );
  }

  const duplicates = selected
    .map((record) => record.repo_name.toLowerCase())
    .filter((repo, index, repos) => repos.indexOf(repo) !== index);

  if (duplicates.length) {
    throw new Error(
      `Duplicate selected landscape repositories: ${[
        ...new Set(duplicates),
      ].join(", ")}`,
    );
  }

  return selected
    .map((record) => ({
      record,
      section: sectionByZone.get(record.landscape_section)!,
    }))
    .sort(
      (a, b) =>
        a.section.index - b.section.index ||
        (latestOpenrank(b.record) ?? -1) -
          (latestOpenrank(a.record) ?? -1) ||
        a.record.repo_name.localeCompare(b.record.repo_name),
    );
}

export function getLandscapeRepositories() {
  return readSelectedRecords().map(({ record }) => record.repo_name);
}

export function getLandscapePoolRepositories() {
  return readCsvRecords(resolveLandscapeDataPath()).map(
    (record) => record.repo_name,
  );
}

export function getMay2026TrackedRepositories() {
  return readCsvRecords(resolveMay2026SnapshotPath()).map(
    (record) => record.repo_name,
  );
}

export function getLandscapeProjects(): LandscapeProject[] {
  return readSelectedRecords().map(({ record, section }) => {
    const [owner] = record.repo_name.split("/");

    return {
      id: record.repo_id,
      repo: record.repo_name,
      owner,
      name: displayName(record.repo_name),
      description: record.description,
      stars: numberOrZero(record.stars),
      contributors: nullableNumber(record.contributors),
      forks: numberOrZero(record.forks),
      openIssues: numberOrZero(record.open_issues),
      license: record.license || "—",
      openrank: latestOpenrank(record),
      participants: nullableNumber(record.participants_2607),
      language: record.language || "—",
      createdAt: record.created_at,
      pushedAt: record.pushed_at,
      selectionReason: record.selection_reason,
      selectionCaveat: record.selection_caveat,
      landscapeAction:
        record.landscape_action.trim().toLowerCase() === "add"
          ? "add"
          : "keep",
      trendSignals: parseTrendSignals(record.trend_signal ?? ""),
      trendSignalReason: record.trend_signal_reason ?? "",
      topics: record.topics.split(",").filter(Boolean),
      categories: [record.landscape_layer, record.landscape_section],
      trend: latestOpenrankTrend(record),
      stage: section.stage,
      zone: section.zone,
    };
  });
}
