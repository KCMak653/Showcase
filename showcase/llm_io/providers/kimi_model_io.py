import os
from typing import Optional

from showcase.llm_io.chat_completions_model_io import ChatCompletionsModelIO


class KimiModelIO(ChatCompletionsModelIO):
    """ModelIO implementation for Kimi Code's OpenAI-compatible API (Allegro subscription)."""

    def __init__(self, model: Optional[str] = None, max_retries_on_rate_limit: int = 3):
        resolved_model = model or os.environ.get("KIMI_MODEL", "kimi-for-coding")
        super().__init__(
            resolved_model,
            api_key_env="KIMI_API_KEY",
            base_url_env="KIMI_BASE_URL",
            default_base_url="https://api.kimi.com/coding/v1",
            provider_name="kimi",
            max_retries_on_rate_limit=max_retries_on_rate_limit,
        )
