"""CountingRepository: Consolidated counting minigame data access.

Replaces 21 individual API functions in api.py with a single typed service.
"""

from enum import IntEnum

from api import execute_action, execute_query


class CountingMode(IntEnum):
    """Enum for the three counting table variants."""

    NORMAL = 0
    CHALLENGE = 1
    MODES = 2


_TABLE_MAP = {
    CountingMode.NORMAL: "counting",
    CountingMode.CHALLENGE: "counting_challenge",
    CountingMode.MODES: "counting_modes",
}


class CountingRepository:
    """Typed repository for counting-related database operations.

    Provides a single interface over the three counting tables:
    counting, counting_challenge, counting_modes.
    """

    @staticmethod
    def _table(mode: CountingMode) -> str:
        return _TABLE_MAP[mode]

    # ── Progress ──────────────────────────────────────────────

    @staticmethod
    async def set_progress(
        mode: CountingMode,
        channel_id: str | int,
        progress: int,
        guild_id: str | int,
    ) -> None:
        """Insert or update progress for a counting channel."""
        table = _TABLE_MAP[mode]
        query = (
            f"INSERT INTO {table} (channel_id, progress, guild_id) "
            "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s"
        )
        await execute_action(query, (channel_id, progress, guild_id, progress))

    @staticmethod
    async def get_progress(
        mode: CountingMode, channel_id: str | int
    ) -> int | None:
        """Get the current progress for a channel, or None if not configured."""
        table = _TABLE_MAP[mode]
        query = f"SELECT progress FROM {table} WHERE channel_id = %s"
        result = await execute_query(query, (channel_id,))
        return result[0][0] if result else None

    @staticmethod
    async def get_channel_count(
        mode: CountingMode, guild_id: str | int
    ) -> int:
        """Count how many channels have a non-null progress for this mode."""
        table = _TABLE_MAP[mode]
        query = f"SELECT COUNT(progress) FROM {table} WHERE guild_id = %s"
        result = await execute_query(query, (guild_id,))
        return result[0][0] if result else 0

    # ── Last counter / increment ─────────────────────────────

    @staticmethod
    async def get_last_counter_id(
        mode: CountingMode, channel_id: str | int
    ) -> str | None:
        """Get the last counter's user ID for a channel."""
        table = _TABLE_MAP[mode]
        query = f"SELECT last_counter_id FROM {table} WHERE channel_id = %s"
        result = await execute_query(query, (channel_id,))
        return result[0][0] if result else None

    @staticmethod
    async def increment_progress(
        mode: CountingMode,
        channel_id: str | int,
        last_counter_id: str | int,
    ) -> None:
        """Increment progress by 1 and update the last counter ID."""
        table = _TABLE_MAP[mode]
        query = (
            f"UPDATE {table} "
            "SET progress = progress + 1, last_counter_id = %s "
            "WHERE channel_id = %s"
        )
        await execute_action(query, (last_counter_id, channel_id))

    # ── Clear ────────────────────────────────────────────────

    @staticmethod
    async def clear(mode: CountingMode, channel_id: str | int) -> None:
        """Delete the counting entry for a channel."""
        table = _TABLE_MAP[mode]
        query = f"DELETE FROM {table} WHERE channel_id = %s"
        await execute_action(query, (channel_id,))

    # ── Mode-specific (only applies to CountingMode.MODES) ───

    @staticmethod
    async def get_mode(channel_id: str | int) -> int | None:
        """Get the active mode for a counting_modes channel."""
        query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
        result = await execute_query(query, (channel_id,))
        return result[0][0] if result else None

    @staticmethod
    async def get_goal(channel_id: str | int) -> int | None:
        """Get the goal for a counting_modes channel."""
        query = "SELECT goal FROM counting_modes WHERE channel_id = %s"
        result = await execute_query(query, (channel_id,))
        return result[0][0] if result else None

    @staticmethod
    async def set_mode_progress(
        channel_id: str | int,
        progress: int,
        guild_id: str | int,
        mode: int,
        goal: int,
        counter_id: str | int,
    ) -> None:
        """Full upsert for counting_modes (includes mode, goal, counter)."""
        query = (
            "INSERT INTO counting_modes "
            "(channel_id, progress, guild_id, mode, goal, last_counter_id) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE "
            "guild_id = VALUES(guild_id), "
            "mode = VALUES(mode), "
            "goal = VALUES(goal), "
            "progress = VALUES(progress), "
            "last_counter_id = VALUES(last_counter_id)"
        )
        await execute_action(
            query,
            (
                channel_id,
                progress,
                guild_id,
                mode,
                goal,
                counter_id,
            ),
        )

    @staticmethod
    async def set_challenge_progress(
        mode: CountingMode,
        channel_id: str | int,
        progress: int,
        guild_id: str | int = 0,
    ) -> None:
        """Insert or update for challenge — inserts row, sets progress.

        For CountingMode.CHALLENGE the guild_id field may be omitted in some
        legacy call-sites, but we accept it for consistency.
        """
        table = _TABLE_MAP[mode]
        query = (
            f"INSERT INTO {table} (channel_id, progress, guild_id) "
            "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s"
        )
        await execute_action(query, (channel_id, progress, guild_id, progress))

    # ── Batch helpers for listeners ──────────────────────────

    @staticmethod
    async def get_configs(
        channel_id: str | int,
    ) -> tuple[dict | None, dict | None, dict | None]:
        """Fetch configs for all three counting modes in parallel.

        Returns (normal_config, challenge_config, modes_config).
        """
        import asyncio

        counting_query = (
            "SELECT progress, last_counter_id, guild_id FROM counting WHERE channel_id = %s"
        )
        challenge_query = (
            "SELECT progress, last_counter_id, guild_id FROM counting_challenge WHERE channel_id = %s"
        )
        modes_query = (
            "SELECT progress, mode, goal, last_counter_id, guild_id "
            "FROM counting_modes WHERE channel_id = %s"
        )
        params = (channel_id,)
        cr, ch_r, mr = await asyncio.gather(
            execute_query(counting_query, params),
            execute_query(challenge_query, params),
            execute_query(modes_query, params),
        )
        counting_config = (
            {"progress": cr[0][0], "last_counter_id": cr[0][1], "guild_id": cr[0][2]}
            if cr
            else None
        )
        challenge_config = (
            {"progress": ch_r[0][0], "last_counter_id": ch_r[0][1], "guild_id": ch_r[0][2]}
            if ch_r
            else None
        )
        modes_config = (
            {
                "progress": mr[0][0],
                "mode": mr[0][1],
                "goal": mr[0][2],
                "last_counter_id": mr[0][3],
                "guild_id": mr[0][4],
            }
            if mr
            else None
        )
        return counting_config, challenge_config, modes_config
