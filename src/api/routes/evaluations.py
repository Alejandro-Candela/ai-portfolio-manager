from __future__ import annotations

import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from src.agents.evaluation_graph import run_evaluation
from src.agents.state import UseCaseData
from src.db.connection import get_connection
from src.scoring.engine import compute_composite_score
from src.tenancy.middleware import CurrentUser, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["evaluations"])


@router.post("/use-cases/{use_case_id}/evaluate")
async def trigger_evaluation(
    use_case_id: str,
    background_tasks: BackgroundTasks,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict[str, str]:
    """Trigger evaluation pipeline for a use case (runs in background)."""
    # Verify use case exists and belongs to tenant
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            "SELECT id, title, problem_statement, description, stakeholders, "
            "available_data, expected_outcome, urgency, tenant_id "
            "FROM use_cases WHERE id = %s AND tenant_id = %s",
            (use_case_id, current_user.tenant_id),
        )
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Use case not found")

    use_case = UseCaseData(
        id=use_case_id,
        title=row["title"],
        problem_statement=row["problem_statement"],
        description=row["description"] or "",
        stakeholders=json.loads(row["stakeholders"]) if row["stakeholders"] else [],
        available_data=row["available_data"] or "",
        expected_outcome=row["expected_outcome"] or "",
        urgency=str(row["urgency"].value)
        if hasattr(row["urgency"], "value")
        else str(row["urgency"]),
        tenant_id=current_user.tenant_id,
    )

    background_tasks.add_task(_run_and_store_evaluation, use_case, current_user.tenant_id)

    return {"message": "Evaluation started", "use_case_id": use_case_id}


async def _run_and_store_evaluation(use_case: UseCaseData, tenant_id: str) -> None:
    """Background task: run all evaluators and persist results."""
    try:
        # Update status to evaluating
        async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
            await cur.execute(
                "UPDATE use_cases SET status = 'evaluating', updated_at = NOW() WHERE id = %s",
                (use_case.id,),
            )
            await conn.commit()

        evaluations = await run_evaluation(use_case)

        async with get_connection(tenant_id=tenant_id) as conn:
            async with conn.cursor() as cur:
                for eval_result in evaluations:
                    eval_id = str(uuid.uuid4())
                    await cur.execute(
                        """
                        INSERT INTO evaluations (id, use_case_id, dimension, score, justification, model_used)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT ON CONSTRAINT uq_evaluation_use_case_dimension
                        DO UPDATE SET score = EXCLUDED.score, justification = EXCLUDED.justification,
                                      created_at = NOW()
                        """,
                        (
                            eval_id,
                            use_case.id,
                            eval_result.dimension,
                            eval_result.score,
                            eval_result.justification,
                            "gpt-4o",
                        ),
                    )

                # Compute and store composite score
                composite = await compute_composite_score(
                    tenant_id=tenant_id,
                    evaluations=evaluations,
                )
                await cur.execute(
                    """
                    UPDATE use_cases
                    SET composite_score = %s, status = 'scored', updated_at = NOW()
                    WHERE id = %s
                    """,
                    (composite, use_case.id),
                )
                await conn.commit()

        logger.info("Evaluation complete for use case %s, score: %.1f", use_case.id, composite)

    except Exception:
        logger.exception("Evaluation failed for use case %s", use_case.id)
        async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
            await cur.execute(
                "UPDATE use_cases SET status = 'new', updated_at = NOW() WHERE id = %s",
                (use_case.id,),
            )
            await conn.commit()


@router.get("/use-cases/{use_case_id}/evaluations")
async def get_evaluations(
    use_case_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[dict]:
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        # Verify ownership
        await cur.execute(
            "SELECT id FROM use_cases WHERE id = %s AND tenant_id = %s",
            (use_case_id, current_user.tenant_id),
        )
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Use case not found")

        await cur.execute(
            "SELECT id, use_case_id, dimension, score, justification, model_used, created_at "
            "FROM evaluations WHERE use_case_id = %s ORDER BY dimension",
            (use_case_id,),
        )
        rows = await cur.fetchall()

    for row in rows:
        row["created_at"] = row["created_at"].isoformat()
        if hasattr(row.get("dimension"), "value"):
            row["dimension"] = row["dimension"].value
    return rows
