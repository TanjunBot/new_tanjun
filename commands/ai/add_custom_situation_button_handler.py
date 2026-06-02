from locale_keys import locale as l10n
import logging
import discord
import utility
from services.ai_service import AiService

async def approve_custom_situation(interaction) -> None:
    situation_id = interaction.data['custom_id'].split(';')[1]
    situation = await AiService.get_user_situation(situation_id)
    locale_str = interaction.data['custom_id'].split(';')[2]
    if not situation:
        await interaction.response.send_message(l10n.commands.admin.administration.situation_not_found(locale_str))
        return
    situation_creator = interaction.client.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(l10n.commands.admin.administration.situation_creator_gone(locale_str), delete_after=25)
        return
    locale_str = interaction.data['custom_id'].split(';')[2]
    embed = utility.tanjunEmbed(title=l10n.commands.ai.approvecustom.success.title(locale_str), description=l10n.commands.ai.approvecustom.success.description(locale_str))
    await AiService.unlock_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception('Failed to send approval DM to situation creator')
    await interaction.channel.send(l10n.commands.admin.administration.situation_approved(locale_str), delete_after=25)

async def deny_custom_situation(interaction) -> None:
    situation_id = interaction.data['custom_id'].split(';')[1]
    situation = await AiService.get_user_situation(situation_id)
    locale_str = interaction.data['custom_id'].split(';')[2]
    if not situation:
        await interaction.response.send_message(l10n.commands.admin.administration.situation_not_found(locale_str))
        return
    situation_creator = interaction.bot.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(l10n.commands.admin.administration.situation_creator_gone(locale_str), delete_after=25)
        return
    locale_str = interaction.data['custom_id'].split(';')[2]
    embed = utility.tanjunEmbed(title=l10n.commands.ai.dencustom.success.title(locale_str), description=l10n.commands.ai.dencustom.success.description(locale_str))
    await AiService.delete_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception('Failed to send denial DM to situation creator')
    await interaction.channel.send(l10n.commands.admin.administration.situation_deleted(locale_str), delete_after=25)