import asyncio

from commands.giveaway.utility import endGiveaway, sendGiveaway
from loops._voice_tracker import voice_user_manager
from services.giveaway_service import giveaway_service

_send_lock = asyncio.Lock()
_end_lock = asyncio.Lock()
_voice_lock = asyncio.Lock()


async def sendReadyGiveaways(client):
    # The scheduler can be ticked again while a previous tick is still
    # sending a message.  Serialising the batch prevents duplicate sends.
    if _send_lock.locked():
        return
    async with _send_lock:
        ready_giveaways = await giveaway_service.get_send_ready()
        if ready_giveaways:
            for giveaway_id in ready_giveaways:
                await sendGiveaway(giveawayid=giveaway_id, client=client)


async def checkVoiceUsers(client):
    if _voice_lock.locked():
        return
    async with _voice_lock:
        for user_id, guild_id in voice_user_manager.get_active_users():
            await giveaway_service.add_voice_minutes(user_id, guild_id)


async def endGiveaways(client):
    if _end_lock.locked():
        return
    async with _end_lock:
        ready_giveaways = await giveaway_service.get_end_ready()
        if ready_giveaways:
            for giveaway_id in ready_giveaways:
                await endGiveaway(giveaway_id=giveaway_id, client=client)
