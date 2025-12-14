"""
LLM Client Module - Azure AI Foundry wrapper for OpenAI-compatible API.

Provides both synchronous and asynchronous client interfaces for interacting
with Azure AI Foundry models through an OpenAI-compatible API endpoint.
"""

from typing import Optional
from openai import OpenAI, AsyncOpenAI

from src.config import settings

# Singleton instances for efficient resource management
_client: Optional[OpenAI] = None
_async_client: Optional[AsyncOpenAI] = None


def _ensure_proper_base_url(base_url: str) -> str:
    """
    Ensure the base URL has the correct /openai/v1/ suffix.

    Args:
        base_url: The base URL to normalize

    Returns:
        Properly formatted base URL with /openai/v1/ suffix
    """
    if not base_url.endswith("/openai/v1/"):
        base_url = base_url.rstrip("/") + "/openai/v1/"
    return base_url


def get_client() -> OpenAI:
    """
    Get or create a synchronous OpenAI-compatible client for Azure AI Foundry.

    The client is configured with the base URL and API key from settings.

    Returns:
        OpenAI client instance configured for Azure AI Foundry
    """
    base_url = _ensure_proper_base_url(settings.BASE_URL)

    return OpenAI(
        base_url=base_url,
        api_key=settings.API_KEY,
    )


def get_async_client() -> AsyncOpenAI:
    """
    Get or create an asynchronous OpenAI-compatible client for Azure AI Foundry.

    The client is configured with the base URL and API key from settings.

    Returns:
        AsyncOpenAI client instance configured for Azure AI Foundry
    """
    base_url = _ensure_proper_base_url(settings.BASE_URL)

    return AsyncOpenAI(
        base_url=base_url,
        api_key=settings.API_KEY,
    )


def get_singleton_client() -> OpenAI:
    """
    Get or create a singleton synchronous client instance.

    Using singleton instances can improve performance by reusing connections.

    Returns:
        Cached OpenAI client instance
    """
    global _client
    if _client is None:
        _client = get_client()
    return _client


def get_singleton_async_client() -> AsyncOpenAI:
    """
    Get or create a singleton asynchronous client instance.

    Using singleton instances can improve performance by reusing connections.

    Returns:
        Cached AsyncOpenAI client instance
    """
    global _async_client
    if _async_client is None:
        _async_client = get_async_client()
    return _async_client
