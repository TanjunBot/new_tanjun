import utility
from localizer import tanjunLocalizer
from api import addCustomSituation, getCustomSituationFromUser, getCustomSituation
import discord

async def add_custom_situation(
        commandInfo: utility.commandInfo,
        name: str,
        situation: str,
        temperature: float = 1,
        top_p: float = 1,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
):
    if not utility.checkIfhasPlus(commandInfo.user):
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.notplus.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.notplus.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if len(situation) < 10:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.shortsituation.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.shortsituation.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if len(name) < 3:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.shortname.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.shortname.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if len(situation) > 4000:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.longsituation.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.longsituation.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if len(name) > 15:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.longname.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.longname.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if temperature < 0 or temperature > 2:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidtemperature.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidtemperature.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if top_p < 0 or top_p > 1:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidtop_p.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidtop_p.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if frequency_penalty < 0 or frequency_penalty > 2:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidfrequency_penalty.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidfrequency_penalty.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if presence_penalty < 0 or presence_penalty > 2:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidpresence_penalty.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.invalidpresence_penalty.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    customSituation = await getCustomSituation(name=name)

    if customSituation and commandInfo.user.id != 689755528947433555:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.namealreadyexists.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.namealreadyexists.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    userCustomSituation = await getCustomSituationFromUser(commandInfo.user.id)

    if userCustomSituation:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.alreadyexists.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.alreadyexists.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    customSituationId = await addCustomSituation(
        name=name,
        user_id=commandInfo.user.id,
        situation=situation,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )

    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.success.title"),
        description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.addcustom.success.description", name=name),
    )
    await commandInfo.reply(embed=embed)

    channel = await commandInfo.client.fetch_channel(1259800737479917578)

    embed = utility.tanjunEmbed(
        title = "neue Custom Situation",
        description = f"Name: `{name}`\nUser: `{commandInfo.user.name}`\nSituation: \n```\n{situation}\n```",
    )
    view = discord.ui.View()
    btn = discord.ui.Button(
        label = "Akzeptieren",
        style = discord.ButtonStyle.success,
        custom_id = "ai_add_custom_situation_approve;" + str(commandInfo.user.id) + ";" + str(commandInfo.locale),
        row = 0,
    )
    view.add_item(btn)
    btn = discord.ui.Button(
        label = "Ablehnen",
        style = discord.ButtonStyle.danger,
        custom_id = "ai_add_custom_situation_deny;" + str(commandInfo.user.id) + ";" + str(commandInfo.locale),
        row = 0,
    )
    view.add_item(btn)
    await channel.send("<@&1152916080986161225>", embed=embed, view=view)
