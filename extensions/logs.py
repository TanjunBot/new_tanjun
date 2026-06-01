from locale_keys import locale
import asyncio
import difflib
import logging
from collections.abc import Callable
import discord
from discord import app_commands
from discord.ext import commands
import utility
from api import LogBlacklistType, get_log_blacklist, get_log_channel, get_log_enable, is_log_entity_blacklisted
from commands.logs.blacklist_category.blacklist_category import blacklist_category
from commands.logs.blacklist_category.blacklist_list_category import blacklist_list_category
from commands.logs.blacklist_category.blacklist_remove_category import blacklist_remove_category
from commands.logs.blacklist_channel.blacklist_channel import blacklist_channel
from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel
from commands.logs.blacklist_channel.blacklist_remove_channel import blacklist_remove_channel
from commands.logs.blacklist_role.blacklist_list_role import blacklist_list_role
from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role
from commands.logs.blacklist_role.blacklist_role import blacklist_role
from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user
from commands.logs.blacklist_user.blacklist_remove_user import blacklist_remove_user
from commands.logs.blacklist_user.blacklist_user import blacklist_user
from commands.logs.blacklist_voice.blacklist_list_voice import blacklist_list_voice
from commands.logs.blacklist_voice.blacklist_remove_voice import blacklist_remove_voice
from commands.logs.blacklist_voice.blacklist_voice import blacklist_voice
from commands.logs.configure_logs import configure_logs
from commands.logs.remove_log_channel import remove_log_channel
from commands.logs.set_log_channel import set_log_channel
from utility import EmbedColor, upload_image_to_imgbb, upload_to_tanjun_logs

async def _is_channel_or_category_blacklisted(guild_id: str, channel: discord.abc.GuildChannel | None) -> bool:
    """
    Check if a channel is blacklisted.
    Returns True if:
    - The channel itself is in the channel blacklist
    - The channel is a voice channel and is in the voice channel blacklist
    - The channel's parent category is in the category blacklist
    """
    if channel is None:
        return False
    channel_id = str(channel.id)
    if await is_log_entity_blacklisted(guild_id, channel_id, LogBlacklistType.CHANNEL):
        return True
    if isinstance(channel, discord.VoiceChannel) and await is_log_entity_blacklisted(guild_id, channel_id, LogBlacklistType.VOICE_CHANNEL):
        return True
    if channel.category is not None and await is_log_entity_blacklisted(guild_id, str(channel.category.id), LogBlacklistType.CATEGORY):
        return True
    return False

async def _find_audit_log_entry(guild: discord.Guild, action: discord.AuditLogAction, predicate: Callable[[discord.AuditLogEntry], bool], *, limit: int=5) -> discord.AuditLogEntry | None:
    try:
        async for entry in guild.audit_logs(limit=limit, action=action):
            if predicate(entry):
                return entry
    except discord.Forbidden:
        pass
    return None
embeds = {}
_log_queue: asyncio.Queue[tuple[str, discord.Embed]] = asyncio.Queue(maxsize=200)

async def log_event_producer(guild_id: str, embed: discord.Embed) -> None:
    """Called by event listeners - never blocks."""
    try:
        _log_queue.put_nowait((guild_id, embed))
    except asyncio.QueueFull:
        pass

async def send_logEmbeds(guild_id: str, embed: discord.Embed) -> None:
    """Backward-compatible shim for send_logEmbeds - enqueues log events."""
    await log_event_producer(guild_id, embed)

async def log_event_consumer(bot: commands.Bot) -> None:
    """Background task that processes the queue asynchronously."""
    while True:
        guild_id, embed = await _log_queue.get()
        try:
            destination = await get_log_channel(str(guild_id))
            if destination is None:
                continue
            destination_channel = bot.get_channel(int(destination))
            if not isinstance(destination_channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.Thread)):
                continue
            await destination_channel.send(embed=embed)
        except Exception:
            logging.exception('Error in log event consumer loop processing guild %s', guild_id)

class ChannelBlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.blacklistc.add.name.discord_key, description=locale.logs.blacklistc.add.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistc.add.params.channel.description.discord_key)
    async def add_blacklist_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            channel = ctx.channel
        await blacklist_channel(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistc.remove.name.discord_key, description=locale.logs.blacklistc.remove.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistc.remove.params.channel.description.discord_key)
    async def remove_blacklist_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            channel = ctx.channel
        await blacklist_remove_channel(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistc.show.name.discord_key, description=locale.logs.blacklistc.show.description.discord_key)
    async def show_blacklist_channel_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_list_channel(command_info=command_info)

class UserBlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.blacklistu.add.name.discord_key, description=locale.logs.blacklistu.add.description.discord_key)
    @app_commands.describe(user=locale.logs.blacklistu.add.params.user.description.discord_key)
    async def add_blacklist_user_cmd(self, ctx: discord.Interaction, user: discord.Member) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_user(command_info=command_info, user=user)

    @app_commands.command(name=locale.logs.blacklistu.remove.name.discord_key, description=locale.logs.blacklistu.remove.description.discord_key)
    @app_commands.describe(user=locale.logs.blacklistu.remove.params.user.description.discord_key)
    async def remove_blacklist_user_cmd(self, ctx: discord.Interaction, user: discord.Member) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_remove_user(command_info=command_info, user=user)

    @app_commands.command(name=locale.logs.blacklistu.show.name.discord_key, description=locale.logs.blacklistu.show.description.discord_key)
    async def show_blacklist_user_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_list_user(command_info=command_info)

class RoleBlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.blacklistr.add.name.discord_key, description=locale.logs.blacklistr.add.description.discord_key)
    @app_commands.describe(role=locale.logs.blacklistr.add.params.role.description.discord_key)
    async def add_blacklist_role_cmd(self, ctx: discord.Interaction, role: discord.Role) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_role(command_info=command_info, role=role)

    @app_commands.command(name=locale.logs.blacklistr.remove.name.discord_key, description=locale.logs.blacklistr.remove.description.discord_key)
    @app_commands.describe(role=locale.logs.blacklistr.remove.params.role.description.discord_key)
    async def remove_blacklist_role_cmd(self, ctx: discord.Interaction, role: discord.Role) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_remove_role(command_info=command_info, role=role)

    @app_commands.command(name=locale.logs.blacklistr.show.name.discord_key, description=locale.logs.blacklistr.show.description.discord_key)
    async def show_blacklist_role_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_list_role(command_info=command_info)

class VoiceBlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.blacklistv.add.name.discord_key, description=locale.logs.blacklistv.add.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistv.add.params.channel.description.discord_key)
    async def add_blacklist_voice_cmd(self, ctx: discord.Interaction, channel: discord.VoiceChannel | None=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistVoiceChannel.missingChannel.title(ctx.locale), description=locale.commands.logs.blacklistVoiceChannel.missingChannel.description(ctx.locale))
            await ctx.followup.send(embed=embed)
            return
        await blacklist_voice(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistv.remove.name.discord_key, description=locale.logs.blacklistv.remove.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistv.remove.params.channel.description.discord_key)
    async def remove_blacklist_voice_cmd(self, ctx: discord.Interaction, channel: discord.VoiceChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveVoiceChannel.missingChannel.title(ctx.locale), description=locale.commands.logs.blacklistRemoveVoiceChannel.missingChannel.description(ctx.locale))
            await ctx.followup.send(embed=embed)
            return
        await blacklist_remove_voice(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistv.show.name.discord_key, description=locale.logs.blacklistv.show.description.discord_key)
    async def show_blacklist_voice_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_list_voice(command_info=command_info)

class CategoryBlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.blacklistcat.add.name.discord_key, description=locale.logs.blacklistcat.add.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistcat.add.params.channel.description.discord_key)
    async def add_blacklist_category_cmd(self, ctx: discord.Interaction, channel: discord.CategoryChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistCategory.missingChannel.title(ctx.locale), description=locale.commands.logs.blacklistCategory.missingChannel.description(ctx.locale))
            await ctx.followup.send(embed=embed)
            return
        await blacklist_category(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistcat.remove.name.discord_key, description=locale.logs.blacklistcat.remove.description.discord_key)
    @app_commands.describe(channel=locale.logs.blacklistcat.remove.params.channel.description.discord_key)
    async def remove_blacklist_category_cmd(self, ctx: discord.Interaction, channel: discord.CategoryChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveCategory.missingChannel.title(ctx.locale), description=locale.commands.logs.blacklistRemoveCategory.missingChannel.description(ctx.locale))
            await ctx.followup.send(embed=embed)
            return
        await blacklist_remove_category(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.blacklistcat.show.name.discord_key, description=locale.logs.blacklistcat.show.description.discord_key)
    async def show_blacklist_category_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await blacklist_list_category(command_info=command_info)

class LogsCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.logs.set.name.discord_key, description=locale.logs.set.description.discord_key)
    @app_commands.describe(channel=locale.logs.set.params.channel.description.discord_key)
    async def set_log_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if channel is None:
            channel = ctx.channel
        await set_log_channel(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.logs.remove.name.discord_key, description=locale.logs.remove.description.discord_key)
    async def remove_log_channel_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await remove_log_channel(command_info=command_info)

    @app_commands.command(name=locale.logs.configure.name.discord_key, description=locale.logs.configure.description.discord_key)
    async def configure_logs_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await configure_logs(command_info=command_info)

class LogsCog(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot
        self._log_consumer_task: asyncio.Task[None] | None = None

    @commands.Cog.listener()
    async def on_automod_rule_create(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_create
        if not log_enable:
            return
        if rule.channel_id is not None:
            channel = rule.guild.get_channel(rule.channel_id)
            if await _is_channel_or_category_blacklisted(rule.guild.id, channel):
                return
        locale = rule.guild.preferred_locale if hasattr(rule.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.automodRuleCreate.created_by(locale, creator=rule.creator.mention))
        description_parts.append(locale.logs.automodRuleCreate.enabled(locale, enabled='✅' if rule.enabled else '❌'))
        description_parts.append(locale.logs.automodRuleCreate.name(locale, name=rule.name))
        description_parts.append(locale.logs.automodRuleCreate.trigger(locale))
        description_parts.append(locale.logs.automodRuleCreate.triggerType(locale, triggerType=str(locale.logs.automodRuleCreate.resolve(str(rule.trigger.type))(locale))))
        if rule.trigger.keyword_filter:
            filters = '\n'.join((f'- {keyword}' for keyword in rule.trigger.keyword_filter))
            description_parts.append(locale.logs.automodRuleCreate.keywordFilters(locale, keywordFilters=filters))
        if rule.trigger.regex_patterns:
            patterns = '\n'.join((f'- {regex}' for regex in rule.trigger.regex_patterns))
            description_parts.append(locale.logs.automodRuleCreate.regexPatterns(locale, regexPatterns=patterns))
        description_parts.append(locale.logs.automodRuleCreate.presets(locale, profanityFilter='✅' if rule.trigger.presets.profanity else '❌', sexualContentFilter='✅' if rule.trigger.presets.sexual_content else '❌', slurFilter='✅' if rule.trigger.presets.slurs else '❌'))
        if rule.trigger.allow_list:
            allows = '\n'.join((f'- {allow}' for allow in rule.trigger.allow_list))
            description_parts.append(locale.logs.automodRuleCreate.allow_list(locale, allow_list=allows))
        if rule.trigger.mention_limit:
            description_parts.append(locale.logs.automodRuleCreate.max_mentions(locale, max_mentions=rule.trigger.mention_limit))
        if rule.trigger.mention_raid_protection:
            description_parts.append(locale.logs.automodRuleCreate.mentionSpamProtection(locale))
        if rule.exempt_roles:
            roles = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_roles))
            description_parts.append(locale.logs.automodRuleCreate.excluded_roles(locale, excluded_roles=roles or '-'))
        if rule.exempt_channels:
            channels = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_channels))
            description_parts.append(locale.logs.automodRuleCreate.excluded_channels(locale, excluded_channels=channels or '-'))
        if len(rule.actions) > 0:
            description_parts.append(locale.logs.automodRuleCreate.actions(locale))
            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(locale.logs.automodRuleCreate.block_message(locale))
                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(locale.logs.automodRuleCreate.send_warning_message(locale, channel=r.channel_id))
                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(locale.logs.automodRuleCreate.timeout(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(locale.logs.automodRuleCreate.block_member_interaction(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.automodRuleCreate.title(locale), description=description)
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_rule_update(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_update
        if not log_enable:
            return
        if rule.channel_id is not None and await is_log_entity_blacklisted(rule.guild.id, str(rule.channel_id), LogBlacklistType.CHANNEL):
            return
        locale = rule.guild.preferred_locale if hasattr(rule.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        entry = await _find_audit_log_entry(rule.guild, discord.AuditLogAction.automod_rule_update, lambda e: e.target.id == rule.id)
        updater = entry.user.mention if entry else None
        if updater:
            description_parts.append(locale.logs.automodRuleUpdate.updated_by(locale, updater=updater))
        description_parts.append(locale.logs.automodRuleCreate.enabled(locale, enabled='✅' if rule.enabled else '❌'))
        description_parts.append(locale.logs.automodRuleCreate.name(locale, name=rule.name))
        description_parts.append(locale.logs.automodRuleCreate.trigger(locale))
        description_parts.append(locale.logs.automodRuleCreate.triggerType(locale, triggerType=str(locale.logs.automodRuleCreate.resolve(str(rule.trigger.type))(locale))))
        if rule.trigger.keyword_filter:
            filters = '\n'.join((f'- {keyword}' for keyword in rule.trigger.keyword_filter))
            description_parts.append(locale.logs.automodRuleCreate.keywordFilters(locale, keywordFilters=filters))
        if rule.trigger.regex_patterns:
            patterns = '\n'.join((f'- {regex}' for regex in rule.trigger.regex_patterns))
            description_parts.append(locale.logs.automodRuleCreate.regexPatterns(locale, regexPatterns=patterns))
        description_parts.append(locale.logs.automodRuleCreate.presets(locale, profanityFilter='✅' if rule.trigger.presets.profanity else '❌', sexualContentFilter='✅' if rule.trigger.presets.sexual_content else '❌', slurFilter='✅' if rule.trigger.presets.slurs else '❌'))
        if rule.trigger.allow_list:
            allows = '\n'.join((f'- {allow}' for allow in rule.trigger.allow_list))
            description_parts.append(locale.logs.automodRuleCreate.allow_list(locale, allow_list=allows))
        if rule.trigger.mention_limit:
            description_parts.append(locale.logs.automodRuleCreate.max_mentions(locale, max_mentions=rule.trigger.mention_limit))
        if rule.trigger.mention_raid_protection:
            description_parts.append(locale.logs.automodRuleCreate.mentionSpamProtection(locale))
        if rule.exempt_roles:
            roles = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_roles))
            description_parts.append(locale.logs.automodRuleCreate.excluded_roles(locale, excluded_roles=roles or '-'))
        if rule.exempt_channels:
            channels = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_channels))
            description_parts.append(locale.logs.automodRuleCreate.excluded_channels(locale, excluded_channels=channels or '-'))
        if len(rule.actions) > 0:
            description_parts.append(locale.logs.automodRuleCreate.actions(locale))
            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(locale.logs.automodRuleCreate.block_message(locale))
                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(locale.logs.automodRuleCreate.send_warning_message(locale, channel=r.channel_id))
                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(locale.logs.automodRuleCreate.timeout(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(locale.logs.automodRuleCreate.block_member_interaction(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.automodRuleUpdate.title(locale), description=description)
        embed.set_footer(text=locale.logs.automodRuleUpdate.footer(locale))
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_rule_delete(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_delete
        if not log_enable:
            return
        if rule.channel_id is not None and await is_log_entity_blacklisted(rule.guild.id, str(rule.channel_id), LogBlacklistType.CHANNEL):
            return
        locale = rule.guild.preferred_locale if hasattr(rule.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        entry = await _find_audit_log_entry(rule.guild, discord.AuditLogAction.automod_rule_delete, lambda e: e.target.id == rule.id)
        updater = entry.user.mention if entry else None
        if updater:
            description_parts.append(locale.logs.automodRuleDelete.deleted_by(locale, updater=updater))
        description_parts.append(locale.logs.automodRuleCreate.enabled(locale, enabled='✅' if rule.enabled else '❌'))
        description_parts.append(locale.logs.automodRuleCreate.name(locale, name=rule.name))
        description_parts.append(locale.logs.automodRuleCreate.trigger(locale))
        description_parts.append(locale.logs.automodRuleCreate.triggerType(locale, triggerType=str(locale.logs.automodRuleCreate.resolve(str(rule.trigger.type))(locale))))
        if rule.trigger.keyword_filter:
            filters = '\n'.join((f'- {keyword}' for keyword in rule.trigger.keyword_filter))
            description_parts.append(locale.logs.automodRuleCreate.keywordFilters(locale, keywordFilters=filters))
        if rule.trigger.regex_patterns:
            patterns = '\n'.join((f'- {regex}' for regex in rule.trigger.regex_patterns))
            description_parts.append(locale.logs.automodRuleCreate.regexPatterns(locale, regexPatterns=patterns))
        description_parts.append(locale.logs.automodRuleCreate.presets(locale, profanityFilter='✅' if rule.trigger.presets.profanity else '❌', sexualContentFilter='✅' if rule.trigger.presets.sexual_content else '❌', slurFilter='✅' if rule.trigger.presets.slurs else '❌'))
        if rule.trigger.allow_list:
            allows = '\n'.join((f'- {allow}' for allow in rule.trigger.allow_list))
            description_parts.append(locale.logs.automodRuleCreate.allow_list(locale, allow_list=allows))
        if rule.trigger.mention_limit:
            description_parts.append(locale.logs.automodRuleCreate.max_mentions(locale, max_mentions=rule.trigger.mention_limit))
        if rule.trigger.mention_raid_protection:
            description_parts.append(locale.logs.automodRuleCreate.mentionSpamProtection(locale))
        if rule.exempt_roles:
            roles = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_roles))
            description_parts.append(locale.logs.automodRuleCreate.excluded_roles(locale, excluded_roles=roles or '-'))
        if rule.exempt_channels:
            channels = '\n'.join((f'- {excluded.mention}' for excluded in rule.exempt_channels))
            description_parts.append(locale.logs.automodRuleCreate.excluded_channels(locale, excluded_channels=channels or '-'))
        if len(rule.actions) > 0:
            description_parts.append(locale.logs.automodRuleCreate.actions(locale))
            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(locale.logs.automodRuleCreate.block_message(locale))
                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(locale.logs.automodRuleCreate.send_warning_message(locale, channel=r.channel_id))
                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(locale.logs.automodRuleCreate.timeout(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(locale.logs.automodRuleCreate.block_member_interaction(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(r.duration))(locale))))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.automodRuleDelete.title(locale), description=description)
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction) -> None:
        log_enable = execution.guild and (await get_log_enable(execution.guild.id)).automod_action
        if not log_enable:
            return
        if execution.channel is not None and await _is_channel_or_category_blacklisted(str(execution.guild.id), execution.channel):
            return
        locale = execution.guild.preferred_locale if hasattr(execution.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.automodAction.actionWasTaken(locale, user=execution.member.mention, channel=execution.channel.mention))
        description_parts.append(locale.logs.automodAction.action(locale))
        if execution.action.type == discord.AutoModRuleActionType.block_message:
            description_parts.append(locale.logs.automodRuleCreate.block_message(locale))
        elif execution.action.type == discord.AutoModRuleActionType.send_alert_message:
            description_parts.append(locale.logs.automodRuleCreate.send_warning_message(locale, channel=execution.action.channel_id))
        elif execution.action.type == discord.AutoModRuleActionType.timeout:
            description_parts.append(locale.logs.automodRuleCreate.timeout(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(execution.action.duration))(locale))))
        elif execution.action.type == discord.AutoModRuleActionType.block_member_interactions:
            description_parts.append(locale.logs.automodRuleCreate.block_member_interaction(locale, duration=str(locale.logs.automodRuleCreate.resolve('timeout_duration.' + str(execution.action.duration))(locale))))
        description_parts.append(locale.logs.automodAction.message(locale, message=execution.action.content[0:1000] + '...' if len(execution.action.content) > 1000 else execution.action.content))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.automodRuleDelete.title(locale), description=description)
        await log_event_producer(str(execution.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        log_enable = channel.guild and (await get_log_enable(channel.guild.id)).guild_channel_delete
        if not log_enable:
            return
        if await _is_channel_or_category_blacklisted(str(channel.guild.id), channel):
            return
        locale = channel.guild.preferred_locale if hasattr(channel.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        entry = await _find_audit_log_entry(channel.guild, discord.AuditLogAction.channel_delete, lambda e: e.target.id == channel.id)
        deleter = entry.user.mention if entry else None
        if deleter:
            description_parts.append(locale.logs.guild_channelDelete.deleted_by(locale, deleter=deleter))
        description_parts.append(locale.logs.guild_channelDelete.name(locale, channel=channel.name))
        description_parts.append(locale.logs.guild_channelDelete.type(locale, type=str(locale.logs.guild_channelDelete.types.resolve(str(channel.type))(locale))))
        description_parts.append(locale.logs.guild_channelDelete.created_at(locale, created_at=utility.date_time_to_timestamp(channel.created_at)))
        if channel.category:
            description_parts.append(locale.logs.guild_channelDelete.category(locale, category=channel.category))
        if channel.topic:
            description_parts.append(locale.logs.guild_channelDelete.topic(locale, topic=channel.topic))
        if len(channel.overwrites.keys()) > 0:
            description_parts.append(locale.logs.guild_channelDelete.permissionOverwrites(locale))
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    local_perm = locale.logs.permissions.resolve(perm)(locale)
                    if value is True:
                        allowed.append(f'`{local_perm}`')
                    elif value is False:
                        denied.append(f'`{local_perm}`')
                target_str = target.mention if hasattr(target, 'mention') else target.name
                description_parts.append(locale.logs.guild_channelDelete.permissionOverwriteTarget(locale, target=target_str))
                if allowed:
                    description_parts.append(locale.logs.guild_channelDelete.permissionOverwriteAllowed(locale, permissions=', '.join(allowed)))
                if denied:
                    description_parts.append(locale.logs.guild_channelDelete.permissionOverwriteDenied(locale, permissions=', '.join(denied)))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.guild_channelDelete.title(locale), description=description)
        await log_event_producer(str(channel.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        log_enable = channel.guild and (await get_log_enable(channel.guild.id)).guild_channel_create
        if not log_enable:
            return
        if await _is_channel_or_category_blacklisted(str(channel.guild.id), channel):
            return
        locale = channel.guild.preferred_locale if hasattr(channel.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        entry = await _find_audit_log_entry(channel.guild, discord.AuditLogAction.channel_create, lambda e: e.target.id == channel.id)
        creator = entry.user.mention if entry else None
        if creator:
            description_parts.append(locale.logs.guild_channelCreate.created_by(locale, creator=creator))
        description_parts.append(locale.logs.guild_channelCreate.name(locale, name=channel.name))
        description_parts.append(locale.logs.guild_channelCreate.type(locale, type=str(locale.logs.guild_channelCreate.types.resolve(str(channel.type))(locale))))
        description_parts.append(locale.logs.guild_channelCreate.created_at(locale, created_at=utility.date_time_to_timestamp(channel.created_at)))
        if channel.category:
            description_parts.append(locale.logs.guild_channelCreate.category(locale, category=channel.category))
        if channel.topic:
            description_parts.append(locale.logs.guild_channelCreate.topic(locale, topic=channel.topic))
        if len(channel.overwrites.keys()) > 0:
            description_parts.append(locale.logs.guild_channelCreate.permissionOverwrites(locale))
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    local_perm = locale.logs.permissions.resolve(perm)(locale)
                    if value is True:
                        allowed.append(f'`{local_perm}`')
                    elif value is False:
                        denied.append(f'`{local_perm}`')
                target_str = target.mention if hasattr(target, 'mention') else target.name
                description_parts.append(f'### {target_str}')
                if allowed:
                    description_parts.append('✅ ' + ', '.join(allowed))
                if denied:
                    description_parts.append('❌ ' + ', '.join(denied))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.guild_channelCreate.title(locale), description=description)
        await log_event_producer(str(channel.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_channel_update
        if not log_enable:
            return
        if await _is_channel_or_category_blacklisted(str(after.guild.id), after):
            return
        locale = after.guild.preferred_locale if hasattr(after.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        entry = await _find_audit_log_entry(after.guild, discord.AuditLogAction.channel_update, lambda e: e.target.id == after.id)
        updater = entry.user.mention if entry else None
        if updater:
            description_parts.append(locale.logs.guild_channelUpdate.updated_by(locale, updater=updater))
        description_parts.append(locale.logs.guild_channelUpdate.mention(locale, mention=before.mention))
        if before.name != after.name:
            description_parts.append(locale.logs.guild_channelUpdate.name(locale, before=before.name, after=after.name))
        if hasattr(before, 'type') and before.type != after.type:
            description_parts.append(locale.logs.guild_channelUpdate.type(locale, before=str(locale.logs.guild_channelUpdate.types.resolve(str(before.type))(locale)), after=str(locale.logs.guild_channelUpdate.types.resolve(str(after.type))(locale))))
        if hasattr(before, 'category') and before.category != after.category:
            description_parts.append(locale.logs.guild_channelUpdate.category(locale, before=before.category, after=after.category))
        if hasattr(before, 'topic') and before.topic != after.topic:
            description_parts.append(locale.logs.guild_channelUpdate.topic(locale, before=before.topic, after=after.topic))
        if before.overwrites != after.overwrites:
            for target in before.overwrites:
                if target not in after.overwrites:
                    target_str = target.mention if hasattr(target, 'mention') else target.name
                    description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteRemoved(locale, target=target_str))
            for target, new_overwrite in after.overwrites.items():
                old_overwrite = before.overwrites.get(target, None)
                target_str = target.mention if hasattr(target, 'mention') else target.name
                if old_overwrite is None:
                    allowed = []
                    denied = []
                    neutral = []
                    for perm, value in new_overwrite:
                        local_perm = locale.logs.permissions.resolve(perm)(locale)
                        if value is True:
                            allowed.append(f'`{local_perm}`')
                        elif value is False:
                            denied.append(f'`{local_perm}`')
                        else:
                            neutral.append(f'`{local_perm}`')
                    description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteNew(locale, target=target_str))
                    if allowed:
                        description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteAllowed(locale, permissions=', '.join(allowed)))
                    if denied:
                        description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteDenied(locale, permissions=', '.join(denied)))
                    if neutral:
                        description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteNeutral(locale, permissions=', '.join(neutral)))
                else:
                    added_allow = []
                    added_deny = []
                    added_neutral = []
                    removed_allow = []
                    removed_deny = []
                    removed_neutral = []
                    for perm, new_value in new_overwrite:
                        old_value = dict(old_overwrite)[perm]
                        if new_value != old_value:
                            local_perm = locale.logs.permissions.resolve(perm)(locale)
                            if new_value is True:
                                added_allow.append(f'`{local_perm}`')
                            elif new_value is False:
                                added_deny.append(f'`{local_perm}`')
                            elif new_value is None:
                                added_neutral.append(f'`{local_perm}`')
                            if old_value is True:
                                removed_allow.append(f'`{local_perm}`')
                            elif old_value is False:
                                removed_deny.append(f'`{local_perm}`')
                            elif old_value is None:
                                removed_neutral.append(f'`{local_perm}`')
                    if any([added_allow, added_deny, added_neutral, removed_allow, removed_deny, removed_neutral]):
                        description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteModified(locale, target=target_str))
                        if added_allow:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteAddedAllow(locale, permissions=', '.join(added_allow)))
                        if added_deny:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteAddedDeny(locale, permissions=', '.join(added_deny)))
                        if added_neutral:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteAddedNeutral(locale, permissions=', '.join(added_neutral)))
                        if removed_allow:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteRemovedAllow(locale, permissions=', '.join(removed_allow)))
                        if removed_deny:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteRemovedDeny(locale, permissions=', '.join(removed_deny)))
                        if removed_neutral:
                            description_parts.append(locale.logs.guild_channelUpdate.permissionOverwriteRemovedNeutral(locale, permissions=', '.join(removed_neutral)))
        if hasattr(after, 'default_auto_archive_duration') and after.default_auto_archive_duration != before.default_auto_archive_duration:
            description_parts.append(locale.logs.guild_channelUpdate.defaultAutoArchiveDuration(locale, before=before.default_auto_archive_duration, after=after.default_auto_archive_duration))
        if hasattr(after, 'default_thread_auto_archive_duration') and after.default_thread_auto_archive_duration != before.default_thread_auto_archive_duration:
            description_parts.append(locale.logs.guild_channelUpdate.defaultThreadAutoArchiveDuration(locale, before=before.default_thread_auto_archive_duration, after=after.default_thread_auto_archive_duration))
        if hasattr(after, 'nsfw') and after.nsfw != before.nsfw:
            description_parts.append(locale.logs.guild_channelUpdate.nsfw(locale, before=str(locale.logs.guild_channelUpdate.yes(locale)) if before.nsfw else str(locale.logs.guild_channelUpdate.no(locale)), after=str(locale.logs.guild_channelUpdate.yes(locale)) if after.nsfw else str(locale.logs.guild_channelUpdate.no(locale))))
        if hasattr(after, 'slowmode_delay') and after.slowmode_delay != before.slowmode_delay:
            description_parts.append(locale.logs.guild_channelUpdate.slowmodeDelay(locale, before=before.slowmode_delay, after=after.slowmode_delay))
        if len(description_parts) == 2:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.guild_channelUpdate.title(locale), description=description)
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_update
        if not log_enable:
            return
        locale = after.locale if hasattr(after, 'preferred_locale') else 'en_US'
        description_parts = []
        keiner_locale = locale.logs.guildUpdate.none(locale)
        if before.afk_channel != after.afk_channel:
            description_parts.append(locale.logs.guildUpdate.afkChannel(locale, before=before.afk_channel.mention if before.afk_channel else keiner_locale, after=after.afk_channel.mention if after.afk_channel else keiner_locale))
        if before.afk_timeout != after.afk_timeout:
            description_parts.append(locale.logs.guildUpdate.afkTimeout(locale, before=before.afk_timeout, after=after.afk_timeout))
        if before.banner != after.banner:
            description_parts.append(locale.logs.guildUpdate.banner(locale, before=before.banner if before.banner else keiner_locale, after=after.banner if after.banner else keiner_locale))
        if before.default_notifications != after.default_notifications:
            all_members_locale = locale.logs.guildUpdate.defaultNotificationsLocales.all_members(locale)
            only_mentions = locale.logs.guildUpdate.defaultNotificationsLocales.onlyMentions(locale)
            description_parts.append(locale.logs.guildUpdate.defaultNotifications(locale, before=all_members_locale if before.default_notifications else only_mentions, after=all_members_locale if after.default_notifications else only_mentions))
        if before.description != after.description:
            description_parts.append(locale.logs.guildUpdate.description(locale, before=before.description, after=after.description))
        if before.discovery_splash != after.discovery_splash:
            url_locale = locale.logs.guildUpdate.discoverySplashLocales.url(locale)
            description_parts.append(locale.logs.guildUpdate.discoverySplash(locale, before='[' + url_locale + '](' + before.discovery_splash.url + ')' if before.discovery_splash else keiner_locale, after='[' + url_locale + '](' + after.discovery_splash.url + ')' if after.discovery_splash else keiner_locale))
        if before.emoji_limit != after.emoji_limit:
            description_parts.append(locale.logs.guildUpdate.emojiLimit(locale, before=before.emoji_limit, after=after.emoji_limit))
        added_emojis = [emoji for emoji in after.emojis if emoji not in before.emojis]
        removed_emojis = [emoji for emoji in before.emojis if emoji not in after.emojis]
        if added_emojis:
            added_list = '\n'.join((f'- {emoji} : {emoji.name}' for emoji in added_emojis))
            description_parts.append(locale.logs.guildUpdate.addedEmojis(locale, added_emojis=added_list))
        if removed_emojis:
            removed_list = '\n'.join((f'- {emoji} : {emoji.name}' for emoji in removed_emojis))
            description_parts.append(locale.logs.guildUpdate.removedEmojis(locale, removed_emojis=removed_list))
        if before.explicit_content_filter != after.explicit_content_filter:
            disabled = locale.logs.guildUpdate.explicitContentFilterLocales.disabled(locale)
            no_role = locale.logs.guildUpdate.explicitContentFilterLocales.no_role(locale)
            all_members = locale.logs.guildUpdate.explicitContentFilterLocales.all_members(locale)
            description_parts.append(locale.logs.guildUpdate.explicitContentFilter(locale, before=disabled if before.explicit_content_filter.disabled else no_role if before.explicit_content_filter.no_role else all_members, after=disabled if after.explicit_content_filter.disabled else no_role if after.explicit_content_filter.no_role else all_members))
        added_features = [feature for feature in after.features if feature not in before.features]
        removed_features = [feature for feature in before.features if feature not in after.features]
        if added_features:
            added_list = '\n'.join((f'- {locale.logs.guildUpdate.featuresLocales.resolve(feature)(locale)}' for feature in added_features))
            description_parts.append(locale.logs.guildUpdate.addedFeatures(locale, added_features=added_list))
        if removed_features:
            removed_list = '\n'.join((f'- {locale.logs.guildUpdate.featuresLocales.resolve(feature)(locale)}' for feature in removed_features))
            description_parts.append(locale.logs.guildUpdate.removedFeatures(locale, removed_features=removed_list))
        if before.icon != after.icon:
            url_locale = locale.logs.guildUpdate.iconLocales.url(locale)
            no_icon_locale = locale.logs.guildUpdate.iconLocales.noIcon(locale)
            description_parts.append(locale.logs.guildUpdate.icon(locale, before='[' + url_locale + '](' + before.icon + ')' if before.icon else no_icon_locale, after='[' + url_locale + '](' + after.icon + ')' if after.icon else no_icon_locale))
        if before.filesize_limit != after.filesize_limit:
            description_parts.append(locale.logs.guildUpdate.filesizeLimit(locale, before=before.filesize_limit, after=after.filesize_limit))
        if before.invites_paused_until != after.invites_paused_until:
            not_paused_locale = locale.logs.guildUpdate.invitesPausedUntilLocales.notPaused(locale)
            description_parts.append(locale.logs.guildUpdate.invitesPausedUntil(locale, before='<t:' + str(utility.date_time_to_timestamp(before.invites_paused_until)) + ':R>' if before.invites_paused_until else not_paused_locale, after='<t:' + str(utility.date_time_to_timestamp(after.invites_paused_until)) + ':R>' if after.invites_paused_until else not_paused_locale))
        if before.max_members != after.max_members:
            description_parts.append(locale.logs.guildUpdate.maxMembers(locale, before=before.max_members if before.max_members else '0', after=after.max_members if after.max_members else '0'))
        if before.max_presences != after.max_presences:
            description_parts.append(locale.logs.guildUpdate.maxPresences(locale, before=before.max_presences if before.max_presences else keiner_locale, after=after.max_presences if after.max_presences else keiner_locale))
        if before.max_video_channel_users != after.max_video_channel_users:
            description_parts.append(locale.logs.guildUpdate.maxVideoChannelUsers(locale, before=before.max_video_channel_users if before.max_video_channel_users else keiner_locale, after=after.max_video_channel_users if after.max_video_channel_users else keiner_locale))
        if before.name != after.name:
            description_parts.append(locale.logs.guildUpdate.name(locale, before=before.name, after=after.name))
        if before.nsfw_level != after.nsfw_level:
            default_locale = locale.logs.guildUpdate.nsfwLevelLocales.default(locale)
            explicit_locale = locale.logs.guildUpdate.nsfwLevelLocales.explicit(locale)
            safe_locale = locale.logs.guildUpdate.nsfwLevelLocales.safe(locale)
            age_registered_locale = locale.logs.guildUpdate.nsfwLevelLocales.ageRegistered(locale)
            description_parts.append(locale.logs.guildUpdate.nsfwLevel(locale, before=default_locale if before.nsfw_level.default else explicit_locale if before.nsfw_level.explicit else safe_locale if before.nsfw_level.safe else age_registered_locale if before.nsfw_level.age_restricted else keiner_locale, after=default_locale if after.nsfw_level.default else explicit_locale if after.nsfw_level.explicit else safe_locale if after.nsfw_level.safe else age_registered_locale if after.nsfw_level.age_restricted else keiner_locale))
        if before.owner != after.owner:
            description_parts.append(locale.logs.guildUpdate.owner(locale, before=before.owner.mention if before.owner else keiner_locale, after=after.owner.mention if after.owner else keiner_locale))
        if before.preferred_locale != after.preferred_locale:
            before_locale = locale.logs.guildUpdate.featuresLocales.resolve('preferredLocaleLocales.' + str(before.preferred_locale))(locale)
            after_locale = locale.logs.guildUpdate.preferredLocaleLocales.resolve(str(after.preferred_locale))(locale)
            description_parts.append(locale.logs.guildUpdate.preferredLocale(locale, before=before_locale, after=after_locale))
        if before.premium_progress_bar_enabled != after.premium_progress_bar_enabled:
            if before.premium_progress_bar_enabled:
                description_parts.append(locale.logs.guildUpdate.premiumProgressBarEnabled.activated(locale))
            else:
                description_parts.append(locale.logs.guildUpdate.premiumProgressBarEnabled.deactivated(locale))
        if before.premium_subscriber_role != after.premium_subscriber_role:
            description_parts.append(locale.logs.guildUpdate.premiumSubscriberRole(locale, before=before.premium_subscriber_role.mention if before.premium_subscriber_role else keiner_locale, after=after.premium_subscriber_role.mention if after.premium_subscriber_role else keiner_locale))
        if before.premium_subscribers != after.premium_subscribers:
            description_parts.append(locale.logs.guildUpdate.premiumSubscribers(locale, before=before.premium_subscribers, after=after.premium_subscribers))
        if before.premium_tier != after.premium_tier:
            description_parts.append(locale.logs.guildUpdate.premiumTier(locale, before=before.premium_tier, after=after.premium_tier))
        if before.public_updates_channel != after.public_updates_channel:
            description_parts.append(locale.logs.guildUpdate.publicUpdatesChannel(locale, before=before.public_updates_channel.mention if before.public_updates_channel else keiner_locale, after=after.public_updates_channel.mention if after.public_updates_channel else keiner_locale))
        if before.rules_channel != after.rules_channel:
            description_parts.append(locale.logs.guildUpdate.rulesChannel(locale, before=before.rules_channel.mention if before.rules_channel else keiner_locale, after=after.rules_channel.mention if after.rules_channel else keiner_locale))
        if before.safety_alerts_channel != after.safety_alerts_channel:
            description_parts.append(locale.logs.guildUpdate.safetyAlertsChannel(locale, before=before.safety_alerts_channel.mention if before.safety_alerts_channel else keiner_locale, after=after.safety_alerts_channel.mention if after.safety_alerts_channel else keiner_locale))
        if before.unavailable != after.unavailable:
            if before.unavailable:
                description_parts.append(locale.logs.guildUpdate.unavailableLocales.available(locale))
            else:
                description_parts.append(locale.logs.guildUpdate.unavailableLocales.unavailable(locale))
        if before.verification_level != after.verification_level:
            none_locale = locale.logs.guildUpdate.verificationLevelLocales.none(locale)
            low_locale = locale.logs.guildUpdate.verificationLevelLocales.low(locale)
            medium_locale = locale.logs.guildUpdate.verificationLevelLocales.medium(locale)
            high_locale = locale.logs.guildUpdate.verificationLevelLocales.high(locale)
            highest_locale = locale.logs.guildUpdate.verificationLevelLocales.highest(locale)
            description_parts.append(locale.logs.guildUpdate.verificationLevel(locale, before=none_locale if before.verification_level.none else low_locale if before.verification_level.low else medium_locale if before.verification_level.medium else high_locale if before.verification_level.high else highest_locale, after=none_locale if after.verification_level.none else low_locale if after.verification_level.low else medium_locale if after.verification_level.medium else high_locale if after.verification_level.high else highest_locale))
        if len(description_parts) == 0:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.guildUpdate.title(locale), description=description)
        await log_event_producer(str(after.id), embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        log_enable = invite.guild and (await get_log_enable(invite.guild.id)).invite_create
        if not log_enable:
            return
        if await is_log_entity_blacklisted(invite.guild.id, str(invite.inviter.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(invite.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in invite.inviter.roles)):
                return
        locale = invite.guild.preferred_locale if hasattr(invite.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        never_locale = locale.logs.inviteCreate.expiresLocales.never(locale)
        infinite_locale = locale.logs.inviteCreate.maxUsesLocales.infinite(locale)
        description_parts.append(locale.logs.inviteCreate.createdBy(locale, created_by=invite.inviter.mention))
        description_parts.append(locale.logs.inviteCreate.expires(locale, expires=never_locale if invite.expires_at is None else '<t:' + str(utility.date_time_to_timestamp(invite.expires_at)) + ':R>'))
        description_parts.append(locale.logs.inviteCreate.max_uses(locale, max_uses=infinite_locale if invite.max_uses is None else invite.max_uses))
        if invite.channel:
            description_parts.append(locale.logs.inviteCreate.channel(locale, channel=invite.channel.mention))
        if invite.scheduled_event:
            description_parts.append(locale.logs.inviteCreate.scheduledEvent(locale, scheduled_event=invite.scheduled_event.url))
        if invite.target_application:
            description_parts.append(locale.logs.inviteCreate.targetApplication(locale, target_application=invite.target_application.name))
        if str(invite.target_type) != 'InviteTarget.unknown':
            description_parts.append(locale.logs.inviteCreate.targetTypeLocales.resolve(str(invite.target_type))(locale))
        if invite.target_user:
            description_parts.append(locale.logs.inviteCreate.targetUser(locale, target_user=invite.target_user.mention))
        if invite.temporary:
            description_parts.append(locale.logs.inviteCreate.temporary(locale))
        description_parts.append(locale.logs.inviteCreate.invite(locale, invite=invite.url))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.inviteCreate.title(locale), description=description)
        await log_event_producer(str(invite.guild.id), embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        log_enable = invite.guild and (await get_log_enable(invite.guild.id)).invite_delete
        if not log_enable:
            return
        if await is_log_entity_blacklisted(invite.guild.id, str(invite.inviter.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(invite.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in invite.inviter.roles)):
                return
        locale = invite.guild.preferred_locale if hasattr(invite.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        never_locale = locale.logs.inviteCreate.expiresLocales.never(locale)
        infinite_locale = locale.logs.inviteCreate.maxUsesLocales.infinite(locale)
        description_parts.append(locale.logs.inviteCreate.expires(locale, expires=never_locale if invite.expires_at is None else '<t:' + str(utility.date_time_to_timestamp(invite.expires_at)) + ':R>'))
        description_parts.append(locale.logs.inviteCreate.max_uses(locale, max_uses=infinite_locale if invite.max_uses is None else invite.max_uses))
        if invite.channel:
            description_parts.append(locale.logs.inviteCreate.channel(locale, channel=invite.channel.mention))
        if invite.scheduled_event:
            description_parts.append(locale.logs.inviteCreate.scheduledEvent(locale, scheduled_event=invite.scheduled_event.url))
        if invite.target_application:
            description_parts.append(locale.logs.inviteCreate.targetApplication(locale, target_application=invite.target_application.name))
        if str(invite.target_type) != 'InviteTarget.unknown':
            description_parts.append(locale.logs.inviteCreate.targetTypeLocales.resolve(str(invite.target_type))(locale))
        if invite.target_user:
            description_parts.append(locale.logs.inviteCreate.targetUser(locale, target_user=invite.target_user.mention))
        if invite.temporary:
            description_parts.append(locale.logs.inviteCreate.temporary(locale))
        description_parts.append(locale.logs.inviteDelete.invite(locale, invite=invite.url))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.inviteDelete.title(locale), description=description)
        await log_event_producer(str(invite.guild.id), embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        log_enable = member.guild and (await get_log_enable(member.guild.id)).member_join
        if not log_enable:
            return
        if await is_log_entity_blacklisted(member.guild.id, str(member.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(member.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in member.roles)):
                return
        locale = member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.memberJoin.name(locale, joined=member.mention))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.memberJoin.title(locale), description=description)
        await log_event_producer(str(member.guild.id), embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        log_enable = member.guild and (await get_log_enable(member.guild.id)).member_leave
        if not log_enable:
            return
        if await is_log_entity_blacklisted(member.guild.id, str(member.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(member.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in member.roles)):
                return
        locale = member.guild.preferred_locale if hasattr(member.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.memberRemove.name(locale, left=member.mention))
        description_parts.append(locale.logs.memberRemove.roles(locale, roles=', '.join((role.mention for role in member.roles))))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.memberJoin.title(locale), description=description)
        await log_event_producer(str(member.guild.id), embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).member_update
        if not log_enable:
            return
        if await is_log_entity_blacklisted(after.guild.id, str(after.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(after.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in after.roles)):
                return
        locale = after.guild.preferred_locale if hasattr(after.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.memberUpdate.name(locale, member=after.mention))
        if before.display_avatar != after.display_avatar:
            default_avatar_url = 'https://cdn.discordapp.com/embed/avatars/0.png'
            url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
            avatar_bytes = await before.display_avatar.read() if before.display_avatar else None
            avatar_upload_response = await utility.upload_image_to_imgbb(avatar_bytes, 'png') if avatar_bytes else {}
            avatar_url_before = avatar_upload_response.get('data', {}).get('url', default_avatar_url)
            new_avatar_bytes = await after.display_avatar.read() if after.display_avatar else None
            new_avatar_upload_response = await utility.upload_image_to_imgbb(new_avatar_bytes, 'png') if new_avatar_bytes else {}
            new_avatar_url = new_avatar_upload_response.get('data', {}).get('url', default_avatar_url)
            description_parts.append(locale.logs.userUpdate.avatar(locale, before=f'[{url_locale}]({avatar_url_before})', after=f'[{url_locale}]({new_avatar_url})'))
        if before.banner != after.banner:
            none_locale = locale.logs.userUpdate.guildAvatarLocales.none(locale)
            url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
            banner_bytes = await before.banner.read() if before.banner else None
            banner_upload_response = await utility.upload_image_to_imgbb(banner_bytes, 'png') if banner_bytes else {}
            banner_url_before = banner_upload_response.get('data', {}).get('url', none_locale)
            if after.banner:
                new_banner_bytes = await after.banner.read()
                new_banner_upload_response = await utility.upload_image_to_imgbb(new_banner_bytes, 'png')
                new_banner_url = new_banner_upload_response.get('data', {}).get('url', none_locale)
            else:
                new_banner_url = none_locale
            description_parts.append(locale.logs.userUpdate.banner(locale, before=f'[{url_locale}]({banner_url_before})', after=f'[{url_locale}]({new_banner_url})'))
        if before.display_name != after.display_name:
            description_parts.append(locale.logs.memberUpdate.displayName(locale, before=before.display_name, after=after.display_name))
        added_roles = [role.mention for role in after.roles if role not in before.roles]
        removed_roles = [role.mention for role in before.roles if role not in after.roles]
        if added_roles:
            description_parts.append(locale.logs.memberUpdate.addedRoles(locale, roles=', '.join(added_roles)))
        if removed_roles:
            description_parts.append(locale.logs.memberUpdate.removedRoles(locale, roles=', '.join(removed_roles)))
        if before.pending != after.pending:
            if before.pending:
                description_parts.append(locale.logs.memberUpdate.pending(locale))
            else:
                description_parts.append(locale.logs.memberUpdate.pendingRemoved(locale))
        if before.timed_out_until != after.timed_out_until:
            if before.timed_out_until is None:
                description_parts.append(locale.logs.memberUpdate.timeout(locale, timeout=utility.date_time_to_timestamp(after.timed_out_until)))
            else:
                description_parts.append(locale.logs.memberUpdate.timeoutRemoved(locale))
        if len(description_parts) >= 2:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.memberUpdate.title(locale), description=description)
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        for guild in self.bot.guilds:
            user = guild.get_member(before.id)
            if not user:
                continue
            log_enable = guild and (await get_log_enable(guild.id)).user_update
            if not log_enable:
                continue
            if await is_log_entity_blacklisted(guild.id, str(before.id), LogBlacklistType.USER):
                continue
            blacklisted_roles = await get_log_blacklist(guild.id, LogBlacklistType.ROLE)
            for blacklisted_role in blacklisted_roles:
                if any((str(role.id) == blacklisted_role for role in user.roles)):
                    continue
            locale = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
            description_parts = []
            description_parts.append(locale.logs.userUpdate.name(locale, user=before.mention))
            if before.avatar != after.avatar:
                description_parts.append(locale.logs.userUpdate.avatar(locale))
            if before.banner != after.banner:
                none_locale = locale.logs.userUpdate.guildAvatarLocales.none(locale)
                url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
                banner_bytes = await before.banner.read() if before.banner else None
                banner_upload_response = await utility.upload_image_to_imgbb(banner_bytes, 'png') if banner_bytes else {}
                banner_url_before = banner_upload_response.get('data', {}).get('url', none_locale)
                if after.banner:
                    new_banner_bytes = await after.banner.read()
                    new_banner_upload_response = await utility.upload_image_to_imgbb(new_banner_bytes, 'png')
                    new_banner_url = new_banner_upload_response.get('data', {}).get('url', none_locale)
                else:
                    new_banner_url = none_locale
                description_parts.append(locale.logs.userUpdate.banner(locale, before=f'[{url_locale}]({banner_url_before})', after=f'[{url_locale}]({new_banner_url})'))
            if len(description_parts) == 1:
                return
            description = '\n'.join(description_parts)
            embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.userUpdate.title(locale), description=description)
            await log_event_producer(str(guild.id), embed)

    @commands.Cog.listener()
    async def on_member_ban(self, user: discord.Member) -> None:
        log_enable = user.guild and (await get_log_enable(user.guild.id)).member_ban
        if not log_enable:
            return
        if await is_log_entity_blacklisted(user.guild.id, str(user.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(user.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in user.roles)):
                return
        locale = user.guild.preferred_locale if hasattr(user.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.memberBan.name(locale, user=user.mention))
        ban_entry = await _find_audit_log_entry(user.guild, discord.AuditLogAction.ban, lambda e: e.target == user, limit=1)
        banner = ban_entry.user if ban_entry else None
        if banner:
            description_parts.append(locale.logs.memberBan.banned_by(locale, banner=banner.mention))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.memberBan.title(locale), description=description)
        await log_event_producer(str(user.guild.id), embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        log_enable = guild and (await get_log_enable(guild.id)).member_unban
        if not log_enable:
            return
        if await is_log_entity_blacklisted(guild.id, str(user.id), LogBlacklistType.USER):
            return
        locale = str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.memberUnban.name(locale, user=user.mention))
        unban_entry = await _find_audit_log_entry(guild, discord.AuditLogAction.unban, lambda e: e.target == user, limit=1)
        unbanned_by = unban_entry.user if unban_entry else None
        if unbanned_by:
            description_parts.append(locale.logs.memberUnban.unbanned_by(locale, unbanned_by=unbanned_by.mention))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.memberUnban.title(locale), description=description)
        await log_event_producer(str(guild.id), embed)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).presence_update
        if not log_enable:
            return
        if await is_log_entity_blacklisted(after.guild.id, str(after.id), LogBlacklistType.USER):
            return
        blacklisted_roles = await get_log_blacklist(after.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in after.roles)):
                return
        locale = after.guild.preferred_locale if hasattr(after.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.presenceUpdate.name(locale, user=after.mention))
        if before.activity != after.activity:
            description_parts.append(locale.logs.presenceUpdate.activity(locale, before=before.activity, after=after.activity))
        if len(description_parts) == 1:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.presenceUpdate.title(locale), description=description)
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).message_edit
        if not log_enable:
            return
        if await is_log_entity_blacklisted(after.guild.id, str(after.author.id), LogBlacklistType.USER):
            return
        if after.channel is not None and after.guild is not None and await _is_channel_or_category_blacklisted(str(after.guild.id), after.channel):
            return
        blacklisted_roles = await get_log_blacklist(after.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in after.author.roles)):
                return
        locale = after.guild.preferred_locale if hasattr(after, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.messageEdit.name(locale, user=after.author.mention, url=after.jump_url))
        if before.content != after.content:
            diff = difflib.ndiff(before.content.splitlines(keepends=True), after.content.splitlines(keepends=True))
            diff_summary = '\n'.join(diff)
            truncated_notice = locale.logs.messageEdit.truncatedNotice(locale)
            if len(diff_summary) > 1500:
                diff_summary_url = await upload_to_tanjun_logs(locale.logs.messageEdit.diff(locale, diff=diff_summary))
                description_parts.append(locale.logs.messageEdit.tooLongNotice(locale, url=diff_summary_url))
            else:
                description_parts.append(locale.logs.messageEdit.diff(locale, diff=diff_summary))
        if before.attachments != after.attachments:
            added_attachments = [f'[{attachment.filename}]({attachment.url})' for attachment in after.attachments if attachment not in before.attachments]
            removed_attachments = []
            url_not_available_locale = locale.logs.messageEdit.url_not_available_locale(locale)
            for attachment in before.attachments:
                if attachment not in after.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        attachment_bytes = await attachment.read()
                        url = await upload_image_to_imgbb(attachment_bytes, attachment.filename.split('.')[-1])
                        if url:
                            url = url['data']['display_url']
                    else:
                        url = None
                    removed_attachments.append(f'[{attachment.filename}]({(url if url else url_not_available_locale)})')
            if added_attachments:
                description_parts.append(locale.logs.messageEdit.addedAttachments(locale, attachments=', '.join(added_attachments)))
            if removed_attachments:
                description_parts.append(locale.logs.messageEdit.removedAttachments(locale, attachments=', '.join(removed_attachments)))
        if len(description_parts) == 1:
            return
        description = '\n'.join(description_parts)
        if len(description) > 4000:
            description = description[:3000] + f' {truncated_notice}'
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.messageEdit.title(locale), description=description)
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        log_enable = message.guild and (await get_log_enable(message.guild.id)).message_delete
        if not log_enable:
            return
        if await is_log_entity_blacklisted(message.guild.id, str(message.author.id), LogBlacklistType.USER):
            return
        if message.channel is not None and message.guild is not None and await _is_channel_or_category_blacklisted(str(message.guild.id), message.channel):
            return
        blacklisted_roles = await get_log_blacklist(message.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in message.author.roles)):
                return
        locale = str(message.guild.preferred_locale) if hasattr(message.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.messageDelete.name(locale, user=message.author.mention, channel=message.channel.mention))
        send_log = False
        delete_entry = await _find_audit_log_entry(message.guild, discord.AuditLogAction.message_delete, lambda e: e.target.id == message.author.id and e.extra.channel.id == message.channel.id)
        deleted_by = delete_entry.user if delete_entry else None
        if deleted_by:
            description_parts.append(locale.logs.messageDelete.deletedBy(locale, deleted_by=deleted_by.mention))
        if message.content:
            send_log = True
            description_parts.append(locale.logs.messageDelete.content(locale, content=message.content))
        if message.attachments:
            send_log = True
            attachment_parts = []
            url_not_available_locale = locale.logs.messageDelete.url_not_available_locale(locale)
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    try:
                        attachment_bytes = await attachment.read()
                        url = await upload_image_to_imgbb(attachment_bytes, attachment.filename.split('.')[-1])
                        if url:
                            url = url['data']['display_url']
                    except Exception:
                        url = None
                else:
                    url = None
                attachment_parts.append(f'[{attachment.filename}]({(url if url else url_not_available_locale)})')
            attachments = '\n- '.join(attachment_parts)
            description_parts.append(locale.logs.messageDelete.attachments(locale, attachments=attachments))
        if message.embeds:
            send_log = True
            description_parts.append(locale.logs.messageDelete.embeds(locale))
        if not send_log:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.messageDelete.title(locale), description=description)
        await log_event_producer(str(message.guild.id), embed)
        for emb in message.embeds:
            await log_event_producer(str(message.guild.id), emb)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        log_enable = reaction.guild and (await get_log_enable(reaction.guild.id)).reaction_add
        if not log_enable:
            return
        if await is_log_entity_blacklisted(reaction.guild.id, str(user.id), LogBlacklistType.USER):
            return
        if reaction.message.channel is not None and reaction.guild is not None and await _is_channel_or_category_blacklisted(str(reaction.guild.id), reaction.message.channel):
            return
        blacklisted_roles = await get_log_blacklist(reaction.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in user.roles)):
                return
        locale = reaction.guild.preferred_locale if hasattr(reaction.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.reactionAdd.name(locale, user=user.mention, emoji=reaction.emoji, message=reaction.message.jump_url))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.reactionAdd.title(locale), description=description)
        await log_event_producer(str(reaction.guild.id), embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User) -> None:
        log_enable = reaction.guild and (await get_log_enable(reaction.guild.id)).reaction_remove
        if not log_enable:
            return
        if await is_log_entity_blacklisted(reaction.guild.id, str(user.id), LogBlacklistType.USER):
            return
        if reaction.message.channel is not None and reaction.guild is not None and await _is_channel_or_category_blacklisted(str(reaction.guild.id), reaction.message.channel):
            return
        blacklisted_roles = await get_log_blacklist(reaction.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any((str(role.id) == blacklisted_role for role in user.roles)):
                return
        locale = reaction.guild.preferred_locale if hasattr(reaction.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.reactionRemove.name(locale, user=user.mention, emoji=reaction.emoji, message=reaction.message.jump_url))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.reactionRemove.title(locale), description=description)
        await log_event_producer(str(reaction.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        log_enable = role.guild and (await get_log_enable(role.guild.id)).guild_role_create
        if not log_enable:
            return
        locale = role.guild.preferred_locale if hasattr(role.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.guildRoleCreate.name(locale, role=role.mention))
        create_entry = await _find_audit_log_entry(role.guild, discord.AuditLogAction.role_create, lambda e: e.target.id == role.id)
        created_by = create_entry.user if create_entry else None
        if created_by:
            description_parts.append(locale.logs.guildRoleCreate.createdBy(locale, created_by=created_by.mention))
        if role.color:
            description_parts.append(locale.logs.guildRoleCreate.color(locale, color=role.color))
        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
                description_parts.append(locale.logs.guildRoleCreate.displayIcon(locale, displayIcon=f'[{url_locale}]({role.display_icon.url})'))
            else:
                description_parts.append(locale.logs.guildRoleCreate.displayIcon(locale, displayIcon=role.display_icon))
        if role.hoist:
            description_parts.append(locale.logs.guildRoleCreate.hoist(locale))
        if role.managed:
            description_parts.append(locale.logs.guildRoleCreate.managed(locale))
        if role.mentionable:
            description_parts.append(locale.logs.guildRoleCreate.mentionable(locale))
        if role.permissions:
            permissions_list = [perm for perm, value in role.permissions if value]
            if permissions_list:
                formatted_permissions = ', '.join([f'`{locale.logs.permissions.resolve(perm)(locale)}`' for perm in permissions_list])
                description_parts.append(locale.logs.guildRoleCreate.permissions(locale, permissions=formatted_permissions))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.SUCCESS, title=locale.logs.guildRoleCreate.title(locale), description=description)
        await log_event_producer(str(role.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        log_enable = role.guild and (await get_log_enable(role.guild.id)).guild_role_delete
        if not log_enable:
            return
        locale = role.guild.preferred_locale if hasattr(role.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        description_parts.append(locale.logs.guildRoleDelete.name(locale, role=role.name))
        delete_entry = await _find_audit_log_entry(role.guild, discord.AuditLogAction.role_delete, lambda e: e.target.id == role.id)
        deleted_by = delete_entry.user if delete_entry else None
        if deleted_by:
            description_parts.append(locale.logs.guildRoleDelete.deletedBy(locale, deleted_by=deleted_by.mention))
        if role.color:
            description_parts.append(locale.logs.guildRoleCreate.color(locale, color=role.color))
        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
                description_parts.append(locale.logs.guildRoleCreate.displayIcon(locale, displayIcon=f'[{url_locale}]({role.display_icon.url})'))
            else:
                description_parts.append(locale.logs.guildRoleCreate.displayIcon(locale, displayIcon=role.display_icon))
        if role.hoist:
            description_parts.append(locale.logs.guildRoleCreate.hoist(locale))
        if role.managed:
            description_parts.append(locale.logs.guildRoleCreate.managed(locale))
        if role.mentionable:
            description_parts.append(locale.logs.guildRoleCreate.mentionable(locale))
        if role.permissions:
            permissions_list = [perm for perm, value in role.permissions if value]
            if permissions_list:
                formatted_permissions = ', '.join([f'`{locale.logs.permissions.resolve(perm)(locale)}`' for perm in permissions_list])
                description_parts.append(locale.logs.guildRoleDelete.permissions(locale, permissions=formatted_permissions))
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.ERROR, title=locale.logs.guildRoleDelete.title(locale), description=description)
        await log_event_producer(str(role.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_role_update
        if not log_enable:
            return
        locale = after.guild.preferred_locale if hasattr(after.guild, 'preferred_locale') else 'en_US'
        description_parts = []
        if before.name != after.name:
            description_parts.append(locale.logs.guildRoleUpdate.name(locale, role=after.name))
        update_entry = await _find_audit_log_entry(after.guild, discord.AuditLogAction.role_update, lambda e: e.target.id == after.id)
        updated_by = update_entry.user if update_entry else None
        if updated_by:
            description_parts.append(locale.logs.guildRoleUpdate.updatedBy(locale, updated_by=updated_by.mention))
        if before.color != after.color:
            description_parts.append(locale.logs.guildRoleUpdate.color(locale, before=before.color, after=after.color))
        if before.hoist != after.hoist:
            if after.hoist:
                description_parts.append(locale.logs.guildRoleUpdate.hoistNow(locale, role=after.name))
            else:
                description_parts.append(locale.logs.guildRoleUpdate.hoistNoLonger(locale, role=after.name))
        if before.mentionable != after.mentionable:
            if after.mentionable:
                description_parts.append(locale.logs.guildRoleUpdate.mentionableNow(locale, role=after.name))
            else:
                description_parts.append(locale.logs.guildRoleUpdate.mentionableNoLonger(locale, role=after.name))
        if before.managed != after.managed:
            if after.managed:
                description_parts.append(locale.logs.guildRoleUpdate.managedNow(locale, role=after.name))
            else:
                description_parts.append(locale.logs.guildRoleUpdate.managedNoLonger(locale, role=after.name))
        before_perms = {perm for perm, value in before.permissions if value}
        after_perms = {perm for perm, value in after.permissions if value}
        added_perms = after_perms - before_perms
        removed_perms = before_perms - after_perms
        if added_perms:
            added_perms_list = ', '.join([f'`{locale.logs.permissions.resolve(perm)(locale)}`' for perm in added_perms])
            description_parts.append(locale.logs.guildRoleUpdate.addedPermissions(locale, permissions=added_perms_list))
        if removed_perms:
            removed_perms_list = ', '.join([f'`{locale.logs.permissions.resolve(perm)(locale)}`' for perm in removed_perms])
            description_parts.append(locale.logs.guildRoleUpdate.removedPermissions(locale, permissions=removed_perms_list))
        if before.display_icon != after.display_icon:
            url_locale = locale.logs.userUpdate.guildAvatarLocales.url(locale)
            description_parts.append(locale.logs.guildRoleUpdate.displayIcon(locale, before=f'[{url_locale}]({before.display_icon.url})' if before.display_icon else 'None', after=f'[{url_locale}]({after.display_icon.url})' if after.display_icon else 'None'))
        if before.icon != after.icon:
            description_parts.append(locale.logs.guildRoleUpdate.icon(locale, before=before.icon, after=after.icon))
        if len(description_parts) == 1:
            return
        description = '\n'.join(description_parts)
        embed = discord.Embed(color=EmbedColor.WARNING, title=locale.logs.guildRoleUpdate.title(locale), description=description)
        await log_event_producer(str(after.guild.id), embed)

    async def log_consumer_task(self) -> None:
        """Run the log event consumer as a background task."""
        try:
            await log_event_consumer(self.bot)
        finally:
            self._log_consumer_task = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logcmds = LogsCommands(name=locale.logs.name.discord_key, description=locale.logs.description.discord_key)
        channel_blacklist = ChannelBlacklistCommands(name=locale.logs.blacklist.name.discord_key, description=locale.logs.blacklist.description.discord_key)
        user_blacklist = UserBlacklistCommands(name=locale.logs.blacklistu.name.discord_key, description=locale.logs.blacklistu.description.discord_key)
        role_blacklist = RoleBlacklistCommands(name=locale.logs.blacklistr.name.discord_key, description=locale.logs.blacklistr.description.discord_key)
        voice_blacklist = VoiceBlacklistCommands(name=locale.logs.blacklistv.name.discord_key, description=locale.logs.blacklistv.description.discord_key)
        category_blacklist = CategoryBlacklistCommands(name=locale.logs.blacklistcat.name.discord_key, description=locale.logs.blacklistcat.description.discord_key)
        logcmds.add_command(channel_blacklist)
        logcmds.add_command(user_blacklist)
        logcmds.add_command(role_blacklist)
        logcmds.add_command(voice_blacklist)
        logcmds.add_command(category_blacklist)
        self.bot.tree.add_command(logcmds)
        if self._log_consumer_task is None or self._log_consumer_task.done():
            self._log_consumer_task = self.bot.loop.create_task(self.log_consumer_task())

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LogsCog(bot))