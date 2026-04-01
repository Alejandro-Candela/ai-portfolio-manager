from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel

from src.agents.business_case import business_case_graph
from src.agents.state import BusinessCaseState, EvaluationResult, UseCaseData
from src.db.connection import get_connection
from src.tenancy.middleware import CurrentUser, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["business-cases"])


async def _load_use_case_and_evals(
    use_case_id: str, tenant_id: str
) -> tuple[UseCaseData, list[EvaluationResult]]:
    async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            "SELECT id, title, problem_statement, description, stakeholders, "
            "available_data, expected_outcome, urgency, tenant_id "
            "FROM use_cases WHERE id = %s AND tenant_id = %s",
            (use_case_id, tenant_id),
        )
        uc_row = await cur.fetchone()
        if not uc_row:
            raise HTTPException(status_code=404, detail="Use case not found")

        await cur.execute(
            "SELECT dimension, score, justification FROM evaluations WHERE use_case_id = %s",
            (use_case_id,),
        )
        eval_rows = await cur.fetchall()

    use_case = UseCaseData(
        id=use_case_id,
        title=uc_row["title"],
        problem_statement=uc_row["problem_statement"],
        description=uc_row["description"] or "",
        stakeholders=json.loads(uc_row["stakeholders"]) if uc_row["stakeholders"] else [],
        available_data=uc_row["available_data"] or "",
        expected_outcome=uc_row["expected_outcome"] or "",
        urgency=str(uc_row["urgency"].value) if hasattr(uc_row["urgency"], "value") else str(uc_row["urgency"]),
        tenant_id=tenant_id,
    )
    evaluations = [
        EvaluationResult(
            dimension=str(r["dimension"].value) if hasattr(r["dimension"], "value") else str(r["dimension"]),
            score=float(r["score"]),
            justification=r["justification"],
        )
        for r in eval_rows
    ]
    return use_case, evaluations


