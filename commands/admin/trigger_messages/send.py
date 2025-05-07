import discord

from api import check_if_opted_out, is_trigger_message


async def send_trigger_message(message: discord.Message):
    if not message.guild:
        return

    if not message.channel:
        return

    if not message.content:
        return

    if message.author.bot:
        return

    trigger_message = await is_trigger_message(message.guild.id, message.content, message.channel.id)
    if not trigger_message:
        return

    if await check_if_opted_out(message.author.id):
        return
    response = trigger_message[3]
    await message.reply(response)
