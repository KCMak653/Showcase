"""ModelIO exception hierarchy."""


class ModelIOException(Exception):
    """Base exception for all ModelIO issues."""
    pass


class RateLimitedException(ModelIOException):
    """Rate limit (e.g. 429, TPM exceeded). May succeed if retried after backoff."""
    pass


class FatalException(ModelIOException):
    """Exceptions that will not succeed on retry (e.g. 400 Bad Request, invalid API key)."""
    pass
