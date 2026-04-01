"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { UseCase, Evaluation, BusinessCase } from "@/types";
import { ScoreRadar } from "@/components/ScoreRadar";

interface Props {
  id: string;
}

export function BusinessCaseViewer({ id }: Props) {
  const [useCase, setUseCase] = useState<UseCase | null>(null);
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [businessCase, setBusinessCase] = useState<BusinessCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      api.useCases.get(id),
      api.evaluations.list(id).catch(() => []),
      api.businessCases.get(id).catch(() => null),
    ])
      .then(([uc, evals, bc]) => {
        setUseCase(uc);
        setEvaluations(evals);
        setBusinessCase(bc);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const handleApprove = async () => {
    setActionLoading(true);
    try {
      await api.businessCases.approve(id);
      setUseCase((prev) => prev && { ...prev, status: "approved" });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    const reason = prompt("Reason for rejection:");
    if (!reason) return;
    setActionLoading(true);
    try {
      await api.businessCases.reject(id, reason);
      setUseCase((prev) => prev && { ...prev, status: "rejected" });
    } finally {
      setActionLoading(false);
    }
  };

  const handleGenerateBusinessCase = async () => {
    setActionLoading(true);
    try {
      await api.businessCases.generate(id);
      const bc = await api.businessCases.get(id);
      setBusinessCase(bc);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="text-gray-500 text-sm">Loading...</div>;
  if (!useCase) return <div className="text-red-500 text-sm">Use case not found.</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main content */}
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <h1 className="text-xl font-bold text-gray-900">{useCase.title}</h1>
            <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium capitalize">
              {useCase.status.replace("_", " ")}
            </span>
          </div>
          <p className="text-gray-700 text-sm leading-relaxed">
            {useCase.problem_statement}
          </p>
        </div>

        {businessCase ? (
          <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
            <h2 className="text-lg font-semibold text-gray-900">
              Business Case
            </h2>
            {[
              ["Executive Summary", businessCase.executive_summary],
              ["Problem & Opportunity", businessCase.problem_and_opportunity],
              ["Proposed Solution", businessCase.proposed_solution],
              ["Cost-Benefit Analysis", businessCase.cost_benefit_analysis],
              ["Risks & Mitigations", businessCase.risks_and_mitigations],
              ["Timeline", businessCase.timeline],
            ].map(([title, content]) => (
              <section key={title}>
                <h3 className="text-sm font-semibold text-gray-800 mb-1">
                  {title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {content}
                </p>
              </section>
            ))}
            <div className="pt-4 border-t border-gray-100 flex gap-3">
              <span
                className={`text-sm font-semibold px-3 py-1 rounded-full ${
                  businessCase.recommendation === "go"
                    ? "bg-green-100 text-green-700"
                    : businessCase.recommendation === "no_go"
                    ? "bg-red-100 text-red-700"
                    : "bg-yellow-100 text-yellow-700"
                }`}
              >
                Recommendation:{" "}
                {businessCase.recommendation.replace("_", " ").toUpperCase()}
              </span>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
            <p className="text-gray-500 text-sm mb-4">
              No business case generated yet.
            </p>
            <button
              onClick={handleGenerateBusinessCase}
              disabled={actionLoading}
              className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {actionLoading ? "Generating..." : "Generate Business Case"}
            </button>
          </div>
        )}
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {evaluations.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Evaluation Scores
            </h3>
            <ScoreRadar evaluations={evaluations} />
            <div className="mt-3 space-y-2">
              {evaluations.map((e) => (
                <div key={e.dimension} className="flex items-start gap-2">
                  <span className="text-xs font-medium text-gray-700 w-24 capitalize flex-shrink-0">
                    {e.dimension}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full"
                          style={{ width: `${e.score * 10}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600 w-6">
                        {e.score}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {useCase.status === "review" && businessCase && (
          <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-900">Decision</h3>
            <button
              onClick={handleApprove}
              disabled={actionLoading}
              className="w-full bg-green-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              Approve
            </button>
            <button
              onClick={handleReject}
              disabled={actionLoading}
              className="w-full bg-red-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              Reject
            </button>
          </div>
        )}

        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Details</h3>
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-gray-500 text-xs">Urgency</dt>
              <dd className="text-gray-800 capitalize">{useCase.urgency}</dd>
            </div>
            <div>
              <dt className="text-gray-500 text-xs">Composite Score</dt>
              <dd className="text-gray-800">
                {useCase.composite_score !== null
                  ? Math.round(useCase.composite_score)
                  : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500 text-xs">Created</dt>
              <dd className="text-gray-800">
                {new Date(useCase.created_at).toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
}
