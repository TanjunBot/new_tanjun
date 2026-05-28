"""
AiService: Encapsulate AI token management, custom situation CRUD, and AI chat.

Consolidates the loose AI functions from api.py (useToken, addToken, getToken,
getTokenOverview, includeToToken, resetToken, consumePaidToken, addCustomSituation,
getCustomSituations, getCustomSituation, getCustomSituationFromUser,
deleteCustomSituation, unlockCustomSituation) and ai/refill_token.py into a single
service with Pydantic-validated parameter models.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from config import openAiKey

# --- Type aliases ---

UserId = Annotated[str, StringConstraints(pattern=r"^\d{17,20}$")]


# --- Pydantic models ---

class AiTokenUsage(BaseModel):
    """Represents a user's current AI token balance."""

    user_id: UserId
    free_token: int = 500
    plus_token: int = 0
    paid_token: int = 0
    used_token: int = 0

    @property
    def total_available(self) -> int:
        """Sum of all non-used token pools."""
        return self.free_token + self.plus_token + self.paid_token


class CreateSituationParams(BaseModel):
    """Validated parameters for creating a custom AI situation."""

    user_id: UserId
    situation: Annotated[str, StringConstraints(min_length=10, max_length=4000)]
    name: Annotated[str, StringConstraints(min_length=3, max_length=15)]
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)


class AiSituation(BaseModel):
    """Represents a custom AI situation from the database."""

    user_id: str
    situation: str | None
    name: str | None
    created_at: object  # datetime
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    unlocked: bool


class TokenOverview(BaseModel):
    """Represents a user's token overview from the database."""

    free_token: int
    plus_token: int
    paid_token: int
    used_token: int


# --- Service ---

