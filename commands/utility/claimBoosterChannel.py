import discord

from api import (
    claim_booster_channel,
    get_booster_channel,
    get_claimed_booster_channel,
    remove_claimed_booster_channel,
)
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def claimBoosterChannel(commandInfo: commandInfo, name: str):
    booster_channel = await get_booster_channel(commandInfo.guild.id)
    if not booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.no_booster_role.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.user.premium_since:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.nobooster.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.nobooster.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    claimed_booster_channel = await get_claimed_booster_channel(commandInfo.user.id)
    if claimed_booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.already_claimed.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.already_claimed.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    channel = commandInfo.guild.get_channel(int(booster_channel))
    if not channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.category_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.claimboosterchannel.category_not_found.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    reason = tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.claimboosterchannel.success.reason")
    overwrites = {
        commandInfo.guild.default_role: discord.PermissionOverwrite(connect=False),
        commandInfo.user: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True),
    }
    newChannel = await commandInfo.guild.create_voice_channel(
        name=name, reason=reason, category=channel, overwrites=overwrites
    )
    await claim_booster_channel(commandInfo.user.id, newChannel.id, commandInfo.guild.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.claimboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.claimboosterchannel.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def remove_claimed_booster_channels_that_are_expired(client: discord.Client):
    claimed_booster_channels = await get_claimed_booster_channel()
    for user, channel, guild_id in claimed_booster_channels:
        guild = client.get_guild(int(guild_id))
        user = guild.get_member(int(user))
        channel = guild.get_channel(int(channel))
        if not user.premium_since and channel:
            await remove_claimed_booster_channel(user.id, guild_id)
            await channel.delete(
                reason=tanjunLocalizer.localize(
                    str(guild.preferred_locale) if hasattr(guild, "preferred_locale") else "en_US",
                    "commands.utility.claimboosterchannel.expired.reason",
                )
            )
        if not channel:
            await remove_claimed_booster_channel(user.id, guild_id)
