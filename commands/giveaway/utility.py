from locale_keys import locale
import contextlib
import logging
import random
import discord
from api import check_if_opted_out
from models import GiveawayChannelRequirementModel, GiveawayModel
from services.giveaway_service import giveaway_service
from utility import relativeTimeStrToDate, tanjunEmbed

async def generateGiveawayEmbed(giveaway: GiveawayModel, locale_str: str, role_requirements: list[str], channel_requirements: list[GiveawayChannelRequirementModel]) -> discord.Embed:
    requirements_parts = []
    if giveaway.new_message_requirement:
        requirements_parts.append(locale.commands.giveaway.giveawayEmbed.new_message_requirement(locale_str, count=giveaway.new_message_requirement))
    if giveaway.day_requirement:
        requirements_parts.append(locale.commands.giveaway.giveawayEmbed.day_requirement(locale_str, count=giveaway.day_requirement))
    if role_requirements:
        requirements_parts.append(locale.commands.giveaway.giveawayEmbed.role_requirement(locale_str, roles=', '.join((f'<@&{role}>' for role in role_requirements))))
    if giveaway.voice_requirement:
        requirements_parts.append(locale.commands.giveaway.giveawayEmbed.voice_requirement(locale_str, minutes=giveaway.voice_requirement))
    if channel_requirements:
        channels_desc = ', '.join((f'<#{req.channel_id}>: {req.amount}' for req in channel_requirements))
        requirements_parts.append(locale.commands.giveaway.giveawayEmbed.channel_requirements(locale_str, channels=channels_desc))
    requirements_text = '\n'.join(requirements_parts) if requirements_parts else locale.commands.giveaway.giveawayEmbed.no_requirements(locale_str)
    description = ''
    if giveaway.description:
        description += giveaway.description + '\n\n'
    if giveaway.price:
        description += locale.commands.giveaway.giveawayEmbed.price(locale_str, price=giveaway.price)
    if giveaway.sponsor:
        description += locale.commands.giveaway.giveawayEmbed.sponsor(locale_str, sponsor=f'<@{giveaway.sponsor}>') + '\n'
    description += locale.commands.giveaway.giveawayEmbed.description(locale_str, requirements=requirements_text, winners=giveaway.winners)
    if giveaway.end_time:
        description += '\n' + locale.commands.giveaway.giveawayEmbed.end_time(locale_str, date=f'<t:{int((relativeTimeStrToDate(giveaway.end_time) if isinstance(giveaway.end_time, str) else giveaway.end_time).timestamp())}:R>')
    embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.title(locale_str, title=giveaway.title), description=description)
    return embed

async def sendGiveaway(giveawayid, client) -> None:
    giveaway = await giveaway_service.get(giveawayid)
    if not giveaway:
        return
    guild_id = giveaway.guild_id
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    locale_str = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
    role_requirements = await giveaway_service.get_role_requirements(giveawayid)
    channel_requirements = await giveaway_service.get_channel_requirements(giveawayid)
    embed = await generateGiveawayEmbed(giveaway, locale_str, role_requirements, channel_requirements)
    channel = guild.get_channel(int(giveaway.channel_id))
    if not channel:
        return
    view = discord.ui.View()
    participants = await giveaway_service.get_participants(giveawayid)
    btn = discord.ui.Button(style=discord.ButtonStyle.primary, label=locale.commands.giveaway.giveawayEmbed.button_text(locale_str) + '(' + str(len(participants if participants else [])) + ')', custom_id='giveaway_enter; ' + str(giveawayid))
    view.add_item(btn)
    message = await channel.send(giveaway.message, embed=embed, view=view)
    await giveaway_service.mark_sent(giveawayid, message.id)

async def updateGiveawayEmbed(giveawayid, client) -> None:
    giveaway = await giveaway_service.get(giveawayid)
    if not giveaway:
        return
    guild_id = giveaway.guild_id
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    locale_str = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
    role_requirements = await giveaway_service.get_role_requirements(giveawayid)
    channel_requirements = await giveaway_service.get_channel_requirements(giveawayid)
    embed = await generateGiveawayEmbed(giveaway, locale_str, role_requirements, channel_requirements)
    channel = guild.get_channel(int(giveaway.channel_id))
    if not channel:
        return
    message = await channel.fetch_message(int(giveaway.message_id))
    await message.edit(embed=embed)

