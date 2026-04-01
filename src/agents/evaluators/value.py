from src.agents.evaluators.base import run_evaluator
from src.agents.state import EvaluationResult, UseCaseData


async def evaluate_value(use_case: UseCaseData) -> EvaluationResult:
    return await run_evaluator(use_case, "value", "value_evaluator.md")
