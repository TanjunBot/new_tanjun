import discord

import utility
from api import create_ticket_message
from localizer import tanjunLocalizer


async def create_ticket(
    command_info: utility.CommandInfo,
    channel: discord.TextChannel,
    name: str,
    description: str,
    ping_role: discord.Role | None = None,
    summary_channel: discord.TextChannel | None = None,
    introduction: str | None = None,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).moderate_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.create_ticket.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.create_ticket.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.create_ticket.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.create_ticket.missingBotPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    ticket_id = await create_ticket_message(
        guild_id=command_info.guild.id,
        channel_id=channel.id,
        name=name,
        description=description,
        ping_role=ping_role.id if ping_role is not None else None,  # type: ignore[arg-type]
        summary_channel_id=summary_channel.id if summary_channel is not None else None,  # type: ignore[arg-type]
        introduction=introduction,  # type: ignore[arg-type]
    )

    view = discord.ui.View()
    label = tanjunLocalizer.localize(str(command_info.locale), "commands.admin.create_ticket.button.label")
    btn = discord.ui.Button(  # type: ignore[var-annotated]
        label=label,
        style=discord.ButtonStyle.success,
        emoji="🎫",
        custom_id=f"ticket_create;{ticket_id}",
    )
    view.add_item(btn)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.create_ticket.embed.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.create_ticket.embed.description",
            name=name,
            description=description,
            ping_role=ping_role,
            summary_channel=summary_channel,
        ),
    )

    await channel.send(embed=embed, view=view)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.create_ticket.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.create_ticket.success.description"),
    )
    await command_info.reply(embed=embed)