@router.post("/use-cases/{use_case_id}/generate-business-case")
async def generate_business_case(
    use_case_id: str,
    background_tasks: BackgroundTasks,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    use_case, evaluations = await _load_use_case_and_evals(use_case_id, current_user.tenant_id)

    thread_id = str(uuid.uuid4())
    background_tasks.add_task(
        _run_business_case_graph, use_case, evaluations, use_case_id, current_user.tenant_id, thread_id
    )
    return {"message": "Business case generation started", "thread_id": thread_id}


async def _run_business_case_graph(
    use_case: UseCaseData,
    evaluations: list[EvaluationResult],
    use_case_id: str,
    tenant_id: str,
    thread_id: str,
) -> None:
    """Run the business case graph until HITL interrupt."""
    try:
        # Update status
        async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
            await cur.execute(
                "UPDATE use_cases SET status = 'business_case', updated_at = NOW() WHERE id = %s",
                (use_case_id,),
            )
            await conn.commit()

        initial_state: BusinessCaseState = {
            "messages": [],
            "use_case": use_case,
            "evaluations": evaluations,
            "draft": "",
            "critic_feedback": "",
            "iteration": 0,
            "human_decision": None,
            "business_case_id": "",
        }

        config = {"configurable": {"thread_id": thread_id}}

        # Run until interrupt (HITL)
        result = await business_case_graph.ainvoke(initial_state, config=config)
        draft = result.get("draft", "")

        # Parse draft JSON
        draft_data = {}
        try:
            content = draft.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            draft_data = json.loads(content)
        except (json.JSONDecodeError, IndexError):
            draft_data = {
                "executive_summary": draft[:500] if draft else "Generation in progress",
                "problem_and_opportunity": "",
                "proposed_solution": "",
                "cost_benefit_analysis": "",
                "risks_and_mitigations": "",
                "timeline": "",
                "recommendation": "conditional",
            }

        # Persist business case with pending_human status
        bc_id = str(uuid.uuid4())
        async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
            await cur.execute(
                """
                    INSERT INTO business_cases (
                        id, use_case_id, executive_summary, problem_and_opportunity,
                        proposed_solution, cost_benefit_analysis, risks_and_mitigations,
                        timeline, recommendation, status, langgraph_thread_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending_human', %s)
                    ON CONFLICT (use_case_id)
                    DO UPDATE SET
                        executive_summary = EXCLUDED.executive_summary,
                        problem_and_opportunity = EXCLUDED.problem_and_opportunity,
                        proposed_solution = EXCLUDED.proposed_solution,
                        cost_benefit_analysis = EXCLUDED.cost_benefit_analysis,
                        risks_and_mitigations = EXCLUDED.risks_and_mitigations,
                        timeline = EXCLUDED.timeline,
                        recommendation = EXCLUDED.recommendation,
                        status = 'pending_human',
                        langgraph_thread_id = EXCLUDED.langgraph_thread_id,
                        updated_at = NOW()
                    """,
                (
                    bc_id,
                    use_case_id,
                    draft_data.get("executive_summary", ""),
                    draft_data.get("problem_and_opportunity", ""),
                    draft_data.get("proposed_solution", ""),
                    draft_data.get("cost_benefit_analysis", ""),
                    draft_data.get("risks_and_mitigations", ""),
                    draft_data.get("timeline", ""),
                    draft_data.get("recommendation", "conditional"),
                    thread_id,
                ),
            )
            await cur.execute(
                "UPDATE use_cases SET status = 'review', updated_at = NOW() WHERE id = %s",
                (use_case_id,),
            )
            await conn.commit()

        logger.info("Business case ready for review: use case %s", use_case_id)

    except Exception:
        logger.exception("Business case generation failed for use case %s", use_case_id)


@router.get("/use-cases/{use_case_id}/business-case")
async def get_business_case(
    use_case_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            "SELECT id FROM use_cases WHERE id = %s AND tenant_id = %s",
            (use_case_id, current_user.tenant_id),
        )
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Use case not found")

        await cur.execute(
            """
                SELECT id, use_case_id, executive_summary, problem_and_opportunity,
                       proposed_solution, cost_benefit_analysis, risks_and_mitigations,
                       timeline, recommendation, status, langgraph_thread_id,
                       created_at, updated_at
                FROM business_cases WHERE use_case_id = %s
                """,
            (use_case_id,),
        )
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Business case not found")

    row["created_at"] = row["created_at"].isoformat()
    row["updated_at"] = row["updated_at"].isoformat()
    for field in ("recommendation", "status"):
        if row.get(field) and hasattr(row[field], "value"):
            row[field] = row[field].value
    return row


class DecisionBody(BaseModel):
    reason: str = ""


@router.post("/use-cases/{use_case_id}/business-case/approve")
async def approve_business_case(
    use_case_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    return await _handle_hitl_decision(use_case_id, current_user.tenant_id, "approve")


@router.post("/use-cases/{use_case_id}/business-case/reject")
async def reject_business_case(
    use_case_id: str,
    body: DecisionBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    return await _handle_hitl_decision(use_case_id, current_user.tenant_id, "reject", body.reason)


@router.post("/use-cases/{use_case_id}/business-case/request-info")
async def request_more_info(
    use_case_id: str,
    body: DecisionBody,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    return await _handle_hitl_decision(use_case_id, current_user.tenant_id, "request_info", body.reason)


async def _handle_hitl_decision(
    use_case_id: str,
    tenant_id: str,
    decision: str,
    reason: str = "",
) -> dict[str, str]:
    async with get_connection(tenant_id=tenant_id) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id FROM use_cases WHERE id = %s AND tenant_id = %s",
                (use_case_id, tenant_id),
            )
            if not await cur.fetchone():
                raise HTTPException(status_code=404, detail="Use case not found")

            new_bc_status = "approved" if decision == "approve" else ("rejected" if decision == "reject" else "draft")
            new_uc_status = "approved" if decision == "approve" else ("rejected" if decision == "reject" else "review")

            await cur.execute(
                """
                UPDATE business_cases SET status = %s, updated_at = NOW()
                WHERE use_case_id = %s
                """,
                (new_bc_status, use_case_id),
            )
            await cur.execute(
                "UPDATE use_cases SET status = %s, updated_at = NOW() WHERE id = %s",
                (new_uc_status, use_case_id),
            )
            await conn.commit()

    return {"message": f"Decision recorded: {decision}", "use_case_id": use_case_id}
