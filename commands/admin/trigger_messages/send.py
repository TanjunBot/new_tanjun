import discord

from api import check_if_opted_out
from services.trigger_message_service import trigger_message_service


async def send_trigger_message(message: discord.Message) -> None:
    if not message.guild:
        return

    if not message.channel:  # type: ignore[truthy-bool]
        return

    if not message.content:
        return

    trigger_message = await trigger_message_service.match(message.guild.id, message.content, message.channel.id)
    if not trigger_message:
        return

    if await check_if_opted_out(message.author.id):
        return
    response = trigger_message.response
    await message.reply(response)