class AiService:
    """Single responsible service for all AI-related concerns.

    Handles token management, custom situation CRUD, and OpenAI chat.
    """

    def __init__(self) -> None:
        self._openai_key: str | None = openAiKey or os.getenv("OPENAI_API_KEY")

    # ── Token management ──────────────────────────────────────────────────

    @staticmethod
    async def get_usage(user_id: UserId) -> AiTokenUsage | None:
        """Return token usage overview for a user."""
        from api import execute_query

        query = (
            "SELECT user_id, freeToken, plusToken, paidToken, usedToken "
            "FROM aiToken WHERE user_id = %s"
        )
        result = await execute_query(query, (user_id,))
        if not result:
            return None
        row = result[0]
        return AiTokenUsage(
            user_id=row[0],
            free_token=row[1],
            plus_token=row[2],
            paid_token=row[3],
            used_token=row[4],
        )

    @staticmethod
    async def consume(user_id: UserId, amount: int) -> bool:
        """Try to consume *amount* tokens from the user's pools.

        Tries freeToken first, then plusToken, then paidToken.
        Returns ``True`` if tokens were consumed, ``False`` if insufficient.
        """
        from api import execute_action

        # This mirrors the original useToken logic: three UPDATEs that only
        # fire when the preceding pool is exhausted.
        query = """
        UPDATE aiToken
        SET freeToken = CASE
                            WHEN freeToken >= %s THEN freeToken - %s
                            ELSE freeToken
                        END,
            usedToken = CASE
                            WHEN freeToken >= %s THEN usedToken + %s
                            ELSE usedToken
                        END
        WHERE user_id = %s AND freeToken >= %s;
        UPDATE aiToken
        SET plusToken = CASE
                            WHEN freeToken < %s AND plusToken >= %s THEN plusToken - %s
                            ELSE plusToken
                        END,
            usedToken = CASE
                            WHEN freeToken < %s AND plusToken >= %s THEN usedToken + %s
                            ELSE usedToken
                        END
        WHERE user_id = %s AND freeToken < %s AND plusToken >= %s;
        UPDATE aiToken
        SET paidToken = CASE
                            WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN paidToken - %s
                            ELSE paidToken
                        END,
            usedToken = CASE
                            WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN usedToken + %s
                            ELSE usedToken
                        END
        WHERE user_id = %s AND freeToken < %s AND plusToken < %s AND paidToken >= %s;
        """
        params = (
            amount, amount, amount, amount, user_id, amount,  # 1st UPDATE
            amount, amount, amount, amount, amount, amount, amount, user_id, amount, amount, amount,  # 2nd UPDATE
            amount, amount, amount, amount, amount, amount, amount, amount, amount, amount, amount, amount, user_id, amount, amount, amount,  # 3rd UPDATE
        )
        rows_affected = await execute_action(query, params)
        return rows_affected is not None and rows_affected > 0

    @staticmethod
    async def get_available_tokens(user_id: UserId) -> int:
        """Return the total number of tokens available for a user.

        Returns 0 if the user has no token record.
        """
        usage = await AiService.get_usage(user_id)
        return usage.total_available if usage else 0

    @staticmethod
    async def initialize_user(user_id: UserId) -> None:
        """Insert a default token row for a new user if one doesn't exist."""
        from api import execute_action

        query = "INSERT INTO aiToken (user_id) VALUES (%s)"
        await execute_action(query, (user_id,))

    @staticmethod
    async def add_paid_tokens(user_id: UserId, amount: int) -> None:
        """Add paid tokens to a user's balance (upsert)."""
        from api import execute_action

        query = """
        INSERT INTO aiToken (user_id, paidToken)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE paidToken = paidToken + %s
        """
        await execute_action(query, (user_id, amount, amount))

    @staticmethod
    async def refill(entitlements: list | None = None) -> None:
        """Reset free tokens and optionally add plus-tier entitlements."""
        from api import execute_action

        query = "UPDATE aiToken SET freeToken = 500"
        await execute_action(query)
        if entitlements is not None:
            for entitlement in entitlements:
                await execute_action(
                    "UPDATE aiToken SET plusToken = 2000 WHERE user_id = %s",
                    (str(entitlement.user_id),),
                )

    @staticmethod
    async def get_token_overview(user_id: UserId) -> TokenOverview | None:
        """Return the raw token overview (free, plus, paid, used)."""
        from api import execute_query

        query = (
            "SELECT freeToken, plusToken, paidToken, usedToken "
            "FROM aiToken WHERE user_id = %s"
        )
        result = await execute_query(query, (user_id,))
        if not result:
            return None
        row = result[0]
        return TokenOverview(free_token=row[0], plus_token=row[1], paid_token=row[2], used_token=row[3])

    # ── Custom situations ─────────────────────────────────────────────────

    @staticmethod
    async def get_situation(name: str) -> AiSituation | None:
        """Look up a situation by its name."""
        from api import execute_query

        query = (
            "SELECT user_id, situation, name, created_at, temperature, top_p, "
            "frequency_penalty, presence_penalty, unlocked "
            "FROM aiSituations WHERE name = %s"
        )
        result = await execute_query(query, (name,))
        if not result:
            return None
        row = result[0]
        return AiSituation(
            user_id=row[0],
            situation=row[1],
            name=row[2],
            created_at=row[3],
            temperature=row[4],
            top_p=row[5],
            frequency_penalty=row[6],
            presence_penalty=row[7],
            unlocked=row[8],
        )

    @staticmethod
    async def get_user_situation(user_id: UserId) -> AiSituation | None:
        """Look up a situation by the user who created it."""
        from api import execute_query

        query = (
            "SELECT user_id, situation, name, created_at, temperature, top_p, "
            "frequency_penalty, presence_penalty, unlocked "
            "FROM aiSituations WHERE user_id = %s"
        )
        result = await execute_query(query, (user_id,))
        if not result:
            return None
        row = result[0]
        return AiSituation(
            user_id=row[0],
            situation=row[1],
            name=row[2],
            created_at=row[3],
            temperature=row[4],
            top_p=row[5],
            frequency_penalty=row[6],
            presence_penalty=row[7],
            unlocked=row[8],
        )

    @staticmethod
    async def create_situation(params: CreateSituationParams) -> None:
        """Create a new custom situation."""
        from api import execute_action

        query = """
        INSERT INTO aiSituations (user_id, situation, name, temperature, top_p,
                                  frequency_penalty, presence_penalty)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        await execute_action(query, (params.user_id, params.situation, params.name,
                                     params.temperature, params.top_p,
                                     params.frequency_penalty, params.presence_penalty))

    @staticmethod
    async def delete_situation(user_id: UserId) -> None:
        """Delete a custom situation by user ID."""
        from api import execute_action

        query = "DELETE FROM aiSituations WHERE user_id = %s"
        await execute_action(query, (user_id,))

    @staticmethod
    async def unlock_situation(user_id: UserId) -> None:
        """Mark a custom situation as unlocked (approved)."""
        from api import execute_action

        query = "UPDATE aiSituations SET unlocked = 1 WHERE user_id = %s"
        await execute_action(query, (user_id,))

    @staticmethod
    async def get_public_situations() -> list[str]:
        """Return names of all unlocked (public) situations."""
        from api import safe_execute_query

        result = await safe_execute_query("SELECT name FROM aiSituations WHERE unlocked = 1")
        return [row[0] for row in result]

    @staticmethod
    async def get_public_situations_iterator() -> AsyncIterator[str]:
        """Iterate over all unlocked situation names one at a time."""
        from api import execute_query_iter

        async for row in execute_query_iter(
            "SELECT name FROM aiSituations WHERE unlocked = 1"
        ):
            yield row[0]
