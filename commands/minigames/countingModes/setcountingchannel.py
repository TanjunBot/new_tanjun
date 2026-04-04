from typing import cast
import discord

from api import set_counting_mode_progress
from localizer import tanjunLocalizer
from utility import checkIfHasPro, CommandInfo, tanjunEmbed


async def setCountingChannel(commandInfo: CommandInfo, channel: discord.TextChannel) -> None:
    if commandInfo.guild is None:
        return
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).moderate_members
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_moderate_members_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro((commandInfo.guild.id if commandInfo.guild else 0) if commandInfo.guild else 0):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.setcountingchannel.error.no_pro.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_pro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild or not commandInfo.client.user:
        return
    selfMember = (commandInfo.guild.get_member if commandInfo.guild else None)(commandInfo.client.user.id)
    if selfMember is None:
        return

    if not channel.permissions_for(selfMember).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_send_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_send_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_message_delete_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_message_delete_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).read_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_read_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_read_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).view_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_view_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_view_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_counting_mode_progress(
        channel_id=channel.id,
        (commandInfo.guild.id if commandInfo.guild else 0),
        progress=1,
        mode=8,
        goal=128,
        counter_id="nobody",
    )

    introductionEmbed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.setcountingchannel.modesintroduction.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.setcountingchannel.modesintroduction.description",
        ),
    )
    await channel.send(embed=introductionEmbed)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.setcountingchannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.setcountingchannel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)
