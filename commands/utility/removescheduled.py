import discord
from discord.ui import Select, View

import utility
from services.scheduled_message_service import ScheduledMessageService
from localizer import tanjunLocalizer
from models import ScheduledMessageModel


class MessageSelectView(View):
    def __init__(self, messages: list[ScheduledMessageModel], locale: str) -> None:
        super().__init__(timeout=300)  # 5 minute timeout
        self.locale = locale

        Select(
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


async def remove_scheduled_message(command_info: utility.CommandInfo, message_id: int | None = None) -> None:
    messages = await ScheduledMessageService.get_user_messages(str(command_info.user.id))

    if not messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.removescheduled.error.no_messages.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.removescheduled.error.no_messages.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not message_id:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.removescheduled.select.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.removescheduled.select.description",
            ),
        )
        view = MessageSelectView(messages, command_info.locale)
        view.set_message(await command_info.reply(embed=embed, view=view))
        return

    message_exists = False
    for msg in messages:
        if msg.message_id == message_id:
            message_exists = True
            break

    if not message_exists:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.removescheduled.error.not_found.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.removescheduled.error.not_found.description",
                id=message_id,
            ),
        )
        await command_info.reply(embed=embed)
        return

    await ScheduledMessageService.cancel(message_id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.removescheduled.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.removescheduled.success.description",
            id=message_id,
        ),
    )
    await command_info.reply(embed=embed)
