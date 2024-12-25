from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import (
    get_booster_role,
    get_claimed_booster_role,
    remove_claimed_booster_role,
    add_claimed_booster_role,
)
import utility
import discord


async def claimBoosterRole(
    commandInfo: commandInfo, name: str, color: discord.Color, icon: discord.Attachment
):
    booster_role = await get_booster_role(commandInfo.guild.id)
    if not booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.no_booster_role.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.user.premium_since:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.claimboosterrole.nobooster.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.nobooster.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    claimed_booster_role = await get_claimed_booster_role(commandInfo.user.id)
    if claimed_booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.already_claimed.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.already_claimed.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if color and color.startswith("#"):
        color = color[1:]

    if not utility.check_if_str_is_hex_color(color):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.invalid_color.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.invalid_color.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    role = commandInfo.guild.get_role(int(booster_role))
    if not role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterrole.role_not_found.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    reason = tanjunLocalizer.localize(
        commandInfo.locale, "commands.utility.claimboosterrole.success.reason"
    )
    newRole = await commandInfo.guild.create_role(
        name=name,
        color=int(color, 16) if color else role.color,
        display_icon=icon if icon else None,
        permissions=role.permissions,
        hoist=role.hoist,
        mentionable=role.mentionable,
        reason=reason,
    )
    await newRole.edit(position=role.position + 1)
    await add_claimed_booster_role(
        commandInfo.user.id, newRole.id, commandInfo.guild.id
    )
    await commandInfo.user.add_roles(newRole)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.claimboosterrole.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.claimboosterrole.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_claimed_booster_roles_that_are_expired(client: discord.Client):
    claimed_booster_roles = await get_claimed_booster_role()
    for user, role, guild_id in claimed_booster_roles:
        guild = client.get_guild(int(guild_id))
        user = guild.get_member(int(user))
        role = guild.get_role(int(role))
        if not user.premium_since and role:
            await user.remove_roles(role)
            await remove_claimed_booster_role(user.id, guild_id)
            await role.delete(
                reason=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "de",
                    "commands.utility.claimboosterrole.expired.reason",
                )
            )
        if not role:
            await remove_claimed_booster_role(user.id, guild_id)
