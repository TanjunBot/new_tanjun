"""DynamicSlowmodeService — Consolidates slowmode CRUD and logic into a single service."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from models import DynamicSlowmodeMessageModel, DynamicSlowmodeModel


class DynamicSlowmodeConfig(BaseModel):
    """Pydantic model for dynamic slowmode configuration.

    Validates that numeric fields are positive integers.
    """

    guild_id: str
    channel_id: str
    messages: int = Field(gt=0)
    per: int = Field(gt=0)
    reset_after: int = Field(gt=0)
    cached_slowmode: int | None = None

    @classmethod
    def from_db_model(cls, db_model: DynamicSlowmodeModel) -> DynamicSlowmodeConfig:
        """Convert a legacy dataclass DB model to the Pydantic config."""
        return cls(
            guild_id=db_model.guild_id,
            channel_id=db_model.channel_id,
            messages=db_model.messages,
            per=db_model.per,
            reset_after=db_model.reset_after,
            cached_slowmode=db_model.cached_slowmode,
        )


class DynamicSlowmodeService:
    """Service for managing dynamic slowmode configuration and message tracking.

    Bundles all database operations (CRUD for configs, message tracking)
    together with the in-memory message tracking and throttle logic.
    """

    def __init__(self) -> None:
        # In-memory message tracking per channel
        # Maps channel_id -> deque of timestamps (maxlen=100 to bound memory usage)
        self._recent_messages: dict[int, deque[float]] = defaultdict(
            lambda: deque(maxlen=100)
        )

    # ------------------------------------------------------------------
    # Config CRUD
    # ------------------------------------------------------------------

    async def get_all_configs(
        self, guild_id: str
    ) -> list[DynamicSlowmodeConfig]:
        """Fetch all dynamic slowmode configs for a guild."""
        from api import get_dynamicslowmode_channels

        db_models = await get_dynamicslowmode_channels(guild_id)
        return [DynamicSlowmodeConfig.from_db_model(m) for m in db_models]

    async def get_config(
        self, channel_id: str
    ) -> DynamicSlowmodeConfig | None:
        """Fetch slowmode config for a single channel."""
        from api import get_dynamicslowmode

        db_model = await get_dynamicslowmode(channel_id)
        return DynamicSlowmodeConfig.from_db_model(db_model) if db_model else None

    async def configure(
        self,
        guild_id: str,
        channel_id: str,
        messages: int,
        per: int,
        reset_after: int,
    ) -> None:
        """Add a new dynamic slowmode configuration."""
        from api import add_dynamicslowmode

        await add_dynamicslowmode(guild_id, channel_id, messages, per, reset_after)

    async def remove(self, guild_id: str, channel_id: str) -> None:
        """Remove dynamic slowmode for a channel and clear in-memory tracking."""
        from api import remove_dynamicslowmode

        await remove_dynamicslowmode(guild_id, channel_id)
        self._recent_messages.pop(int(channel_id), None)

    # ------------------------------------------------------------------
    # Message tracking
    # ------------------------------------------------------------------

    async def track_message(
        self, channel_id: str, message_id: str, send_time: datetime
    ) -> None:
        """Record a message in the tracking tables."""
        from api import add_dynamicslowmode_message

        await add_dynamicslowmode_message(channel_id, message_id, send_time)

    async def get_recent_messages(
        self, channel_id: str
    ) -> list[DynamicSlowmodeMessageModel]:
        """Fetch tracked messages for a channel from the DB."""
        from api import get_dynamicslowmode_messages

        return await get_dynamicslowmode_messages(channel_id)

    async def clean_old(
        self, channel_id: str, older_than: datetime
    ) -> None:
        """Delete tracked messages older than a cutoff."""
        from api import clear_old_dynamicslowmode_messages

        await clear_old_dynamicslowmode_messages(channel_id, older_than)

    # ------------------------------------------------------------------
    # Slowmode management
    # ------------------------------------------------------------------

    async def cache_current_slowmode(
        self, channel_id: str, delay: int
    ) -> None:
        """Cache the current channel slowmode delay before adjusting it."""
        from api import cash_slowmode_delay

        await cash_slowmode_delay(channel_id, delay)

    async def restore_slowmode(self, channel_id: str) -> None:
        """Remove the cached slowmode delay (restore is implied by edit)."""
        from api import remove_cashed_slowmode_delay

        await remove_cashed_slowmode_delay(channel_id)

    async def should_throttle(
        self, channel_id: int, config: DynamicSlowmodeConfig
    ) -> bool:
        """Check if a channel should be throttled based on recent message rate.

        Uses in-memory tracking for fast checks. Returns True if the
        message threshold within the reset window has been exceeded.
        """
        channel_int = channel_id
        now = time.time()

        # Track in memory
        self._recent_messages[channel_int].append(now)

        # Count messages in the time window
        cutoff = now - config.reset_after
        messages_in_window = sum(
            1 for t in self._recent_messages[channel_int] if t > cutoff
        )

        return messages_in_window > config.messages
