import logging

import discord

import utility
from localizer import tanjunLocalizer
from services.ai_service import AiService


async def approve_custom_situation(interaction) -> None:  # type: ignore[no-untyped-def]
    situation_id = interaction.data["custom_id"].split(";")[1]
    situation = await AiService.get_user_situation(situation_id)
    locale = interaction.data["custom_id"].split(";")[2]
    if not situation:
        await interaction.response.send_message(tanjunLocalizer.localize(locale, "commands.admin.administration.situation_not_found"))
        return
    situation_creator = interaction.client.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(
            tanjunLocalizer.localize(locale, "commands.admin.administration.situation_creator_gone"),
            delete_after=25,
        )
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.title"),
        description=tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.description"),
    )

    await AiService.unlock_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception("Failed to send approval DM to situation creator")
    await interaction.channel.send(tanjunLocalizer.localize(locale, "commands.admin.administration.situation_approved"), delete_after=25)


async def deny_custom_situation(interaction) -> None:  # type: ignore[no-untyped-def]
    situation_id = interaction.data["custom_id"].split(";")[1]
    situation = await AiService.get_user_situation(situation_id)
    locale = interaction.data["custom_id"].split(";")[2]
    if not situation:
        await interaction.response.send_message(tanjunLocalizer.localize(locale, "commands.admin.administration.situation_not_found"))
        return

    situation_creator = interaction.bot.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(
            tanjunLocalizer.localize(locale, "commands.admin.administration.situation_creator_gone"),
            delete_after=25,
        )
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.title"),
        description=tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.description"),
    )

    await AiService.delete_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException):
        logging.exception("Failed to send denial DM to situation creator")
    await interaction.channel.send(tanjunLocalizer.localize(locale, "commands.admin.administration.situation_deleted"), delete_after=25)
