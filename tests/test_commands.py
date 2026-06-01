"""Command availability test for the test_bot admin command.

Called by extensions/administration.py test_bot command.
Verifies that critical slash commands and prefixes commands are registered.
"""

from discord.ext import commands

__test__ = False

_REQUIRED_ROOT_GROUPS = {
    "image_name",
    "games_name",
    "minigame_name",
    "giveaway_name",
}

_MINIGAME_SUBGROUPS = {
    "minigames_countingcmds_name",
    "minigames_cchcmds_name",
    "minigames_cmodescmds_name",
}


def _command_names(commands_list: list[object]) -> set[str]:
    return {getattr(cmd, "name", str(cmd)) for cmd in commands_list}


async def test_commands(self: commands.Cog, ctx: commands.Context) -> None:
    """Verify critical commands are registered on the bot's tree."""
    tree = ctx.bot.tree
    if tree is None:
        raise RuntimeError("Command tree not available")

    root_commands = tree.get_commands()
    root_names = _command_names(root_commands)

    missing_roots = _REQUIRED_ROOT_GROUPS - root_names
    if missing_roots:
        raise AssertionError(f"Missing required command groups: {', '.join(sorted(missing_roots))}")

    minigame_group = next(cmd for cmd in root_commands if getattr(cmd, "name", None) == "minigame_name")
    sub_names = _command_names(list(getattr(minigame_group, "commands", [])))
    missing_subs = _MINIGAME_SUBGROUPS - sub_names
    if missing_subs:
        raise AssertionError(f"Missing required minigame subcommands: {', '.join(sorted(missing_subs))}")

    await ctx.send(
        f"✅ All {len(_REQUIRED_ROOT_GROUPS)} critical command groups and "
        f"{len(_MINIGAME_SUBGROUPS)} minigame subcommands registered"
    )
