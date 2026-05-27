import discord

from api import (
    claim_booster_channel,
    get_booster_channel,
    get_claimed_booster_channel,
    remove_claimed_booster_channel,
)
from localizer import tanjunLocalizer
from utility import command_info, tanjunEmbed


async def claimBoosterChannel(command_info: command_info, name: str):
    booster_channel = await get_booster_channel(command_info.guild.id)
    if not booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.no_booster_role.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not command_info.user.premium_since:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.nobooster.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.nobooster.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    claimed_booster_channel = await get_claimed_booster_channel(command_info.user.id)
    if claimed_booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.already_claimed.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.already_claimed.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    channel = command_info.guild.get_channel(int(booster_channel))
    if not channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.category_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.claimboosterchannel.category_not_found.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    reason = tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterchannel.success.reason")
    overwrites = {
        command_info.guild.default_role: discord.PermissionOverwrite(connect=False),
        command_info.user: discord.PermissionOverwrite(manage_channels=True, connect=True, speak=True),
    }
    new_channel = await command_info.guild.create_voice_channel(
        name=name, reason=reason, category=channel, overwrites=overwrites
    )
    await claim_booster_channel(command_info.user.id, new_channel.id, command_info.guild.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.utility.claimboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.claimboosterchannel.success.description",
        ),
    )
    await command_info.reply(embed=embed)


async def remove_claimed_booster_channels_that_are_expired(client: discord.Client):
    claimed_booster_channels = await get_claimed_booster_channel()
    for entry in claimed_booster_channels:
        guild = client.get_guild(int(entry.guild_id))
        user = guild.get_member(int(entry.user_id))
        channel = guild.get_channel(int(entry.channel_id))
        if not user.premium_since and channel:
            await remove_claimed_booster_channel(user.id, entry.guild_id)
            await channel.delete(
                reason=tanjunLocalizer.localize(
                    guild.preferred_locale if hasattr(guild, "preferred_locale") else "en_US",
                    "commands.utility.claimboosterchannel.expired.reason",
                )
            )
        if not channel:
            await remove_claimed_booster_channel(user.id, entry.guild_id)
