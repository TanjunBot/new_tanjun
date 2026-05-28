from services.giveaway_service import giveaway_service
from commands.giveaway.utility import endGiveaway, sendGiveaway
from loops._voice_tracker import voice_user_ids


async def sendReadyGiveaways(client):
    ready_giveaways = await giveaway_service.get_send_ready()
    if ready_giveaways:
        for giveaway_id in ready_giveaways:
            await sendGiveaway(giveawayid=giveaway_id, client=client)


async def checkVoiceUsers(client):
    for user_id, guild_id in list(voice_user_ids):
        await giveaway_service.add_voice_minutes(user_id, guild_id)


async def endGiveaways(client):
    ready_giveaways = await giveaway_service.get_end_ready()
    if ready_giveaways:
        for giveaway_id in ready_giveaways:
            await endGiveaway(giveaway_id=giveaway_id, client=client)
