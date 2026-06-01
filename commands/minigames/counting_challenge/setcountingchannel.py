import discord
from commands.minigames._counting_common import require_bot_permissions, require_moderate_members
from services.counting_repository import CountingMode, CountingRepository
from utility import CommandInfo, tanjunEmbed
from locale_keys.nav import at
LOCALE_KEY = 'minigames.setcountingchallengechannel'
_NS = at(LOCALE_KEY)
_repo = CountingRepository

async def setCountingChannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return
    if command_info.guild is None:
        return
    if await require_bot_permissions(command_info, channel):
        return
    await _repo.set_challenge_progress(CountingMode.CHALLENGE, channel_id=channel.id, progress=0, guild_id=command_info.guild.id)
    introduction_embed = tanjunEmbed(title=_NS.challengeintroduction.title(command_info.locale), description=_NS.challengeintroduction.description(command_info.locale))
    await channel.send(embed=introduction_embed)
    embed = tanjunEmbed(title=_NS.success.title(str(command_info.locale)), description=_NS.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)
