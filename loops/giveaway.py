from commands.giveaway.utility import sendGiveaway
from api import get_send_ready_giveaways, add_giveaway_voice_minutes_if_needed, check_if_opted_out

voiceUsers = []

async def sendReadyGiveaways(client):
    ready_giveaways = await get_send_ready_giveaways()
    print("ready_giveaways", ready_giveaways)
    if ready_giveaways:    
        for giveaway in ready_giveaways:
            await sendGiveaway(giveawayid=giveaway[0], client=client)

async def checkVoiceUsers(client):
    print(voiceUsers)
    for user in voiceUsers:
        await add_giveaway_voice_minutes_if_needed(user.id, user.guild.id)

def handleVoiceChange(user, before, after):
    if check_if_opted_out(user.id):
        return
    if not after.channel:
        removeVoiceUser(user)
        if len(before.channel.members) == 1:
            removeVoiceUser(before.channel.members[0])
    elif after.afk:
        removeVoiceUser(user)
    elif after.self_mute or after.self_deaf:
        removeVoiceUser(user)
    else:
        addVoiceUser(user)

def addVoiceUser(user):
    if not user in voiceUsers:
        voiceUsers.append(user)

def removeVoiceUser(user):
    if user in voiceUsers:
        voiceUsers.remove(user)