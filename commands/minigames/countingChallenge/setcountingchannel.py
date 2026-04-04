import discord

from api import set_counting_challenge_progress
from localizer import tanjunLocalizer
from utility import CommandInfo, checkIfHasPro, tanjunEmbed


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

    if commandInfo.client.user is None:
        return
    selfMember = commandInfo.guild.get_member(commandInfo.client.user.id)
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

<<<<<<< HEAD
    await set_counting_challenge_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)
=======
    await set_counting_challenge_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)  # type: ignore[call-arg]
>>>>>>> 9d4519f (hopefully finally fix all mypy issues.)

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
