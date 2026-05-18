"""Command availability test for the test_bot admin command.

Called by extensions/administration.py test_bot command.
Verifies that critical slash commands and prefixes commands are registered.
"""

from discord.ext import commands

__test__ = False


# Critical command groups that must be registered
_REQUIRED_COMMAND_GROUPS = {
    "image",
    "games",
    "counting",
    "counting challenge",
    "counting modes",
    "giveaway",
}


async def test_commands(self: commands.Cog, ctx: commands.Context) -> None:  # type: ignore[type-arg]
    """Verify critical commands are registered on the bot's tree."""
    tree = ctx.bot.tree
    if tree is None:
        raise RuntimeError("Command tree not available")

    commands_list = tree.get_commands()
    command_names = {cmd.name for cmd in commands_list}

    missing = _REQUIRED_COMMAND_GROUPS - command_names
    if missing:
        raise AssertionError(f"Missing required command groups: {', '.join(sorted(missing))}")

    await ctx.send(f"✅ All {len(_REQUIRED_COMMAND_GROUPS)} critical command groups registered")
