import os
from typing import Optional

from .openai_compatible_model_io import OpenAICompatibleModelIO


class OllamaModelIO(OpenAICompatibleModelIO):
    """ModelIO implementation for Ollama (local or cloud via OpenAI-compatible API)."""

    def __init__(self, model: Optional[str] = None, max_retries_on_rate_limit: int = 3):
        resolved_model = model or os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")
        default_base_url = os.environ.get(
            "OLLAMA_BASE_URL",
            "https://ollama.com/v1"
            if os.environ.get("OLLAMA_API_KEY") and os.environ.get("OLLAMA_API_KEY") != "ollama"
            else "http://localhost:11434/v1",
        )
        super().__init__(
            resolved_model,
            api_key_env="OLLAMA_API_KEY",
            base_url_env="OLLAMA_BASE_URL",
            default_base_url=default_base_url,
            default_api_key="ollama",
            provider_name="ollama",
            max_retries_on_rate_limit=max_retries_on_rate_limit,
        )
