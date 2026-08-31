import os
from typing import Optional

from showcase.llm_io.providers import (
    KimiModelIO,
    OllamaModelIO,
    OpenAIModelIO,
    OpenRouterModelIO,
)

_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "openrouter": "deepseek/deepseek-chat-v3-0324",
    "ollama": "gpt-oss:20b",
    "kimi": "kimi-for-coding",
}


def create_model_io(model_name: Optional[str] = None):
    provider = os.environ.get("LLM_PROVIDER", "openrouter").lower()
    resolved_model = model_name or os.environ.get("LLM_MODEL") or _DEFAULT_MODELS.get(provider, "")

    if provider == "openai":
        return OpenAIModelIO(resolved_model)
    if provider == "openrouter":
        return OpenRouterModelIO(resolved_model)
    if provider == "ollama":
        return OllamaModelIO(resolved_model)
    if provider == "kimi":
        return KimiModelIO(resolved_model)
    if provider == "cursor":
        raise ValueError(
            "LLM_PROVIDER=cursor is not supported for Showcase's scrape/format pipeline. "
            "CURSOR_API_KEY powers the Cursor Agent SDK, not chat completions. "
            "Use openrouter, openai, ollama, or kimi instead."
        )
    raise ValueError(
        f"Unknown LLM_PROVIDER {provider!r}. "
        "Expected one of: openai, openrouter, ollama, kimi."
    )
