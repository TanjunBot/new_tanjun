from locale_keys import locale
import discord
import utility
from services.ticket_service import TicketMessageConfig, ticket_service

async def create_ticket(command_info: utility.CommandInfo, channel: discord.TextChannel, name: str, description: str, ping_role: discord.Role | None=None, summary_channel: discord.TextChannel | None=None, introduction: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).moderate_members):
        embed = utility.tanjunEmbed(title=locale.commands.admin.create_ticket.missingPermission.title(command_info.locale), description=locale.commands.admin.create_ticket.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(title=locale.commands.admin.create_ticket.missingBotPermission.title(command_info.locale), description=locale.commands.admin.create_ticket.missingBotPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    ticket_id = await ticket_service.create_config(TicketMessageConfig(guild_id=str(command_info.guild.id), channel_id=str(channel.id), name=name, description=description, ping_role=str(ping_role.id) if ping_role is not None else None, summary_channel_id=str(summary_channel.id) if summary_channel is not None else None, introduction=introduction))
    if ticket_id is None:
        embed = utility.tanjunEmbed(title=locale.commands.admin.create_ticket.error.title(command_info.locale), description=locale.commands.admin.create_ticket.error.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    view = discord.ui.View()
    label = locale.commands.admin.create_ticket.button.label(str(command_info.locale))
    btn = discord.ui.Button(label=label, style=discord.ButtonStyle.success, emoji='🎫', custom_id=f'ticket_create;{ticket_id}')
    view.add_item(btn)
    embed = utility.tanjunEmbed(title=locale.commands.admin.create_ticket.embed.title(str(command_info.locale)), description=locale.commands.admin.create_ticket.embed.description(command_info.locale, name=name, description=description, ping_role=ping_role, summary_channel=summary_channel))
    await channel.send(embed=embed, view=view)
    embed = utility.tanjunEmbed(title=locale.commands.admin.create_ticket.success.title(str(command_info.locale)), description=locale.commands.admin.create_ticket.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)