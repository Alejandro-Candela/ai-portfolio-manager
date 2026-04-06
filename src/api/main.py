from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from ag_ui_langgraph import LangGraphAgent, add_langgraph_fastapi_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents.intake import intake_graph
from src.api.routes.analytics import router as analytics_router
from src.api.routes.business_cases import router as business_cases_router
from src.api.routes.evaluations import router as evaluations_router
from src.api.routes.use_cases import router as use_cases_router
from src.config.settings import get_settings
from src.db.connection import close_pool, init_pool
from src.db.seeds import seed_dev_tenant


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    """Initialize and teardown application resources."""
    settings = get_settings()
    await init_pool()

    if settings.dev_auth_bypass:
        await seed_dev_tenant(settings.dev_tenant_id)

    yield

    await close_pool()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="AI Portfolio Manager",
        description="Multi-tenant AI use case portfolio manager",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"] if settings.is_dev else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(use_cases_router, prefix="/api")
    app.include_router(evaluations_router, prefix="/api")
    app.include_router(business_cases_router, prefix="/api")
    app.include_router(analytics_router, prefix="/api")

    # Register AG-UI / CopilotKit intake agent endpoint
    # Routes must be added at app creation time, not inside lifespan
    add_langgraph_fastapi_endpoint(
        app=app,
        agent=LangGraphAgent(
            name="default",
            description="Use case intake agent",
            graph=intake_graph,
        ),
        path="/api/copilotkit",
    )

    @app.get("/api/copilotkit")
    async def copilotkit_discovery_get():
        """Discovery endpoint for CopilotKit agent discovery."""
        return {
            "agents": {
                "default": {
                    "description": "Use case intake agent",
                }
            }
        }

    @app.get("/api/copilotkit/info")
    async def copilotkit_discovery():
        """Metadata for CopilotKit agent discovery."""
        return {
            "agents": {
                "default": {
                    "description": "Use case intake agent",
                }
            }
        }

    return app


app = create_app()
