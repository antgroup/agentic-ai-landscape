import {
  getLandscapePoolRepositories,
  getLandscapeProjects,
  getMay2026TrackedRepositories,
} from "@/lib/landscape-data";

import type { LandscapeProject, StageId } from "@/lib/landscape-types";

export type MacroGroup = {
  label: string;
  projects: number;
  projectShare: number;
  openrank: number;
  openrankShare: number;
  newlyTracked: number;
};

export type LanguageMixGroup = {
  label: string;
  agent: number;
  model: number;
};

export type RuntimePathPoint = {
  label: string;
  shortLabel: string;
  projects: number;
  examples: Array<{
    name: string;
    repo: string;
  }>;
};

export type InfraTrendStats = {
  layer: "agent" | "model";
  projects: number;
  stars: number;
  contributors: number;
  openrank: number;
  openrankCoverage: number;
  monthly: Array<{ month: string; label: string; value: number }>;
  domains: Array<{
    label: string;
    projects: number;
    stars: number;
    contributors: number;
    openrank: number;
    openrankCoverage: number;
    delta: number;
  }>;
  languages: Array<{
    label: string;
    projects: number;
    stars: number;
    contributors: number;
    openrank: number;
    projectShare: number;
    starShare: number;
    openrankShare: number;
  }>;
  scaleLeaders: Array<{
    name: string;
    repo: string;
    zone: string;
    openrank: number;
    stars: number;
    contributors: number;
  }>;
  momentumLeaders: Array<{
    name: string;
    repo: string;
    zone: string;
    delta: number;
    openrank: number;
    stars: number;
    contributors: number;
  }>;
  miniMax: null | {
    name: string;
    repo: string;
    stars: number;
    contributors: number;
    createdAt: string;
    openrankIndexed: boolean;
  };
};

export type InclusionResearchStats = {
  total: number;
  agent: number;
  model: number;
  mayTracked: number;
  currentTracked: number;
  trackedDelta: number;
  selectedOutsideMay: number;
  agentOutsideMay: number;
  runtimeOutsideMay: number;
  runtimeOutsideMayProjects: Array<{
    name: string;
    repo: string;
    zone: string;
  }>;
  agentRecent: number;
  modelRecent: number;
  agentMacro: MacroGroup[];
  modelMacro: MacroGroup[];
  growthLeaders: Array<{
    name: string;
    repo: string;
    zone: string;
    growth: number;
  }>;
  languageMix: LanguageMixGroup[];
  runtimePath: RuntimePathPoint[];
  infraTrends: {
    agent: InfraTrendStats;
    model: InfraTrendStats;
  };
  collaboration: CollaborationResearchStats;
};

export type CollaborationResearchStats = {
  repositoryProfile: {
    repositories: number;
    repositoryItems: Array<{
      repo: string;
      technicalRoleKey: string;
      technicalRoleLabel: string;
      identityKey: string;
      identityLabel: string;
      openrank: number;
      stars: number;
    }>;
    identities: Array<{
      key: string;
      label: string;
      count: number;
      description?: string;
    }>;
    technicalRoles: Array<{ key: string; label: string; count: number }>;
    ageCohorts: Array<{ key: string; label: string; count: number }>;
    languages: Array<{ key: string; label: string; count: number }>;
  };
  activityFlow: {
    window: string;
    issuesOpened: number;
    issuesUnresolved: number;
    pullRequestsOpened: number;
    pullRequestsUnresolved: number;
    pullRequestIssueRatio: number;
    issueTopFiveShare: number;
    pullRequestTopFiveShare: number;
    issueTopFive: Array<{ repo: string; count: number }>;
    pullRequestTopFive: Array<{ repo: string; count: number }>;
    monthly: Array<{
      month: string;
      label: string;
      issues: number;
      pullRequests: number;
      ratio: number;
    }>;
    niches: Array<{
      key: string;
      label: string;
      repositories: number;
      issues: number;
      issueUnresolvedShare: number;
      pullRequests: number;
      pullRequestUnresolvedShare: number;
      ratio: number;
    }>;
    constantCohortRepositories: number;
    history: Array<{
      year: number;
      repositories: number;
      issues: number;
      pullRequests: number;
      issueUnresolvedShare: number;
      pullRequestUnresolvedShare: number;
    }>;
    releases: {
      observationDays: number;
      repositoriesWithRelease: number;
      medianReleaseDays: number;
      lowerQuartileReleaseDays: number;
      upperQuartileReleaseDays: number;
      buckets: Array<{ label: string; count: number }>;
      leaders: Array<{
        repo: string;
        releaseDays: number;
        releaseRecords: number;
      }>;
    };
  };
  systemPressure: {
    matchedRepositories: number;
    roleFlows: Array<{
      key: string;
      label: string;
      repositories: number;
      issuesOpened: number;
      issueBalance: number;
      repositoriesWithPositiveIssueBalance: number;
      repositoryMedianIssueBalanceShare: number;
      pullRequestsOpened: number;
      pullRequestBalance: number;
      repositoriesWithPositivePullRequestBalance: number;
      repositoryMedianPullRequestBalanceShare: number;
      repositoryMedianPullRequestUnresolved90dShare: number;
      repositoryMedianPullRequestMerged90dShare: number;
    }>;
    history: Array<{
      year: number;
      issuesOpened: number;
      issuesClosed: number;
      issuesOpenAtCutoff: number;
      issueBalance: number;
      repositoriesWithPositiveIssueBalance: number;
      pullRequestsOpened: number;
      pullRequestsClosed: number;
      pullRequestsOpenAtCutoff: number;
      pullRequestBalance: number;
      repositoriesWithPositivePullRequestBalance: number;
      issueUnresolved90dShare: number;
      pullRequestUnresolved90dShare: number;
      pullRequestMerged90dShare: number;
      repositoryMedianPullRequestMerged90dShare: number;
    }>;
    pushHistory: Array<{
      year: number;
      pushActors: number;
      actorsForHalfOfPushes: number;
      topFiveActorShare: number;
    }>;
    pushBenchmarks: Array<{
      label: string;
      repositories: number;
      pushActors: number;
      actorsForHalfOfPushes: number;
      topFiveActorShare: number;
    }>;
  };
  threadPanel: {
    matchedRepositories: number;
    years: Array<{
      year: number;
      threads: number;
      issues: number;
      pullRequests: number;
      agentParticipationShare: number;
      humanResponseWithin7dShare: number;
      maintainerResponseWithin7dShare: number;
      issueResolvedWithin30dShare: number;
      pullRequestResolvedWithin30dShare: number;
      pullRequestReviewedShare: number;
      pullRequestRequestedRevisionShare: number;
      requestedRevisionFollowedByCommitShare: number;
      pullRequestTwoPlusRevisionShare: number;
      medianRequestedRevisionCycles: number;
      medianCommitsAfterFirstReview: number;
    }>;
  };
  sampleThreads: number;
  samplePullRequests: number;
  activeRepositories: number;
  codingAgentRepositories: number;
  agentMarkerCoverage: Array<{
    key: string;
    label: string;
    count: number;
  }>;
  agentMarkerLeaders: Array<{
    repo: string;
    count: number;
    labels: string[];
  }>;
  observedParticipationRepositories: number;
  attributableAgentIdentities: number;
  highConfidenceAgentIdentities: number;
  mediumConfidenceAgentIdentities: number;
  botTypedAgentIdentities: number;
  userTypedAgentIdentities: number;
  appMediatedUserIdentities: number;
  participationSampleThreads: number;
  participationOpenerSampleThreads: number;
  participationThreadShare: number;
  participationMacroShare: number;
  participationOpenerShare: number;
  participationResponseShare: number;
  threadParticipationStages: Array<{
    id: "opened" | "response" | "review" | "final-state";
    denominator: number;
    agent: number;
    user: number;
    repositoryTeam: number;
  }>;
  knownAutomationShare: number;
  agentReviewShare: number;
  userReviewShare: number;
  maintainerReviewShare: number;
  userGateShare: number;
  maintainerGateShare: number;
  agentGateShare: number;
  userResponseShare: number;
  maintainerResponseShare: number;
  externalPrShare: number;
  externalMergeFlagShare: number;
  internalMergeFlagShare: number;
  explicitInvitations: number;
  gatedPolicies: number;
  restrictedCreationPolicies: number;
  noDetectedPolicySignal: number;
  top100PrUnresolvedMedian: number;
  controlPrUnresolvedMedian: number;
  controlsWithRisingPrBacklog: number;
  controlsTotal: number;
  reviewedPrShare: number;
  reviewedPrFollowupCommitShare: number;
  firstReviewAgentPrs: number;
  firstReviewAgentFollowupCommits: number;
  firstReviewAgentFollowupShare: number;
  firstReviewGithubUserPrs: number;
  firstReviewGithubUserFollowupCommits: number;
  firstReviewGithubUserFollowupShare: number;
  changeRequestPrs: number;
  changeRequestFollowupCommits: number;
  changeRequestFollowupCommitShare: number;
  agentChangeRequestPrs: number;
  agentChangeRequestFollowupCommits: number;
  agentChangeRequestFollowupCommitShare: number;
  humanChangeRequestPrs: number;
  humanChangeRequestFollowupCommits: number;
  humanChangeRequestFollowupCommitShare: number;
  publicEventsAnalyzed: number;
  agentTaskEvents: {
    review: number;
    triage: number;
    discussion: number;
    codeCommit: number;
    openedThread: number;
  };
  automationByItem: Array<{
    label: "Issues" | "Pull requests";
    knownAutomation: number;
    verifiedAgent: number;
    conventionalAutomation: number;
    automationOnly: number;
  }>;
  markerTransitions: {
    strict: { retained: number; added: number; none: number };
    active: { retained: number; added: number; none: number };
  };
  projectStages: Array<{
    project: string;
    identity: string;
    niche: string;
    stages: Array<{
      stage: string;
      label: string;
      agentParticipation: number | null;
      maintainerParticipation: number | null;
      mergedWithin30Days: number | null;
      pullRequests: number;
    }>;
  }>;
  codeLineages: Array<{
    project: string;
    number: number;
    href: string;
    outcome: string;
    additions: number;
    deletions: number;
    commits: number;
    agentCommits: number;
    otherCommits: number;
  }>;
  efficiencyExperiment: {
    sampleThreads: number;
    eligibleSevenDayThreads: number;
    eligibleThirtyDayThreads: number;
    timelineCompleteness: number;
    population: {
      earlier: number;
      later: number;
      growth: number;
    };
    adoption: {
      allAgentsEarlier: number;
      allAgentsLater: number;
      codingReviewEarlier: number;
      codingReviewLater: number;
    };
    panel: Array<{
      key: string;
      label: string;
      earlier: number;
      later: number;
      format: "percent" | "count";
      direction: "efficiency" | "burden";
    }>;
    exposure: Array<{
      key: string;
      label: string;
      agentVisible: number;
      noVisibleAgent: number;
      format: "percent" | "count";
      direction: "outcome" | "iteration";
    }>;
    maintainerActionEstimate: {
      earlier: number;
      later: number;
      laterLow: number;
      laterHigh: number;
    };
  };
};

