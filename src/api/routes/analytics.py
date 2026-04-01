from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from src.db.connection import get_connection
from src.scoring.ranking import get_ranked_use_cases
from src.tenancy.middleware import CurrentUser, get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/ranking")
async def get_ranking(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> list[dict]:
    return await get_ranked_use_cases(current_user.tenant_id)


@router.get("/summary")
async def get_summary(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    async with get_connection(tenant_id=current_user.tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE status = 'approved') AS approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') AS rejected,
                    COUNT(*) FILTER (WHERE status = 'review') AS in_review,
                    AVG(composite_score) FILTER (WHERE composite_score IS NOT NULL) AS avg_score
                FROM use_cases
                WHERE tenant_id = %s AND status != 'archived'
                """,
            (current_user.tenant_id,),
        )
        row = await cur.fetchone()

    return {
        "total": int(row["total"]) if row else 0,
        "approved": int(row["approved"]) if row else 0,
        "rejected": int(row["rejected"]) if row else 0,
        "in_review": int(row["in_review"]) if row else 0,
        "avg_score": round(float(row["avg_score"]), 1) if row and row["avg_score"] else None,
    }
