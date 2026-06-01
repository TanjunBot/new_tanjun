import discord
from commands.minigames._counting_common import require_counting_channel, require_moderate_members
from services.counting_repository import CountingMode, CountingRepository
from utility import CommandInfo, tanjunEmbed
from locale_keys.nav import at
LOCALE_KEY = 'minigames.removecountingchallengechannel'
_NS = at(LOCALE_KEY)
_repo = CountingRepository

async def removecountingchallengechannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return
    current_progress = await require_counting_channel(command_info, channel.id, lambda cid: _repo.get_progress(CountingMode.CHALLENGE, cid), LOCALE_KEY)
    if current_progress is None:
        return
    await _repo.clear(CountingMode.CHALLENGE, channel.id)
    embed = tanjunEmbed(title=_NS.success.title(str(command_info.locale)), description=_NS.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)
    info_embed = tanjunEmbed(title=_NS.channel_message.title(command_info.locale), description=_NS.channel_message.description(command_info.locale))
    await channel.send(embed=info_embed)
