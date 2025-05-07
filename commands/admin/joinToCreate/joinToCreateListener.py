import discord

import utility
from api import get_join_to_create_channel
from localizer import tanjunLocalizer

joinToCreateChannels = []


async def memberJoin(voiceState: discord.VoiceState, member: discord.Member):
    print("memberJoin")
    if not voiceState.channel:
        return

    masterChannel = await get_join_to_create_channel(voiceState.channel.id)

    print("masterChannel", masterChannel)

    if not masterChannel:
        return

    newChannel = await voiceState.channel.clone(name=f"{member.name}")

    print("newChannel", newChannel)

    overwrites = {member: discord.PermissionOverwrite(view_channel=True, manage_channels=True)}

    await newChannel.edit(overwrites=overwrites)

    await member.move_to(newChannel)

    joinToCreateChannels.append(newChannel)

    await newChannel.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en",
                "commands.admin.joinToCreateListener.success.title",
            ),
            description=tanjunLocalizer.localize(
                member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en",
                "commands.admin.joinToCreateListener.success.description",
            ),
        ),
        content=member.mention,
    )


async def memberLeave(beforeVoice: discord.VoiceState):
    if not beforeVoice.channel:
        return

    if beforeVoice.channel.id in joinToCreateChannels:
        if len(beforeVoice.channel.members) >= 1:
            return
        await beforeVoice.channel.delete()
        joinToCreateChannels.remove(beforeVoice.channel)


async def removeAllJoinToCreateChannels():
    for channel in joinToCreateChannels:
        for member in channel.members:
            await member.send(
                embed=utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en",
                        "commands.admin.joinToCreateListener.channelDeleted.title",
                    ),
                    description=tanjunLocalizer.localize(
                        member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en",
                        "commands.admin.joinToCreateListener.channelDeleted.description",
                    ),
                )
            )
        await channel.delete()
    joinToCreateChannels.clear()
