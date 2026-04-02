from __future__ import annotations

import logging

from src.agents.state import EvaluationResult
from src.db.connection import get_connection

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS: dict[str, float] = {
    "security": 0.25,
    "feasibility": 0.25,
    "cost": 0.25,
    "value": 0.25,
}


async def _get_weights(tenant_id: str) -> dict[str, float]:
    """Load per-tenant scoring weights from DB. Falls back to defaults."""
    try:
        async with get_connection(tenant_id=tenant_id) as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT dimension, weight FROM scoring_configs WHERE tenant_id = %s",
                (tenant_id,),
            )
            rows = await cur.fetchall()

        if not rows:
            return DEFAULT_WEIGHTS.copy()

        weights: dict[str, float] = {}
        for row in rows:
            dim = (
                str(row["dimension"].value)
                if hasattr(row["dimension"], "value")
                else str(row["dimension"])
            )
            weights[dim] = float(row["weight"])
        return weights

    except Exception:
        logger.warning("Failed to load weights for tenant %s, using defaults", tenant_id)
        return DEFAULT_WEIGHTS.copy()


def _weighted_score(
    evaluations: list[EvaluationResult],
    weights: dict[str, float],
) -> float:
    """
    Compute weighted sum normalized to 0-100.
    Formula: sum(score_i * weight_i) / sum(weight_i) * 10
    (scores are 1-10, output is 0-100)
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for eval_result in evaluations:
        w = weights.get(eval_result.dimension, 0.25)
        weighted_sum += eval_result.score * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    # Normalize to 0-100 (score 1-10 → 10-100)
    return (weighted_sum / total_weight) * 10


async def compute_composite_score(
    tenant_id: str,
    evaluations: list[EvaluationResult],
) -> float:
    weights = await _get_weights(tenant_id)
    score = _weighted_score(evaluations, weights)
    return round(score, 2)
