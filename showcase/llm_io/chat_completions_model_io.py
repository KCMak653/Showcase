"""
OpenAI-compatible chat completions client for providers like Ollama and Kimi.
"""
import logging
import os
from typing import Optional

import openai
from openai import OpenAI

from showcase.llm_io.exceptions import RateLimitedException
from showcase.llm_io.model_io import ModelIO

logger = logging.getLogger(__name__)


class ChatCompletionsModelIO(ModelIO):
    """ModelIO implementation for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        model: str,
        *,
        api_key_env: str,
        base_url_env: str,
        default_base_url: str,
        default_api_key: str = "",
        provider_name: str = "provider",
        max_retries_on_rate_limit: int = 3,
    ):
        super().__init__(max_retries_on_rate_limit=max_retries_on_rate_limit)
        self.model = model
        self.api_key_env = api_key_env
        self.base_url_env = base_url_env
        self.default_base_url = default_base_url
        self.default_api_key = default_api_key
        self.provider_name = provider_name
        self.authenticate()

    def authenticate(self) -> None:
        api_key = os.environ.get(self.api_key_env, self.default_api_key)
        base_url = os.environ.get(self.base_url_env, self.default_base_url)
        if not api_key and self.provider_name != "ollama":
            logger.error(
                "Error initializing %s client. Is %s set?",
                self.provider_name,
                self.api_key_env,
            )
            raise SystemExit(1)
        try:
            self.client = OpenAI(api_key=api_key or "ollama", base_url=base_url)
        except Exception as e:
            logger.error(
                "Error initializing %s client at %s: %s",
                self.provider_name,
                base_url,
                e,
            )
            raise SystemExit(1) from e

    def _do_request(self, input_text: str, prompt: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            if hasattr(openai, "RateLimitError") and isinstance(e, openai.RateLimitError):
                raise RateLimitedException(str(e)) from e
            raise
