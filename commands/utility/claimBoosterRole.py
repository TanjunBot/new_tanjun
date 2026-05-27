import discord

import utility
from api import (
    add_claimed_booster_role,
    get_booster_role,
    get_claimed_booster_role,
    remove_claimed_booster_role,
)
from localizer import tanjunLocalizer
from utility import command_info, tanjunEmbed


async def claimBoosterRole(command_info: command_info, name: str, color: discord.Color, icon: discord.Attachment):
    booster_role = await get_booster_role(command_info.guild.id)
    if not booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.no_booster_role.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not command_info.user.premium_since:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.nobooster.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.nobooster.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    claimed_booster_role = await get_claimed_booster_role(command_info.user.id)
    if claimed_booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.already_claimed.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.already_claimed.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if color and color.startswith("#"):
        color = color[1:]

    if not utility.check_if_str_is_hex_color(color):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.invalid_color.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.invalid_color.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    role = command_info.guild.get_role(int(booster_role))
    if not role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterrole.role_not_found.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    reason = tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.success.reason")
    new_role = await command_info.guild.create_role(
        name=name,
        color=int(color, 16) if color else role.color,
        display_icon=icon if icon else None,
        permissions=role.permissions,
        hoist=role.hoist,
        mentionable=role.mentionable,
        reason=reason,
    )
    await new_role.edit(position=role.position + 1)
    await add_claimed_booster_role(command_info.user.id, new_role.id, command_info.guild.id)
    await command_info.user.add_roles(new_role)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.success.title"),
        description=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.success.description"),
    )
    await command_info.reply(embed=embed)


async def remove_claimed_booster_roles_that_are_expired(client: discord.Client):
    claimed_booster_roles = await get_claimed_booster_role()
    for entry in claimed_booster_roles:
        guild = client.get_guild(int(entry.guild_id))
        user = guild.get_member(int(entry.user_id))
        role = guild.get_role(int(entry.role_id))
        if not user.premium_since and role:
            await user.remove_roles(role)
            await remove_claimed_booster_role(user.id, entry.guild_id)
            await role.delete(
                reason=tanjunLocalizer.localize(
                    guild.preferred_locale if hasattr(guild, "preferred_locale") else "en_US",
                    "commands.utility.claimboosterrole.expired.reason",
                )
            )
        if not role:
            await remove_claimed_booster_role(user.id, entry.guild_id)