function resolveResearchFile(filename: string) {
  const relative = path.join(
    "insights",
    "260912_open_collaboration_ai",
    "research",
    filename,
  );
  const candidates = [
    path.resolve(process.cwd(), "../..", relative),
    path.resolve(process.cwd(), relative),
    path.resolve(process.cwd(), "../../../..", relative),
  ];
  const existing = candidates.find((candidate) => fs.existsSync(candidate));
  if (!existing) throw new Error(`Unable to locate research file ${relative}`);
  return existing;
}

function parseCsvLine(line: string) {
  const values: string[] = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '"') {
      if (quoted && line[index + 1] === '"') {
        value += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (character === "," && !quoted) {
      values.push(value);
      value = "";
    } else {
      value += character;
    }
  }
  values.push(value);
  return values;
}

function readCsv(filename: string) {
  const lines = fs
    .readFileSync(resolveResearchFile(filename), "utf8")
    .trim()
    .split(/\r?\n/);
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function numberValue(value: string | undefined) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function collaborationResearchStats(): CollaborationResearchStats {
  const sample = readCsv("collaboration-sample-top100-2607.csv");
  const repositoryMonth = readCsv("collaboration-repository-month-2026.csv").filter(
    (row) => row.month === "2026-08",
  );
  if (repositoryMonth.length !== sample.length) {
    throw new Error("Repository-month sampling frame does not cover the Top 100");
  }
  const repositoryProfile = readCsv("collaboration-repository-profile-2026.csv");
  if (repositoryProfile.length !== sample.length) {
    throw new Error("Repository collaboration profile does not cover the Top 100");
  }
  const markerSnapshot = readCsv(
    "collaboration-agent-markers-260531-260831-summary.csv",
  ).filter((row) => row.snapshot_date === "2026-08-31");
  if (markerSnapshot.length !== sample.length) {
    throw new Error("Current Agent marker snapshot does not cover the Top 100");
  }
  const repositoryMonthAll = readCsv("collaboration-repository-month-2026.csv");
  const fixedWindow = readCsv("collaboration-repository-fixed-window-2022-2026.csv");
  if (fixedWindow.length !== sample.length * 5) {
    throw new Error("Matched repository-year activity panel does not cover the Top 100");
  }
  const systemPressure = readCsv(
    "collaboration-system-pressure-summary-2024-2026.csv",
  );
  const threadPanel = readCsv(
    "collaboration-thread-panel-summary-2025-2026.csv",
  );
  const pressureRow = (
    section: string,
    panel: string,
    year: number,
    scopeValue = "all",
  ) => {
    const row = systemPressure.find(
      (candidate) =>
        candidate.section === section &&
        candidate.panel === panel &&
        Number(candidate.year) === year &&
        candidate.scope_value === scopeValue,
    );
    if (!row) {
      throw new Error(
        `System-pressure row is missing: ${section} · ${panel} · ${year} · ${scopeValue}`,
      );
    }
    return row;
  };
  const efficiencyPanel = readCsv(
    "collaboration-efficiency-burden-panel-summary.csv",
  ).filter((row) => row.comparison === "2025_to_2026");
  const efficiencyExposure = readCsv(
    "collaboration-efficiency-burden-agent-exposure.csv",
  ).filter(
    (row) =>
      row.comparison ===
      "2026_early_coding_or_review_agent_vs_none_first_24h",
  );
  const efficiencyVolume = readCsv(
    "collaboration-efficiency-burden-volume-summary.csv",
  );
  const efficiencyValidation = JSON.parse(
    fs.readFileSync(
      resolveResearchFile("collaboration-efficiency-burden-validation.json"),
      "utf8",
    ),
  ) as {
    threads: number;
    eligible_7d_threads: number;
    eligible_30d_threads: number;
    timeline_completeness: number;
  };
  const summary = readCsv("collaboration-thread-analysis-2026-summary.csv");
  const overall = summary.find(
    (row) => row.scope_type === "overall" && row.scope_value === "all",
  );
  if (!overall) throw new Error("Overall collaboration thread summary is missing");
  const issueSummary = summary.find(
    (row) => row.scope_type === "item_type" && row.scope_value === "issue",
  );
  const pullRequestSummary = summary.find(
    (row) => row.scope_type === "item_type" && row.scope_value === "pull_request",
  );
  if (!issueSummary || !pullRequestSummary) {
    throw new Error("Issue / pull-request collaboration summary rows are missing");
  }

  const efficiencyPanelMetric = (metric: string, scope: string) => {
    const row = efficiencyPanel.find(
      (candidate) =>
        candidate.metric === metric && candidate.item_scope === scope,
    );
    if (!row) {
      throw new Error(`Efficiency panel metric is missing: ${metric} · ${scope}`);
    }
    return row;
  };
  const efficiencyExposureMetric = (metric: string, scope: string) => {
    const row = efficiencyExposure.find(
      (candidate) =>
        candidate.metric === metric && candidate.item_scope === scope,
    );
    if (!row) {
      throw new Error(`Efficiency exposure metric is missing: ${metric} · ${scope}`);
    }
    return row;
  };
  const efficiencyVolumeYear = (year: string) => {
    const row = efficiencyVolume.find((candidate) => candidate.panel_year === year);
    if (!row) throw new Error(`Efficiency volume row is missing: ${year}`);
    return row;
  };

  const sensitivity = readCsv("collaboration-agent-participation-sensitivity-2026.csv");
  const strict = sensitivity.find((row) => row.scenario === "strict_verified");
  if (!strict) throw new Error("Strict Agent participation sensitivity row is missing");

  const participationRoles = new Set([
    "coding_agent",
    "review_agent",
    "security_review_agent",
    "support_agent",
    "agent_mediated_user",
  ]);
  const attributableAgentActors = readCsv("collaboration-actor-registry-2026.csv").filter(
    (row) => participationRoles.has(row.automation_role),
  );

  const policies = readCsv("collaboration-contribution-policies-reviewed-260829.csv");
  const policyCount = (classes: string[]) =>
    policies.filter((row) => classes.includes(row.final_policy_class)).length;

  const maturity = readCsv("collaboration-fixed-90d-summary.csv");
  const top100 = maturity.find(
    (row) => row.panel === "agentic_top100" && row.scope_type === "overall",
  );
  const control = maturity.find(
    (row) =>
      row.panel === "long_lived_benchmark" &&
      row.scope_type === "overall" &&
      row.year === "2026",
  );
  if (!top100 || !control) throw new Error("Fixed-maturity comparison rows are missing");

  const transitions = readCsv("collaboration-control-2022-2026-transitions.csv");
  const threadRows = readCsv("collaboration-thread-analysis-2026.csv");
  const threadAnalysisRun = JSON.parse(
    fs.readFileSync(
      resolveResearchFile("collaboration-thread-analysis-2026-run.json"),
      "utf8",
    ),
  ) as { events_within_window: number };
  const taskRows = readCsv("collaboration-agent-observed-tasks-2026.csv");
  const markerTransitions = readCsv("collaboration-marker-transitions-2025-2026.csv");
  const deepStages = readCsv("collaboration-deep-stage-metrics-2026.csv");
  const codeAttribution = readCsv("collaboration-agent-code-attribution-2026.csv");
  const taskEvents = (task: string) =>
    taskRows
      .filter((row) => row.task === task)
      .reduce((sum, row) => sum + numberValue(row.observed_events), 0);
  const repositoryTeamAssociations = new Set(["OWNER", "MEMBER", "COLLABORATOR"]);
  const countThreads = (
    rows: Array<Record<string, string>>,
    predicate: (row: Record<string, string>) => boolean,
  ) => rows.filter(predicate).length;
  const pullRequestThreads = threadRows.filter(
    (row) => row.item_type === "pull_request",
  );
  const resolvedThreadsWithVisibleFinalActor = threadRows.filter(
    (row) => row.outcome !== "open" && Boolean(row.gate_actor_login),
  );
  const threadParticipationStages: CollaborationResearchStats["threadParticipationStages"] = [
    {
      id: "opened",
      denominator: threadRows.length,
      agent: countThreads(
        threadRows,
        (row) => row.agent_participation_opened_thread === "yes",
      ),
      user: countThreads(
        threadRows,
        (row) => row.opener_class === "human_account",
      ),
      repositoryTeam: countThreads(
        threadRows,
        (row) => repositoryTeamAssociations.has(row.author_association),
      ),
    },
    {
      id: "response",
      denominator: threadRows.length,
      agent: countThreads(
        threadRows,
        (row) => row.agent_participation_response_present === "yes",
      ),
      user: countThreads(
        threadRows,
        (row) => row.no_human_account_response === "no",
      ),
      repositoryTeam: countThreads(
        threadRows,
        (row) => row.no_maintainer_account_response === "no",
      ),
    },
    {
      id: "review",
      denominator: pullRequestThreads.length,
      agent: countThreads(
        pullRequestThreads,
        (row) => row.agent_review_event_present === "yes",
      ),
      user: countThreads(
        pullRequestThreads,
        (row) => row.human_account_review_event_present === "yes",
      ),
      repositoryTeam: countThreads(
        pullRequestThreads,
        (row) => row.maintainer_account_review_event_present === "yes",
      ),
    },
    {
      id: "final-state",
      denominator: resolvedThreadsWithVisibleFinalActor.length,
      agent: countThreads(
        resolvedThreadsWithVisibleFinalActor,
        (row) => row.agent_gate === "yes",
      ),
      user: countThreads(
        resolvedThreadsWithVisibleFinalActor,
        (row) => row.human_account_gate === "yes",
      ),
      repositoryTeam: countThreads(
        resolvedThreadsWithVisibleFinalActor,
        (row) => row.maintainer_account_gate === "yes",
      ),
    },
  ];

  const countBy = (column: string, value: string) =>
    sample.filter((row) => row[column] === value).length;
  const quantileValue = (values: number[], quantile: number) => {
    const ordered = [...values].sort((a, b) => a - b);
    const position = (ordered.length - 1) * quantile;
    const lower = Math.floor(position);
    const upper = Math.ceil(position);
    if (lower === upper) return ordered[lower];
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower);
  };
  const namedLanguages = ["Python", "TypeScript", "Go"];
  const namedLanguageCount = namedLanguages.reduce(
    (sum, language) => sum + countBy("language", language),
    0,
  );
  const technicalRoleMeta: Record<string, { key: string; label: string }> = {
    model_infra: { key: "model-infra", label: "Model infrastructure" },
    agent_application: { key: "agent-application", label: "Agent applications" },
    agent_framework: { key: "agent-framework", label: "Agent frameworks" },
    agent_runtime_infra: {
      key: "agent-runtime",
      label: "Agent runtime infrastructure",
    },
  };
  const identityMeta: Record<string, { key: string; label: string }> = {
    llm_native: { key: "llm-native", label: "LLM-native" },
    traditional: { key: "traditional", label: "Traditional" },
    mixed: { key: "mixed", label: "Mixed" },
  };
  const currentActivity = fixedWindow.filter((row) => row.year === "2026");
  const sumActivity = (rows: Array<Record<string, string>>, field: string) =>
    rows.reduce((sum, row) => sum + numberValue(row[field]), 0);
  const issueTotal = sumActivity(currentActivity, "issues_opened");
  const pullRequestTotal = sumActivity(currentActivity, "prs_opened");
  const nicheOrder = [
    "agent_application",
    "agent_framework",
    "agent_runtime_infra",
    "model_infra",
  ];
  const nicheLabels: Record<string, string> = {
    agent_application: "Agent applications",
    agent_framework: "Agent frameworks",
    agent_runtime_infra: "Agent runtime infrastructure",
    model_infra: "Model infrastructure",
  };
  const matchedPressureRows = [2024, 2025, 2026].map((year) =>
    pressureRow("queue_flow", "matched_top100", year),
  );
  const constantCohortRepos = new Set(
    readCsv("collaboration-system-pressure-repositories-2024-2026.csv")
      .filter((row) => row.matched_historical_panel === "yes")
      .map((row) => row.repo_name),
  );
  const activityHistory = [2024, 2025, 2026].map((year) => {
    const row = matchedPressureRows.find((candidate) => Number(candidate.year) === year)!;
    const issues = numberValue(row.issues_opened);
    const pullRequests = numberValue(row.prs_opened);
    const fixed = pressureRow("fixed_90d_outcome", "matched_top100", year);
    return {
      year,
      repositories: numberValue(row.repositories),
      issues,
      pullRequests,
      issueUnresolvedShare: numberValue(fixed.issue_unresolved_90d_share),
      pullRequestUnresolvedShare: numberValue(fixed.pr_unresolved_90d_share),
    };
  });
  const releaseDays = repositoryProfile.map((row) => numberValue(row.github_release_days));
  const releaseBuckets = [
    { label: "None", count: releaseDays.filter((value) => value === 0).length },
    { label: "1 day", count: releaseDays.filter((value) => value === 1).length },
    { label: "2–9", count: releaseDays.filter((value) => value >= 2 && value <= 9).length },
    { label: "10–29", count: releaseDays.filter((value) => value >= 10 && value <= 29).length },
    { label: "30–89", count: releaseDays.filter((value) => value >= 30 && value <= 89).length },
    { label: "90–179", count: releaseDays.filter((value) => value >= 90 && value <= 179).length },
    { label: "180+", count: releaseDays.filter((value) => value >= 180).length },
  ];
  const agentMarkerMeta = [
    { key: "cross_agent", label: "Works across Agents" },
    { key: "claude_code", label: "Claude Code" },
    { key: "codex", label: "Codex" },
    { key: "github_copilot", label: "GitHub Copilot" },
    { key: "cursor", label: "Cursor" },
    { key: "gemini", label: "Gemini" },
  ];
  const markerTools = (row: Record<string, string>) =>
    row.distinct_active_tools.split("|").filter(Boolean);
  const markerLabels = new Map(
    [
      ...agentMarkerMeta,
      { key: "cline", label: "Cline" },
    ].map((item) => [item.key, item.label]),
  );
  const agentMarkerCoverage = agentMarkerMeta.map((item) => ({
    ...item,
    count: markerSnapshot.filter((row) => markerTools(row).includes(item.key)).length,
  }));
  const agentMarkerLeaders = markerSnapshot
    .map((row) => {
      const tools = markerTools(row).filter((tool) => tool !== "cross_agent");
      return {
        repo: row.repo_name,
        count: tools.length,
        labels: tools.map((tool) => markerLabels.get(tool) ?? tool),
      };
    })
    .sort((a, b) => b.count - a.count || a.repo.localeCompare(b.repo))
    .slice(0, 4);

  const transitionCounts = (column: "strict_transition" | "any_active_transition") => ({
    retained: markerTransitions.filter((row) => row[column] === "retained").length,
    added: markerTransitions.filter((row) => row[column] === "added").length,
    none: markerTransitions.filter((row) => row[column] === "none").length,
  });

  const selectedStageProjects = [
    "langchain-ai/langchain",
    "coder/coder",
    "pytorch/pytorch",
    "anthropics/claude-code",
  ];
  const stageOrder = ["launch_120d", "previous_2025q4", "current_2026m5_m8"];
  const stageLabels: Record<string, string> = {
    launch_120d: "Launch window",
    previous_2025q4: "2025 Q4",
    current_2026m5_m8: "May–Aug 2026",
  };
  const projectStages = selectedStageProjects.map((project) => {
    const rows = deepStages.filter((row) => row.repo_name === project);
    if (rows.length !== 3) throw new Error(`Missing stage rows for ${project}`);
    const first = rows[0];
    return {
      project,
      identity: first.llm_native_manual,
      niche: first.collaboration_niche,
      stages: stageOrder.map((stage) => {
        const row = rows.find((candidate) => candidate.study_stage === stage);
        if (!row) throw new Error(`Missing ${stage} row for ${project}`);
        const nullableNumber = (value: string | undefined) =>
          value === undefined || value === "" ? null : numberValue(value);
        return {
          stage,
          label: stageLabels[stage],
          agentParticipation: nullableNumber(row.agent_participation_share),
          maintainerParticipation: nullableNumber(row.maintainer_present_share),
          mergedWithin30Days: nullableNumber(row.pr_merged_within_30d_share),
          pullRequests: numberValue(row.pull_requests),
        };
      }),
    };
  });

  const selectedLineages = new Map([
    ["vercel/ai#18818", { project: "Vercel AI SDK", number: 18818 }],
    ["microsoft/onnxruntime#28045", { project: "ONNX Runtime", number: 28045 }],
    ["open-metadata/OpenMetadata#25243", { project: "OpenMetadata", number: 25243 }],
    ["OpenHands/software-agent-sdk#2614", { project: "OpenHands SDK", number: 2614 }],
  ]);
  const codeLineages = codeAttribution
    .filter((row) => selectedLineages.has(`${row.repo_name}#${row.number}`))
    .map((row) => {
      const selected = selectedLineages.get(`${row.repo_name}#${row.number}`)!;
      return {
        project: selected.project,
        number: selected.number,
        href: row.html_url,
        outcome: row.outcome,
        additions: numberValue(row.additions),
        deletions: numberValue(row.deletions),
        commits: numberValue(row.commits_total),
        agentCommits: numberValue(row.direct_agent_commit_count),
        otherCommits: numberValue(row.human_or_unknown_commit_count),
      };
    });
  return {
    repositoryProfile: {
      repositories: sample.length,
      repositoryItems: sample
        .map((row) => {
          const technicalRole = technicalRoleMeta[row.collaboration_niche];
          const identity = identityMeta[row.llm_native_manual];
          if (!technicalRole || !identity) {
            throw new Error(`Missing repository profile mapping for ${row.repo_name}`);
          }
          return {
            repo: row.repo_name,
            technicalRoleKey: technicalRole.key,
            technicalRoleLabel: technicalRole.label,
            identityKey: identity.key,
            identityLabel: identity.label,
            openrank: numberValue(row.openrank_2607),
            stars: numberValue(row.stars),
          };
        })
        .sort((a, b) => {
          const roleOrder = [
            "model-infra",
            "agent-application",
            "agent-framework",
            "agent-runtime",
          ];
          return (
            roleOrder.indexOf(a.technicalRoleKey) -
              roleOrder.indexOf(b.technicalRoleKey) ||
            b.openrank - a.openrank
          );
        }),
      identities: [
        {
          key: "llm-native",
          label: "LLM-native",
          count: countBy("llm_native_manual", "llm_native"),
          description:
            "The project’s main purpose depends on language models or agents. Remove the LLM, and the core product no longer works as intended. LangChain and vLLM are examples.",
        },
        {
          key: "traditional",
          label: "Traditional",
          count: countBy("llm_native_manual", "traditional"),
          description:
            "The project has a complete core purpose without language models. It may serve AI workloads, but that does not define the project. PyTorch and ONNX Runtime are examples.",
        },
        {
          key: "mixed",
          label: "Mixed",
          count: countBy("llm_native_manual", "mixed"),
          description:
            "The project began with a broader software purpose, while AI or agents now form a substantial product surface. The non-AI product still stands. n8n, Warp and MLflow are examples.",
        },
      ],
      technicalRoles: [
        { key: "model-infra", label: "Model infrastructure", count: countBy("collaboration_niche", "model_infra") },
        { key: "agent-application", label: "Agent applications", count: countBy("collaboration_niche", "agent_application") },
        { key: "agent-framework", label: "Agent frameworks", count: countBy("collaboration_niche", "agent_framework") },
        { key: "agent-runtime", label: "Agent runtime infrastructure", count: countBy("collaboration_niche", "agent_runtime_infra") },
      ],
      ageCohorts: [
        { key: "recent", label: "Created Dec 2022 or later", count: countBy("age_cohort", "created_2022_12_or_later") },
        { key: "earlier", label: "Created earlier", count: countBy("age_cohort", "created_before_2022_12") },
      ],
      languages: [
        { key: "python", label: "Python", count: countBy("language", "Python") },
        { key: "typescript", label: "TypeScript", count: countBy("language", "TypeScript") },
        { key: "go", label: "Go", count: countBy("language", "Go") },
        { key: "other", label: "Other", count: sample.length - namedLanguageCount },
      ],
    },
    activityFlow: {
      window: "1 Jan–31 Aug 2026",
      issuesOpened: issueTotal,
      issuesUnresolved: sumActivity(currentActivity, "issues_unresolved_from_cohort"),
      pullRequestsOpened: pullRequestTotal,
      pullRequestsUnresolved: sumActivity(currentActivity, "prs_unresolved_from_cohort"),
      pullRequestIssueRatio: pullRequestTotal / issueTotal,
      issueTopFiveShare:
        [...currentActivity]
          .sort((a, b) => numberValue(b.issues_opened) - numberValue(a.issues_opened))
          .slice(0, 5)
          .reduce((sum, row) => sum + numberValue(row.issues_opened), 0) / issueTotal,
      pullRequestTopFiveShare:
        [...currentActivity]
          .sort((a, b) => numberValue(b.prs_opened) - numberValue(a.prs_opened))
          .slice(0, 5)
          .reduce((sum, row) => sum + numberValue(row.prs_opened), 0) / pullRequestTotal,
      issueTopFive: [...currentActivity]
        .sort((a, b) => numberValue(b.issues_opened) - numberValue(a.issues_opened))
        .slice(0, 5)
        .map((row) => ({ repo: row.repo_name, count: numberValue(row.issues_opened) })),
      pullRequestTopFive: [...currentActivity]
        .sort((a, b) => numberValue(b.prs_opened) - numberValue(a.prs_opened))
        .slice(0, 5)
        .map((row) => ({ repo: row.repo_name, count: numberValue(row.prs_opened) })),
      monthly: Array.from(new Set(repositoryMonthAll.map((row) => row.month)))
        .sort()
        .map((month) => {
          const rows = repositoryMonthAll.filter((row) => row.month === month);
          const issues = sumActivity(rows, "issues_opened_in_month");
          const pullRequests = sumActivity(rows, "prs_opened_in_month");
          return {
            month,
            label: new Date(`${month}-01T00:00:00Z`).toLocaleDateString("en-US", { month: "short", timeZone: "UTC" }),
            issues,
            pullRequests,
            ratio: pullRequests / issues,
          };
        }),
      niches: nicheOrder.map((key) => {
        const rows = currentActivity.filter((row) => row.collaboration_niche === key);
        const issues = sumActivity(rows, "issues_opened");
        const pullRequests = sumActivity(rows, "prs_opened");
        return {
          key,
          label: nicheLabels[key],
          repositories: rows.length,
          issues,
          issueUnresolvedShare:
            sumActivity(rows, "issues_unresolved_from_cohort") / issues,
          pullRequests,
          pullRequestUnresolvedShare:
            sumActivity(rows, "prs_unresolved_from_cohort") / pullRequests,
          ratio: pullRequests / issues,
        };
      }),
      constantCohortRepositories: constantCohortRepos.size,
      history: activityHistory,
      releases: {
        observationDays: 243,
        repositoriesWithRelease: releaseDays.filter((value) => value > 0).length,
        medianReleaseDays: quantileValue(releaseDays, 0.5),
        lowerQuartileReleaseDays: quantileValue(releaseDays, 0.25),
        upperQuartileReleaseDays: quantileValue(releaseDays, 0.75),
        buckets: releaseBuckets,
        leaders: [...repositoryProfile]
          .sort((a, b) => numberValue(b.github_release_days) - numberValue(a.github_release_days))
          .slice(0, 6)
          .map((row) => ({
            repo: row.repo_name,
            releaseDays: numberValue(row.github_release_days),
            releaseRecords: numberValue(row.github_releases),
          })),
      },
    },
    systemPressure: {
      matchedRepositories: numberValue(
        pressureRow("queue_flow", "matched_top100", 2026).repositories,
      ),
      roleFlows: nicheOrder.map((key) => {
        const row = pressureRow("queue_flow", "current_top100", 2026, key);
        const outcome = pressureRow(
          "fixed_90d_outcome",
          "current_top100",
          2026,
          key,
        );
        return {
          key,
          label: nicheLabels[key],
          repositories: numberValue(row.repositories),
          issuesOpened: numberValue(row.issues_opened),
          issueBalance: numberValue(row.issue_flow_balance),
          repositoriesWithPositiveIssueBalance: numberValue(
            row.repositories_with_positive_issue_balance,
          ),
          repositoryMedianIssueBalanceShare: numberValue(
            row.repo_median_issue_flow_balance_share,
          ),
          pullRequestsOpened: numberValue(row.prs_opened),
          pullRequestBalance: numberValue(row.pr_flow_balance),
          repositoriesWithPositivePullRequestBalance: numberValue(
            row.repositories_with_positive_pr_balance,
          ),
          repositoryMedianPullRequestBalanceShare: numberValue(
            row.repo_median_pr_flow_balance_share,
          ),
          repositoryMedianPullRequestUnresolved90dShare: numberValue(
            outcome.repo_median_pr_unresolved_90d_share,
          ),
          repositoryMedianPullRequestMerged90dShare: numberValue(
            outcome.repo_median_pr_merged_90d_share,
          ),
        };
      }),
      history: [2024, 2025, 2026].map((year) => {
        const flow = pressureRow("queue_flow", "matched_top100", year);
        const outcome = pressureRow("fixed_90d_outcome", "matched_top100", year);
        return {
          year,
          issuesOpened: numberValue(flow.issues_opened),
          issuesClosed: numberValue(flow.issues_closed),
          issuesOpenAtCutoff: numberValue(flow.issues_open_at_cutoff),
          issueBalance: numberValue(flow.issue_flow_balance),
          repositoriesWithPositiveIssueBalance: numberValue(
            flow.repositories_with_positive_issue_balance,
          ),
          pullRequestsOpened: numberValue(flow.prs_opened),
          pullRequestsClosed: numberValue(flow.prs_closed),
          pullRequestsOpenAtCutoff: numberValue(flow.prs_open_at_cutoff),
          pullRequestBalance: numberValue(flow.pr_flow_balance),
          repositoriesWithPositivePullRequestBalance: numberValue(
            flow.repositories_with_positive_pr_balance,
          ),
          issueUnresolved90dShare: numberValue(outcome.issue_unresolved_90d_share),
          pullRequestUnresolved90dShare: numberValue(outcome.pr_unresolved_90d_share),
          pullRequestMerged90dShare: numberValue(outcome.pr_merged_90d_share),
          repositoryMedianPullRequestMerged90dShare: numberValue(
            outcome.repo_median_pr_merged_90d_share,
          ),
        };
      }),
      pushHistory: [2024, 2025, 2026].map((year) => {
        const row = pressureRow(
          "push_concentration",
          "matched_top100",
          year,
          "Agentic AI Top 100",
        );
        return {
          year,
          pushActors: numberValue(row.median_push_actors),
          actorsForHalfOfPushes: numberValue(row.median_actors_for_50pct_pushes),
          topFiveActorShare: numberValue(row.median_top_5_actor_share),
        };
      }),
      pushBenchmarks: [
        ["Agentic AI Top 100", "matched_top100"],
        ["Cloud Native benchmark", "current_benchmark"],
        ["Big Data benchmark", "current_benchmark"],
      ].map(([label, panel]) => {
        const row = pressureRow("push_concentration", panel, 2026, label);
        return {
          label,
          repositories: numberValue(row.repositories),
          pushActors: numberValue(row.median_push_actors),
          actorsForHalfOfPushes: numberValue(row.median_actors_for_50pct_pushes),
          topFiveActorShare: numberValue(row.median_top_5_actor_share),
        };
      }),
    },
    threadPanel: {
      matchedRepositories: numberValue(threadPanel[0]?.repositories),
      years: threadPanel.map((row) => ({
        year: numberValue(row.year),
        threads: numberValue(row.threads),
        issues: numberValue(row.issues),
        pullRequests: numberValue(row.pull_requests),
        agentParticipationShare: numberValue(row.agent_participation_share),
        humanResponseWithin7dShare: numberValue(row.human_response_within_7d_share),
        maintainerResponseWithin7dShare: numberValue(
          row.maintainer_response_within_7d_share,
        ),
        issueResolvedWithin30dShare: numberValue(row.issue_resolved_within_30d_share),
        pullRequestResolvedWithin30dShare: numberValue(row.pr_resolved_within_30d_share),
        pullRequestReviewedShare: numberValue(row.pr_reviewed_share),
        pullRequestRequestedRevisionShare: numberValue(row.pr_requested_revision_share),
        requestedRevisionFollowedByCommitShare: numberValue(
          row.requested_revision_followed_by_commit_share,
        ),
        pullRequestTwoPlusRevisionShare: numberValue(
          row.pr_two_plus_requested_revision_share,
        ),
        medianRequestedRevisionCycles: numberValue(
          row.median_requested_revision_cycles_among_requested_prs,
        ),
        medianCommitsAfterFirstReview: numberValue(row.median_commits_after_first_review),
      })),
    },
    sampleThreads: numberValue(overall.threads),
    samplePullRequests: threadRows.filter((row) => row.item_type === "pull_request").length,
    activeRepositories: 100,
    codingAgentRepositories: markerSnapshot.filter(
      (row) => row.has_any_active_marker === "yes",
    ).length,
    agentMarkerCoverage,
    agentMarkerLeaders,
    observedParticipationRepositories: numberValue(strict.repositories_with_observed_participation),
    attributableAgentIdentities: attributableAgentActors.length,
    highConfidenceAgentIdentities: attributableAgentActors.filter(
      (row) => row.automation_role_confidence === "high",
    ).length,
    mediumConfidenceAgentIdentities: attributableAgentActors.filter(
      (row) => row.automation_role_confidence === "medium",
    ).length,
    botTypedAgentIdentities: attributableAgentActors.filter((row) =>
      row.github_types.split("|").includes("Bot"),
    ).length,
    userTypedAgentIdentities: attributableAgentActors.filter((row) =>
      row.github_types.split("|").includes("User"),
    ).length,
    appMediatedUserIdentities: attributableAgentActors.filter(
      (row) => row.automation_role === "agent_mediated_user",
    ).length,
    participationSampleThreads: numberValue(strict.threads_with_participation),
    participationOpenerSampleThreads: numberValue(strict.opener_threads),
    participationThreadShare: numberValue(strict.sample_thread_share),
    participationMacroShare: numberValue(strict.repository_mean_thread_share),
    participationOpenerShare: numberValue(strict.sample_opener_share),
    participationResponseShare: numberValue(overall.agent_participation_response_present_share_weighted),
    threadParticipationStages,
    knownAutomationShare: numberValue(overall.known_automation_bot_present_share_weighted),
    agentReviewShare: numberValue(overall.agent_review_event_present_share_pr_weighted),
    userReviewShare: numberValue(overall.human_account_review_event_present_share_pr_weighted),
    maintainerReviewShare: numberValue(overall.maintainer_account_review_event_present_share_pr_weighted),
    userGateShare: numberValue(overall.human_account_gate_share_resolved_with_visible_gate_weighted),
    maintainerGateShare: numberValue(overall.maintainer_account_gate_share_resolved_with_visible_gate_weighted),
    agentGateShare: numberValue(overall.agent_gate_share_resolved_with_visible_gate_weighted),
    userResponseShare: numberValue(overall.human_account_response_share_weighted),
    maintainerResponseShare: numberValue(overall.maintainer_account_response_share_weighted),
    externalPrShare: numberValue(overall.external_pr_author_share_weighted),
    externalMergeFlagShare: numberValue(overall.external_pr_github_merge_flag_share_resolved_fixed_maturity_weighted),
    internalMergeFlagShare: numberValue(overall.internal_pr_github_merge_flag_share_resolved_fixed_maturity_weighted),
    explicitInvitations: policyCount(["explicit_invitation"]),
    gatedPolicies: policyCount(["conditional_gate", "issue_first", "conditional_restriction"]),
    restrictedCreationPolicies: policyCount(["collaborators_only", "pull_requests_disabled"]),
    noDetectedPolicySignal: policyCount(["no_detected_policy_signal"]),
    top100PrUnresolvedMedian: numberValue(top100.pr_unresolved_share_median_repo),
    controlPrUnresolvedMedian: numberValue(control.pr_unresolved_share_median_repo),
    controlsWithRisingPrBacklog: transitions.filter(
      (row) => numberValue(row.pr_unresolved_share_change) > 0,
    ).length,
    controlsTotal: transitions.length,
    reviewedPrShare: numberValue(overall.pr_review_observed_share_weighted),
    reviewedPrFollowupCommitShare: numberValue(overall.reviewed_pr_post_review_commit_share_weighted),
    firstReviewAgentPrs: numberValue(overall.first_review_agent_prs_count),
    firstReviewAgentFollowupCommits: numberValue(overall.first_review_agent_prs_followup_commit_count),
    firstReviewAgentFollowupShare: numberValue(overall.first_review_agent_prs_followup_commit_share),
    firstReviewGithubUserPrs: numberValue(overall.first_review_github_user_prs_count),
    firstReviewGithubUserFollowupCommits: numberValue(overall.first_review_github_user_prs_followup_commit_count),
    firstReviewGithubUserFollowupShare: numberValue(overall.first_review_github_user_prs_followup_commit_share),
    changeRequestPrs: countThreads(
      pullRequestThreads,
      (row) => row.change_request_observed === "yes",
    ),
    changeRequestFollowupCommits: countThreads(
      pullRequestThreads,
      (row) =>
        row.change_request_observed === "yes" &&
        row.change_request_followed_by_commit === "yes",
    ),
    changeRequestFollowupCommitShare: numberValue(overall.change_requested_pr_followup_commit_share_weighted),
    agentChangeRequestPrs: countThreads(
      pullRequestThreads,
      (row) => row.agent_change_request_present === "yes",
    ),
    agentChangeRequestFollowupCommits: countThreads(
      pullRequestThreads,
      (row) =>
        row.agent_change_request_present === "yes" &&
        row.change_request_followed_by_commit === "yes",
    ),
    agentChangeRequestFollowupCommitShare: numberValue(overall.agent_change_requested_pr_followup_commit_share_weighted),
    humanChangeRequestPrs: countThreads(
      pullRequestThreads,
      (row) => row.human_account_change_request_present === "yes",
    ),
    humanChangeRequestFollowupCommits: countThreads(
      pullRequestThreads,
      (row) =>
        row.human_account_change_request_present === "yes" &&
        row.change_request_followed_by_commit === "yes",
    ),
    humanChangeRequestFollowupCommitShare: numberValue(overall.human_change_requested_pr_followup_commit_share_weighted),
    publicEventsAnalyzed: threadAnalysisRun.events_within_window,
    agentTaskEvents: {
      review: taskEvents("code_review"),
      triage: taskEvents("triage_and_routing") + taskEvents("review_routing"),
      discussion: taskEvents("discussion_comment"),
      codeCommit: taskEvents("code_commit"),
      openedThread: taskEvents("opened_issue") + taskEvents("opened_pull_request"),
    },
    automationByItem: [
      { label: "Issues", row: issueSummary },
      { label: "Pull requests", row: pullRequestSummary },
    ].map(({ label, row }) => ({
      label: label as "Issues" | "Pull requests",
      knownAutomation: numberValue(row.known_automation_bot_present_share_weighted),
      verifiedAgent: numberValue(row.agent_participation_present_share_weighted),
      conventionalAutomation: numberValue(row.conventional_automation_present_share_weighted),
      automationOnly: numberValue(row.automation_only_visible_thread_share_weighted),
    })),
    markerTransitions: {
      strict: transitionCounts("strict_transition"),
      active: transitionCounts("any_active_transition"),
    },
    projectStages,
    codeLineages,
    efficiencyExperiment: {
      sampleThreads: efficiencyValidation.threads,
      eligibleSevenDayThreads: efficiencyValidation.eligible_7d_threads,
      eligibleThirtyDayThreads: efficiencyValidation.eligible_30d_threads,
      timelineCompleteness: efficiencyValidation.timeline_completeness,
      population: {
        earlier: numberValue(efficiencyVolumeYear("2025").population_threads),
        later: numberValue(efficiencyVolumeYear("2026").population_threads),
        growth: numberValue(
          efficiencyVolumeYear("2026").population_change_from_2025,
        ),
      },
      adoption: {
        allAgentsEarlier: numberValue(
          efficiencyPanelMetric("agent_visible_30d", "all").earlier_value,
        ),
        allAgentsLater: numberValue(
          efficiencyPanelMetric("agent_visible_30d", "all").later_value,
        ),
        codingReviewEarlier: numberValue(
          efficiencyPanelMetric(
            "coding_or_review_agent_visible_30d",
            "all",
          ).earlier_value,
        ),
        codingReviewLater: numberValue(
          efficiencyPanelMetric(
            "coding_or_review_agent_visible_30d",
            "all",
          ).later_value,
        ),
      },
      panel: [
        ["human_response_7d", "all", "Human response within 7 days", "percent", "efficiency"],
        ["maintainer_response_7d", "all", "Maintainer response within 7 days", "percent", "efficiency"],
        ["issue_closed_30d", "issue", "Issues closed within 30 days", "percent", "efficiency"],
        ["pr_merged_30d", "pull_request", "Pull requests merged within 30 days", "percent", "efficiency"],
        ["maintainer_actions_30d", "all", "Maintainer actions per thread", "count", "burden"],
        ["maintainer_review_events_30d", "pull_request", "Maintainer reviews per pull request", "count", "burden"],
      ].map(([key, scope, label, format, direction]) => {
        const row = efficiencyPanelMetric(key, scope);
        return {
          key,
          label,
          earlier: numberValue(row.earlier_value),
          later: numberValue(row.later_value),
          format: format as "percent" | "count",
          direction: direction as "efficiency" | "burden",
        };
      }),
      exposure: [
        ["pr_merged_30d", "pull_request", "30-day merge rate", "percent", "outcome"],
        ["conversation_runs_30d", "all", "Conversation runs", "count", "iteration"],
        ["maintainer_review_events_30d", "pull_request", "Maintainer reviews", "count", "iteration"],
        ["commits_after_first_review_30d", "pull_request", "Commits after first review", "count", "iteration"],
      ].map(([key, scope, label, format, direction]) => {
        const row = efficiencyExposureMetric(key, scope);
        return {
          key,
          label,
          agentVisible: numberValue(row.agent_exposed_value),
          noVisibleAgent: numberValue(row.no_visible_agent_value),
          format: format as "percent" | "count",
          direction: direction as "outcome" | "iteration",
        };
      }),
      maintainerActionEstimate: {
        earlier: numberValue(
          efficiencyVolumeYear("2025").estimated_maintainer_actions_30d,
        ),
        later: numberValue(
          efficiencyVolumeYear("2026").estimated_maintainer_actions_30d,
        ),
        laterLow: numberValue(
          efficiencyVolumeYear("2026").estimated_maintainer_actions_ci_low,
        ),
        laterHigh: numberValue(
          efficiencyVolumeYear("2026").estimated_maintainer_actions_ci_high,
        ),
      },
    },
  };
}

