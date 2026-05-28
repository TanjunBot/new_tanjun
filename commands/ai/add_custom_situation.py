import random

import discord

import config
import utility
from localizer import tanjunLocalizer
from services.ai_service import AiService, CreateSituationParams


async def add_custom_situation(  # type: ignore[no-untyped-def]
    command_info: utility.CommandInfo,
    name: str,
    situation: str,
    temperature: float = 1,
    top_p: float = 1,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
):
    if len(situation) < 10:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.shortsituation.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.shortsituation.description"),
        )
        await command_info.reply(embed=embed)
        return

    if len(name) < 3:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.shortname.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.shortname.description"),
        )
        await command_info.reply(embed=embed)
        return

    if len(situation) > 4000:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.longsituation.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.longsituation.description"),
        )
        await command_info.reply(embed=embed)
        return

    if len(name) > 15:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.longname.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.longname.description"),
        )
        await command_info.reply(embed=embed)
        return

    if temperature < 0 or temperature > 2:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.invalidtemperature.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.invalidtemperature.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if top_p < 0 or top_p > 1:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.invalidtop_p.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.invalidtop_p.description"),
        )
        await command_info.reply(embed=embed)
        return

    if frequency_penalty < 0 or frequency_penalty > 2:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.invalidfrequency_penalty.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.invalidfrequency_penalty.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if presence_penalty < 0 or presence_penalty > 2:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.invalidpresence_penalty.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.invalidpresence_penalty.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    custom_situation = await AiService.get_situation(name=name)

    is_admin = command_info.user.id in config.adminIds

    if custom_situation and not is_admin:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.namealreadyexists.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.ai.addcustom.namealreadyexists.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    user_custom_situation = await AiService.get_user_situation(command_info.user.id)

    if user_custom_situation and not is_admin:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.alreadyexists.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.alreadyexists.description"),
        )
        await command_info.reply(embed=embed)
        return

    params = CreateSituationParams(
        name=name,
        user_id=(command_info.user.id if not is_admin else random.randint(100000000000000000, 999999999999999999)),
        situation=situation,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    await AiService.create_situation(params)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.addcustom.success.description", name=name),
    )
    await command_info.reply(embed=embed)

    channel = await command_info.client.fetch_channel(1259800737479917578)

    embed = utility.tanjunEmbed(
        title="neue Custom Situation",
        description=f"Name: `{name}`\nUser: `{command_info.user.name}`\nSituation: \n```\n{situation}\n```",
    )
    view = discord.ui.View()
    btn = discord.ui.Button(  # type: ignore[var-annotated]
        label="Akzeptieren",
        style=discord.ButtonStyle.success,
        custom_id="ai_add_custom_situation_approve;" + str(command_info.user.id) + ";" + str(command_info.locale),
        row=0,
    )
    view.add_item(btn)
    btn = discord.ui.Button(
        label="Ablehnen",
        style=discord.ButtonStyle.danger,
        custom_id="ai_add_custom_situation_deny;" + str(command_info.user.id) + ";" + str(command_info.locale),
        row=0,
    )
    view.add_item(btn)
    await channel.send("<@&1152916080986161225>", embed=embed, view=view)  # type: ignore[union-attr]
