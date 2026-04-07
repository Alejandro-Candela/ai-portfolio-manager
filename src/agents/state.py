from __future__ import annotations

import operator
from typing import Annotated

from copilotkit import CopilotKitState
from langgraph.graph import MessagesState
from pydantic import BaseModel


class EvaluationResult(BaseModel):
    dimension: str  # security | feasibility | cost | value
    score: float  # 1-10
    justification: str


class UseCaseData(BaseModel):
    id: str = ""
    title: str = ""
    problem_statement: str = ""
    description: str = ""
    stakeholders: list[str] = []
    available_data: str = ""
    expected_outcome: str = ""
    urgency: str = "medium"
    tenant_id: str = ""


# State for intake graph — uses CopilotKitState to receive frontend actions
class IntakeState(CopilotKitState):
    use_case: UseCaseData | None = None
    extraction_complete: bool = False


# State for each evaluator (fan-out subgraph)
class EvaluatorState(BaseModel):
    use_case: UseCaseData
    result: EvaluationResult | None = None


# State for the top-level evaluation graph
class EvaluationGraphState(BaseModel):
    use_case: UseCaseData
    evaluations: Annotated[list[EvaluationResult], operator.add]
    all_complete: bool = False


# State for business case graph
class BusinessCaseState(MessagesState):
    use_case: UseCaseData
    evaluations: list[EvaluationResult]
    draft: str
    critic_feedback: str
    iteration: int
    human_decision: str | None  # "approve" | "reject" | "request_info"
    business_case_id: str
