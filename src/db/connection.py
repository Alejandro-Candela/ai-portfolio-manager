from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from src.config.settings import get_settings

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None


async def init_pool() -> None:
    global _pool
    settings = get_settings()
    _pool = AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=2,
        max_size=settings.database_pool_size,
        open=False,
    )
    await _pool.open()
    logger.info("Database pool initialized")


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")


def get_pool() -> AsyncConnectionPool:
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


@asynccontextmanager
async def get_connection(
    tenant_id: str | None = None,
) -> AsyncGenerator[psycopg.AsyncConnection[Any], None]:
    pool = get_pool()
    async with pool.connection() as conn:
        conn.row_factory = dict_row
        if tenant_id:
            await conn.execute("SELECT set_config('app.tenant_id', %s, true)", (tenant_id,))
        yield conn
