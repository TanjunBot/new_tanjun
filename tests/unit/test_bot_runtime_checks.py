from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.test_commands import test_commands as verify_command_tree


@pytest.mark.asyncio
async def test_verify_command_tree_passes_when_required_groups_present() -> None:
    minigame = MagicMock(name="minigame_name")
    minigame.name = "minigame_name"
    counting = MagicMock()
    counting.name = "minigames_countingcmds_name"
    challenge = MagicMock()
    challenge.name = "minigames_cchcmds_name"
    modes = MagicMock()
    modes.name = "minigames_cmodescmds_name"
    minigame.commands = [counting, challenge, modes]

    image = MagicMock()
    image.name = "image_name"
    games = MagicMock()
    games.name = "games_name"
    giveaway = MagicMock()
    giveaway.name = "giveaway_name"

    ctx = MagicMock()
    ctx.bot.tree = MagicMock()
    ctx.bot.tree.get_commands.return_value = [image, games, minigame, giveaway]
    ctx.send = AsyncMock()

    await verify_command_tree(MagicMock(), ctx)

    ctx.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_command_tree_fails_when_root_group_missing() -> None:
    ctx = MagicMock()
    ctx.bot.tree = MagicMock()
    ctx.bot.tree.get_commands.return_value = []
    ctx.send = AsyncMock()

    with pytest.raises(AssertionError, match="Missing required command groups"):
        await verify_command_tree(MagicMock(), ctx)
