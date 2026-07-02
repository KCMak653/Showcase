from abc import ABC, abstractmethod
import logging
import time
from typing import Optional

from .exceptions import RateLimitedException

logger = logging.getLogger(__name__)


class ModelIO(ABC):
    """
    Abstract base for model I/O. Specific providers (OpenAI, etc.) subclass and
    implement _do_request. get_response() adds retry/backoff for rate limits.
    """

    def __init__(self, max_retries_on_rate_limit: int = 3):
        self.max_retries_on_rate_limit = max_retries_on_rate_limit

    @abstractmethod
    def authenticate(self) -> None:
        """
        Perform provider-specific authentication (e.g. obtain API client, tokens).
        Subclasses must implement. Called by subclasses during initialization.
        """
        ...

    @abstractmethod
    def _do_request(self, input_text: str, prompt: str) -> Optional[str]:
        """
        Perform one model request. Subclasses implement provider-specific logic.
        Returns response text or None on non-rate-limit failure.
        """
        ...

    def get_response(self, input_text: str, prompt: str) -> Optional[str]:
        """
        Send a request with retries on RateLimitedException (429 / rate limit).
        Subclasses raise RateLimitedException from _do_request when rate-limited.
        """
        for attempt in range(self.max_retries_on_rate_limit + 1):
            try:
                return self._do_request(input_text, prompt)
            except RateLimitedException as e:
                if attempt < self.max_retries_on_rate_limit:
                    wait_sec = 50 + (2 ** attempt) * 10
                    logger.warning(
                        "Rate limit (429) hit, retrying in %ds (attempt %d/%d): %s",
                        wait_sec,
                        attempt + 1,
                        self.max_retries_on_rate_limit,
                        e,
                    )
                    time.sleep(wait_sec)
                else:
                    logger.error(
                        "Rate limit exceeded after %d retries: %s",
                        self.max_retries_on_rate_limit,
                        e,
                    )
                    raise RuntimeError(
                        f"Rate limit exceeded after {self.max_retries_on_rate_limit} retries"
                    ) from e
            except Exception as e:
                logger.error("Error in chat completion: %s", e)
                raise RuntimeError("Chat completion failed") from e
        return None
