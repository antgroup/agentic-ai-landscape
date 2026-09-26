import type { Metadata } from "next";

import { getMiniMaxDeveloperPresentationCopy } from "@/lib/minimax-developer-presentation-copy";

import { getInclusionResearchData } from "../260910_inclusion/research-data";
import InclusionPresentation from "../260910_inclusion/present/presentation";

export const metadata: Metadata = {
  title: "Agent 进入开源协作之后 | MiniMax Developer",
  description:
    "从 Agentic AI Landscape、生态趋势到仓库协作模式的中文演讲。",
};

export default function MiniMaxDeveloperPresentationPage() {
  const { projects, stats } = getInclusionResearchData();
  const initialCopy = getMiniMaxDeveloperPresentationCopy();

  return (
    <InclusionPresentation
      copyEndpoint="/api/minimax-developer-presentation-copy"
      initialCopy={initialCopy}
      inlineLandscapeRankings
      projects={projects}
      stats={stats}
    />
  );
}