async def add_giveaway_participant(giveawayid, userid, client) -> None:
    giveaway = await giveaway_service.get(giveawayid)
    if not giveaway:
        return
    guild_id = giveaway.guild_id
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    member = guild.get_member(userid)
    if not member:
        return
    if await giveaway_service.is_participant(giveawayid, userid):
        await giveaway_service.remove_participant(giveawayid, userid)
        embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_removed.title(guild.preferred_locale if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_removed.description(guild.preferred_locale if hasattr(guild, 'preferred_locale') else 'en_US'))
        giveaway_channel = guild.get_channel(int(giveaway.channel_id))
        giveawaymessage = await giveaway_channel.fetch_message(int(giveaway.message_id))
        view = discord.ui.View()
        participants = await giveaway_service.get_participants(giveawayid)
        btn = discord.ui.Button(style=discord.ButtonStyle.primary, label=locale.commands.giveaway.giveawayEmbed.button_text(guild.preferred_locale if hasattr(guild, 'preferred_locale') else 'en_US') + '(' + str(len(participants if participants else []) - (1 if userid in (participants if participants else []) else 0)) + ')', custom_id='giveaway_enter; ' + str(giveawayid))
        view.add_item(btn)
        await giveawaymessage.edit(view=view)
        return embed
    if await giveaway_service.is_user_blacklisted(guild_id, userid):
        embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.blacklisted(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'))
        return embed
    if await check_if_opted_out(userid):
        embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.opted_out(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'))
        return embed
    blacklisted_roles = await giveaway_service.get_blacklisted_roles(guild_id)
    if blacklisted_roles:
        if any((str(role.id) in [bl.entity_id for bl in blacklisted_roles] for role in member.roles)):
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.blacklisted_role(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'))
            return embed
    if giveaway.new_message_requirement:
        new_messages = await giveaway_service.get_new_messages(giveaway_id=giveawayid, user_id=userid)
        if not new_messages:
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.message_requirement(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', new_messages=0, required_messages=giveaway.new_message_requirement, missing_messages=giveaway.new_message_requirement))
            return embed
        elif new_messages < giveaway.new_message_requirement:
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.message_requirement(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', new_messages=new_messages, required_messages=giveaway.new_message_requirement, missing_messages=giveaway.new_message_requirement - new_messages))
            return embed
    if giveaway.day_requirement:
        member = guild.get_member(userid)
        if not member:
            return
        join_date = member.joined_at.replace(tzinfo=None)
        if not join_date:
            return
        giveaway_start_date = giveaway.start_time
        if not giveaway_start_date:
            return
        days = (giveaway_start_date - join_date).days
        if days < giveaway.day_requirement:
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.day_requirement(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', required_days=giveaway.day_requirement))
            return embed
    if giveaway.voice_requirement:
        member = guild.get_member(userid)
        if not member:
            return
        voice_time = await giveaway_service.get_voice_time(giveawayid, userid)
        if not voice_time:
            voice_time = 0
        if voice_time < giveaway.voice_requirement:
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.voice_requirement(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', required_minutes=giveaway.voice_requirement, missing_minutes=giveaway.voice_requirement - voice_time))
            return embed
    role_requirements = await giveaway_service.get_role_requirements(giveawayid)
    if role_requirements:
        member = guild.get_member(userid)
        if not member:
            return
        if not any((role.id in [int(roleid) for roleid in role_requirements] for role in member.roles)):
            embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.role_requirement(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', roles=', '.join((f'<@&{role}>' for role in role_requirements))))
            return embed
    channel_requirements = await giveaway_service.get_channel_requirements(giveawayid)
    if channel_requirements:
        member = guild.get_member(userid)
        if not member:
            return
        for req in channel_requirements:
            messages = await giveaway_service.get_new_messages_channel(giveawayid, req.channel_id, userid)
            if not messages or messages < req.amount:
                embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_failed.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_failed.channel_requirements(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US', channel=req.channel_id, required_messages=req.amount, missing_messages=req.amount))
                return embed
    await giveaway_service.add_participant(giveawayid, userid)
    giveaway_channel = guild.get_channel(int(giveaway.channel_id))
    giveawaymessage = await giveaway_channel.fetch_message(int(giveaway.message_id))
    view = discord.ui.View()
    participants = await giveaway_service.get_participants(giveawayid)
    btn = discord.ui.Button(style=discord.ButtonStyle.primary, label=locale.commands.giveaway.giveawayEmbed.button_text(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US') + '(' + str(len(participants if participants else [])) + ')', custom_id='giveaway_enter; ' + str(giveawayid))
    view.add_item(btn)
    await giveawaymessage.edit(view=view)
    embed = tanjunEmbed(title=locale.commands.giveaway.giveawayEmbed.participation_success.title(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'), description=locale.commands.giveaway.giveawayEmbed.participation_success.description(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'))
    return embed

async def addMessageToGiveaway(message: discord.Message):
    if await check_if_opted_out(message.author.id):
        return
    await giveaway_service.add_new_message(message.author.id, message.guild.id)
    await giveaway_service.add_new_message_channel(message.author.id, message.guild.id, message.channel.id)

async def endGiveaway(giveaway_id, client) -> None:
    giveaway = await giveaway_service.get(giveaway_id)
    if not giveaway:
        return
    if giveaway.ended:
        return
    guild_id = giveaway.guild_id
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    locale_str = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
    try:
        participants = await giveaway_service.get_participants(giveaway_id)
        if not participants:
            embed = tanjunEmbed(title=locale.commands.giveaway.endedGiveaway.no_participants.title(locale_str), description=locale.commands.giveaway.endedGiveaway.no_participants.description(locale_str))
            giveaway_channel = guild.get_channel(int(giveaway.channel_id))
            if not giveaway_channel:
                return
            try:
                giveawaymessage = await giveaway_channel.fetch_message(int(giveaway.message_id))
            except Exception:
                logging.exception('Failed to fetch giveaway message %s for no-participants path', giveaway.message_id)
                return
            if not giveawaymessage:
                return
            view = discord.ui.View()
            btn = discord.ui.Button(style=discord.ButtonStyle.primary, label=locale.commands.giveaway.endedGiveaway.button_text(locale_str, participants=0), disabled=True)
            view.add_item(btn)
            await giveawaymessage.edit(view=view)
            await giveawaymessage.reply(embed=embed)
            await giveaway_service.set_ended(giveaway_id)
            return
        winners = []
        if not participants:
            participants = []
        participant_amount = len(participants)
        if giveaway.winners > participant_amount:
            winners = participants
        else:
            for _i in range(giveaway.winners):
                winner = random.choice(participants)
                participants.remove(winner)
                winners.append(winner)
        embed = tanjunEmbed(title=locale.commands.giveaway.endedGiveaway.title(locale_str), description=locale.commands.giveaway.endedGiveaway.description(locale_str, winners=', '.join((f'<@{winner}>' for winner in winners))))
        for winner in winners:
            await giveaway_service.remove_participant(giveaway_id, winner)
            member = guild.get_member(winner)
            if member:
                with contextlib.suppress(discord.Forbidden, discord.HTTPException):
                    await member.send(locale.commands.giveaway.endedGiveaway.winnerDM(locale_str, guild_name=guild.name))
        giveaway_channel = guild.get_channel(int(giveaway.channel_id))
        if not giveaway_channel:
            return
        try:
            giveawaymessage = await giveaway_channel.fetch_message(int(giveaway.message_id))
        except Exception:
            logging.exception('Failed to fetch giveaway message %s for winner announcement path', giveaway.message_id)
            return
        if not giveawaymessage:
            return
        view = discord.ui.View()
        btn = discord.ui.Button(style=discord.ButtonStyle.primary, label=locale.commands.giveaway.endedGiveaway.button_text(locale_str, participants=participant_amount), disabled=True)
        view.add_item(btn)
        await giveawaymessage.edit(view=view)
        await giveawaymessage.reply(embed=embed)
        for winner in winners:
            member = guild.get_member(winner)
            if not member:
                continue
            await member.send(locale.commands.giveaway.endedGiveaway.dm(locale_str, guild_name=guild.name))
        await giveaway_service.set_ended(giveaway_id)
    except Exception:
        logging.exception('Failed to end giveaway %s, will retry', giveaway_id)
        raise
    return embed

async def updateGiveawayMessage(giveaway_id, client) -> None:
    giveaway = await giveaway_service.get(giveaway_id)
    if not giveaway:
        return
    guild_id = giveaway.guild_id
    guild = client.get_guild(int(guild_id))
    if not guild:
        return
    locale_str = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
    role_requirements = await giveaway_service.get_role_requirements(giveaway_id)
    channel_requirements = await giveaway_service.get_channel_requirements(giveaway_id)
    embed = await generateGiveawayEmbed(giveaway, locale_str, role_requirements, channel_requirements)
    channel = guild.get_channel(int(giveaway.channel_id))
    if not channel:
        return
    try:
        message = await channel.fetch_message(int(giveaway.message_id))
        await message.edit(embed=embed)
    except discord.errors.NotFound:
        pass