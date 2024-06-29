from utility import tanjunEmbed, relativeTimeStrToDate
from localizer import tanjunLocalizer
from api import (
    get_giveaway,
    get_giveaway_channel_requirements,
    get_giveaway_role_requirements,
    get_giveaway_participants,
    get_new_messages,
    get_voice_time,
    get_new_messages_channel,
    get_blacklisted_roles,
    check_if_user_blacklisted,
    check_if_opted_out,
    check_if_giveaway_participant,
    add_giveaway_participant as add_giveaway_participant_api,
    remove_giveaway_participant,
    set_giveaway_message_id,
    set_giveaway_started,
    add_giveaway_new_message_channel_if_needed,
    add_giveaway_new_message_if_needed,
    set_giveaway_ended
)
import discord
from datetime import date
import random


async def generateGiveawayEmbed(giveawayInformation, locale):
    requirements_parts = []

    if giveawayInformation["new_message_requirement"]:
        requirements_parts.append(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.new_message_requirement",
                count=giveawayInformation["new_message_requirement"],
            )
        )
    if giveawayInformation["day_requirement"]:
        requirements_parts.append(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.day_requirement",
                count=giveawayInformation["day_requirement"],
            )
        )
    if giveawayInformation["role_requirement"]:
        requirements_parts.append(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.role_requirement",
                roles=", ".join(
                    f"<@&{role}>" for role in giveawayInformation["role_requirement"]
                ),
            )
        )
    if giveawayInformation["voice_requirement"]:
        requirements_parts.append(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.voice_requirement",
                minutes=giveawayInformation["voice_requirement"],
            )
        )
    if giveawayInformation["channel_requirements"]:
        channels_desc = ", ".join(
            f"<#{k}>: {v}"
            for k, v in giveawayInformation["channel_requirements"].items()
        )
        requirements_parts.append(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.channel_requirements",
                channels=channels_desc,
            )
        )

    requirements_text = (
        "\n".join(requirements_parts)
        if requirements_parts
        else tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.no_requirements"
        )
    )

    description = ""

    if giveawayInformation["description"]:
        description += giveawayInformation["description"] + "\n\n"

    if giveawayInformation["price"]:
        description += tanjunLocalizer.localize(
            locale,
            "commands.giveaway.giveawayEmbed.price",
            price=giveawayInformation["price"],
        )

    if giveawayInformation["sponsor"]:
        description += (
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.giveawayEmbed.sponsor",
                sponsor=f"<@{giveawayInformation['sponsor']}>",
            )
            + "\n"
        )

    description += tanjunLocalizer.localize(
        locale,
        "commands.giveaway.giveawayEmbed.description",
        requirements=requirements_text,
        winners=giveawayInformation["winners"],
    )

    if giveawayInformation["end_time"]:
        description += "\n" + tanjunLocalizer.localize(
            locale,
            "commands.giveaway.giveawayEmbed.end_time",
            date=f"<t:{int((relativeTimeStrToDate(giveawayInformation['end_time']) if type(giveawayInformation['end_time']) == str else giveawayInformation['end_time']).timestamp())}:R>",
        )

    # Creating embed with localized content
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            locale,
            "commands.giveaway.giveawayEmbed.title",
            title=giveawayInformation["title"],
        ),
        description=description,
    )

    return embed


async def sendGiveaway(giveawayid, client):
    giveawayInformation = await get_giveaway(giveawayid)

    if not giveawayInformation:
        return

    guildId = giveawayInformation[1]

    guild = client.get_guild(int(guildId))

    if not guild:
        return

    locale = guild.locale if hasattr(guild, "locale") else "en_US"

    role_requirements = await get_giveaway_role_requirements(giveawayid)

    channel_requirements = await get_giveaway_channel_requirements(giveawayid)

    giveawayData = {
        "title": giveawayInformation[2],
        "description": giveawayInformation[3],
        "winners": giveawayInformation[4],
        "with_button": giveawayInformation[5],
        "custom_name": giveawayInformation[6],
        "sponsor": giveawayInformation[7],
        "price": giveawayInformation[8],
        "message": giveawayInformation[9],
        "end_time": giveawayInformation[10],
        "start_time": giveawayInformation[11],
        "new_message_requirement": giveawayInformation[14],
        "day_requirement": giveawayInformation[15],
        "role_requirement": role_requirements,
        "voice_requirement": giveawayInformation[16],
        "channel_requirements": channel_requirements,
    }

    embed = await generateGiveawayEmbed(giveawayData, locale)

    channel = guild.get_channel(int(giveawayInformation[18]))

    if not channel:
        return

    view = discord.ui.View()

    participants = await get_giveaway_participants(giveawayid)

    btn = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label=tanjunLocalizer.localize(
            locale, "commands.giveaway.giveawayEmbed.button_text"
        )
        + "("
        + str(len(participants if participants else []))
        + ")",
        custom_id="giveaway_enter; " + str(giveawayid),
    )
    view.add_item(btn)

    message = await channel.send(
        giveawayInformation[9], embed=embed, view=view
    )

    await set_giveaway_message_id(giveawayid, message.id)
    await set_giveaway_started(giveawayid)

