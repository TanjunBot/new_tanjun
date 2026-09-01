from locale_keys import locale
import discord
import utility
from services.booster_service import BoosterType, ClaimedBoosterType, booster_service
from utility import command_info, tanjunEmbed

async def claimBoosterRole(command_info: command_info, name: str, color: discord.Color, icon: discord.Attachment):
    booster_role = await booster_service.get(BoosterType.ROLE, str(command_info.guild.id))
    if not booster_role:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.no_booster_role.title(command_info.locale), description=locale.commands.utility.claimboosterrole.no_booster_role.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not command_info.user.premium_since:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.nobooster.title(command_info.locale), description=locale.commands.utility.claimboosterrole.nobooster.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    claimed_booster_role = await booster_service.get_claim_for_user(ClaimedBoosterType.ROLE, str(command_info.user.id), str(command_info.guild.id))
    if claimed_booster_role:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.already_claimed.title(command_info.locale), description=locale.commands.utility.claimboosterrole.already_claimed.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if color and color.startswith('#'):
        color = color[1:]
    if not utility.check_if_str_is_hex_color(color):
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.invalid_color.title(command_info.locale), description=locale.commands.utility.claimboosterrole.invalid_color.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    role = command_info.guild.get_role(int(booster_role))
    if not role:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.role_not_found.title(command_info.locale), description=locale.commands.utility.claimboosterrole.role_not_found.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    reason = locale.commands.utility.claimboosterrole.success.reason(command_info.locale)
    new_role = await command_info.guild.create_role(name=name, color=int(color, 16) if color else role.color, display_icon=icon if icon else None, permissions=role.permissions, hoist=role.hoist, mentionable=role.mentionable, reason=reason)
    await new_role.edit(position=role.position + 1)
    await booster_service.claim(ClaimedBoosterType.ROLE, str(command_info.user.id), str(new_role.id), str(command_info.guild.id))
    await command_info.user.add_roles(new_role)
    embed = tanjunEmbed(title=locale.commands.utility.claimboosterrole.success.title(command_info.locale), description=locale.commands.utility.claimboosterrole.success.description(command_info.locale))
    await command_info.reply(embed=embed)

async def remove_claimed_booster_roles_that_are_expired(client: discord.Client):
    claimed_booster_roles = await booster_service.get_all_claims(ClaimedBoosterType.ROLE)
    for entry in claimed_booster_roles:
        guild = client.get_guild(int(entry.guild_id))
        if not guild:
            await booster_service.unclaim(ClaimedBoosterType.ROLE, str(entry.user_id), str(entry.guild_id))
            continue
        user = guild.get_member(int(entry.user_id))
        role = guild.get_role(int(entry.role_id))
        if user and role and (not user.premium_since):
            await user.remove_roles(role)
            await booster_service.unclaim(ClaimedBoosterType.ROLE, str(entry.user_id), str(entry.guild_id))
            await role.delete(reason=locale.commands.utility.claimboosterrole.expired.reason(guild.preferred_locale if hasattr(guild, 'preferred_locale') else 'en_US'))
        elif not user or not role:
            await booster_service.unclaim(ClaimedBoosterType.ROLE, str(entry.user_id), str(entry.guild_id))