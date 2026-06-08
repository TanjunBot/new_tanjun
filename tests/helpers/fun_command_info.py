from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from tests.helpers.permission_profiles import PermissionProfile, command_info_for_permission


def command_info_for_profile(profile: PermissionProfile, *, reply: AsyncMock | None = None) -> MagicMock:
    return command_info_for_permission(profile, reply=reply)
