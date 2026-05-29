"""Repositories package - domain-specific data access layers.

Each repository encapsulates the CRUD operations for a specific domain,
replacing scattered functions in api.py with cohesive, testable classes.
"""

from repositories.level_config_repository import LevelConfigRepository, level_config_repo
from repositories.level_role_repository import LevelRoleRepository, level_role_repo
from repositories.log_blacklist_repository import LogBlacklistRepository, LogBlacklistType, log_blacklist_repo
from repositories.trigger_message_repository import TriggerMessageRepository, trigger_message_repo
from repositories.twitch_repository import TwitchRepository, twitch_repo
from repositories.warning_repository import WarningRepository, warning_repo
from repositories.xp_boost_repository import BoostTarget, XpBoostRepository, xp_boost_repo

__all__ = [
    "BoostTarget",
    "LevelConfigRepository",
    "LevelRoleRepository",
    "LogBlacklistRepository",
    "LogBlacklistType",
    "TriggerMessageRepository",
    "TwitchRepository",
    "WarningRepository",
    "XpBoostRepository",
    "level_config_repo",
    "level_role_repo",
    "log_blacklist_repo",
    "trigger_message_repo",
    "twitch_repo",
    "warning_repo",
    "xp_boost_repo",
]
