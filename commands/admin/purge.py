from typing import cast

import discord

import utility
from localizer import tanjunLocalizer
from utils.checks import check_bot_permission, check_user_permission, send_check_failure


async def purge(
    command_info: utility.CommandInfo,
    amount: int,
    channel: discord.TextChannel | None = None,
    setting: str = "all",
) -> None:
    if channel is None:
        assert command_info.channel is not None
        channel = cast(discord.TextChannel, command_info.channel)  # type: ignore[name-defined]

    # User permission check (channel-scoped)
    result = check_user_permission(command_info, "manage_messages", use_guild_permissions=False, channel=channel)
    if await send_check_failure(command_info, "purge", result):
        return

    # Bot permission check (channel-scoped for purge)
    result = check_bot_permission(command_info, "manage_messages", channel=channel)
    if await send_check_failure(command_info, "purge", result):
        return

    if amount <= 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.invalidAmount.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.invalidAmount.description"),
        )
        await command_info.reply(embed=embed)
        return

    try:
        def check(m: discord.Message) -> bool:  # type: ignore[return]
            if setting == "all":
                return True
            elif setting == "bot":
                return m.author.bot
            elif setting == "user":
                return not m.author.bot
            elif setting == "notPinned":
                return not m.pinned
            elif setting == "userNotPinned":
                return not m.pinned and not m.author.bot
            elif setting == "botNotPinned":
                return not m.pinned and m.author.bot
            elif setting == "notAdmin":
                return not m.author.guild_permissions.administrator  # type: ignore[union-attr]
            elif setting == "userNotAdmin":
                return not m.author.guild_permissions.administrator and not m.author.bot  # type: ignore[union-attr]
            elif setting == "embeds":
                return m.embeds  # type: ignore[return-value]
            elif setting == "files":
                return m.attachments  # type: ignore[return-value]
            elif setting == "notAdminNotPinned":
                return not m.author.guild_permissions.administrator and not m.pinned  # type: ignore[union-attr]

        deleted = await channel.purge(limit=amount, check=check, bulk=True)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.purge.success.description",
                amount=len(deleted),
                channel=channel.mention,
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.purge.error.description"),
        )
        await command_info.reply(embed=embed)
