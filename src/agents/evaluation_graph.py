"""
Evaluation graph: runs 4 evaluator agents in parallel (fan-out via Send),
collects results (fan-in), then persists to DB.

Graph shape:
  START → prepare → [Send to each evaluator] → collect → persist → END
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from src.agents.evaluators.cost import evaluate_cost
from src.agents.evaluators.feasibility import evaluate_feasibility
from src.agents.evaluators.security import evaluate_security
from src.agents.evaluators.value import evaluate_value
from src.agents.state import (
    EvaluationGraphState,
    EvaluationResult,
    EvaluatorState,
    UseCaseData,
)

logger = logging.getLogger(__name__)

EVALUATORS = {
    "security": evaluate_security,
    "feasibility": evaluate_feasibility,
    "cost": evaluate_cost,
    "value": evaluate_value,
}


def route_to_evaluators(state: EvaluationGraphState) -> list[Send]:
    """Fan-out: send use case to all 4 evaluators in parallel."""
    return [
        Send(f"evaluate_{dim}", EvaluatorState(use_case=state.use_case))
        for dim in EVALUATORS
    ]


async def _run_evaluator(evaluator_fn: Any, state: EvaluatorState) -> dict:
    result = await evaluator_fn(state.use_case)
    return {"evaluations": [result]}


async def evaluate_security_node(state: EvaluatorState) -> dict:
    return await _run_evaluator(evaluate_security, state)


async def evaluate_feasibility_node(state: EvaluatorState) -> dict:
    return await _run_evaluator(evaluate_feasibility, state)


async def evaluate_cost_node(state: EvaluatorState) -> dict:
    return await _run_evaluator(evaluate_cost, state)


async def evaluate_value_node(state: EvaluatorState) -> dict:
    return await _run_evaluator(evaluate_value, state)


def collect_results(state: EvaluationGraphState) -> dict:
    """Fan-in: verify all 4 evaluations are present."""
    expected = {"security", "feasibility", "cost", "value"}
    received = {e.dimension for e in state.evaluations}
    if expected != received:
        logger.warning("Missing evaluations: %s", expected - received)
    return {"all_complete": True}


def build_evaluation_graph() -> Any:
    builder = StateGraph(EvaluationGraphState)

    # Evaluator nodes (fan-out targets)
    builder.add_node("evaluate_security", evaluate_security_node)
    builder.add_node("evaluate_feasibility", evaluate_feasibility_node)
    builder.add_node("evaluate_cost", evaluate_cost_node)
    builder.add_node("evaluate_value", evaluate_value_node)
    builder.add_node("collect", collect_results)

    # Fan-out from START
    builder.add_conditional_edges(START, route_to_evaluators)

    # Fan-in: all evaluators → collect
    for dim in EVALUATORS:
        builder.add_edge(f"evaluate_{dim}", "collect")

    builder.add_edge("collect", END)

    return builder.compile()


evaluation_graph = build_evaluation_graph()


async def run_evaluation(use_case: UseCaseData) -> list[EvaluationResult]:
    """
    Run the full evaluation pipeline for a use case.
    Returns list of 4 EvaluationResult objects.
    """
    initial_state = EvaluationGraphState(
        use_case=use_case,
        evaluations=[],
    )
    result = await evaluation_graph.ainvoke(initial_state)
    return result["evaluations"]
