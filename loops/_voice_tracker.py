"""Shared voice user tracker for level XP and giveaway voice time.

Both loops/level.py and loops/giveaway.py need to track which users are
currently in active voice channels. Previously each module maintained its
own copy of the voiceUsers list and all four management functions, causing
duplicate Discord API calls on every voice state update.

This module provides a VoiceUserManager class — a single, typed, encapsulated
manager that replaces the old module-level functions and global set.
"""

from __future__ import annotations

import discord

from api import check_if_opted_out


class VoiceUserManager:
    """Typed, encapsulated manager for tracking active voice users.

    Stores (user_id, guild_id) pairs instead of discord.Member objects to
    prevent memory leaks from stale/disconnected member references. IDs are
    stable across Discord reconnections and provide O(1) lookup & removal.
    """

    def __init__(self) -> None:
        self._users: set[tuple[int, int]] = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, user_id: int, guild_id: int) -> None:
        """Register a user as active in a voice channel."""
        self._users.add((user_id, guild_id))

    def remove(self, user_id: int, guild_id: int) -> None:
        """Remove a user from the active set (no-op if absent)."""
        self._users.discard((user_id, guild_id))

    def get_active_users(self) -> list[tuple[int, int]]:
        """Return a snapshot copy of all active (user_id, guild_id) pairs."""
        return list(self._users)

    def clear(self) -> None:
        """Remove all tracked users."""
        self._users.clear()

    @property
    def user_ids(self) -> set[tuple[int, int]]:
        """Direct read-only access to the underlying set."""
        return self._users

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _synchronize(self, active_ids: list[tuple[int, int]]) -> None:
        """Synchronize the managed set with a fresh list of active IDs.

        Computes the diff between the current set and the provided list,
        then adds/removes accordingly.  This avoids clearing and rebuilding
        the entire set on every voice-state update.
        """
        current = self._users
        active = set(active_ids)

        users_to_add = active - current
        users_to_remove = current - active

        for user_id, guild_id in users_to_add:
            self.add(user_id, guild_id)
        for user_id, guild_id in users_to_remove:
            self.remove(user_id, guild_id)

    async def handle_voice_change(
        self,
        user: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """React to a ``on_voice_state_update`` event.

        Filters out self-muted/deafened members and only keeps channels
        with 2+ active participants.  Users from channels that drop below
        2 participants are removed.
        """
        if await check_if_opted_out(user.id):
            self.remove(user.id, user.guild.id)
            return

        channel_members_before = before.channel.members if before.channel else []
        channel_members_after = after.channel.members if after.channel else []

        # Get active members from both channels
        active_members_before = [
            member
            for member in channel_members_before
            if not (member.voice.self_mute or member.voice.self_deaf)
        ]
        active_members_after = [
            member
            for member in channel_members_after
            if not (member.voice.self_mute or member.voice.self_deaf)
        ]

        # Collect all affected active member IDs
        all_active_ids = set()

        # Handle before channel
        if len(active_members_before) >= 2:
            all_active_ids.update((m.id, m.guild.id) for m in active_members_before)
        else:
            # Remove members from before channel if it drops below 2 active
            for member in channel_members_before:
                self.remove(member.id, member.guild.id)

        # Handle after channel
        if len(active_members_after) >= 2:
            all_active_ids.update((m.id, m.guild.id) for m in active_members_after)
        else:
            # Remove members from after channel if it drops below 2 active
            for member in channel_members_after:
                self.remove(member.id, member.guild.id)

        # Synchronize with all active members from both channels
        if all_active_ids:
            self._synchronize(list(all_active_ids))


# ------------------------------------------------------------------
# Singleton instance — the canonical store shared across the bot.
# Import this from other modules to get the single tracker.
# ------------------------------------------------------------------
voice_user_manager = VoiceUserManager()

# Backward-compatible aliases so existing importers continue to work
# without code changes.  These will be removed once all callers have
# been updated to use the manager directly.
voice_user_ids: set[tuple[int, int]] = voice_user_manager._users  # noqa: SLF001 — temporary compat shim


async def handle_voice_change(
    user: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
) -> None:
    """Deprecated: prefer ``voice_user_manager.handle_voice_change(...)``."""
    await voice_user_manager.handle_voice_change(user, before, after)


def add_voice_user(user_id: int, guild_id: int) -> None:
    """Deprecated: prefer ``voice_user_manager.add(...)``."""
    voice_user_manager.add(user_id, guild_id)


def remove_voice_user(user_id: int, guild_id: int) -> None:
    """Deprecated: prefer ``voice_user_manager.remove(...)``."""
    voice_user_manager.remove(user_id, guild_id)


def update_voice_users(active_user_ids: list[tuple[int, int]]) -> None:
    """Deprecated: prefer ``voice_user_manager._synchronize(...)``."""
    voice_user_manager._synchronize(active_user_ids)  # noqa: SLF001
