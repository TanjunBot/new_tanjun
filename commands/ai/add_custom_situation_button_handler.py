from locale_keys import locale
import logging
import discord
import utility
from services.ai_service import AiService

async def approve_custom_situation(interaction) -> None:
    situation_id = interaction.data['custom_id'].split(';')[1]
    situation = await AiService.get_user_situation(situation_id)
    locale = interaction.data['custom_id'].split(';')[2]
    if not situation:
        await interaction.response.send_message(locale.commands.admin.administration.situation_not_found(locale))
        return
    situation_creator = interaction.client.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(locale.commands.admin.administration.situation_creator_gone(locale), delete_after=25)
        return
    locale = interaction.data['custom_id'].split(';')[2]
    embed = utility.tanjunEmbed(title=locale.commands.ai.approvecustom.success.title(locale), description=locale.commands.ai.approvecustom.success.description(locale))
    await AiService.unlock_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception('Failed to send approval DM to situation creator')
    await interaction.channel.send(locale.commands.admin.administration.situation_approved(locale), delete_after=25)

async def deny_custom_situation(interaction) -> None:
    situation_id = interaction.data['custom_id'].split(';')[1]
    situation = await AiService.get_user_situation(situation_id)
    locale = interaction.data['custom_id'].split(';')[2]
    if not situation:
        await interaction.response.send_message(locale.commands.admin.administration.situation_not_found(locale))
        return
    situation_creator = interaction.bot.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(locale.commands.admin.administration.situation_creator_gone(locale), delete_after=25)
        return
    locale = interaction.data['custom_id'].split(';')[2]
    embed = utility.tanjunEmbed(title=locale.commands.ai.dencustom.success.title(locale), description=locale.commands.ai.dencustom.success.description(locale))
    await AiService.delete_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception('Failed to send denial DM to situation creator')
    await interaction.channel.send(locale.commands.admin.administration.situation_deleted(locale), delete_after=25)