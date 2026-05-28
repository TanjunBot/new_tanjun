import discord

from api import get_custom_formula, get_user_xp, get_xp_scaling, update_user_xp
from localizer import tanjunLocalizer
from utility import CommandInfo, get_level_for_xp_async, tanjunEmbed


async def take_xp_command(command_info: CommandInfo, user: discord.Member, amount: int) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_guild
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.takexp.error.no_permission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.takexp.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if amount <= 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.takexp.error.invalid_amount.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.takexp.error.invalid_amount.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    current_xp = await get_user_xp(str(command_info.guild.id), str(user.id)) or 0
    new_xp = max(0, current_xp - amount)  # Ensure XP doesn't go below 0

    scaling = await get_xp_scaling(str(command_info.guild.id))
    custom_formula = await get_custom_formula(str(command_info.guild.id))

    old_level = await get_level_for_xp_async(current_xp, scaling, custom_formula)
    new_level = await get_level_for_xp_async(new_xp, scaling, custom_formula)

    await update_user_xp(str(command_info.guild.id), str(user.id), new_xp)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.takexp.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.level.takexp.success.description",
            user=user.mention,
            amount=amount,
            new_xp=new_xp,
            old_level=old_level,
            new_level=new_level,
        ),
    )
    await command_info.reply(embed=embed)