async def updateGiveawayEmbed(giveawayid, client):
    giveawayInformation = await get_giveaway(giveawayid)

    if not giveawayInformation:
        return

    guildId = giveawayInformation[1]

    guild = client.get_guild(int(guildId))

    if not guild:
        return

    locale = guild.locale if hasattr(guild, "locale") else "en_US"

    role_requirements = await get_giveaway_role_requirements(giveawayid)

    channel_requirements = await get_giveaway_channel_requirements(giveawayid)

    giveawayData = {
        "title": giveawayInformation[2],
        "description": giveawayInformation[3],
        "winners": giveawayInformation[4],
        "with_button": giveawayInformation[5],
        "custom_name": giveawayInformation[6],
        "sponsor": giveawayInformation[7],
        "price": giveawayInformation[8],
        "message": giveawayInformation[9],
        "end_time": giveawayInformation[10],
        "start_time": giveawayInformation[11],
        "new_message_requirement": giveawayInformation[14],
        "day_requirement": giveawayInformation[15],
        "role_requirement": role_requirements,
        "voice_requirement": giveawayInformation[16],
        "channel_requirements": channel_requirements,
    }

    embed = await generateGiveawayEmbed(giveawayData, locale)

    channel = guild.get_channel(int(giveawayInformation[18]))

    if not channel:
        return

    message = await channel.fetch_message(int(giveawayInformation[19]))

    await message.edit(embed=embed)

