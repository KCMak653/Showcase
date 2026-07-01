"""
OpenAI concrete implementation of ModelIO.
"""
import logging
from typing import Optional

import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from llm_io.model_io import ModelIO
from llm_io.exceptions import RateLimitedException

logger = logging.getLogger(__name__)


class OpenAIModelIO(ModelIO):
    """ModelIO implementation using the OpenAI API."""

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
            self.client = OpenAI()
        except Exception as e:
            logger.error(
                "Error initializing OpenAI client. Is OPENAI_API_KEY set? Error: %s",
                e,
            )
            raise SystemExit(1) from e

    def _do_request(self, input_text: str, prompt: str) -> Optional[str]:
        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=prompt,
                input=input_text,
            )
            return response.output_text
        except Exception as e:
            if hasattr(openai, "RateLimitError") and isinstance(e, openai.RateLimitError):
                raise RateLimitedException(str(e)) from e
            raise