const agentMacroByStage: Record<Exclude<StageId, "model">, string> = {
  application: "Application",
  framework: "Framework",
  runtime: "Runtime",
};

function modelMacro(zone: string) {
  if (zone.startsWith("Serving") || zone === "Model API gateways") {
    return "Serving";
  }
  if (zone.startsWith("Pre-Train")) return "Pre-Train";
  if (zone.startsWith("Post-Train")) return "Post-Train";
  if (zone.startsWith("Data")) return "Data";
  return "Compute";
}

function projectGrowth(project: LandscapeProject) {
  const april = project.trend[8];
  const july = project.trend[11];
  if (typeof april !== "number" || typeof july !== "number") return null;
  return Math.round((july - april) * 100) / 100;
}

const LANGUAGE_GROUPS = ["TypeScript", "Python", "Go", "C++"] as const;

function languageMix(projects: LandscapeProject[]) {
  const agentProjects = projects.filter((project) => project.stage !== "model");
  const modelProjects = projects.filter((project) => project.stage === "model");

  return [...LANGUAGE_GROUPS, "Other"].map((label) => {
    const belongs = (project: LandscapeProject) =>
      label === "Other"
        ? !LANGUAGE_GROUPS.includes(
            project.language as (typeof LANGUAGE_GROUPS)[number],
          )
        : project.language === label;

    return {
      label,
      agent: agentProjects.filter(belongs).length,
      model: modelProjects.filter(belongs).length,
    };
  });
}

