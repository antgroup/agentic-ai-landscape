import "server-only";

import fs from "node:fs";
import path from "node:path";

export const PRESENTATION_COPY_KEYS = [
  "coverTitleLine1",
  "coverTitleLine2",
  "coverSubtitle",
  "evolutionTitle",
  "evolutionBody",
  "evolution2025Label",
  "evolution2026Label",
  "evolutionInclusionLabel",
  "coverSpeakerName",
  "coverSpeakerOrg",
  "coverEvent",
  "coverDate",
  "questionKicker",
  "questionTitle",
  "questionBody",
  "questionIssueLabel",
  "questionPrLabel",
  "questionAgentLabel",
  "questionResolutionLabel",
  "agentTrendTitle",
  "agentTrendBody",
  "modelTrendTitle",
  "modelTrendBody",
  "landscapeTrendTitle",
  "landscapeTrendBody",
  "agentInsight1Angle",
  "agentInsight1Metric",
  "agentInsight1Title",
  "agentInsight1Note",
  "agentInsight2Angle",
  "agentInsight2Metric",
  "agentInsight2Title",
  "agentInsight2Note",
  "agentInsight3Angle",
  "agentInsight3Metric",
  "agentInsight3Title",
  "agentInsight3Note",
  "agentRankingLabel",
  "modelInsight1Angle",
  "modelInsight1Metric",
  "modelInsight1Title",
  "modelInsight1Note",
  "modelInsight2Angle",
  "modelInsight2Metric",
  "modelInsight2Title",
  "modelInsight2Note",
  "modelInsight3Angle",
  "modelInsight3Metric",
  "modelInsight3Title",
  "modelInsight3Note",
  "modelRankingLabel",
  "languageTrendTitle",
  "languageTrendBody",
  "runtimeTrendTitle",
  "runtimeTrendBody",
  "flowTitle",
  "flowBody",
  "flowIssueLabel",
  "flowPrLabel",
  "flowNote",
  "backlogTitle",
  "backlogBody",
  "backlogScope",
  "coreTitle",
  "coreBody",
  "coreHistoryTitle",
  "coreBenchmarkTitle",
  "accessTitle",
  "accessBody",
  "accessReadyTitle",
  "accessReadyBody",
  "accessPolicyTitle",
  "accessPolicyNote",
  "handoffTitle",
  "handoffBody",
  "handoffNote",
  "tasksTitle",
  "tasksBody",
  "reviewTitle",
  "reviewBody",
  "reviewNote",
  "lineageTitle",
  "lineageBody",
  "outcomesTitle",
  "outcomesBody",
  "outcomesNote",
  "deepseekKicker",
  "deepseekTitle",
  "deepseekBody",
  "deepseekQuote",
  "closingKicker",
  "closingTitleLine1",
  "closingTitleLine2",
  "closingBody",
  "closingLink",
  "closingPathCode",
  "closingPathResponse",
  "closingPathReview",
  "closingPathMerge",
  "closingPathMaintain",
  "closingWebsiteLabel",
  "closingGithubLabel",
  "closingHuggingFaceLabel",
  "closingXLabel",
  "closingTalkLabel",
  "closingQrNote",
] as const;

export type PresentationCopyKey = (typeof PRESENTATION_COPY_KEYS)[number];
type OptionalPresentationCopyKey =
  | "coverSubtitle"
  | "evolutionTitle"
  | "evolutionBody"
  | "evolution2025Label"
  | "evolution2026Label"
  | "evolutionInclusionLabel"
  | "closingWebsiteLabel"
  | "closingGithubLabel"
  | "closingHuggingFaceLabel"
  | "closingXLabel"
  | "closingTalkLabel"
  | "closingQrNote";
type RequiredPresentationCopyKey = Exclude<
  PresentationCopyKey,
  OptionalPresentationCopyKey
>;

const OPTIONAL_PRESENTATION_COPY_KEYS: readonly OptionalPresentationCopyKey[] = [
  "coverSubtitle",
  "evolutionTitle",
  "evolutionBody",
  "evolution2025Label",
  "evolution2026Label",
  "evolutionInclusionLabel",
  "closingWebsiteLabel",
  "closingGithubLabel",
  "closingHuggingFaceLabel",
  "closingXLabel",
  "closingTalkLabel",
  "closingQrNote",
];

export type PresentationCopy = Record<RequiredPresentationCopyKey, string> &
  Partial<Record<OptionalPresentationCopyKey, string>>;

const PRESENTATION_COPY_RELATIVE_PATH = path.join(
  "insights",
  "presentations",
  "260910-InclusionConf",
  "presentation-copy.json",
);

function resolvePresentationCopyPath() {
  const candidates = [
    path.resolve(process.cwd(), "../..", PRESENTATION_COPY_RELATIVE_PATH),
    path.resolve(process.cwd(), PRESENTATION_COPY_RELATIVE_PATH),
    path.resolve(process.cwd(), "../../../..", PRESENTATION_COPY_RELATIVE_PATH),
  ];

  const existing = candidates.find((candidate) => fs.existsSync(candidate));
  if (!existing) {
    throw new Error(
      `Unable to locate presentation copy at ${PRESENTATION_COPY_RELATIVE_PATH}`,
    );
  }
  return existing;
}

export function validatePresentationCopy(
  value: unknown,
): value is PresentationCopy {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  const keys = Object.keys(record);

  const requiredKeys = PRESENTATION_COPY_KEYS.filter(
    (key): key is RequiredPresentationCopyKey =>
      !OPTIONAL_PRESENTATION_COPY_KEYS.includes(
        key as OptionalPresentationCopyKey,
      ),
  );

  return (
    requiredKeys.every(
      (key) =>
        typeof record[key] === "string" &&
        (record[key] as string).length <= 12_000,
    ) &&
    keys.every(
      (key) =>
        PRESENTATION_COPY_KEYS.includes(key as PresentationCopyKey) &&
        typeof record[key] === "string" &&
        (record[key] as string).length <= 12_000,
    )
  );
}

export function getPresentationCopy(): PresentationCopy {
  const parsed: unknown = JSON.parse(
    fs.readFileSync(resolvePresentationCopyPath(), "utf8"),
  );
  if (!validatePresentationCopy(parsed)) {
    throw new Error("Invalid Inclusion Conference presentation-copy.json schema");
  }
  return parsed;
}

export async function writePresentationCopy(copy: PresentationCopy) {
  const target = resolvePresentationCopyPath();
  const temporary = `${target}.tmp`;
  await fs.promises.writeFile(temporary, `${JSON.stringify(copy, null, 2)}\n`);
  await fs.promises.rename(temporary, target);
}
