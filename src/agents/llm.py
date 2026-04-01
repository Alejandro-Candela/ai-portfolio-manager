from __future__ import annotations

from functools import lru_cache

from langchain_openai import AzureChatOpenAI

from src.config.settings import get_settings


@lru_cache(maxsize=2)
def get_llm(model: str = "gpt4o") -> AzureChatOpenAI:
    """
    Factory for Azure AI Foundry LLM clients.
    model: "gpt4o" (default, for evaluation) | "o3mini" (supervisor/critic)
    """
    settings = get_settings()

    if model == "o3mini":
        deployment = settings.azure_openai_o3mini_deployment
    else:
        deployment = settings.azure_openai_gpt4o_deployment

    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=deployment,
        temperature=0,
        max_retries=2,
    )
