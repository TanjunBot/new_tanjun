import discord
from discord.ui import Select, View

import utility
from api import get_scheduled_messages
from api import remove_scheduled_message as remove_message
from localizer import tanjunLocalizer
from typing import Any


class MessageSelectView(View):
    def __init__(self, messages: list[tuple[Any, ...]], locale: str):
        super().__init__(timeout=300)  # 5 minute timeout
        self.locale = locale

        Select(
            placeholder=tanjunLocalizer.localize(locale, "commands.utility.removescheduled.select.placeholder"),
            options=[
                discord.SelectOption(
                    label=f"ID: {msg[0]} - {msg[4][:50]}...", 
                    description=f"{msg[3]} | {msg[2] or 'DM'}",
                    value=str(msg[0]),
                )
                for msg in messages
            ][:25],
        )

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
        if self.message:
            await self.message.edit(embed=embed, view=None)


async def remove_scheduled_message(commandInfo: utility.commandInfo, message_id: int | None = None) -> None:
    messages = await get_scheduled_messages(commandInfo.user.id)

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
        view = MessageSelectView(messages, commandInfo.locale)
        view.set_message(await commandInfo.reply(embed=embed, view=view))
        return

    message_exists = False
    for msg in messages:
        if msg[0] == message_id:
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
