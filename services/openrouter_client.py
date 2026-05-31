from __future__ import annotations

import os

from openai import AsyncOpenAI

from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-v4-flash:free"


def get_openrouter_api_key() -> str:
    return OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY", "")


def get_openrouter_model() -> str:
    return OPENROUTER_MODEL or os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)


def get_openrouter_client() -> AsyncOpenAI | None:
    api_key = get_openrouter_api_key()
    if not api_key:
        return None
    return AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://tanjun.bot",
            "X-Title": "Tanjun Discord Bot",
        },
    )