async def add_giveaway_participant(giveawayid, userid, client):
    giveawayInformation = await get_giveaway(giveawayid)

    if not giveawayInformation:
        return

    guildId = giveawayInformation[1]

    guild = client.get_guild(int(guildId))

    if not guild:
        return

    member = guild.get_member(userid)

    if not member:
        return

    if await check_if_giveaway_participant(giveawayid, userid):
        await remove_giveaway_participant(giveawayid, userid)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_removed.title",
            ),
            description=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_removed.description",
            ),
        )

        giveawayChannel = guild.get_channel(int(giveawayInformation[18]))
        giveawaymessage = await giveawayChannel.fetch_message(
            int(giveawayInformation[19])
        )

        view = discord.ui.View()

        participants = await get_giveaway_participants(giveawayid)
        print("participants: ", participants)
        btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US", "commands.giveaway.giveawayEmbed.button_text"
            )
            + "("
            + str(len(participants if participants else []) - (1 if userid in (participants if participants else []) else 0))
            + ")",
            custom_id="giveaway_enter; " + str(giveawayid),
        )
        view.add_item(btn)

        await giveawaymessage.edit(view=view)

        return embed

    if await check_if_user_blacklisted(guildId, userid):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_failed.title",
            ),
            description=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_failed.blacklisted",
            ),
        )
        return embed

    if await check_if_opted_out(userid):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_failed.title",
            ),
            description=tanjunLocalizer.localize(
                guild.locale if hasattr(guild, "locale") else "en_US",
                "commands.giveaway.giveawayEmbed.participation_failed.opted_out",
            ),
        )
        return embed

    # check if has a role that is blacklisted
    blacklisted_roles = await get_blacklisted_roles(guildId)

    if blacklisted_roles:
        if any(str(role.id) in blacklisted_roles for role in member.roles):
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.blacklisted_role",
                ),
            )
            return embed

    # check if new Message requirement is met
    if giveawayInformation[14]:
        new_messages = await get_new_messages(giveaway_id=giveawayid, user_id=userid)
        if not new_messages:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.message_requirement",
                    new_messages=0,
                    required_messages=giveawayInformation[14],
                    missing_messages=giveawayInformation[14],
                ),
            )
            return embed
        
        elif new_messages < giveawayInformation[14]:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.message_requirement",
                    new_messages=new_messages,
                    required_messages=giveawayInformation[14],
                    missing_messages=giveawayInformation[14] - new_messages,
                ),
            )
            return embed

    # check if day requirement is met
    if giveawayInformation[15]:
        member = guild.get_member(userid)
        if not member:
            return

        joinDate = member.joined_at.replace(tzinfo=None)

        if not joinDate:
            return

        giveawayStartDate = giveawayInformation[11]

        if not giveawayStartDate:
            return

        days = (giveawayStartDate - joinDate).days

        if days < giveawayInformation[15]:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.day_requirement",
                    required_days=giveawayInformation[15],
                ),
            )
            return embed

    # check if voice requirement is met
    if giveawayInformation[16]:
        member = guild.get_member(userid)
        if not member:
            return

        voice_time = await get_voice_time(guildId, userid)

        if not voice_time:
            voice_time = 0

        if voice_time < giveawayInformation[16]:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.voice_requirement",
                    required_minutes=giveawayInformation[16],
                    missing_minutes=giveawayInformation[16] - voice_time,
                ),
            )
            return embed

    # check if role requirement is met
    role_requirements = await get_giveaway_role_requirements(giveawayid)

    if role_requirements:
        member = guild.get_member(userid)
        if not member:
            return

        if not any(role in role_requirements for role in member.roles):
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.title",
                ),
                description=tanjunLocalizer.localize(
                    guild.locale if hasattr(guild, "locale") else "en_US",
                    "commands.giveaway.giveawayEmbed.participation_failed.role_requirement",
                    roles=", ".join(f"<@&{role}>" for role in role_requirements),
                ),
            )
            return embed

    # check if channel requirement is met
    channel_requirements = await get_giveaway_channel_requirements(giveawayid)

    if channel_requirements:
        member = guild.get_member(userid)
        if not member:
            return

        for channel, count in channel_requirements.items():
            messages = await get_new_messages_channel(guildId, userid, channel, count)

            if not messages:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        guild.locale if hasattr(guild, "locale") else "en_US",
                        "commands.giveaway.giveawayEmbed.participation_failed.title",
                    ),
                    description=tanjunLocalizer.localize(
                        guild.locale if hasattr(guild, "locale") else "en_US",
                        "commands.giveaway.giveawayEmbed.participation_failed.channel_requirement",
                        channel=channel,
                        required_messages=count,
                        missing_messages=count,
                    ),
                )
                return embed

    # add participant to giveaway
    await add_giveaway_participant_api(giveawayid, userid)

    giveawayChannel = guild.get_channel(int(giveawayInformation[18]))
    giveawaymessage = await giveawayChannel.fetch_message(int(giveawayInformation[19]))

    view = discord.ui.View()

    participants = await get_giveaway_participants(giveawayid)
    btn = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label=tanjunLocalizer.localize(
            guild.locale if hasattr(guild, "locale") else "en_US", "commands.giveaway.giveawayEmbed.button_text"
        )
        + "("
        + str(len(participants if participants else []) + (1 if not userid in (participants if participants else []) else 0))
        + ")",
        custom_id="giveaway_enter; " + str(giveawayid),
    )
    view.add_item(btn)

    await giveawaymessage.edit(view=view)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            guild.locale if hasattr(guild, "locale") else "en_US",
            "commands.giveaway.giveawayEmbed.participation_success.title",
        ),
        description=tanjunLocalizer.localize(
            guild.locale if hasattr(guild, "locale") else "en_US",
            "commands.giveaway.giveawayEmbed.participation_success.description",
        ),
    )

    return embed

async def addMessageToGiveaway(message: discord.Message):
    if await check_if_opted_out(message.author.id):
        return
    
    if message.author.bot:
        return
    
    await add_giveaway_new_message_if_needed(message.author.id, message.guild.id)

    await add_giveaway_new_message_channel_if_needed(message.author.id, message.guild.id, message.channel.id)

