from typing import Any

import discord

import utility
from api import check_if_opted_out, get_ticket_messages_by_id, open_ticket
from localizer import tanjunLocalizer


async def openTicket(interaction: discord.Interaction) -> None:
    data: Any = interaction.data
    if data["custom_id"].split(";")[0] != "ticket_create" or data["custom_id"].split(";")[-1] == "optedOutConfirm":
        return

    await interaction.response.defer(ephemeral=True)

    class OptedOutView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(interaction.locale), "commands.admin.open_ticket.optedOutWarning.confirm"),
            custom_id=interaction.data["custom_id"] + ";optedOutConfirm",  # type: ignore[index, typeddict-item]
        )
        async def optedOutConfirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await open_ticket_2(interaction)
            return

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(interaction.locale), "commands.admin.open_ticket.optedOutWarning.decline"),
            custom_id="optedOutDecline",
        )
        async def optedOutDecline(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    interaction.locale,
                    "commands.admin.open_ticket.optedOutWarning.declined",
                ),
                ephemeral=True,
            )
            return

        async def on_timeout(self) -> None:
            for item in self.children:
                item.disabled = True  # type: ignore[attr-defined]
            await self.message.edit(view=self)  # type: ignore[attr-defined]

    if await check_if_opted_out(interaction.user.id):
        view = OptedOutView()
        await interaction.followup.send(
            tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.admin.open_ticket.optedOutWarning.description",
            ),
            view=view,
            ephemeral=True,
        )
        return
    else:
        await open_ticket_2(interaction)


async def open_ticket_2(interaction: discord.Interaction) -> None:
    data: Any = interaction.data
    ticket_id = data["custom_id"].split(";")[1]
    print("ticket_id", ticket_id)
    ticket = await get_ticket_messages_by_id(ticket_id)

    if not ticket:
        await interaction.response.send_message(
            tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.admin.open_ticket.error.ticketNotFound",
            ),
            ephemeral=True,
        )
        return

    introduction = ticket.introduction
    ping_role = ticket.ping_role

    assert interaction.channel is not None
    assert interaction.guild is not None
    channel = interaction.channel
    if (
        not isinstance(channel, discord.TextChannel)
        or not channel.permissions_for(interaction.guild.me).create_private_threads
    ):
        await interaction.response.send_message(
            tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.admin.open_ticket.error.channelMissingPermission",
            ),
            ephemeral=True,
        )
        return

    locale_str = str(
        interaction.guild.preferred_locale.value if interaction.guild.preferred_locale else interaction.locale.value  # type: ignore[truthy-bool, redundant-expr]
    )
    ticket_created_locale = tanjunLocalizer.localize(
        locale_str,
        "commands.admin.open_ticket.success.ticketCreated",
        user=interaction.user,
    )

    thread = await channel.create_thread(
        name=interaction.user.name,
        reason=ticket_created_locale,
        type=discord.ChannelType.private_thread,
        invitable=False,
    )

    await thread.add_user(interaction.user)

    if ping_role:
        await thread.send(f"<@&{ping_role}>")

    if introduction:
        await thread.send(introduction)

    view = discord.ui.View()
    btn = discord.ui.Button(  # type: ignore[var-annotated]
        style=discord.ButtonStyle.danger,
        label=tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.close_ticket.button.label",
        ),
        custom_id=f"ticket_close;{ticket_id};{thread.id}",
    )
    view.add_item(btn)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.open_ticket.success.ticketCreated",
        ),
    )

    await thread.send(embed=embed, view=view)

    await interaction.followup.send(
        tanjunLocalizer.localize(
            interaction.locale,
            "commands.admin.open_ticket.success.ticketCreated",
        ),
        ephemeral=True,
    )

    await open_ticket(
        guild_id=interaction.guild.id,
        opener_id=interaction.user.id,  # type: ignore[arg-type]
        ticket_message_id=ticket_id,
        channel_id=thread.id,
    )
