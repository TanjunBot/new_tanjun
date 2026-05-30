"""
GiveawayService: Encapsulate 50+ giveaway API functions into a single service.

Consolidates the loose giveaway functions from api.py (add_giveaway, get_giveaway,
update_giveaway, delete_giveaway, participant CRUD, blacklist CRUD, etc.) into a
single GiveawayService class with Pydantic-validated parameter models.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from api import (
    execute_action,
    execute_query,
    execute_query_iter,
    safe_execute_query,
    transaction,
)
from models import GiveawayBlacklistEntryModel, GiveawayChannelRequirementModel, GiveawayModel

# ------------------------------------------------------------------ #
# Pydantic models
# ------------------------------------------------------------------ #


class GiveawayCreateParams(BaseModel):
    """Validated parameters for creating a new giveaway."""

    guild_id: str
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    winners: int = Field(default=1, ge=1)
    with_button: bool = True
    channel_id: str
    custom_name: str | None = None
    sponsor: str | None = None
    price: str | None = None
    message: str | None = None
    end_time: datetime
    start_time: datetime | None = None
    new_message_requirement: int | None = Field(default=None, ge=0)
    day_requirement: int | None = Field(default=None, ge=0)
    channel_requirements: dict[str, int] = Field(default_factory=dict)
    role_requirement: list[str] = Field(default_factory=list)
    voice_requirement: int | None = Field(default=None, ge=0)


class GiveawayUpdateParams(BaseModel):
    """Validated parameters for updating an existing giveaway."""

    guild_id: str
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    winners: int = Field(default=1, ge=1)
    with_button: bool = True
    custom_name: str | None = None
    sponsor: str | None = None
    price: str | None = None
    message: str | None = None
    end_time: datetime
    start_time: datetime | None = None
    new_message_requirement: int | None = Field(default=None, ge=0)
    day_requirement: int | None = Field(default=None, ge=0)
    channel_requirements: dict[str, int] = Field(default_factory=dict)
    role_requirement: list[str] = Field(default_factory=list)
    voice_requirement: int | None = Field(default=None, ge=0)
    channel_id: str


# ------------------------------------------------------------------ #
# Service class
# ------------------------------------------------------------------ #


class GiveawayService:
    """Service for managing giveaways, participants, and blacklists."""

    # ------------------------------------------------------------------ #
    # Giveaway CRUD
    # ------------------------------------------------------------------ #

    @staticmethod
    async def create(params: GiveawayCreateParams) -> int | None:
        """Create a new giveaway and return its ID."""
        query = """
        INSERT INTO giveaway (
            guild_id, title, description, winners, withButton, customName, sponsor, price, message,
            endtime, starttime, newMessageRequirement, dayRequirement, voiceRequirement, channel_id
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        sql_params = (
            params.guild_id,
            params.title,
            params.description,
            params.winners,
            params.with_button,
            params.custom_name,
            params.sponsor,
            params.price,
            params.message,
            params.end_time,
            params.start_time,
            params.new_message_requirement,
            params.day_requirement,
            params.voice_requirement,
            params.channel_id,
        )
        try:
            async with transaction() as conn, conn.cursor() as cursor:
                await cursor.execute(query, sql_params)
                await cursor.execute("SELECT LAST_INSERT_ID()")
                last_id = await cursor.fetchone()
                giveaway_id = last_id[0] if last_id else None
                if giveaway_id is None:
                    raise RuntimeError("Failed to get last insert ID for giveaway")

                if params.channel_requirements:
                    channel_req_query = (
                        "INSERT INTO giveaway_channelRequirement (giveaway_id, channel_id, amount) VALUES (%s, %s, %s)"
                    )
                    channel_req_params = [
                        (giveaway_id, ch_id, amount) for ch_id, amount in params.channel_requirements.items()
                    ]
                    await cursor.executemany(channel_req_query, channel_req_params)

                if params.role_requirement:
                    role_req_query = "INSERT INTO giveawayRoleRequirement (role_id, giveaway_id) VALUES (%s, %s)"
                    role_req_params = [(role_id, giveaway_id) for role_id in params.role_requirement]
                    await cursor.executemany(role_req_query, role_req_params)
        except Exception as e:
            print(f"Error creating giveaway: {e}")
            return None

        return giveaway_id

    @staticmethod
    async def get(giveaway_id: int) -> GiveawayModel | None:
        """Get a giveaway by ID."""
        query = (
            "SELECT giveaway_id, guild_id, title, description, winners, withButton, "
            "customName, sponsor, price, message, endtime, starttime, started, ended, "
            "newMessageRequirement, dayRequirement, voiceRequirement, sendFailed, "
            "channel_id, messageId, created_at "
            "FROM giveaway WHERE giveaway_id = %s"
        )
        params = (giveaway_id,)
        result = await safe_execute_query(query, params)
        return GiveawayModel.from_row(result[0]) if result else None

    @staticmethod
    async def update(giveaway_id: int, params: GiveawayUpdateParams) -> None:
        """Update an existing giveaway."""
        query = """
        UPDATE giveaway SET
            guild_id = %s,
            title = %s,
            description = %s,
            winners = %s,
            withButton = %s,
            customName = %s,
            sponsor = %s,
            price = %s,
            message = %s,
            endtime = %s,
            starttime = %s,
            newMessageRequirement = %s,
            dayRequirement = %s,
            voiceRequirement = %s,
            channel_id = %s
        WHERE giveaway_id = %s
        """
        vals = (
            params.guild_id,
            params.title,
            params.description,
            params.winners,
            params.with_button,
            params.custom_name,
            params.sponsor,
            params.price,
            params.message,
            params.end_time,
            params.start_time,
            params.new_message_requirement,
            params.day_requirement,
            params.voice_requirement,
            params.channel_id,
            giveaway_id,
        )
        try:
            async with transaction() as conn, conn.cursor() as cursor:
                await cursor.execute(query, vals)
                await cursor.execute(
                    "DELETE FROM giveaway_channelRequirement WHERE giveaway_id = %s",
                    (giveaway_id,),
                )
                if params.channel_requirements:
                    for ch_id, amount in params.channel_requirements.items():
                        await cursor.execute(
                            "INSERT INTO giveaway_channelRequirement (giveaway_id, channel_id, amount) VALUES (%s, %s, %s)",
                            (giveaway_id, ch_id, amount),
                        )
                await cursor.execute(
                    "DELETE FROM giveawayRoleRequirement WHERE giveaway_id = %s",
                    (giveaway_id,),
                )
                for role_id in params.role_requirement:
                    await cursor.execute(
                        "INSERT INTO giveawayRoleRequirement (role_id, giveaway_id) VALUES (%s, %s)",
                        (role_id, giveaway_id),
                    )
        except Exception as e:
            print(f"Error during giveaway update for {giveaway_id}: {e}")
            raise

    @staticmethod
    async def delete(giveaway_id: int) -> None:
        """Delete a giveaway and all related data in a single transaction."""
        related_tables = [
            "giveaway_channelRequirement",
            "giveawayRoleRequirement",
            "giveawayParticipant",
            "giveawayVoiceTime",
            "giveawayNewMessage",
            "giveaway_channelMessages",
        ]
        try:
            async with transaction() as conn, conn.cursor() as cursor:
                for table in related_tables:
                    await cursor.execute(f"DELETE FROM {table} WHERE giveaway_id = %s", (giveaway_id,))
                await cursor.execute("DELETE FROM giveaway WHERE giveaway_id = %s", (giveaway_id,))
        except Exception as e:
            print(f"Error deleting giveaway {giveaway_id}: {e}")
            raise

    @staticmethod
    async def delete_old() -> None:
        """Delete old ended giveaways and their related data."""
        try:
            async with transaction() as conn, conn.cursor() as cursor:
                await cursor.execute("SELECT giveaway_id FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK")
                old_ids = [row[0] for row in await cursor.fetchall()]
                if not old_ids:
                    return

                related_tables = [
                    "giveaway_channelRequirement",
                    "giveawayRoleRequirement",
                    "giveawayParticipant",
                    "giveawayVoiceTime",
                    "giveawayNewMessage",
                    "giveaway_channelMessages",
                ]
                for give_id in old_ids:
                    for table in related_tables:
                        await cursor.execute(f"DELETE FROM {table} WHERE giveaway_id = %s", (give_id,))
                await cursor.execute("DELETE FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK")
        except Exception as e:
            print(f"Error deleting old giveaways: {e}")
            raise

    # ------------------------------------------------------------------ #
    # Giveaway state management
    # ------------------------------------------------------------------ #

    @staticmethod
    async def set_message_id(giveaway_id: int, message_id: int | str) -> None:
        """Set the Discord message ID for a giveaway."""
        query = "UPDATE giveaway SET messageId = %s WHERE giveaway_id = %s"
        params = (message_id, giveaway_id)
        await execute_action(query, params)

    @staticmethod
    async def set_started(giveaway_id: int) -> None:
        """Mark a giveaway as started."""
        query = "UPDATE giveaway SET started = 1 WHERE giveaway_id = %s"
        params = (giveaway_id,)
        await execute_action(query, params)

    @staticmethod
    async def mark_sent(giveaway_id: int, message_id: int) -> None:
        """Atomically set both message_id and started for a giveaway."""
        query = "UPDATE giveaway SET messageId = %s, started = 1 WHERE giveaway_id = %s"
        params = (message_id, giveaway_id)
        await execute_action(query, params)

    @staticmethod
    async def set_ended(giveaway_id: int) -> None:
        """Mark a giveaway as ended."""
        query = "UPDATE giveaway SET ended = 1 WHERE giveaway_id = %s"
        params = (giveaway_id,)
        await execute_action(query, params)

    @staticmethod
    async def set_endtime(giveaway_id: int, endtime: datetime) -> None:
        """Update the end time of a giveaway."""
        query = "UPDATE giveaway SET endtime = %s WHERE giveaway_id = %s"
        params = (endtime, giveaway_id)
        await execute_action(query, params)

    @staticmethod
    async def get_send_ready() -> list[int]:
        """Get IDs of giveaways ready to be sent (started=0, starttime < now)."""
        giveaway_ids: list[int] = []
        async for row in execute_query_iter("SELECT giveaway_id FROM giveaway WHERE started = 0 AND starttime < NOW()"):
            giveaway_ids.append(row[0])
        return giveaway_ids

    @staticmethod
    async def get_end_ready() -> list[int]:
        """Get IDs of giveaways ready to end (ended=0, endtime < now, started=1)."""
        giveaway_ids: list[int] = []
        async for row in execute_query_iter(
            "SELECT giveaway_id FROM giveaway WHERE ended = 0 AND endtime < NOW() AND started = 1 AND messageId <> 'pending'"
        ):
            giveaway_ids.append(row[0])
        return giveaway_ids

    # ------------------------------------------------------------------ #
    # Channel & role requirements
    # ------------------------------------------------------------------ #

    @staticmethod
    async def get_channel_requirements(
        giveaway_id: int,
    ) -> list[GiveawayChannelRequirementModel]:
        """Get channel-specific message requirements for a giveaway."""
        query = "SELECT channel_id, amount FROM giveaway_channelRequirement WHERE giveaway_id = %s"
        params = (giveaway_id,)
        rows: list[GiveawayChannelRequirementModel] = []
        async for row in GiveawayChannelRequirementModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def get_role_requirements(giveaway_id: int) -> list[str]:
        """Get role requirements (role IDs) for a giveaway."""
        query = "SELECT role_id FROM giveawayRoleRequirement WHERE giveaway_id = %s"
        params = (giveaway_id,)
        role_ids: list[str] = []
        async for row in execute_query_iter(query, params):
            role_ids.append(row[0])
        return role_ids

    # ------------------------------------------------------------------ #
    # Participants
    # ------------------------------------------------------------------ #

    @staticmethod
    async def get_participants(giveaway_id: int) -> list[str]:
        """Get all participant user IDs for a giveaway."""
        query = "SELECT user_id FROM giveawayParticipant WHERE giveaway_id = %s"
        params = (giveaway_id,)
        user_ids: list[str] = []
        async for row in execute_query_iter(query, params):
            user_ids.append(row[0])
        return user_ids

    @staticmethod
    async def add_participant(giveaway_id: int, user_id: str) -> None:
        """Add a user as a participant to a giveaway."""
        query = "INSERT INTO giveawayParticipant (user_id, giveaway_id) VALUES (%s, %s)"
        params = (user_id, giveaway_id)
        await execute_action(query, params)

    @staticmethod
    async def remove_participant(giveaway_id: int, user_id: str) -> None:
        """Remove a user from a giveaway's participants."""
        query = "DELETE FROM giveawayParticipant WHERE giveaway_id = %s AND user_id = %s"
        params = (giveaway_id, user_id)
        await execute_action(query, params)

    @staticmethod
    async def is_participant(giveaway_id: int, user_id: str) -> bool:
        """Check if a user is a participant in a giveaway."""
        query = "SELECT * FROM giveawayParticipant WHERE giveaway_id = %s AND user_id = %s"
        params = (giveaway_id, user_id)
        result = await safe_execute_query(query, params)
        return bool(result)

    # ------------------------------------------------------------------ #
    # Participant tracking (voice, messages)
    # ------------------------------------------------------------------ #

    @staticmethod
    async def get_new_messages(giveaway_id: int, user_id: str) -> int | None:
        """Get the count of new messages for a user in a giveaway."""
        query = "SELECT messages FROM giveawayNewMessage WHERE giveaway_id = %s AND user_id = %s"
        params = (giveaway_id, user_id)
        result = await execute_query(query, params)
        return result[0][0] if result else None

    @staticmethod
    async def get_new_messages_channel(giveaway_id: int, channel_id: str, user_id: str) -> int | None:
        """Get the count of new messages in a specific channel for a user in a giveaway."""
        query = "SELECT amount FROM giveaway_channelMessages WHERE giveaway_id = %s AND channel_id = %s AND user_id = %s"
        params = (giveaway_id, channel_id, user_id)
        result = await safe_execute_query(query, params)
        return result[0][0] if result else None

    @staticmethod
    async def get_voice_time(giveaway_id: int, user_id: str) -> int | None:
        """Get voice minutes accumulated for a user in a giveaway."""
        query = "SELECT voiceMinutes FROM giveawayVoiceTime WHERE giveaway_id = %s AND user_id = %s"
        params = (giveaway_id, user_id)
        result = await safe_execute_query(query, params)
        return result[0][0] if result else None

    @staticmethod
    async def add_voice_minutes(user_id: str, guild_id: str) -> None:
        """Increment voice minutes for active giveaways in a guild."""
        query = """
            INSERT INTO giveawayVoiceTime (giveaway_id, user_id, voiceMinutes)
            SELECT giveaway_id, %s, 1 FROM giveaway
            WHERE guild_id = %s AND voiceRequirement IS NOT NULL
            ON DUPLICATE KEY UPDATE voiceMinutes = voiceMinutes + 1
        """
        await execute_action(query, (user_id, guild_id))

    @staticmethod
    async def add_new_message(user_id: str, guild_id: str) -> None:
        """Increment message count for active giveaways in a guild."""
        query = """
            INSERT INTO giveawayNewMessage (giveaway_id, user_id, messages)
            SELECT giveaway_id, %s, 1 FROM giveaway
            WHERE guild_id = %s AND newMessageRequirement IS NOT NULL
            ON DUPLICATE KEY UPDATE messages = messages + 1
        """
        await execute_action(query, (user_id, guild_id))

    @staticmethod
    async def add_new_message_channel(user_id: str, guild_id: str, channel_id: str) -> None:
        """Increment per-channel message count for active giveaways in a guild."""
        query = """
            INSERT INTO giveaway_channelMessages (giveaway_id, channel_id, user_id, amount)
            SELECT giveaway_id, %s, %s, 1 FROM giveaway
            WHERE guild_id = %s AND newMessageRequirement IS NOT NULL
            ON DUPLICATE KEY UPDATE amount = amount + 1
        """
        await execute_action(query, (channel_id, user_id, guild_id))

    # ------------------------------------------------------------------ #
    # Blacklist
    # ------------------------------------------------------------------ #

    @staticmethod
    async def add_blacklisted_user(guild_id: str, user_id: str) -> None:
        """Add a user to the giveaway blacklist."""
        query = "INSERT INTO giveawayBlacklistedUser (guild_id, user_id) VALUES (%s, %s)"
        params = (guild_id, user_id)
        await execute_action(query, params)

    @staticmethod
    async def add_blacklisted_role(guild_id: str, role_id: str) -> None:
        """Add a role to the giveaway blacklist."""
        query = "INSERT INTO giveawayBlacklistedRole (guild_id, role_id) VALUES (%s, %s)"
        params = (guild_id, role_id)
        await execute_action(query, params)

    @staticmethod
    async def remove_blacklisted_user(guild_id: str, user_id: str) -> None:
        """Remove a user from the giveaway blacklist."""
        query = "DELETE FROM giveawayBlacklistedUser WHERE guild_id = %s AND user_id = %s"
        params = (guild_id, user_id)
        await execute_action(query, params)

    @staticmethod
    async def remove_blacklisted_role(guild_id: str, role_id: str) -> None:
        """Remove a role from the giveaway blacklist."""
        query = "DELETE FROM giveawayBlacklistedRole WHERE guild_id = %s AND role_id = %s"
        params = (guild_id, role_id)
        await execute_action(query, params)

    @staticmethod
    async def get_blacklisted_users(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
        """Get all blacklisted users for a guild."""
        query = "SELECT user_id, reason FROM giveawayBlacklistedUser WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[GiveawayBlacklistEntryModel] = []
        async for row in GiveawayBlacklistEntryModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def get_blacklisted_roles(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
        """Get all blacklisted roles for a guild."""
        query = "SELECT role_id, reason FROM giveawayBlacklistedRole WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[GiveawayBlacklistEntryModel] = []
        async for row in GiveawayBlacklistEntryModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def is_user_blacklisted(guild_id: str, user_id: str) -> bool:
        """Check if a user is blacklisted from giveaways."""
        query = "SELECT * FROM giveawayBlacklistedUser WHERE guild_id = %s AND user_id = %s"
        params = (guild_id, user_id)
        result = await execute_query(query, params)
        return bool(result and len(result) > 0)


# Module-level convenience instance
giveaway_service = GiveawayService()
