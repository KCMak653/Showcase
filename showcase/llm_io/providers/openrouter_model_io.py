"""
OpenAI concrete implementation of ModelIO.
"""
import logging
import os
from typing import Optional

import openrouter
from openrouter import OpenRouter

from showcase.llm_io.exceptions import RateLimitedException
from showcase.llm_io.model_io import ModelIO

logger = logging.getLogger(__name__)


class OpenRouterModelIO(ModelIO):
    """ModelIO implementation using the OpenRouter API."""

    def __init__(
        self,
        model: str,
        max_retries_on_rate_limit: int = 3,
    ):
        super().__init__(max_retries_on_rate_limit=max_retries_on_rate_limit)
        self.model = model
        self.authenticate()

    def authenticate(self) -> None:
        try:
            self.client = OpenRouter(api_key = os.environ["OPENROUTER_API_KEY"])
        except Exception as e:
            logger.error(
                "Error initializing OpenRouter client. Is OPENROUTER_API_KEY set? Error: %s",
                e,
            )
            raise SystemExit(1) from e

    def _do_request(self, input_text: str, prompt: str) -> Optional[str]:
        try:
            response = self.client.chat.send(
                model=self.model,
                messages = [{
                "content":prompt,
                "role" : "system"},
                {"content":input_text,
                "role":"user"}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise
