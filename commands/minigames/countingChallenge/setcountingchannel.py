import discord

from api import set_counting_challenge_progress
from localizer import tanjunLocalizer
from utility import checkIfHasPro, commandInfo, tanjunEmbed


async def setCountingChannel(commandInfo: commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
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

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.setcountingchannel.error.no_pro.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.setcountingchannel.error.no_pro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    selfMember = commandInfo.guild.get_member(commandInfo.client.user.id)

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

    await set_counting_challenge_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)

    introductionEmbed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.setcountingchannel.challengeintroduction.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.setcountingchannel.challengeintroduction.description",
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
