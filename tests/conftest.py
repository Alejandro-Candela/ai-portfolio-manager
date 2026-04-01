import os

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure test env vars are set before app imports
os.environ.setdefault("DEV_AUTH_BYPASS", "true")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/portfolio_manager")
os.environ.setdefault("APP_ENV", "test")

from src.api.main import app
from src.db.connection import close_pool, init_pool
from src.db.seeds import seed_dev_tenant


@pytest.fixture(scope="session")
async def db_pool():
    """Initialize DB pool once per test session."""
    await init_pool()
    await seed_dev_tenant()
    yield
    await close_pool()


@pytest.fixture
async def client(db_pool) -> AsyncClient:  # type: ignore[override]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
