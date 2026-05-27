from api import add_giveaway_voice_minutes_if_needed, get_end_ready_giveaways, get_send_ready_giveaways
from commands.giveaway.utility import endGiveaway, sendGiveaway
from loops._voice_tracker import voice_user_ids


async def sendReadyGiveaways(client):
    ready_giveaways = await get_send_ready_giveaways()
    if ready_giveaways:
        for giveaway_id in ready_giveaways:
            await sendGiveaway(giveawayid=giveaway_id, client=client)


async def checkVoiceUsers(client):
    for user_id, guild_id in list(voice_user_ids):
        await add_giveaway_voice_minutes_if_needed(user_id, guild_id)


async def endGiveaways(client):
    ready_giveaways = await get_end_ready_giveaways()
    if ready_giveaways:
        for giveaway_id in ready_giveaways:
            await endGiveaway(giveaway_id=giveaway_id, client=client)