async def endGiveaway(giveaway_id, client):
    giveawayInformation = await get_giveaway(giveaway_id)

    if giveawayInformation[13] == 1:
        return

    await set_giveaway_ended(giveaway_id)

    if not giveawayInformation:
        return

    guildId = giveawayInformation[1]

    guild = client.get_guild(int(guildId))

    if not guild:
        return

    locale = guild.locale if hasattr(guild, "locale") else "en_US"

    participants = await get_giveaway_participants(giveaway_id)

    if not participants:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                locale,
                "commands.giveaway.endedGiveaway.no_participants.title",
            ),
            description=tanjunLocalizer.localize(
                locale,
                "commands.giveaway.endedGiveaway.no_participants.description",
            ),
        )
        giveawayChannel = guild.get_channel(int(giveawayInformation[18]))
        if not giveawayChannel:
            return
        try:
            giveawaymessage = await giveawayChannel.fetch_message(
                int(giveawayInformation[19])
            )
        except Exception as e:
            return
        if not giveawaymessage:
            return
        
        view = discord.ui.View()

        btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label=tanjunLocalizer.localize(
                locale, "commands.giveaway.endedGiveaway.button_text", participants=0
            ),
            disabled=True,
        )
        view.add_item(btn)

        await giveawaymessage.edit(view=view)
        await giveawaymessage.reply(embed=embed)
        return
    


    winners = []

    if not participants:
        participants = []

    participantAmount = len(participants)


    if giveawayInformation[4] > participantAmount:
        winners = participants
    else:
        for i in range(giveawayInformation[4]):
            winner = random.choice(participants)
            participants.remove(winner)
            winners.append(winner)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            locale,
            "commands.giveaway.endedGiveaway.title",
        ),
        description=tanjunLocalizer.localize(
            locale,
            "commands.giveaway.endedGiveaway.description",
            winners=", ".join(f"<@{winner}>" for winner in winners),
        ),
    )

    for winner in winners:
        await remove_giveaway_participant(giveaway_id, winner)
        member = guild.get_member(winner)
        if member:
            try:
                await member.send(
                    tanjunLocalizer.localize(
                        locale,
                        "commands.giveaway.endedGiveaway.winnerDM",
                        guild_name=guild.name,
                    )
                )
            except:
                pass

    giveawayChannel = guild.get_channel(int(giveawayInformation[18]))
    if not giveawayChannel:
        return
    try:
        giveawaymessage = await giveawayChannel.fetch_message(
            int(giveawayInformation[19])
        )
    except:
        return
    if not giveawaymessage:
        return

    view = discord.ui.View()

    btn = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label=tanjunLocalizer.localize(
            locale, "commands.giveaway.endedGiveaway.button_text", participants=participantAmount
        ),
        disabled=True,
    )
    view.add_item(btn)

    await giveawaymessage.edit(view=view)
    await giveawaymessage.reply(embed=embed)

    for winner in winners:

        member = guild.get_member(winner)

        if not member:
            continue

        await member.send(
            tanjunLocalizer.localize(
                locale,
                "commands.giveaway.endedGiveaway.dm",
                guild_name=guild.name,
            )
        )

    return embed

async def updateGiveawayMessage(giveaway_id, client):
    giveawayInformation = await get_giveaway(giveaway_id)

    if not giveawayInformation:
        return

    guildId = giveawayInformation[1]

    guild = client.get_guild(int(guildId))

    if not guild:
        return

    locale = guild.locale if hasattr(guild, "locale") else "en_US"

    role_requirements = await get_giveaway_role_requirements(giveaway_id)

    channel_requirements = await get_giveaway_channel_requirements(giveaway_id)

    giveawayData = {
        "title": giveawayInformation[2],
        "description": giveawayInformation[3],
        "winners": giveawayInformation[4],
        "with_button": giveawayInformation[5],
        "custom_name": giveawayInformation[6],
        "sponsor": giveawayInformation[7],
        "price": giveawayInformation[8],
        "message": giveawayInformation[9],
        "end_time": giveawayInformation[10],
        "start_time": giveawayInformation[11],
        "new_message_requirement": giveawayInformation[14],
        "day_requirement": giveawayInformation[15],
        "role_requirement": role_requirements,
        "voice_requirement": giveawayInformation[16],
        "channel_requirements": channel_requirements,
    }

    embed = await generateGiveawayEmbed(giveawayData, locale)

    channel = guild.get_channel(int(giveawayInformation[18]))

    if not channel:
        return

    try:
        message = await channel.fetch_message(int(giveawayInformation[19]))
        await message.edit(embed=embed)
    except discord.errors.NotFound:
        print(f"Giveaway message not found for giveaway ID {giveaway_id}")
