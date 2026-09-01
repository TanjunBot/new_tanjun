from locale_keys import locale
import discord
import utility
from api import get_join_to_create_channel
join_to_create_channels = []

async def memberJoin(voiceState: discord.VoiceState, member: discord.Member) -> None:
    print('memberJoin')
    if not voiceState.channel:
        return
    master_channel = await get_join_to_create_channel(str(voiceState.channel.id))
    print('master_channel', master_channel)
    if not master_channel:
        return
    new_channel = await voiceState.channel.clone(name=f'{member.name}')
    print('new_channel', new_channel)
    overwrites = {member: discord.PermissionOverwrite(view_channel=True, manage_channels=True)}
    await new_channel.edit(overwrites=overwrites)
    await member.move_to(new_channel)
    join_to_create_channels.append(new_channel)
    await new_channel.send(embed=utility.tanjunEmbed(title=locale.commands.admin.joinToCreateListener.success.title(member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en'), description=locale.commands.admin.joinToCreateListener.success.description(member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en')), content=member.mention)

async def memberLeave(beforeVoice: discord.VoiceState) -> None:
    if not beforeVoice.channel:
        return
    if beforeVoice.channel.id in join_to_create_channels:
        if len(beforeVoice.channel.members) >= 1:
            return
        await beforeVoice.channel.delete()
        join_to_create_channels.remove(beforeVoice.channel)

async def removeAllJoinToCreateChannels() -> None:
    for channel in join_to_create_channels:
        for member in channel.members:
            await member.send(embed=utility.tanjunEmbed(title=locale.commands.admin.joinToCreateListener.channelDeleted.title(member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en'), description=locale.commands.admin.joinToCreateListener.channelDeleted.description(member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en')))
        await channel.delete()
    join_to_create_channels.clear()