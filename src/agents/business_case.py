"""
Business case graph: writer → critic loop (max 2 iterations) → HITL interrupt.

Graph shape:
  START → write → critique → [approved?] → hitl_review (interrupt) → END
                     ↑_________________________|no (max 2 iterations)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from src.agents.llm import get_llm
from src.agents.state import BusinessCaseState

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
MAX_ITERATIONS = 2


def _load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")


def _build_context(state: BusinessCaseState) -> str:
    uc = state["use_case"]
    evals = state.get("evaluations", [])

    eval_summary = "\n".join(
        f"- {e.dimension.title()}: {e.score}/10 — {e.justification}" for e in evals
    )

    return f"""
Use Case: {uc.title}
Problem: {uc.problem_statement}
Urgency: {uc.urgency}
Stakeholders: {", ".join(uc.stakeholders) if uc.stakeholders else "Not specified"}
Available Data: {uc.available_data or "Not specified"}
Expected Outcome: {uc.expected_outcome or "Not specified"}

Evaluation Scores:
{eval_summary or "No evaluations available"}
""".strip()


async def write_business_case(state: BusinessCaseState) -> dict:
    """Generate or improve the business case draft."""
    llm = get_llm("gpt4o")
    system_prompt = _load_prompt("business_case_writer.md")
    context = _build_context(state)
    iteration = state.get("iteration", 0)

    critic_feedback = state.get("critic_feedback", "")
    if iteration > 0 and critic_feedback:
        user_content = f"""
{context}

Previous draft had these issues to fix:
{critic_feedback}

Please write an improved business case addressing all the feedback.
"""
    else:
        user_content = context

    response = await llm.ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content.strip())]
    )

    content = str(response.content).strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    return {"draft": content, "iteration": iteration + 1}


async def critique_business_case(state: BusinessCaseState) -> dict:
    """Critic reviews the draft and decides if it's ready for human review."""
    llm = get_llm("o3mini")
    system_prompt = _load_prompt("business_case_critic.md")

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please review this business case:\n\n{state['draft']}"),
        ]
    )

    content = str(response.content).strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    try:
        parsed = json.loads(content)
        approved = bool(parsed.get("approved", False))
        feedback = str(parsed.get("feedback", ""))
    except (json.JSONDecodeError, KeyError):
        approved = True  # If critic fails to parse, proceed to human review
        feedback = "Critic parse error — proceeding to human review"

    return {"critic_feedback": feedback, "critic_approved": approved}


def route_after_critique(state: BusinessCaseState) -> str:
    if state.get("critic_approved") or state.get("iteration", 0) >= MAX_ITERATIONS:
        return "hitl_review"
    return "write"


def human_review(state: BusinessCaseState) -> dict:
    """HITL interrupt: pause graph for human decision."""
    decision = interrupt(
        {
            "business_case": state["draft"],
            "critic_feedback": state.get("critic_feedback", ""),
            "use_case_title": state["use_case"].title,
            "action_required": "Approve, reject, or request more information",
            "options": ["approve", "reject", "request_info"],
        }
    )
    return {"human_decision": str(decision)}


def build_business_case_graph() -> Any:
    builder = StateGraph(BusinessCaseState)

    builder.add_node("write", write_business_case)
    builder.add_node("critique", critique_business_case)
    builder.add_node("hitl_review", human_review)

    builder.add_edge(START, "write")
    builder.add_edge("write", "critique")
    builder.add_conditional_edges("critique", route_after_critique)
    builder.add_edge("hitl_review", END)

    return builder.compile()


business_case_graph = build_business_case_graph()
