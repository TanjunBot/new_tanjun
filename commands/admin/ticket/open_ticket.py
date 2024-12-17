import discord
import utility
from localizer import tanjunLocalizer
from api import get_ticket_messages_by_id, open_ticket


async def openTicket(interaction: discord.Interaction):
    if interaction.data["custom_id"].split(";")[0] != "ticket_create":
        return

    await interaction.response.defer(ephemeral=True)

    ticket_id = interaction.data["custom_id"].split(";")[1]
    ticket = await get_ticket_messages_by_id(ticket_id)

    if not ticket:
        await interaction.reply(
            tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.ticket.open_ticket.error.ticketNotFound",
            ),
            ephemeral=True,
        )
        return
    
    print("ticket", ticket)

    introduction = ticket[3]
    ping_role = ticket[4]
    name = ticket[5]
    description = ticket[6]

    channel = interaction.channel

    if not channel.permissions_for(interaction.guild.me).create_private_threads:
        await interaction.reply(
            tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.ticket.open_ticket.error.channelMissingPermission",
            ),
            ephemeral=True,
        )
        return

    ticket_created_locale = tanjunLocalizer.localize(
        (
            interaction.guild.preferred_locale
            if interaction.guild.preferred_locale
            else interaction.locale
        ),
        "commands.admin.ticket.open_ticket.success.ticketCreated",
        user=interaction.user,
    )

    overwrites = {
        interaction.guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_messages=True,
        ),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_messages=True,
            attach_files=True,
            embed_links=True,
            send_messages_in_threads=True,
        ),
    }

    thread = await channel.create_thread(name=interaction.user.name, reason=ticket_created_locale, type=discord.ChannelType.private_thread, invitable=False)

    await thread.add_user(interaction.user)

    if ping_role:
        await thread.send(f"<@&{ping_role}>")

    if introduction:
        await thread.send(introduction)

    ticket_channel_id = await open_ticket(
        interaction.guild.id, interaction.user.id, ticket_id, thread.id
    )

    view = discord.ui.View()
    btn = discord.ui.Button(
        style=discord.ButtonStyle.danger,
        label=tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.ticket.close_ticket.button.label",
        ),
        custom_id=f"ticket_close;{ticket_id};{thread.id}",
    )
    view.add_item(btn)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.ticket.open_ticket.success.ticketCreated",
        ),
    )

    await thread.send(embed=embed, view=view)

    await interaction.followup.send(
        tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.ticket.open_ticket.success.ticketCreated",
        ),
        ephemeral=True,
    )
