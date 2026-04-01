export type UseCaseStatus =
  | "new"
  | "evaluating"
  | "scored"
  | "business_case"
  | "review"
  | "approved"
  | "rejected"
  | "archived";

export interface UseCase {
  id: string;
  tenant_id: string;
  title: string;
  description: string;
  problem_statement: string;
  stakeholders: string[];
  available_data: string;
  expected_outcome: string;
  urgency: "low" | "medium" | "high" | "critical";
  status: UseCaseStatus;
  composite_score: number | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Evaluation {
  id: string;
  use_case_id: string;
  dimension: "security" | "feasibility" | "cost" | "value";
  score: number;
  justification: string;
  model_used: string;
  created_at: string;
}

export interface BusinessCase {
  id: string;
  use_case_id: string;
  executive_summary: string;
  problem_and_opportunity: string;
  proposed_solution: string;
  cost_benefit_analysis: string;
  risks_and_mitigations: string;
  timeline: string;
  recommendation: "go" | "no_go" | "conditional";
  status: "draft" | "critic_review" | "pending_human" | "approved" | "rejected";
  created_at: string;
  updated_at: string;
}

export interface ScoringConfig {
  tenant_id: string;
  security_weight: number;
  feasibility_weight: number;
  cost_weight: number;
  value_weight: number;
}

export interface ApiError {
  detail: string;
}
