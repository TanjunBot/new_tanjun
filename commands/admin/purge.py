import discord

import utility
from localizer import tanjunLocalizer


async def purge(
    commandInfo: utility.CommandInfo,
    amount: int,
    channel: discord.TextChannel | None = None,
    setting: str = "all",
) -> None:
    if channel is None:
        assert commandInfo.channel is not None
        channel = cast(discord.TextChannel, commandInfo.channel)

    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_messages
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.purge.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if not channel.permissions_for(commandInfo.guild.me).manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if amount <= 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.invalidAmount.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.invalidAmount.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:

        def check(m: discord.Message) -> bool:
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
                return not m.author.guild_permissions.administrator
            elif setting == "userNotAdmin":
                return not m.author.guild_permissions.administrator and not m.author.bot
            elif setting == "embeds":
                return m.embeds
            elif setting == "files":
                return m.attachments
            elif setting == "notAdminNotPinned":
                return not m.author.guild_permissions.administrator and not m.pinned

        deleted = await channel.purge(limit=amount, check=check, bulk=True)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.success.description",
                amount=len(deleted),
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.purge.error.description"),
        )
        await commandInfo.reply(embed=embed)
