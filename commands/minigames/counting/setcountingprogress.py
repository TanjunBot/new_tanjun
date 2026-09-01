import discord
from commands.minigames._counting_common import require_counting_channel, require_moderate_members, require_valid_progress
from services.counting_repository import CountingMode, CountingRepository
from utility import CommandInfo, tanjunEmbed
from locale_keys.nav import at
LOCALE_KEY = 'minigames.setcountingprogress'
_NS = at(LOCALE_KEY)
_repo = CountingRepository

async def setCountingProgress(command_info: CommandInfo, channel: discord.TextChannel, progress: int) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return
    current_progress = await require_counting_channel(command_info, channel.id, lambda cid: _repo.get_progress(CountingMode.NORMAL, cid), LOCALE_KEY)
    if current_progress is None:
        return
    if await require_valid_progress(command_info, progress, LOCALE_KEY):
        return
    await _repo.set_progress(CountingMode.NORMAL, channel.id, progress, command_info.guild.id)
    embed = tanjunEmbed(title=_NS.success.title(str(command_info.locale)), description=_NS.success.description(str(command_info.locale), channel=channel.mention, progress=progress))
    await command_info.reply(embed=embed)
    info_embed = tanjunEmbed(title=_NS.channel_message.title(str(command_info.locale)), description=_NS.channel_message.description(command_info.locale, progress=progress))
    await channel.send(embed=info_embed)
