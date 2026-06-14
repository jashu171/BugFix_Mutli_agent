"""Configuration loader for the BugFix agent.

Reads environment variables from .env and exposes them as typed constants.
Never prints or logs API keys.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def _require_env(name: str) -> str:
    """Return an env var or raise with a helpful message."""
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {name}. "
            f"Set it in {_PROJECT_ROOT / '.env'}"
        )
    return value


# ── Public configuration ─────────────────────────────────────────────
ANTHROPIC_BASE_URL: str = _require_env("ANTHROPIC_BASE_URL")
ANTHROPIC_API_KEY: str = _require_env("ANTHROPIC_API_KEY")
MODEL: str = _require_env("MODEL")
REASONING_MODEL: str = os.environ.get("REASONING_MODEL", "openai/gpt-oss-120b:free")

# Agent behaviour
MAX_REPAIR_ITERATIONS: int = int(os.environ.get("MAX_REPAIR_ITERATIONS", "3"))
PYTEST_TIMEOUT_SECONDS: int = int(os.environ.get("PYTEST_TIMEOUT_SECONDS", "30"))
