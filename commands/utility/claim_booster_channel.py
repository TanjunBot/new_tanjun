from locale_keys import locale
import discord
from services.booster_service import BoosterType, ClaimedBoosterType, booster_service
from utility import command_info, tanjunEmbed

async def claimBoosterChannel(command_info: command_info, name: str):
    booster_channel = await booster_service.get(BoosterType.CHANNEL, str(command_info.guild.id))
    if not booster_channel:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterchannel.no_booster_role.title(command_info.locale), description=locale.commands.utility.claimboosterchannel.no_booster_role.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not command_info.user.premium_since:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterchannel.nobooster.title(command_info.locale), description=locale.commands.utility.claimboosterchannel.nobooster.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    claimed_booster_channel = await booster_service.get_claim_for_user(ClaimedBoosterType.CHANNEL, str(command_info.user.id), str(command_info.guild.id))
    if claimed_booster_channel:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterchannel.already_claimed.title(command_info.locale), description=locale.commands.utility.claimboosterchannel.already_claimed.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    channel = command_info.guild.get_channel(int(booster_channel))
    if not channel:
        embed = tanjunEmbed(title=locale.commands.utility.claimboosterchannel.category_not_found.title(command_info.locale), description=locale.commands.utility.claimboosterchannel.category_not_found.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    reason = locale.commands.utility.claimboosterchannel.success.reason(command_info.locale)
    overwrites = {command_info.guild.default_role: discord.PermissionOverwrite(connect=False), command_info.user: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True)}
    new_channel = await command_info.guild.create_voice_channel(name=name, reason=reason, category=channel, overwrites=overwrites)
    await booster_service.claim(ClaimedBoosterType.CHANNEL, str(command_info.user.id), str(new_channel.id), str(command_info.guild.id))
    embed = tanjunEmbed(title=locale.commands.utility.claimboosterchannel.success.title(command_info.locale), description=locale.commands.utility.claimboosterchannel.success.description(command_info.locale))
    await command_info.reply(embed=embed)

async def remove_claimed_booster_channels_that_are_expired(client: discord.Client):
    claimed_booster_channels = await booster_service.get_all_claims(ClaimedBoosterType.CHANNEL)
    for entry in claimed_booster_channels:
        guild = client.get_guild(int(entry.guild_id))
        if not guild:
            await booster_service.unclaim(ClaimedBoosterType.CHANNEL, str(entry.user_id), str(entry.guild_id))
            continue
        user = guild.get_member(int(entry.user_id))
        if not user:
            await booster_service.unclaim(ClaimedBoosterType.CHANNEL, str(entry.user_id), str(entry.guild_id))
            continue
        channel = guild.get_channel(int(entry.channel_id))
        if not user.premium_since and channel:
            await booster_service.unclaim(ClaimedBoosterType.CHANNEL, str(entry.user_id), str(entry.guild_id))
            await channel.delete(reason=locale.commands.utility.claimboosterchannel.expired.reason(guild.preferred_locale if hasattr(guild, 'preferred_locale') else 'en_US'))
        if not channel:
            await booster_service.unclaim(ClaimedBoosterType.CHANNEL, str(entry.user_id), str(entry.guild_id))