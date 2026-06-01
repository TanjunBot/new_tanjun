from locale_keys import locale
import discord
from discord.ui import Select, View
import utility
from models import ScheduledMessageModel
from services.scheduled_message_service import ScheduledMessageService

class MessageSelectView(View):

    def __init__(self, messages: list[ScheduledMessageModel], locale: str) -> None:
        super().__init__(timeout=300)
        self.locale = locale
        Select(placeholder=locale.commands.utility.removescheduled.select.placeholder(locale), options=[discord.SelectOption(label=f'ID: {msg.message_id} - {msg.content[:50]}...', description=f"{msg.user_id} | {msg.channel_id or 'DM'}", value=str(msg.message_id)) for msg in messages][:25])

    def set_message(self, message: discord.Message) -> None:
        self.message = message

    async def on_timeout(self) -> None:
        embed = utility.tanjunEmbed(title=locale.commands.utility.removescheduled.error.timeout.title(self.locale), description=locale.commands.utility.removescheduled.error.timeout.description(self.locale))
        if self.message is not None:
            await self.message.edit(embed=embed, view=None)

async def remove_scheduled_message(command_info: utility.CommandInfo, message_id: int | None=None) -> None:
    messages = await ScheduledMessageService.get_user_messages(str(command_info.user.id))
    if not messages:
        embed = utility.tanjunEmbed(title=locale.commands.utility.removescheduled.error.no_messages.title(command_info.locale), description=locale.commands.utility.removescheduled.error.no_messages.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not message_id:
        embed = utility.tanjunEmbed(title=locale.commands.utility.removescheduled.select.title(str(command_info.locale)), description=locale.commands.utility.removescheduled.select.description(command_info.locale))
        view = MessageSelectView(messages, command_info.locale)
        view.set_message(await command_info.reply(embed=embed, view=view))
        return
    message_exists = False
    for msg in messages:
        if msg.message_id == message_id:
            message_exists = True
            break
    if not message_exists:
        embed = utility.tanjunEmbed(title=locale.commands.utility.removescheduled.error.not_found.title(command_info.locale), description=locale.commands.utility.removescheduled.error.not_found.description(command_info.locale, id=message_id))
        await command_info.reply(embed=embed)
        return
    await ScheduledMessageService.cancel(message_id)
    embed = utility.tanjunEmbed(title=locale.commands.utility.removescheduled.success.title(str(command_info.locale)), description=locale.commands.utility.removescheduled.success.description(command_info.locale, id=message_id))
    await command_info.reply(embed=embed)