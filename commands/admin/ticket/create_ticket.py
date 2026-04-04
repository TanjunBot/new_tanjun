import discord  # type: ignore[import-not-found]

import utility
from api import create_ticket_message
from localizer import tanjunLocalizer


async def create_ticket(  # type: ignore[no-any-unimported]
    commandInfo: utility.CommandInfo,
    channel: discord.TextChannel,
    name: str,
    description: str,
    ping_role: discord.Role | None = None,
    summary_channel: discord.TextChannel | None = None,
    introduction: str | None = None,
) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).moderate_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.create_ticket.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.create_ticket.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if not channel.permissions_for(commandInfo.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.create_ticket.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.create_ticket.missingBotPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    ticket_id = await create_ticket_message(
        guild_id=commandInfo.guild.id,
        channel_id=channel.id,
        name=name,
        description=description,
        ping_role=ping_role.id if ping_role is not None else None,  # type: ignore[arg-type]
        summary_channel_id=summary_channel.id if summary_channel is not None else None,  # type: ignore[arg-type]
        introduction=introduction,  # type: ignore[arg-type]
    )

    view = discord.ui.View()
    label = tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.create_ticket.button.label")
    btn = discord.ui.Button(
        label=label,
        style=discord.ButtonStyle.success,
        emoji="🎫",
        custom_id=f"ticket_create;{ticket_id}",
    )
    view.add_item(btn)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.create_ticket.embed.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.create_ticket.embed.description",
            name=name,
            description=description,
            ping_role=ping_role,
            summary_channel=summary_channel,
        ),
    )

    await channel.send(embed=embed, view=view)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.create_ticket.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.create_ticket.success.description"),
    )
    await commandInfo.reply(embed=embed)
