from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/portfolio_manager"
    database_pool_size: int = 10

    # Azure AI Foundry
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_gpt4o_deployment: str = "gpt-4o"
    azure_openai_o3mini_deployment: str = "o3-mini"

    # Azure AI Search
    azure_search_endpoint: str = ""
    azure_search_admin_key: str = ""
    azure_search_index_prefix: str = "portfolio"

    # Microsoft Entra ID
    azure_ad_tenant_id: str = ""
    azure_ad_client_id: str = ""
    azure_ad_audience: str = ""

    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "ai-portfolio-manager"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "ai-portfolio-manager"

    # Dev mode
    dev_auth_bypass: bool = False
    dev_tenant_id: str = "dev-tenant-001"

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
