from __future__ import annotations

import json
import logging
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.llm import get_llm
from src.agents.state import EvaluationResult, UseCaseData

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


async def run_evaluator(
    use_case: UseCaseData,
    dimension: str,
    prompt_file: str,
) -> EvaluationResult:
    """Generic evaluator: sends use case context to LLM and parses scored output."""
    system_prompt = _load_prompt(prompt_file)
    llm = get_llm("gpt4o")

    user_message = f"""
Use Case: {use_case.title}

Problem Statement:
{use_case.problem_statement}

Description:
{use_case.description}

Stakeholders: {', '.join(use_case.stakeholders) if use_case.stakeholders else 'Not specified'}

Available Data:
{use_case.available_data or 'Not specified'}

Expected Outcome:
{use_case.expected_outcome or 'Not specified'}

Urgency: {use_case.urgency}

Please evaluate this use case and provide your score and justification.
""".strip()

    response = await llm.ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
    )

    content = str(response.content).strip()

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    try:
        parsed = json.loads(content)
        score = float(parsed["score"])
        score = max(1.0, min(10.0, score))  # clamp to 1-10
        return EvaluationResult(
            dimension=dimension,
            score=score,
            justification=parsed["justification"],
        )
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("Failed to parse evaluator response for %s: %s", dimension, exc)
        return EvaluationResult(
            dimension=dimension,
            score=5.0,
            justification=f"Evaluation completed (parse error: {content[:200]})",
        )