const OPENRANK_MONTHS = [
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
] as const;

function trendValue(project: LandscapeProject, index: number) {
  const value = project.trend[index];
  return typeof value === "number" ? value : null;
}

function sumTrend(projects: LandscapeProject[], index: number) {
  return projects.reduce(
    (sum, project) => sum + (trendValue(project, index) ?? 0),
    0,
  );
}

function infraTrendStats(
  projects: LandscapeProject[],
  layer: "agent" | "model",
): InfraTrendStats {
  const domainLabels = [...new Set(projects.map((project) => project.zone))];
  const latestValues = projects
    .map((project) => trendValue(project, 11))
    .filter((value): value is number => value !== null);
  const totalStars = projects.reduce((sum, project) => sum + project.stars, 0);
  const totalContributors = projects.reduce(
    (sum, project) => sum + (project.contributors ?? 0),
    0,
  );
  const totalOpenrank = latestValues.reduce((sum, value) => sum + value, 0);
  const languageGroups = new Map<string, LandscapeProject[]>();
  projects.forEach((project) => {
    const label = project.language === "—" ? "Other" : project.language;
    const grouped = languageGroups.get(label) ?? [];
    grouped.push(project);
    languageGroups.set(label, grouped);
  });
  const leadingLanguages = [...languageGroups.entries()]
    .map(([label, grouped]) => ({
      label,
      grouped,
      openrank: sumTrend(grouped, 11),
    }))
    .sort(
      (a, b) =>
        b.openrank - a.openrank || b.grouped.length - a.grouped.length,
    );
  const displayedLanguages = leadingLanguages.slice(0, 4);
  const otherProjects = leadingLanguages
    .slice(4)
    .flatMap((item) => item.grouped);
  if (otherProjects.length) {
    displayedLanguages.push({
      label: "Other",
      grouped: otherProjects,
      openrank: sumTrend(otherProjects, 11),
    });
  }

  const miniMaxProject = projects.find(
    (project) => project.repo.toLowerCase() === "minimax-ai/minimax-code",
  );

  return {
    layer,
    projects: projects.length,
    stars: totalStars,
    contributors: totalContributors,
    openrank: Math.round(totalOpenrank * 10) / 10,
    openrankCoverage: latestValues.length,
    monthly: OPENRANK_MONTHS.map((month, index) => ({
      month,
      label: month.slice(2).replace("-", "."),
      value: Math.round(sumTrend(projects, index) * 10) / 10,
    })),
    domains: domainLabels.map((label) => {
      const grouped = projects.filter(
        (project) => project.zone === label,
      );
      return {
        label,
        projects: grouped.length,
        stars: grouped.reduce((sum, project) => sum + project.stars, 0),
        contributors: grouped.reduce(
          (sum, project) => sum + (project.contributors ?? 0),
          0,
        ),
        openrank: Math.round(sumTrend(grouped, 11) * 10) / 10,
        openrankCoverage: grouped.filter(
          (project) => trendValue(project, 11) !== null,
        ).length,
        delta:
          Math.round((sumTrend(grouped, 11) - sumTrend(grouped, 10)) * 10) /
          10,
      };
    }),
    languages: displayedLanguages.map(({ label, grouped, openrank }) => {
      const stars = grouped.reduce((sum, project) => sum + project.stars, 0);
      const contributors = grouped.reduce(
        (sum, project) => sum + (project.contributors ?? 0),
        0,
      );
      return {
        label,
        projects: grouped.length,
        stars,
        contributors,
        openrank: Math.round(openrank * 10) / 10,
        projectShare: Math.round((grouped.length / projects.length) * 100),
        starShare: Math.round((stars / totalStars) * 100),
        openrankShare: Math.round((openrank / totalOpenrank) * 100),
      };
    }),
    scaleLeaders: projects
      .map((project) => ({ project, openrank: trendValue(project, 11) }))
      .filter(
        (item): item is { project: LandscapeProject; openrank: number } =>
          item.openrank !== null,
      )
      .sort((a, b) => b.openrank - a.openrank)
      .slice(0, 6)
      .map(({ project, openrank }) => ({
        name: project.name,
        repo: project.repo,
        zone: project.zone,
        openrank,
        stars: project.stars,
        contributors: project.contributors ?? 0,
      })),
    momentumLeaders: projects
      .map((project) => {
        const july = trendValue(project, 10);
        const august = trendValue(project, 11);
        return {
          project,
          august,
          delta:
            july === null || august === null
              ? null
              : Math.round((august - july) * 100) / 100,
        };
      })
      .filter(
        (
          item,
        ): item is {
          project: LandscapeProject;
          august: number;
          delta: number;
        } => item.august !== null && item.delta !== null && item.delta > 0,
      )
      .sort((a, b) => b.delta - a.delta)
      .slice(0, 6)
      .map(({ project, august, delta }) => ({
        name: project.name,
        repo: project.repo,
        zone: project.zone,
        delta,
        openrank: august,
        stars: project.stars,
        contributors: project.contributors ?? 0,
      })),
    miniMax: miniMaxProject
      ? {
          name: miniMaxProject.name,
          repo: miniMaxProject.repo,
          stars: miniMaxProject.stars,
          contributors: miniMaxProject.contributors ?? 0,
          createdAt: miniMaxProject.createdAt,
          openrankIndexed: trendValue(miniMaxProject, 11) !== null,
        }
      : null,
  };
}

