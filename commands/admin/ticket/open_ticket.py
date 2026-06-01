from locale_keys import locale
from typing import Any
import discord
import utility
from api import check_if_opted_out
from services.ticket_service import ticket_service

async def openTicket(interaction: discord.Interaction) -> None:
    data: Any = interaction.data
    if data['custom_id'].split(';')[0] != 'ticket_create' or data['custom_id'].split(';')[-1] == 'optedOutConfirm':
        return
    await interaction.response.defer(ephemeral=True)

    class OptedOutView(discord.ui.View):

        def __init__(self) -> None:
            super().__init__()

        @discord.ui.button(label=locale.commands.admin.open_ticket.optedOutWarning.confirm(str(interaction.locale)), custom_id=interaction.data['custom_id'] + ';optedOutConfirm')
        async def optedOutConfirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await open_ticket_2(interaction)
            return

        @discord.ui.button(label=locale.commands.admin.open_ticket.optedOutWarning.decline(str(interaction.locale)), custom_id='optedOutDecline')
        async def optedOutDecline(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_message(locale.commands.admin.open_ticket.optedOutWarning.declined(interaction.locale), ephemeral=True)
            return

        async def on_timeout(self) -> None:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
    if await check_if_opted_out(interaction.user.id):
        view = OptedOutView()
        await interaction.followup.send(locale.commands.admin.open_ticket.optedOutWarning.description(str(interaction.locale)), view=view, ephemeral=True)
        return
    else:
        await open_ticket_2(interaction)

async def open_ticket_2(interaction: discord.Interaction) -> None:
    data: Any = interaction.data
    ticket_id = data['custom_id'].split(';')[1]
    print('ticket_id', ticket_id)
    ticket = await ticket_service.get_config(int(ticket_id))
    if not ticket:
        await interaction.response.send_message(locale.commands.admin.open_ticket.error.ticketNotFound(str(interaction.locale)), ephemeral=True)
        return
    introduction = ticket.introduction
    ping_role = ticket.ping_role
    assert interaction.channel is not None
    assert interaction.guild is not None
    channel = interaction.channel
    if not isinstance(channel, discord.TextChannel) or not channel.permissions_for(interaction.guild.me).create_private_threads:
        await interaction.response.send_message(locale.commands.admin.open_ticket.error.channelMissingPermission(str(interaction.locale)), ephemeral=True)
        return
    locale_str = str(interaction.guild.preferred_locale.value if interaction.guild.preferred_locale else interaction.locale.value)
    ticket_created_locale = locale.commands.admin.open_ticket.success.ticketCreated(locale_str, user=interaction.user)
    thread = await channel.create_thread(name=interaction.user.name, reason=ticket_created_locale, type=discord.ChannelType.private_thread, invitable=False)
    await thread.add_user(interaction.user)
    if ping_role:
        await thread.send(f'<@&{ping_role}>')
    if introduction:
        await thread.send(introduction)
    view = discord.ui.View()
    btn = discord.ui.Button(style=discord.ButtonStyle.danger, label=locale.commands.admin.close_ticket.button.label(interaction.locale), custom_id=f'ticket_close;{ticket_id};{thread.id}')
    view.add_item(btn)
    embed = utility.tanjunEmbed(title=locale.commands.admin.open_ticket.success.ticketCreated(interaction.locale))
    await thread.send(embed=embed, view=view)
    try:
        await ticket_service.open(guild_id=str(interaction.guild.id), opener_id=str(interaction.user.id), config_id=int(ticket_id), channel_id=str(thread.id))
    except Exception as e:
        try:
            await thread.delete()
        except Exception:
            pass
        await interaction.followup.send(locale.commands.admin.open_ticket.error.ticketNotCreated(interaction.locale), ephemeral=True)
        raise e
    await interaction.followup.send(locale.commands.admin.open_ticket.success.ticketCreated(interaction.locale), ephemeral=True)