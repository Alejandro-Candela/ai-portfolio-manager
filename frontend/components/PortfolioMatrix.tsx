"use client";

import { useEffect, useState } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { api } from "@/lib/api";
import type { UseCase } from "@/types";
import { useRouter } from "next/navigation";

const RISK_COLORS: Record<string, string> = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#7c3aed",
};

function getRisk(evaluations: { dimension: string; score: number }[]): string {
  const sec = evaluations.find((e) => e.dimension === "security");
  if (!sec) return "medium";
  if (sec.score >= 8) return "low";
  if (sec.score >= 5) return "medium";
  if (sec.score >= 3) return "high";
  return "critical";
}

interface ChartPoint {
  id: string;
  title: string;
  x: number; // business value
  y: number; // feasibility
  z: number; // cost (bubble size)
  risk: string;
}

export function PortfolioMatrix() {
  const [data, setData] = useState<ChartPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api.useCases
      .list()
      .then(async (cases) => {
        const points = await Promise.all(
          cases
            .filter((c: UseCase) => c.composite_score !== null)
            .map(async (c: UseCase) => {
              let evals: { dimension: string; score: number }[] = [];
              try {
                evals = await api.evaluations.list(c.id);
              } catch {
                // evaluations may not be available yet
              }

              const value =
                evals.find((e) => e.dimension === "value")?.score ?? 5;
              const feasibility =
                evals.find((e) => e.dimension === "feasibility")?.score ?? 5;
              const cost =
                evals.find((e) => e.dimension === "cost")?.score ?? 5;

              return {
                id: c.id,
                title: c.title,
                x: value,
                y: feasibility,
                z: (11 - cost) * 10, // inverse: lower cost = smaller bubble
                risk: getRisk(evals),
              };
            })
        );
        setData(points);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-gray-500 text-sm">Loading...</div>;
  if (data.length === 0)
    return (
      <div className="text-gray-500 text-sm">
        No scored use cases yet. Submit one via{" "}
        <a href="/intake" className="text-blue-600 underline">
          Intake
        </a>
        .
      </div>
    );

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <ResponsiveContainer width="100%" height={480}>
        <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            type="number"
            dataKey="x"
            domain={[0, 10]}
            label={{
              value: "Business Value",
              position: "insideBottom",
              offset: -20,
            }}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={[0, 10]}
            label={{
              value: "Feasibility",
              angle: -90,
              position: "insideLeft",
              offset: 20,
            }}
          />
          <Tooltip
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload as ChartPoint;
              return (
                <div className="bg-white border border-gray-200 rounded p-3 shadow text-sm">
                  <p className="font-medium">{d.title}</p>
                  <p className="text-gray-600">Value: {d.x}/10</p>
                  <p className="text-gray-600">Feasibility: {d.y}/10</p>
                </div>
              );
            }}
          />
          <Scatter
            data={data}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            onClick={(data: any) => {
              const useCaseId = (data && data.payload && data.payload.id) || (data && data.id);
              if (useCaseId) router.push(`/cases/${useCaseId}`);
            }}
            style={{ cursor: "pointer" }}
          >
            {data.map((entry) => (
              <Cell
                key={entry.id}
                fill={RISK_COLORS[entry.risk] ?? "#6b7280"}
                fillOpacity={0.7}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 text-xs text-gray-600 justify-center">
        {Object.entries(RISK_COLORS).map(([label, color]) => (
          <span key={label} className="flex items-center gap-1">
            <span
              className="w-3 h-3 rounded-full inline-block"
              style={{ backgroundColor: color }}
            />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
