import discord

import utility
from services.booster_service import BoosterType, ClaimedBoosterType, booster_service
from localizer import tanjunLocalizer
from utility import command_info, tanjunEmbed


async def claimBoosterRole(command_info: command_info, name: str, color: discord.Color, icon: discord.Attachment):
    booster_role = await booster_service.get(BoosterType.ROLE, str(command_info.guild.id))
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

    claimed_booster_role = await booster_service.get_user_claims(ClaimedBoosterType.ROLE, str(command_info.user.id))
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
    await booster_service.claim(ClaimedBoosterType.ROLE, str(command_info.user.id), str(new_role.id), str(command_info.guild.id))
    await command_info.user.add_roles(new_role)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.success.title"),
        description=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterrole.success.description"),
    )
    await command_info.reply(embed=embed)


async def remove_claimed_booster_roles_that_are_expired(client: discord.Client):
    claimed_booster_roles = await booster_service.get_all_claims(ClaimedBoosterType.ROLE)
    for entry in claimed_booster_roles:
        guild = client.get_guild(int(entry.guild_id))
        user = guild.get_member(int(entry.user_id))
        role = guild.get_role(int(entry.role_id))
        if not user.premium_since and role:
            await user.remove_roles(role)
            await booster_service.unclaim(ClaimedBoosterType.ROLE, str(user.id), str(entry.guild_id))
            await role.delete(
                reason=tanjunLocalizer.localize(
                    guild.preferred_locale if hasattr(guild, "preferred_locale") else "en_US",
                    "commands.utility.claimboosterrole.expired.reason",
                )
            )
        if not role:
            await booster_service.unclaim(ClaimedBoosterType.ROLE, str(user.id), str(entry.guild_id))
