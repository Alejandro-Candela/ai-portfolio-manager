"""Development seed data — only runs when DEV_AUTH_BYPASS=true."""
from __future__ import annotations

import logging

from src.db.connection import get_connection

logger = logging.getLogger(__name__)


async def seed_dev_tenant(tenant_id: str = "dev-tenant-001") -> None:
    """Ensure the dev tenant exists in the database."""
    async with get_connection() as conn, conn.cursor() as cur:
        await cur.execute(
            """
                INSERT INTO tenants (id, name, slug, is_active)
                VALUES (%(id)s, 'Dev Tenant', 'dev', true)
                ON CONFLICT (id) DO NOTHING
                """,
            {"id": tenant_id},
        )
        # Default scoring config for dev tenant
        for dimension, weight in [
            ("security", 0.25),
            ("feasibility", 0.25),
            ("cost", 0.25),
            ("value", 0.25),
        ]:
            await cur.execute(
                """
                    INSERT INTO scoring_configs (tenant_id, dimension, weight)
                    VALUES (%(tenant_id)s, %(dimension)s, %(weight)s)
                    ON CONFLICT ON CONSTRAINT uq_scoring_config_tenant_dimension DO NOTHING
                    """,
                {"tenant_id": tenant_id, "dimension": dimension, "weight": weight},
            )
        await conn.commit()
    logger.info("Dev tenant seed complete: %s", tenant_id)