const RUNTIME_PATH = [
  { label: "Memory, knowledge & context", shortLabel: "Context" },
  { label: "Protocols & interoperability", shortLabel: "Interface" },
  { label: "Tools, web & computer use", shortLabel: "Action" },
  { label: "Development sandboxes", shortLabel: "Isolation" },
  { label: "Observability & evaluation", shortLabel: "Evidence" },
] as const;

function runtimePath(projects: LandscapeProject[]) {
  return RUNTIME_PATH.map(({ label, shortLabel }) => {
    const grouped = projects
      .filter((project) => project.zone === label)
      .sort(
        (a, b) =>
          (b.openrank ?? -1) - (a.openrank ?? -1) || b.stars - a.stars,
      );

    return {
      label,
      shortLabel,
      projects: grouped.length,
      examples: grouped.slice(0, 2).map((project) => ({
        name: project.name,
        repo: project.repo,
      })),
    };
  });
}

function buildMacroGroups(
  projects: LandscapeProject[],
  labels: string[],
  groupForProject: (project: LandscapeProject) => string,
  mayRepositories: Set<string>,
) {
  const totalOpenrank = projects.reduce(
    (sum, project) => sum + (project.openrank ?? 0),
    0,
  );

  return labels.map((label) => {
    const groupedProjects = projects.filter(
      (project) => groupForProject(project) === label,
    );
    const openrank = groupedProjects.reduce(
      (sum, project) => sum + (project.openrank ?? 0),
      0,
    );

    return {
      label,
      projects: groupedProjects.length,
      projectShare: Math.round((groupedProjects.length / projects.length) * 100),
      openrank: Math.round(openrank * 10) / 10,
      openrankShare: Math.round((openrank / totalOpenrank) * 100),
      newlyTracked: groupedProjects.filter(
        (project) => !mayRepositories.has(project.repo.toLowerCase()),
      ).length,
    };
  });
}

