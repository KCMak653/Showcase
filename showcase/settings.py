from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Load .env from the repository root."""
    load_dotenv(_REPO_ROOT / ".env")
