"""LevelConfigRepository: Consolidated CRUD for guild level configuration.

Replaces 20+ individual set_/get_ functions in api.py with a single repository
that works with the LevelConfig Pydantic model.
"""

from dataclasses import dataclass

from models import LevelConfig


@dataclass
class LevelConfigRepository:
    """Repository for managing guild level configuration.

    Provides full-config load/save and partial updates, reducing DB
    round-trips from 10+ individual queries to 1-2 per operation.
    """

    async def get_config(self, guild_id: str) -> LevelConfig:
        """Load the full LevelConfig for a guild, returning defaults if none exists."""
        from api import _guild_config_cache, execute_query

        cached = _guild_config_cache.get(guild_id)
        if cached is not None:
            if cached:
                return LevelConfig(
                    guild_id=guild_id,
                    active=cached.get("active", True),
                    difficulty=cached.get("scaling", "medium"),
                    custom_formula=cached.get("custom_formula"),
                    level_up_message_active=cached.get("level_up_message_active", True),
                    level_up_message=cached.get("level_up_message"),
                    level_up_channel_id=cached.get("level_up_channel_id"),
                    text_cooldown=cached.get("text_cooldown", 60),
                    voice_cooldown=cached.get("voice_cooldown", 60),
                )
            return LevelConfig(guild_id=guild_id)

        query = """
        SELECT guild_id, active, difficulty, customFormula, level_up_messageActive,
               level_up_message, level_up_channel_id, textCooldown, voiceCooldown
        FROM levelConfig WHERE guild_id = %s
        """
        params = (guild_id,)
        result = await execute_query(query, params)
        if result and len(result) > 0:
            config = LevelConfig.from_row(result[0])
            _guild_config_cache.set(
                guild_id,
                {
                    "active": config.active,
                    "scaling": config.difficulty,
                    "custom_formula": config.custom_formula,
                    "level_up_message_active": config.level_up_message_active,
                    "level_up_message": config.level_up_message,
                    "level_up_channel_id": config.level_up_channel_id,
                    "text_cooldown": config.text_cooldown,
                    "voice_cooldown": config.voice_cooldown,
                },
            )
            return config
        _guild_config_cache.set(guild_id, {})
        return LevelConfig(guild_id=guild_id)

    async def save_config(self, config: LevelConfig) -> None:
        """Save the full LevelConfig using ON DUPLICATE KEY UPDATE (single query)."""
        from api import execute_action

        query = """
        INSERT INTO levelConfig (guild_id, active, difficulty, customFormula,
            level_up_messageActive, level_up_message, level_up_channel_id,
            textCooldown, voiceCooldown)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            active = VALUES(active),
            difficulty = VALUES(difficulty),
            customFormula = VALUES(customFormula),
            level_up_messageActive = VALUES(level_up_messageActive),
            level_up_message = VALUES(level_up_message),
            level_up_channel_id = VALUES(level_up_channel_id),
            textCooldown = VALUES(textCooldown),
            voiceCooldown = VALUES(voiceCooldown)
        """
        params = (
            config.guild_id,
            config.active,
            config.difficulty,
            config.custom_formula,
            config.level_up_message_active,
            config.level_up_message,
            config.level_up_channel_id,
            config.text_cooldown,
            config.voice_cooldown,
        )
        await execute_action(query, params)
        self._invalidate(guild_id=config.guild_id)

    async def update_field(self, guild_id: str, **kwargs: object) -> None:
        """Update specific fields on an existing config row.

        Only the provided kwargs are written; other columns are preserved.
        Fields are mapped to DB column names automatically.

        Example::
            await repo.update_field("123", active=True)
            await repo.update_field("123", level_up_message="Welcome!", level_up_message_active=True)
        """
        from api import execute_action

        if not kwargs:
            return

        valid_difficulties = {"easy", "medium", "hard", "extreme", "custom"}

        for key, value in kwargs.items():
            if key == "difficulty":
                if value not in valid_difficulties:
                    raise ValueError(f"Invalid difficulty: {value!r}. Must be one of {valid_difficulties}")
            elif key in ("text_cooldown", "voice_cooldown"):
                if not isinstance(value, int) or value < 0:
                    raise ValueError(f"Invalid {key}: {value!r}. Must be a non-negative integer.")
            elif key == "active":
                if not isinstance(value, bool):
                    raise ValueError(f"Invalid active: {value!r}. Must be a boolean.")
            elif key == "level_up_message_active":
                if not isinstance(value, bool):
                    raise ValueError(f"Invalid level_up_message_active: {value!r}. Must be a boolean.")
            elif key in ("custom_formula", "level_up_message", "level_up_channel_id"):
                if value is not None and not isinstance(value, str):
                    raise ValueError(f"Invalid {key}: {value!r}. Must be a string or None.")

        field_map = {
            "active": "active",
            "difficulty": "difficulty",
            "custom_formula": "customFormula",
            "level_up_message_active": "level_up_messageActive",
            "level_up_message": "level_up_message",
            "level_up_channel_id": "level_up_channel_id",
            "text_cooldown": "textCooldown",
            "voice_cooldown": "voiceCooldown",
        }

        set_clauses = []
        params = []
        for key, value in kwargs.items():
            col = field_map.get(key)
            if col is None:
                raise ValueError(f"Unknown level config field: {key}")
            set_clauses.append(f"{col} = %s")
            params.append(value)

        set_str = ", ".join(set_clauses)
        columns = [field_map[k] for k in kwargs]
        placeholders = ["%s"] * len(kwargs)
        query = f"""
        INSERT INTO levelConfig (guild_id, {", ".join(columns)})
        VALUES (%s, {", ".join(placeholders)})
        ON DUPLICATE KEY UPDATE {set_str}
        """
        vals = tuple([guild_id] + list(params))
        await execute_action(query, vals)
        self._invalidate(guild_id=guild_id)

    async def delete_config(self, guild_id: str) -> None:
        """Delete the level config row for a guild."""
        from api import execute_action

        query = "DELETE FROM levelConfig WHERE guild_id = %s"
        params = (guild_id,)
        await execute_action(query, params)
        self._invalidate(guild_id=guild_id)

    @staticmethod
    def _invalidate(guild_id: str) -> None:
        """Invalidate the guild config cache for this guild."""
        from api import _invalidate_guild_cache

        _invalidate_guild_cache(guild_id)


level_config_repo = LevelConfigRepository()