export function getInclusionResearchData() {
  const projects = getLandscapeProjects();
  const agentProjects = projects.filter((project) => project.stage !== "model");
  const modelProjects = projects.filter((project) => project.stage === "model");
  const mayRepositories = new Set(
    getMay2026TrackedRepositories().map((repo) => repo.toLowerCase()),
  );
  const currentTracked = getLandscapePoolRepositories().length;
  const outsideMay = projects.filter(
    (project) => !mayRepositories.has(project.repo.toLowerCase()),
  );
  const stats: InclusionResearchStats = {
    total: projects.length,
    agent: agentProjects.length,
    model: modelProjects.length,
    mayTracked: mayRepositories.size,
    currentTracked,
    trackedDelta: currentTracked - mayRepositories.size,
    selectedOutsideMay: outsideMay.length,
    agentOutsideMay: outsideMay.filter((project) => project.stage !== "model")
      .length,
    runtimeOutsideMay: outsideMay.filter(
      (project) => project.stage === "runtime",
    ).length,
    runtimeOutsideMayProjects: outsideMay
      .filter((project) => project.stage === "runtime")
      .map((project) => ({
        name: project.name,
        repo: project.repo,
        zone: project.zone,
      })),
    agentRecent: agentProjects.filter(
      (project) => project.createdAt >= "2025-01-01",
    ).length,
    modelRecent: modelProjects.filter(
      (project) => project.createdAt >= "2025-01-01",
    ).length,
    agentMacro: buildMacroGroups(
      agentProjects,
      ["Application", "Framework", "Runtime"],
      (project) => agentMacroByStage[project.stage as Exclude<StageId, "model">],
      mayRepositories,
    ),
    modelMacro: buildMacroGroups(
      modelProjects,
      ["Serving", "Pre-Train", "Data", "Compute", "Post-Train"],
      (project) => modelMacro(project.zone),
      mayRepositories,
    ),
    growthLeaders: projects
      .map((project) => ({ project, growth: projectGrowth(project) }))
      .filter(
        (item): item is { project: LandscapeProject; growth: number } =>
          typeof item.growth === "number" && item.growth > 0,
      )
      .sort((a, b) => b.growth - a.growth)
      .slice(0, 6)
      .map(({ project, growth }) => ({
        name: project.name,
        repo: project.repo,
        zone: project.zone,
        growth,
      })),
    languageMix: languageMix(projects),
    runtimePath: runtimePath(agentProjects),
    infraTrends: {
      agent: infraTrendStats(agentProjects, "agent"),
      model: infraTrendStats(modelProjects, "model"),
    },
    collaboration: collaborationResearchStats(),
  };

  return { projects, stats };
}
import fs from "node:fs";
import path from "node:path";
