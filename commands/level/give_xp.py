import discord

from api import get_custom_formula, get_user_xp, get_xp_scaling, update_user_xp
from localizer import tanjunLocalizer
from utility import commandInfo, get_level_for_xp, tanjunEmbed


async def give_xp_command(commandInfo: commandInfo, user: discord.Member, amount: int):
    if not commandInfo.user.guild_permissions.manage_guild:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.givexp.error.no_permission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.givexp.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if amount <= 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.givexp.error.invalid_amount.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.givexp.error.invalid_amount.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_xp = await get_user_xp(str(commandInfo.guild.id), str(user.id)) or 0
    new_xp = current_xp + amount

    scaling = await get_xp_scaling(str(commandInfo.guild.id))
    custom_formula = await get_custom_formula(str(commandInfo.guild.id))

    old_level = get_level_for_xp(current_xp, scaling, custom_formula)
    new_level = get_level_for_xp(new_xp, scaling, custom_formula)

    await update_user_xp(str(commandInfo.guild.id), str(user.id), new_xp)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.givexp.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.givexp.success.description",
            user=user.mention,
            amount=amount,
            new_xp=new_xp,
            old_level=old_level,
            new_level=new_level,
        ),
    )
    await commandInfo.reply(embed=embed)
