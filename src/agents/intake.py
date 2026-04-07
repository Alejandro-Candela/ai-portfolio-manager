"""
Intake graph: conversational agent that extracts use case details.

Uses MessagesState + a tool call / structured output to detect completion.
Exposed via AG-UI through add_langgraph_fastapi_endpoint.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.llm import get_llm
from src.agents.state import IntakeState

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "intake_system.md").read_text(encoding="utf-8")



async def intake_chat_node(state: IntakeState) -> dict:
    """Main intake chat node: calls LLM with frontend actions bound as tools."""
    llm = get_llm("gpt4o")
    system_prompt = _load_system_prompt()

    # Bind CopilotKit frontend actions (e.g. save_use_case) as tools
    frontend_actions = state.get("copilotkit", {}).get("actions", [])
    if frontend_actions:
        llm = llm.bind_tools(frontend_actions)

    messages = [SystemMessage(content=system_prompt), *state["messages"]]
    response = await llm.ainvoke(messages)

    return {"messages": [response]}


def build_intake_graph() -> Any:
    builder = StateGraph(IntakeState)
    builder.add_node("intake_chat", intake_chat_node)
    builder.add_edge(START, "intake_chat")
    builder.add_edge("intake_chat", END)
    return builder.compile(checkpointer=MemorySaver())


intake_graph = build_intake_graph()
