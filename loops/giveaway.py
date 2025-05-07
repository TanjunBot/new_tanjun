from api import add_giveaway_voice_minutes_if_needed, check_if_opted_out, get_end_ready_giveaways, get_send_ready_giveaways
from commands.giveaway.utility import endGiveaway, sendGiveaway

voiceUsers = []


async def sendReadyGiveaways(client):
    ready_giveaways = await get_send_ready_giveaways()
    if ready_giveaways:
        for giveaway in ready_giveaways:
            await sendGiveaway(giveawayid=giveaway[0], client=client)


async def checkVoiceUsers(client):
    for user in voiceUsers:
        await add_giveaway_voice_minutes_if_needed(user.id, user.guild.id)


async def handleVoiceChange(user, before, after):
    if await check_if_opted_out(user.id):
        return

    channel_members = after.channel.members if after.channel else []
    active_members = [member for member in channel_members if not (member.voice.self_mute or member.voice.self_deaf)]

    if len(active_members) < 2:
        for member in channel_members:
            removeVoiceUser(member)
    else:
        updateVoiceUsers(active_members)


def updateVoiceUsers(active_members):
    global voiceUsers
    current_users_set = set(voiceUsers)
    active_users_set = set(active_members)

    users_to_add = active_users_set - current_users_set
    users_to_remove = current_users_set - active_users_set

    for user in users_to_add:
        addVoiceUser(user)
    for user in users_to_remove:
        removeVoiceUser(user)


def addVoiceUser(user):
    if user not in voiceUsers:
        voiceUsers.append(user)


def removeVoiceUser(user):
    if user in voiceUsers:
        voiceUsers.remove(user)


async def endGiveaways(client):
    ready_giveaways = await get_end_ready_giveaways()
    if ready_giveaways:
        for giveaway in ready_giveaways:
            await endGiveaway(giveaway_id=giveaway[0], client=client)
