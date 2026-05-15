import discord
from discord.ui import Select, View

import utility
from api import get_scheduled_messages
from api import remove_scheduled_message as remove_message
from localizer import tanjunLocalizer
from models import ScheduledMessageModel


class MessageSelectView(View):
    def __init__(self, messages: list[ScheduledMessageModel], locale: str, command_info: utility.CommandInfo) -> None:
        super().__init__(timeout=300)  # 5 minute timeout
        self.locale = locale
        self.command_info = command_info
        self.messages = messages

        select = Select(
            placeholder=tanjunLocalizer.localize(locale, "commands.utility.removescheduled.select.placeholder"),
            options=[
                discord.SelectOption(
                    label=f"ID: {msg.message_id} - {msg.content[:50]}...",
                    description=f"{msg.user_id} | {msg.channel_id or 'DM'}",
                    value=str(msg.message_id),
                )
                for msg in messages
            ][:25],
        )
        select.callback = self.select_callback  # type: ignore[method-assign]
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.locale,
                    "commands.utility.removescheduled.error.not_authorized",
                ),
                ephemeral=True,
            )
            return
        selected = interaction.data["values"][0]  # type: ignore[index, typeddict-item]
        await remove_message(int(selected))
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(self.locale), "commands.utility.removescheduled.success.title"),
            description=tanjunLocalizer.localize(
                self.locale,
                "commands.utility.removescheduled.success.description",
                id=selected,
            ),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    def set_message(self, message: discord.Message) -> None:
        self.message = message

    async def on_timeout(self) -> None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(self.locale, "commands.utility.removescheduled.error.timeout.title"),
            description=tanjunLocalizer.localize(
                self.locale,
                "commands.utility.removescheduled.error.timeout.description",
            ),
        )
        if self.message is not None:
            await self.message.edit(embed=embed, view=None)


async def remove_scheduled_message(commandInfo: utility.CommandInfo, message_id: int | None = None) -> None:
    messages = await get_scheduled_messages(str(commandInfo.user.id))

    if not messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.no_messages.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.no_messages.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not message_id:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.removescheduled.select.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.select.description",
            ),
        )
        view = MessageSelectView(messages, commandInfo.locale, commandInfo)
        view.set_message(await commandInfo.reply(embed=embed, view=view))
        return

    message_exists = False
    for msg in messages:
        if msg.message_id == message_id:
            message_exists = True
            break

    if not message_exists:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.removescheduled.error.not_found.description",
                id=message_id,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_message(message_id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.removescheduled.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.removescheduled.success.description",
            id=message_id,
        ),
    )
    await commandInfo.reply(embed=embed)
