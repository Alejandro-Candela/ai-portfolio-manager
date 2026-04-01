from __future__ import annotations

from src.db.connection import get_connection


async def get_ranked_use_cases(tenant_id: str) -> list[dict]:
    """Return all scored use cases for a tenant, ranked by composite score desc."""
    async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
        await cur.execute(
            """
                SELECT id, title, status, urgency, composite_score,
                       created_at, updated_at
                FROM use_cases
                WHERE tenant_id = %s AND composite_score IS NOT NULL
                ORDER BY composite_score DESC
                """,
            (tenant_id,),
        )
        rows = await cur.fetchall()

    result = []
    for i, row in enumerate(rows):
        result.append(
            {
                "rank": i + 1,
                "id": row["id"],
                "title": row["title"],
                "status": str(row["status"].value) if hasattr(row["status"], "value") else str(row["status"]),
                "urgency": str(row["urgency"].value) if hasattr(row["urgency"], "value") else str(row["urgency"]),
                "composite_score": row["composite_score"],
                "created_at": row["created_at"].isoformat(),
            }
        )
    return result
