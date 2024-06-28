from commands.giveaway.utility import sendGiveaway
from api import get_send_ready_giveaways

async def sendReadyGiveaways(client):
    ready_giveaways = await get_send_ready_giveaways()
    print("ready_giveaways", ready_giveaways)
    if ready_giveaways:    
        for giveaway in ready_giveaways:
            await sendGiveaway(giveawayid=giveaway[0], client=client)