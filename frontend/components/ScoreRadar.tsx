"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { Evaluation } from "@/types";

interface Props {
  evaluations: Evaluation[];
}

const DIMENSION_LABELS: Record<string, string> = {
  security: "Security",
  feasibility: "Feasibility",
  cost: "Cost",
  value: "Business Value",
};

export function ScoreRadar({ evaluations }: Props) {
  const data = evaluations.map((e) => ({
    dimension: DIMENSION_LABELS[e.dimension] ?? e.dimension,
    score: e.score,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.3}
        />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
}
