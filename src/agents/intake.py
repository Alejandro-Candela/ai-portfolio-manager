"""
Intake graph: conversational agent that extracts use case details.

Uses MessagesState + a tool call / structured output to detect completion.
Exposed via AG-UI through add_langgraph_fastapi_endpoint.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph

from src.agents.llm import get_llm
from src.agents.state import IntakeState, UseCaseData

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "intake_system.md").read_text(encoding="utf-8")


def _extract_use_case_from_response(content: str) -> UseCaseData | None:
    """Try to parse the structured use case extraction from agent response."""
    # Look for JSON block in the message
    json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if not json_match:
        return None

    try:
        data = json.loads(json_match.group(1))
        if not data.get("extraction_complete"):
            return None
        uc = data.get("use_case", {})
        return UseCaseData(
            title=uc.get("title", "Untitled Use Case"),
            problem_statement=uc.get("problem_statement", ""),
            stakeholders=uc.get("stakeholders", []),
            available_data=uc.get("available_data", ""),
            expected_outcome=uc.get("expected_outcome", ""),
            urgency=uc.get("urgency", "medium"),
        )
    except (json.JSONDecodeError, KeyError):
        return None


async def intake_chat_node(state: IntakeState) -> dict:
    """Main intake chat node: calls LLM and checks for completion."""
    llm = get_llm("gpt4o")
    system_prompt = _load_system_prompt()

    messages = [SystemMessage(content=system_prompt), *state["messages"]]
    response = await llm.ainvoke(messages)

    content = str(response.content)
    use_case = _extract_use_case_from_response(content)

    update: dict = {"messages": [response]}
    if use_case is not None:
        update["use_case"] = use_case
        update["extraction_complete"] = True
    else:
        update["extraction_complete"] = False

    return update


def should_continue(state: IntakeState) -> str:
    if state.get("extraction_complete"):
        return END
    return "intake_chat"


def build_intake_graph() -> Any:
    builder = StateGraph(IntakeState)
    builder.add_node("intake_chat", intake_chat_node)
    builder.add_edge(START, "intake_chat")
    builder.add_conditional_edges("intake_chat", should_continue)
    return builder.compile()


intake_graph = build_intake_graph()
