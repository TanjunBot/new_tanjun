import asyncio
import difflib
import logging

import discord
from discord import app_commands
from discord.ext import commands

import utility
from api import (
    LogBlacklistType,
    get_log_blacklist,
    get_log_channel,
    get_log_enable,
    is_log_entity_blacklisted,
)
from commands.logs.blacklist_category.blacklist_category import blacklist_category
from commands.logs.blacklist_category.blacklist_list_category import (
    blacklist_list_category,
)
from commands.logs.blacklist_category.blacklist_remove_category import (
    blacklist_remove_category,
)
from commands.logs.blacklist_channel.blacklist_channel import blacklist_channel
from commands.logs.blacklist_channel.blacklist_list_channel import (
    blacklist_list_channel,
)
from commands.logs.blacklist_channel.blacklist_remove_channel import (
    blacklist_remove_channel,
)
from commands.logs.blacklist_role.blacklist_list_role import blacklist_list_role
from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role
from commands.logs.blacklist_role.blacklist_role import blacklist_role
from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user
from commands.logs.blacklist_user.blacklist_remove_user import blacklist_remove_user
from commands.logs.blacklist_user.blacklist_user import blacklist_user
from commands.logs.blacklist_voice.blacklist_list_voice import (
    blacklist_list_voice,
)
from commands.logs.blacklist_voice.blacklist_remove_voice import (
    blacklist_remove_voice,
)
from commands.logs.blacklist_voice.blacklist_voice import blacklist_voice
from commands.logs.configure_logs import configure_logs
from commands.logs.remove_log_channel import remove_log_channel
from commands.logs.set_log_channel import set_log_channel
from localizer import tanjunLocalizer
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

    if isinstance(channel, discord.VoiceChannel) and await is_log_entity_blacklisted(
        guild_id, channel_id, LogBlacklistType.VOICE_CHANNEL
    ):
        return True

    if channel.category is not None and await is_log_entity_blacklisted(
        guild_id, str(channel.category.id), LogBlacklistType.CATEGORY
    ):
        return True

    return False


async def _is_category_blacklisted(guild_id: str, category_id: str | None) -> bool:
    """Check if a category ID is blacklisted."""
    if category_id is None:
        return False
    return await is_log_entity_blacklisted(guild_id, category_id, LogBlacklistType.CATEGORY) is not None


embeds = {}  # type: ignore[var-annotated]

_log_queue: asyncio.Queue[tuple[str, discord.Embed]] = asyncio.Queue(maxsize=200)


async def log_event_producer(guild_id: str, embed: discord.Embed) -> None:
    """Called by event listeners - never blocks."""
    try:
        _log_queue.put_nowait((guild_id, embed))
    except asyncio.QueueFull:
        pass  # Drop oldest event silently when queue is full


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
            if not isinstance(
                destination_channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.Thread)
            ):
                continue
            await destination_channel.send(embed=embed)
        except Exception:
            logging.exception("Error in log event consumer loop processing guild %s", guild_id)


class ChannelBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_add_name"),
        description=app_commands.locale_str("logs_blacklistc_add_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistc_add_params_channel_description"))
    async def add_blacklist_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel  # type: ignore[unreachable]

        await blacklist_channel(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_remove_name"),
        description=app_commands.locale_str("logs_blacklistc_remove_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistc_remove_params_channel_description"))
    async def remove_blacklist_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel  # type: ignore[unreachable]

        await blacklist_remove_channel(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_show_name"),
        description=app_commands.locale_str("logs_blacklistc_show_description"),
    )
    async def show_blacklist_channel_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await blacklist_list_channel(command_info=command_info)


class UserBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_add_name"),
        description=app_commands.locale_str("logs_blacklistu_add_description"),
    )
    @app_commands.describe(user=app_commands.locale_str("logs_blacklistu_add_params_user_description"))
    async def add_blacklist_user_cmd(self, ctx: discord.Interaction, user: discord.Member) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_user(command_info=command_info, user=user)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_remove_name"),
        description=app_commands.locale_str("logs_blacklistu_remove_description"),
    )
    @app_commands.describe(user=app_commands.locale_str("logs_blacklistu_remove_params_user_description"))
    async def remove_blacklist_user_cmd(self, ctx: discord.Interaction, user: discord.Member) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_remove_user(command_info=command_info, user=user)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_show_name"),
        description=app_commands.locale_str("logs_blacklistu_show_description"),
    )
    async def show_blacklist_user_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_user(command_info=command_info)


class RoleBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_add_name"),
        description=app_commands.locale_str("logs_blacklistr_add_description"),
    )
    @app_commands.describe(role=app_commands.locale_str("logs_blacklistr_add_params_role_description"))
    async def add_blacklist_role_cmd(self, ctx: discord.Interaction, role: discord.Role) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_role(command_info=command_info, role=role)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_remove_name"),
        description=app_commands.locale_str("logs_blacklistr_remove_description"),
    )
    @app_commands.describe(role=app_commands.locale_str("logs_blacklistr_remove_params_role_description"))
    async def remove_blacklist_role_cmd(self, ctx: discord.Interaction, role: discord.Role) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_remove_role(command_info=command_info, role=role)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_show_name"),
        description=app_commands.locale_str("logs_blacklistr_show_description"),
    )
    async def show_blacklist_role_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_role(command_info=command_info)


class VoiceBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistv_add_name"),
        description=app_commands.locale_str("logs_blacklistv_add_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistv_add_params_channel_description"))
    async def add_blacklist_voice_cmd(self, ctx: discord.Interaction, channel: discord.VoiceChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistVoiceChannel.missingChannel.title",
                ),
                description=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistVoiceChannel.missingChannel.description",
                ),
            )
            await ctx.followup.send(embed=embed)
            return

        await blacklist_voice(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistv_remove_name"),
        description=app_commands.locale_str("logs_blacklistv_remove_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistv_remove_params_channel_description"))
    async def remove_blacklist_voice_cmd(self, ctx: discord.Interaction, channel: discord.VoiceChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistRemoveVoiceChannel.missingChannel.title",
                ),
                description=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistRemoveVoiceChannel.missingChannel.description",
                ),
            )
            await ctx.followup.send(embed=embed)
            return

        await blacklist_remove_voice(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistv_show_name"),
        description=app_commands.locale_str("logs_blacklistv_show_description"),
    )
    async def show_blacklist_voice_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_voice(command_info=command_info)


class CategoryBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistcat_add_name"),
        description=app_commands.locale_str("logs_blacklistcat_add_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistcat_add_params_channel_description"))
    async def add_blacklist_category_cmd(self, ctx: discord.Interaction, channel: discord.CategoryChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistCategory.missingChannel.title",
                ),
                description=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistCategory.missingChannel.description",
                ),
            )
            await ctx.followup.send(embed=embed)
            return

        await blacklist_category(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistcat_remove_name"),
        description=app_commands.locale_str("logs_blacklistcat_remove_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_blacklistcat_remove_params_channel_description"))
    async def remove_blacklist_category_cmd(self, ctx: discord.Interaction, channel: discord.CategoryChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistRemoveCategory.missingChannel.title",
                ),
                description=tanjunLocalizer.localize(
                    ctx.locale,
                    "commands.logs.blacklistRemoveCategory.missingChannel.description",
                ),
            )
            await ctx.followup.send(embed=embed)
            return

        await blacklist_remove_category(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistcat_show_name"),
        description=app_commands.locale_str("logs_blacklistcat_show_description"),
    )
    async def show_blacklist_category_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_category(command_info=command_info)


class LogsCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_set_name"),
        description=app_commands.locale_str("logs_set_description"),
    )
    @app_commands.describe(channel=app_commands.locale_str("logs_set_params_channel_description"))
    async def set_log_channel_cmd(self, ctx: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel  # type: ignore[unreachable]

        await set_log_channel(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_remove_name"),
        description=app_commands.locale_str("logs_remove_description"),
    )
    async def remove_log_channel_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await remove_log_channel(command_info=command_info)

    @app_commands.command(
        name=app_commands.locale_str("logs_configure_name"),
        description=app_commands.locale_str("logs_configure_description"),
    )
    async def configure_logs_cmd(self, ctx: discord.Interaction) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=ctx.channel,  # type: ignore[arg-type]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await configure_logs(command_info=command_info)


class LogsCog(commands.Cog):
    def __init__(self, bot) -> None:  # type: ignore[no-untyped-def]
        self.bot = bot
        self._log_consumer_task: asyncio.Task[None] | None = None

    @commands.Cog.listener()
    async def on_automod_rule_create(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_create
        if not log_enable:
            return

        if rule.channel_id is not None and await is_log_entity_blacklisted(
            rule.guild.id, str(rule.channel_id), LogBlacklistType.CHANNEL
        ):
            return

        locale = rule.guild.preferred_locale if hasattr(rule.guild, "preferred_locale") else "en_US"
        description_parts = []

        # Basic info
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.created_by",
                creator=rule.creator.mention,  # type: ignore[union-attr]
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.name", name=rule.name))

        # Trigger information
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger"))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(tanjunLocalizer.localize(locale, "logs.automodRuleCreate." + str(rule.trigger.type))),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(f"- {keyword}" for keyword in rule.trigger.keyword_filter)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.keywordFilters",
                    keywordFilters=filters,
                )
            )

        # Regex patterns
        if rule.trigger.regex_patterns:
            patterns = "\n".join(f"- {regex}" for regex in rule.trigger.regex_patterns)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.regexPatterns",
                    regexPatterns=patterns,
                )
            )

        # Presets
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.presets",
                profanityFilter="✅" if rule.trigger.presets.profanity else "❌",
                sexualContentFilter=("✅" if rule.trigger.presets.sexual_content else "❌"),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.allow_list", allow_list=allows))

        # Mention limits
        if rule.trigger.mention_limit:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.max_mentions",
                    max_mentions=rule.trigger.mention_limit,
                )
            )

        if rule.trigger.mention_raid_protection:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.mentionSpamProtection"))

        # Exemptions
        if rule.exempt_roles:
            roles = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_roles)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_roles",
                    excluded_roles=roles or "-",
                )
            )

        if rule.exempt_channels:
            channels = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_channels)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions"))

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.block_message"))

                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.send_warning_message",
                            channel=r.channel_id,
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.block_member_interaction",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleCreate.title"),
            description=description,
        )
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_rule_update(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_update
        if not log_enable:
            return

        if rule.channel_id is not None and await is_log_entity_blacklisted(
            rule.guild.id, str(rule.channel_id), LogBlacklistType.CHANNEL
        ):
            return

        locale = rule.guild.preferred_locale if hasattr(rule.guild, "preferred_locale") else "en_US"
        description_parts = []

        updater = None

        async for entry in rule.guild.audit_logs(limit=5, action=discord.AuditLogAction.automod_rule_update):
            if entry.target.id == rule.id:  # type: ignore[union-attr]
                updater = entry.user.mention  # type: ignore[union-attr]
                break

        # Basic info
        if updater:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleUpdate.updated_by", updater=updater))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.name", name=rule.name))

        # Trigger information
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger"))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(tanjunLocalizer.localize(locale, "logs.automodRuleCreate." + str(rule.trigger.type))),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(f"- {keyword}" for keyword in rule.trigger.keyword_filter)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.keywordFilters",
                    keywordFilters=filters,
                )
            )

        # Regex patterns
        if rule.trigger.regex_patterns:
            patterns = "\n".join(f"- {regex}" for regex in rule.trigger.regex_patterns)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.regexPatterns",
                    regexPatterns=patterns,
                )
            )

        # Presets
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.presets",
                profanityFilter="✅" if rule.trigger.presets.profanity else "❌",
                sexualContentFilter=("✅" if rule.trigger.presets.sexual_content else "❌"),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.allow_list", allow_list=allows))

        # Mention limits
        if rule.trigger.mention_limit:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.max_mentions",
                    max_mentions=rule.trigger.mention_limit,
                )
            )

        if rule.trigger.mention_raid_protection:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.mentionSpamProtection"))

        # Exemptions
        if rule.exempt_roles:
            roles = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_roles)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_roles",
                    excluded_roles=roles or "-",
                )
            )

        if rule.exempt_channels:
            channels = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_channels)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions"))

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.block_message"))

                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.send_warning_message",
                            channel=r.channel_id,
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.block_member_interaction",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleUpdate.title"),
            description=description,
        )
        embed.set_footer(text=tanjunLocalizer.localize(locale, "logs.automodRuleUpdate.footer"))
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_rule_delete(self, rule: discord.AutoModRule) -> None:
        log_enable = rule.guild and (await get_log_enable(rule.guild.id)).automod_rule_delete
        if not log_enable:
            return

        if rule.channel_id is not None and await is_log_entity_blacklisted(
            rule.guild.id, str(rule.channel_id), LogBlacklistType.CHANNEL
        ):
            return

        locale = rule.guild.preferred_locale if hasattr(rule.guild, "preferred_locale") else "en_US"
        description_parts = []

        updater = None

        async for entry in rule.guild.audit_logs(limit=5, action=discord.AuditLogAction.automod_rule_delete):
            if entry.target.id == rule.id:  # type: ignore[union-attr]
                updater = entry.user.mention  # type: ignore[union-attr]
                break

        # Basic info
        if updater:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleDelete.deleted_by", updater=updater))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.name", name=rule.name))

        # Trigger information
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger"))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(tanjunLocalizer.localize(locale, "logs.automodRuleCreate." + str(rule.trigger.type))),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(f"- {keyword}" for keyword in rule.trigger.keyword_filter)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.keywordFilters",
                    keywordFilters=filters,
                )
            )

        # Regex patterns
        if rule.trigger.regex_patterns:
            patterns = "\n".join(f"- {regex}" for regex in rule.trigger.regex_patterns)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.regexPatterns",
                    regexPatterns=patterns,
                )
            )

        # Presets
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.presets",
                profanityFilter="✅" if rule.trigger.presets.profanity else "❌",
                sexualContentFilter=("✅" if rule.trigger.presets.sexual_content else "❌"),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.allow_list", allow_list=allows))

        # Mention limits
        if rule.trigger.mention_limit:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.max_mentions",
                    max_mentions=rule.trigger.mention_limit,
                )
            )

        if rule.trigger.mention_raid_protection:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.mentionSpamProtection"))

        # Exemptions
        if rule.exempt_roles:
            roles = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_roles)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_roles",
                    excluded_roles=roles or "-",
                )
            )

        if rule.exempt_channels:
            channels = "\n".join(f"- {excluded.mention}" for excluded in rule.exempt_channels)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions"))

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.block_message"))

                elif r.type == discord.AutoModRuleActionType.send_alert_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.send_warning_message",
                            channel=r.channel_id,
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.timeout:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

                elif r.type == discord.AutoModRuleActionType.block_member_interactions:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.block_member_interaction",
                            duration=str(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.automodRuleCreate.timeout_duration." + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleDelete.title"),
            description=description,
        )
        await log_event_producer(str(rule.guild.id), embed)

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction) -> None:
        log_enable = execution.guild and (await get_log_enable(execution.guild.id)).automod_action
        if not log_enable:
            return

        if execution.channel is not None and await _is_channel_or_category_blacklisted(
            str(execution.guild.id), execution.channel
        ):  # type: ignore[union-attr]
            return

        locale = execution.guild.preferred_locale if hasattr(execution.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodAction.actionWasTaken",
                user=execution.member.mention,  # type: ignore[union-attr]
                channel=execution.channel.mention,  # type: ignore[union-attr]
            )
        )
        # Actions
        description_parts.append(tanjunLocalizer.localize(locale, "logs.automodAction.action"))

        if execution.action.type == discord.AutoModRuleActionType.block_message:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.automodRuleCreate.block_message"))

        elif execution.action.type == discord.AutoModRuleActionType.send_alert_message:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.send_warning_message",
                    channel=execution.action.channel_id,
                )
            )

        elif execution.action.type == discord.AutoModRuleActionType.timeout:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.timeout",
                    duration=str(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout_duration." + str(execution.action.duration),
                        )
                    ),
                )
            )

        elif execution.action.type == discord.AutoModRuleActionType.block_member_interactions:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.block_member_interaction",
                    duration=str(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout_duration." + str(execution.action.duration),
                        )
                    ),
                )
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodAction.message",
                message=(
                    execution.action.content[0:1000] + "..."
                    if len(execution.action.content) > 1000
                    else execution.action.content
                ),
            )
        )

        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleDelete.title"),
            description=description,
        )
        await log_event_producer(str(execution.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        log_enable = channel.guild and (await get_log_enable(channel.guild.id)).guild_channel_delete
        if not log_enable:
            return

        if await _is_channel_or_category_blacklisted(str(channel.guild.id), channel):
            return

        locale = channel.guild.preferred_locale if hasattr(channel.guild, "preferred_locale") else "en_US"
        description_parts = []

        deleter = None
        async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:  # type: ignore[union-attr]
                deleter = entry.user.mention  # type: ignore[union-attr]
                break

        if deleter:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelDelete.deleted_by", deleter=deleter))

        description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelDelete.name", channel=channel.name))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guild_channelDelete.type",
                type=str(tanjunLocalizer.localize(locale, "logs.guild_channelDelete.types." + str(channel.type))),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guild_channelDelete.created_at",
                created_at=utility.date_time_to_timestamp(channel.created_at),
            )
        )
        if channel.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelDelete.category",
                    category=channel.category,
                )
            )

        if channel.topic:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelDelete.topic", topic=channel.topic))

        if len(channel.overwrites.keys()) > 0:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelDelete.permissionOverwrites"))
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    local_perm = tanjunLocalizer.localize(locale, "logs.permissions." + perm)
                    if value is True:
                        allowed.append(f"`{local_perm}`")
                    elif value is False:
                        denied.append(f"`{local_perm}`")

                target_str = target.mention if hasattr(target, "mention") else target.name
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guild_channelDelete.permissionOverwriteTarget",
                        target=target_str,
                    )
                )
                if allowed:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guild_channelDelete.permissionOverwriteAllowed",
                            permissions=", ".join(allowed),
                        )
                    )
                if denied:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guild_channelDelete.permissionOverwriteDenied",
                            permissions=", ".join(denied),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.guild_channelDelete.title"),
            description=description,
        )
        await log_event_producer(str(channel.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        log_enable = channel.guild and (await get_log_enable(channel.guild.id)).guild_channel_create
        if not log_enable:
            return

        if await _is_channel_or_category_blacklisted(str(channel.guild.id), channel):
            return

        locale = channel.guild.preferred_locale if hasattr(channel.guild, "preferred_locale") else "en_US"
        description_parts = []
        creator = None
        async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:  # type: ignore[union-attr]
                creator = entry.user.mention  # type: ignore[union-attr]
                break

        if creator:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelCreate.created_by", creator=creator))

        description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelCreate.name", name=channel.name))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guild_channelCreate.type",
                type=str(tanjunLocalizer.localize(locale, "logs.guild_channelCreate.types." + str(channel.type))),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guild_channelCreate.created_at",
                created_at=utility.date_time_to_timestamp(channel.created_at),
            )
        )
        if channel.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelCreate.category",
                    category=channel.category,
                )
            )

        if channel.topic:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelCreate.topic", topic=channel.topic))

        if len(channel.overwrites.keys()) > 0:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelCreate.permissionOverwrites"))
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    local_perm = tanjunLocalizer.localize(locale, "logs.permissions." + perm)
                    if value is True:
                        allowed.append(f"`{local_perm}`")
                    elif value is False:
                        denied.append(f"`{local_perm}`")

                target_str = target.mention if hasattr(target, "mention") else target.name
                description_parts.append(f"### {target_str}")
                if allowed:
                    description_parts.append("✅ " + ", ".join(allowed))
                if denied:
                    description_parts.append("❌ " + ", ".join(denied))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.guild_channelCreate.title"),
            description=description,
        )
        await log_event_producer(str(channel.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_channel_update
        if not log_enable:
            return

        if await _is_channel_or_category_blacklisted(str(after.guild.id), after):
            return

        locale = after.guild.preferred_locale if hasattr(after.guild, "preferred_locale") else "en_US"
        description_parts = []

        updater = None
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_update):
            if entry.target.id == after.id:  # type: ignore[union-attr]
                updater = entry.user.mention  # type: ignore[union-attr]
                break

        if updater:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.updated_by", updater=updater))

        description_parts.append(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.mention", mention=before.mention))

        if before.name != after.name:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.name",
                    before=before.name,
                    after=after.name,
                )
            )

        if hasattr(before, "type") and before.type != after.type:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.type",
                    before=str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.types." + str(before.type))),
                    after=str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.types." + str(after.type))),
                )
            )

        if hasattr(before, "category") and before.category != after.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.category",
                    before=before.category,
                    after=after.category,
                )
            )

        if hasattr(before, "topic") and before.topic != after.topic:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.topic",
                    before=before.topic,
                    after=after.topic,
                )
            )

        if before.overwrites != after.overwrites:
            # Track removed targets
            for target in before.overwrites:
                if target not in after.overwrites:
                    target_str = target.mention if hasattr(target, "mention") else target.name
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guild_channelUpdate.permissionOverwriteRemoved",
                            target=target_str,
                        )
                    )

            # Track added/modified targets
            for target, new_overwrite in after.overwrites.items():
                old_overwrite = before.overwrites.get(target, None)
                target_str = target.mention if hasattr(target, "mention") else target.name

                if old_overwrite is None:
                    # New target - show all permissions
                    allowed = []
                    denied = []
                    neutral = []
                    for perm, value in new_overwrite:
                        local_perm = tanjunLocalizer.localize(locale, "logs.permissions." + perm)
                        if value is True:
                            allowed.append(f"`{local_perm}`")
                        elif value is False:
                            denied.append(f"`{local_perm}`")
                        else:
                            neutral.append(f"`{local_perm}`")

                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guild_channelUpdate.permissionOverwriteNew",
                            target=target_str,
                        )
                    )
                    if allowed:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guild_channelUpdate.permissionOverwriteAllowed",
                                permissions=", ".join(allowed),
                            )
                        )
                    if denied:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guild_channelUpdate.permissionOverwriteDenied",
                                permissions=", ".join(denied),
                            )
                        )
                    if neutral:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guild_channelUpdate.permissionOverwriteNeutral",
                                permissions=", ".join(neutral),
                            )
                        )
                else:
                    # Modified target - show changes
                    added_allow = []
                    added_deny = []
                    added_neutral = []
                    removed_allow = []
                    removed_deny = []
                    removed_neutral = []

                    for perm, new_value in new_overwrite:
                        old_value = dict(old_overwrite)[perm]
                        if new_value != old_value:
                            local_perm = tanjunLocalizer.localize(locale, "logs.permissions." + perm)
                            if new_value is True:
                                added_allow.append(f"`{local_perm}`")
                            elif new_value is False:
                                added_deny.append(f"`{local_perm}`")
                            elif new_value is None:
                                added_neutral.append(f"`{local_perm}`")

                            if old_value is True:
                                removed_allow.append(f"`{local_perm}`")
                            elif old_value is False:
                                removed_deny.append(f"`{local_perm}`")
                            elif old_value is None:
                                removed_neutral.append(f"`{local_perm}`")

                    if any(
                        [
                            added_allow,
                            added_deny,
                            added_neutral,
                            removed_allow,
                            removed_deny,
                            removed_neutral,
                        ]
                    ):
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guild_channelUpdate.permissionOverwriteModified",
                                target=target_str,
                            )
                        )
                        if added_allow:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteAddedAllow",
                                    permissions=", ".join(added_allow),
                                )
                            )
                        if added_deny:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteAddedDeny",
                                    permissions=", ".join(added_deny),
                                )
                            )
                        if added_neutral:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteAddedNeutral",
                                    permissions=", ".join(added_neutral),
                                )
                            )
                        if removed_allow:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteRemovedAllow",
                                    permissions=", ".join(removed_allow),
                                )
                            )
                        if removed_deny:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteRemovedDeny",
                                    permissions=", ".join(removed_deny),
                                )
                            )
                        if removed_neutral:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guild_channelUpdate.permissionOverwriteRemovedNeutral",
                                    permissions=", ".join(removed_neutral),
                                )
                            )

        if (
            hasattr(after, "default_auto_archive_duration")
            and after.default_auto_archive_duration != before.default_auto_archive_duration
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.defaultAutoArchiveDuration",
                    before=before.default_auto_archive_duration,
                    after=after.default_auto_archive_duration,
                )
            )

        if (
            hasattr(after, "default_thread_auto_archive_duration")
            and after.default_thread_auto_archive_duration != before.default_thread_auto_archive_duration
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.defaultThreadAutoArchiveDuration",
                    before=before.default_thread_auto_archive_duration,
                    after=after.default_thread_auto_archive_duration,
                )
            )

        if hasattr(after, "nsfw") and after.nsfw != before.nsfw:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.nsfw",
                    before=(
                        str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.yes"))
                        if before.nsfw
                        else str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.no"))
                    ),
                    after=(
                        str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.yes"))
                        if after.nsfw
                        else str(tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.no"))
                    ),
                )
            )

        if hasattr(after, "slowmode_delay") and after.slowmode_delay != before.slowmode_delay:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guild_channelUpdate.slowmodeDelay",
                    before=before.slowmode_delay,
                    after=after.slowmode_delay,
                )
            )

        if len(description_parts) == 2:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.guild_channelUpdate.title"),
            description=description,
        )
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_update
        if not log_enable:
            return

        locale = after.locale if hasattr(after, "preferred_locale") else "en_US"
        description_parts = []

        keiner_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.none")

        if before.afk_channel != after.afk_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.afkChannel",
                    before=(before.afk_channel.mention if before.afk_channel else keiner_locale),
                    after=(after.afk_channel.mention if after.afk_channel else keiner_locale),
                )
            )

        if before.afk_timeout != after.afk_timeout:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.afkTimeout",
                    before=before.afk_timeout,
                    after=after.afk_timeout,
                )
            )

        if before.banner != after.banner:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.banner",
                    before=before.banner if before.banner else keiner_locale,
                    after=after.banner if after.banner else keiner_locale,
                )
            )

        if before.default_notifications != after.default_notifications:
            all_members_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.defaultNotificationsLocales.all_members")
            only_mentions = tanjunLocalizer.localize(locale, "logs.guildUpdate.defaultNotificationsLocales.onlyMentions")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.defaultNotifications",
                    before=(all_members_locale if before.default_notifications else only_mentions),  # type: ignore[truthy-bool, redundant-expr]
                    after=(all_members_locale if after.default_notifications else only_mentions),  # type: ignore[truthy-bool, redundant-expr]
                )
            )

        if before.description != after.description:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.description",
                    before=before.description,
                    after=after.description,
                )
            )

        if before.discovery_splash != after.discovery_splash:
            url_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.discoverySplashLocales.url")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.discoverySplash",
                    before=(
                        "[" + url_locale + "](" + before.discovery_splash.url + ")"
                        if before.discovery_splash
                        else keiner_locale
                    ),
                    after=(
                        "[" + url_locale + "](" + after.discovery_splash.url + ")" if after.discovery_splash else keiner_locale
                    ),
                )
            )

        if before.emoji_limit != after.emoji_limit:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.emojiLimit",
                    before=before.emoji_limit,
                    after=after.emoji_limit,
                )
            )

        added_emojis = [emoji for emoji in after.emojis if emoji not in before.emojis]
        removed_emojis = [emoji for emoji in before.emojis if emoji not in after.emojis]

        if added_emojis:
            added_list = "\n".join(f"- {emoji} : {emoji.name}" for emoji in added_emojis)
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildUpdate.addedEmojis", added_emojis=added_list))

        if removed_emojis:
            removed_list = "\n".join(f"- {emoji} : {emoji.name}" for emoji in removed_emojis)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.removedEmojis",
                    removed_emojis=removed_list,
                )
            )

        if before.explicit_content_filter != after.explicit_content_filter:
            disabled = tanjunLocalizer.localize(locale, "logs.guildUpdate.explicitContentFilterLocales.disabled")
            no_role = tanjunLocalizer.localize(locale, "logs.guildUpdate.explicitContentFilterLocales.no_role")
            all_members = tanjunLocalizer.localize(locale, "logs.guildUpdate.explicitContentFilterLocales.all_members")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.explicitContentFilter",
                    before=(
                        disabled
                        if before.explicit_content_filter.disabled  # type: ignore[truthy-bool, redundant-expr]
                        else (no_role if before.explicit_content_filter.no_role else all_members)
                    ),
                    after=(
                        disabled
                        if after.explicit_content_filter.disabled  # type: ignore[truthy-bool, redundant-expr]
                        else (no_role if after.explicit_content_filter.no_role else all_members)
                    ),
                )
            )

        added_features = [feature for feature in after.features if feature not in before.features]
        removed_features = [feature for feature in before.features if feature not in after.features]

        if added_features:
            added_list = "\n".join(
                f"- {tanjunLocalizer.localize(locale, 'logs.guildUpdate.featuresLocales.' + feature)}"
                for feature in added_features
            )
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildUpdate.addedFeatures", added_features=added_list)
            )

        if removed_features:
            removed_list = "\n".join(
                f"- {tanjunLocalizer.localize(locale, 'logs.guildUpdate.featuresLocales.' + feature)}"
                for feature in removed_features
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.removedFeatures",
                    removed_features=removed_list,
                )
            )

        if before.icon != after.icon:
            url_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.iconLocales.url")
            no_icon_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.iconLocales.noIcon")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.icon",
                    before=("[" + url_locale + "](" + before.icon + ")" if before.icon else no_icon_locale),  # type: ignore[operator]
                    after=("[" + url_locale + "](" + after.icon + ")" if after.icon else no_icon_locale),  # type: ignore[operator]
                )
            )

        if before.filesize_limit != after.filesize_limit:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.filesizeLimit",
                    before=before.filesize_limit,
                    after=after.filesize_limit,
                )
            )

        if before.invites_paused_until != after.invites_paused_until:
            not_paused_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.invitesPausedUntilLocales.notPaused")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.invitesPausedUntil",
                    before=(
                        "<t:" + str(utility.date_time_to_timestamp(before.invites_paused_until)) + ":R>"
                        if before.invites_paused_until
                        else not_paused_locale
                    ),
                    after=(
                        "<t:" + str(utility.date_time_to_timestamp(after.invites_paused_until)) + ":R>"
                        if after.invites_paused_until
                        else not_paused_locale
                    ),
                )
            )

        if before.max_members != after.max_members:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.maxMembers",
                    before=before.max_members if before.max_members else "0",
                    after=after.max_members if after.max_members else "0",
                )
            )

        if before.max_presences != after.max_presences:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.maxPresences",
                    before=(before.max_presences if before.max_presences else keiner_locale),
                    after=after.max_presences if after.max_presences else keiner_locale,
                )
            )

        if before.max_video_channel_users != after.max_video_channel_users:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.maxVideoChannelUsers",
                    before=(before.max_video_channel_users if before.max_video_channel_users else keiner_locale),
                    after=(after.max_video_channel_users if after.max_video_channel_users else keiner_locale),
                )
            )

        if before.name != after.name:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.name",
                    before=before.name,
                    after=after.name,
                )
            )

        if before.nsfw_level != after.nsfw_level:
            default_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.nsfwLevelLocales.default")
            explicit_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.nsfwLevelLocales.explicit")
            safe_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.nsfwLevelLocales.safe")
            age_registered_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.nsfwLevelLocales.ageRegistered")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.nsfwLevel",
                    before=(
                        default_locale
                        if before.nsfw_level.default  # type: ignore[truthy-bool, redundant-expr]
                        else (
                            explicit_locale
                            if before.nsfw_level.explicit
                            else (
                                safe_locale
                                if before.nsfw_level.safe
                                else (age_registered_locale if before.nsfw_level.age_restricted else keiner_locale)
                            )
                        )
                    ),
                    after=(
                        default_locale
                        if after.nsfw_level.default  # type: ignore[truthy-bool, redundant-expr]
                        else (
                            explicit_locale
                            if after.nsfw_level.explicit
                            else (
                                safe_locale
                                if after.nsfw_level.safe
                                else (age_registered_locale if after.nsfw_level.age_restricted else keiner_locale)
                            )
                        )
                    ),
                )
            )

        if before.owner != after.owner:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.owner",
                    before=before.owner.mention if before.owner else keiner_locale,
                    after=after.owner.mention if after.owner else keiner_locale,
                )
            )

        if before.preferred_locale != after.preferred_locale:
            before_locale = tanjunLocalizer.localize(
                locale,
                "logs.guildUpdate.preferredLocaleLocales." + str(before.preferred_locale),
            )
            after_locale = tanjunLocalizer.localize(
                locale,
                "logs.guildUpdate.preferredLocaleLocales." + str(after.preferred_locale),
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.preferredLocale",
                    before=before_locale,
                    after=after_locale,
                )
            )

        if before.premium_progress_bar_enabled != after.premium_progress_bar_enabled:
            if before.premium_progress_bar_enabled:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.guildUpdate.premiumProgressBarEnabled.activated")
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.guildUpdate.premiumProgressBarEnabled.deactivated")
                )

        if before.premium_subscriber_role != after.premium_subscriber_role:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.premiumSubscriberRole",
                    before=(before.premium_subscriber_role.mention if before.premium_subscriber_role else keiner_locale),
                    after=(after.premium_subscriber_role.mention if after.premium_subscriber_role else keiner_locale),
                )
            )

        if before.premium_subscribers != after.premium_subscribers:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.premiumSubscribers",
                    before=before.premium_subscribers,
                    after=after.premium_subscribers,
                )
            )

        if before.premium_tier != after.premium_tier:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.premiumTier",
                    before=before.premium_tier,
                    after=after.premium_tier,
                )
            )

        if before.public_updates_channel != after.public_updates_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.publicUpdatesChannel",
                    before=(before.public_updates_channel.mention if before.public_updates_channel else keiner_locale),
                    after=(after.public_updates_channel.mention if after.public_updates_channel else keiner_locale),
                )
            )

        if before.rules_channel != after.rules_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.rulesChannel",
                    before=(before.rules_channel.mention if before.rules_channel else keiner_locale),
                    after=(after.rules_channel.mention if after.rules_channel else keiner_locale),
                )
            )

        if before.safety_alerts_channel != after.safety_alerts_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.safetyAlertsChannel",
                    before=(before.safety_alerts_channel.mention if before.safety_alerts_channel else keiner_locale),
                    after=(after.safety_alerts_channel.mention if after.safety_alerts_channel else keiner_locale),
                )
            )

        if before.unavailable != after.unavailable:
            if before.unavailable:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.guildUpdate.unavailableLocales.available"))
            else:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.guildUpdate.unavailableLocales.unavailable"))

        if before.verification_level != after.verification_level:
            none_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.verificationLevelLocales.none")
            low_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.verificationLevelLocales.low")
            medium_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.verificationLevelLocales.medium")
            high_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.verificationLevelLocales.high")
            highest_locale = tanjunLocalizer.localize(locale, "logs.guildUpdate.verificationLevelLocales.highest")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.verificationLevel",
                    before=(
                        none_locale
                        if before.verification_level.none  # type: ignore[truthy-bool, redundant-expr]
                        else (
                            low_locale
                            if before.verification_level.low
                            else (
                                medium_locale
                                if before.verification_level.medium
                                else (high_locale if before.verification_level.high else highest_locale)
                            )
                        )
                    ),
                    after=(
                        none_locale
                        if after.verification_level.none  # type: ignore[truthy-bool, redundant-expr]
                        else (
                            low_locale
                            if after.verification_level.low
                            else (
                                medium_locale
                                if after.verification_level.medium
                                else (high_locale if after.verification_level.high else highest_locale)
                            )
                        )
                    ),
                )
            )

        if len(description_parts) == 0:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.guildUpdate.title"),
            description=description,
        )
        await log_event_producer(str(after.id), embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        log_enable = invite.guild and (await get_log_enable(invite.guild.id)).invite_create
        if not log_enable:
            return

        if await is_log_entity_blacklisted(invite.guild.id, str(invite.inviter.id), LogBlacklistType.USER):  # type: ignore[union-attr]
            return

        blacklisted_roles = await get_log_blacklist(invite.guild.id, LogBlacklistType.ROLE)  # type: ignore[union-attr]
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in invite.inviter.roles):  # type: ignore[union-attr]
                return

        locale = invite.guild.preferred_locale if hasattr(invite.guild, "preferred_locale") else "en_US"  # type: ignore[union-attr]
        description_parts = []

        never_locale = tanjunLocalizer.localize(locale, "logs.inviteCreate.expiresLocales.never")
        infinite_locale = tanjunLocalizer.localize(locale, "logs.inviteCreate.maxUsesLocales.infinite")

        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.inviteCreate.createdBy", created_by=invite.inviter.mention)  # type: ignore[union-attr]
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.expires",
                expires=(
                    never_locale
                    if invite.expires_at is None
                    else "<t:" + str(utility.date_time_to_timestamp(invite.expires_at)) + ":R>"
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.max_uses",
                max_uses=infinite_locale if invite.max_uses is None else invite.max_uses,
            )
        )

        if invite.channel:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.inviteCreate.channel", channel=invite.channel.mention)  # type: ignore[union-attr]
            )
        if invite.scheduled_event:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.scheduledEvent",
                    scheduled_event=invite.scheduled_event.url,
                )
            )
        if invite.target_application:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetApplication",
                    target_application=invite.target_application.name,
                )
            )

        if str(invite.target_type) != "InviteTarget.unknown":
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetTypeLocales." + str(invite.target_type),
                )
            )

        if invite.target_user:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetUser",
                    target_user=invite.target_user.mention,
                )
            )

        if invite.temporary:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.inviteCreate.temporary"))

        description_parts.append(tanjunLocalizer.localize(locale, "logs.inviteCreate.invite", invite=invite.url))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.inviteCreate.title"),
            description=description,
        )
        await log_event_producer(str(invite.guild.id), embed)  # type: ignore[union-attr]

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        log_enable = invite.guild and (await get_log_enable(invite.guild.id)).invite_delete
        if not log_enable:
            return

        if await is_log_entity_blacklisted(invite.guild.id, str(invite.inviter.id), LogBlacklistType.USER):  # type: ignore[union-attr]
            return

        blacklisted_roles = await get_log_blacklist(invite.guild.id, LogBlacklistType.ROLE)  # type: ignore[union-attr]
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in invite.inviter.roles):  # type: ignore[union-attr]
                return

        locale = invite.guild.preferred_locale if hasattr(invite.guild, "preferred_locale") else "en_US"  # type: ignore[union-attr]
        description_parts = []

        never_locale = tanjunLocalizer.localize(locale, "logs.inviteCreate.expiresLocales.never")
        infinite_locale = tanjunLocalizer.localize(locale, "logs.inviteCreate.maxUsesLocales.infinite")

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.expires",
                expires=(
                    never_locale
                    if invite.expires_at is None
                    else "<t:" + str(utility.date_time_to_timestamp(invite.expires_at)) + ":R>"
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.max_uses",
                max_uses=infinite_locale if invite.max_uses is None else invite.max_uses,
            )
        )

        if invite.channel:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.inviteCreate.channel", channel=invite.channel.mention)  # type: ignore[union-attr]
            )
        if invite.scheduled_event:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.scheduledEvent",
                    scheduled_event=invite.scheduled_event.url,
                )
            )
        if invite.target_application:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetApplication",
                    target_application=invite.target_application.name,
                )
            )

        if str(invite.target_type) != "InviteTarget.unknown":
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetTypeLocales." + str(invite.target_type),
                )
            )

        if invite.target_user:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.inviteCreate.targetUser",
                    target_user=invite.target_user.mention,
                )
            )

        if invite.temporary:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.inviteCreate.temporary"))

        description_parts.append(tanjunLocalizer.localize(locale, "logs.inviteDelete.invite", invite=invite.url))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.inviteDelete.title"),
            description=description,
        )
        await log_event_producer(str(invite.guild.id), embed)  # type: ignore[union-attr]

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        log_enable = member.guild and (await get_log_enable(member.guild.id)).member_join
        if not log_enable:
            return

        if await is_log_entity_blacklisted(member.guild.id, str(member.id), LogBlacklistType.USER):
            return

        blacklisted_roles = await get_log_blacklist(member.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in member.roles):
                return

        locale = member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.memberJoin.name", joined=member.mention))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.memberJoin.title"),
            description=description,
        )
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
            if any(str(role.id) == blacklisted_role for role in member.roles):
                return

        locale = member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.memberRemove.name", left=member.mention))
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.memberRemove.roles",
                roles=", ".join(role.mention for role in member.roles),
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.memberJoin.title"),
            description=description,
        )
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
            if any(str(role.id) == blacklisted_role for role in after.roles):
                return

        locale = after.guild.preferred_locale if hasattr(after.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.memberUpdate.name", member=after.mention))

        # Check for avatar change
        if before.display_avatar != after.display_avatar:
            default_avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
            # Upload old avatar to ImgBB
            avatar_bytes = (
                await before.display_avatar.read() if before.display_avatar else None
            )  # Read the old avatar as bytes
            avatar_upload_response = await utility.upload_image_to_imgbb(avatar_bytes, "png") if avatar_bytes else {}
            avatar_url_before = avatar_upload_response.get("data", {}).get("url", default_avatar_url)  # type: ignore[union-attr]

            # Upload new avatar to ImgBB
            new_avatar_bytes = (
                await after.display_avatar.read() if after.display_avatar else None
            )  # Read the new avatar as bytes
            new_avatar_upload_response = (
                await utility.upload_image_to_imgbb(new_avatar_bytes, "png") if new_avatar_bytes else {}
            )
            new_avatar_url = new_avatar_upload_response.get("data", {}).get("url", default_avatar_url)  # type: ignore[union-attr]

            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.userUpdate.avatar",
                    before=f"[{url_locale}]({avatar_url_before})",
                    after=f"[{url_locale}]({new_avatar_url})",
                )
            )

        # Check for banner change
        if before.banner != after.banner:
            none_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.none")
            url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
            # Upload old banner to ImgBB
            banner_bytes = await before.banner.read() if before.banner else None  # Read the old banner as bytes
            banner_upload_response = await utility.upload_image_to_imgbb(banner_bytes, "png") if banner_bytes else {}
            banner_url_before = banner_upload_response.get("data", {}).get("url", none_locale)  # type: ignore[union-attr]

            # Upload new banner to ImgBB
            if after.banner:
                new_banner_bytes = await after.banner.read()  # Read the new banner as bytes
                new_banner_upload_response = await utility.upload_image_to_imgbb(new_banner_bytes, "png")
                new_banner_url = new_banner_upload_response.get("data", {}).get("url", none_locale)  # type: ignore[union-attr]
            else:
                new_banner_url = none_locale

            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.userUpdate.banner",
                    before=f"[{url_locale}]({banner_url_before})",
                    after=f"[{url_locale}]({new_banner_url})",
                )
            )

        # Check for display name change
        if before.display_name != after.display_name:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.memberUpdate.displayName",
                    before=before.display_name,
                    after=after.display_name,
                )
            )

        # Check for role changes
        added_roles = [role.mention for role in after.roles if role not in before.roles]
        removed_roles = [role.mention for role in before.roles if role not in after.roles]

        if added_roles:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.memberUpdate.addedRoles", roles=", ".join(added_roles))
            )

        if removed_roles:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.memberUpdate.removedRoles",
                    roles=", ".join(removed_roles),
                )
            )

        if before.pending != after.pending:
            if before.pending:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.memberUpdate.pending"))
            else:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.memberUpdate.pendingRemoved"))

        if before.timed_out_until != after.timed_out_until:
            if before.timed_out_until is None:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.memberUpdate.timeout",
                        timeout=utility.date_time_to_timestamp(after.timed_out_until),  # type: ignore[arg-type]
                    )
                )
            else:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.memberUpdate.timeoutRemoved"))

        if len(description_parts) >= 2:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.memberUpdate.title"),
            description=description,
        )
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
                if any(str(role.id) == blacklisted_role for role in user.roles):
                    continue

            locale = str(guild.preferred_locale) if hasattr(guild, "preferred_locale") else "en_US"
            description_parts = []

            description_parts.append(tanjunLocalizer.localize(locale, "logs.userUpdate.name", user=before.mention))

            if before.avatar != after.avatar:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.userUpdate.avatar",
                    )
                )

            if before.banner != after.banner:
                none_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.none")
                url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
                # Upload old banner to ImgBB
                banner_bytes = await before.banner.read() if before.banner else None  # Read the old banner as bytes
                banner_upload_response = await utility.upload_image_to_imgbb(banner_bytes, "png") if banner_bytes else {}
                banner_url_before = banner_upload_response.get("data", {}).get("url", none_locale)  # type: ignore[union-attr]

                # Upload new banner to ImgBB
                if after.banner:
                    new_banner_bytes = await after.banner.read()  # Read the new banner as bytes
                    new_banner_upload_response = await utility.upload_image_to_imgbb(new_banner_bytes, "png")
                    new_banner_url = new_banner_upload_response.get("data", {}).get("url", none_locale)  # type: ignore[union-attr]
                else:
                    new_banner_url = none_locale

                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.userUpdate.banner",
                        before=f"[{url_locale}]({banner_url_before})",
                        after=f"[{url_locale}]({new_banner_url})",
                    )
                )

            if len(description_parts) == 1:
                return

            # Join all parts with newlines
            description = "\n".join(description_parts)

            embed = discord.Embed(
                color=EmbedColor.WARNING,
                title=tanjunLocalizer.localize(locale, "logs.userUpdate.title"),
                description=description,
            )
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
            if any(str(role.id) == blacklisted_role for role in user.roles):
                return

        locale = user.guild.preferred_locale if hasattr(user.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.memberBan.name", user=user.mention))

        banner = None
        async for log in user.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if log.target == user:
                banner = log.user
                break

        if banner:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.memberBan.banned_by", banner=banner.mention))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.memberBan.title"),
            description=description,
        )
        await log_event_producer(str(user.guild.id), embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        log_enable = guild and (await get_log_enable(guild.id)).member_unban
        if not log_enable:
            return

        if await is_log_entity_blacklisted(guild.id, str(user.id), LogBlacklistType.USER):
            return

        locale = str(guild.preferred_locale) if hasattr(guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.memberUnban.name", user=user.mention))

        unbanned_by = None
        async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if log.target == user:
                unbanned_by = log.user
                break

        if unbanned_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.memberUnban.unbanned_by",
                    unbanned_by=unbanned_by.mention,
                )
            )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.memberUnban.title"),
            description=description,
        )
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
            if any(str(role.id) == blacklisted_role for role in after.roles):
                return

        locale = after.guild.preferred_locale if hasattr(after.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.presenceUpdate.name", user=after.mention))

        if before.activity != after.activity:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.presenceUpdate.activity",
                    before=before.activity,
                    after=after.activity,
                )
            )

        if len(description_parts) == 1:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.presenceUpdate.title"),
            description=description,
        )
        await log_event_producer(str(after.guild.id), embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).message_edit
        if not log_enable:
            return

        if await is_log_entity_blacklisted(after.guild.id, str(after.author.id), LogBlacklistType.USER):  # type: ignore[union-attr]
            return

        if (
            after.channel is not None
            and after.guild is not None
            and await _is_channel_or_category_blacklisted(str(after.guild.id), after.channel)
        ):  # type: ignore[union-attr]
            return

        blacklisted_roles = await get_log_blacklist(after.guild.id, LogBlacklistType.ROLE)  # type: ignore[union-attr]
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in after.author.roles):  # type: ignore[union-attr]
                return

        locale = after.guild.preferred_locale if hasattr(after, "preferred_locale") else "en_US"  # type: ignore[union-attr]
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.messageEdit.name",
                user=after.author.mention,
                url=after.jump_url,
            )
        )

        if before.content != after.content:
            # Create a diff of the two message contents
            diff = difflib.ndiff(
                before.content.splitlines(keepends=True),
                after.content.splitlines(keepends=True),
            )
            diff_summary = "\n".join(diff)

            truncated_notice = tanjunLocalizer.localize(locale, "logs.messageEdit.truncatedNotice")

            if len(diff_summary) > 1500:
                diff_summary_url = await upload_to_tanjun_logs(
                    tanjunLocalizer.localize(locale, "logs.messageEdit.diff", diff=diff_summary)
                )

                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.messageEdit.tooLongNotice", url=diff_summary_url)
                )

            else:
                # Append the diff summary
                description_parts.append(tanjunLocalizer.localize(locale, "logs.messageEdit.diff", diff=diff_summary))

        if before.attachments != after.attachments:
            added_attachments = [
                f"[{attachment.filename}]({attachment.url})"
                for attachment in after.attachments
                if attachment not in before.attachments
            ]

            removed_attachments = []
            url_not_available_locale = tanjunLocalizer.localize(locale, "logs.messageEdit.url_not_available_locale")
            for attachment in before.attachments:
                if attachment not in after.attachments:
                    if attachment.content_type and attachment.content_type.startswith("image/"):
                        attachment_bytes = await attachment.read()
                        url = await upload_image_to_imgbb(attachment_bytes, attachment.filename.split(".")[-1])
                        if url:
                            url = url["data"]["display_url"]
                    else:
                        url = None
                    removed_attachments.append(f"[{attachment.filename}]({url if url else url_not_available_locale})")

            if added_attachments:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.messageEdit.addedAttachments",
                        attachments=", ".join(added_attachments),
                    )
                )

            if removed_attachments:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.messageEdit.removedAttachments",
                        attachments=", ".join(removed_attachments),
                    )
                )

        # embedsChanged = False
        # if len(before.embeds) == len(after.embeds):  # Only compare if lengths match
        #     for i in range(len(before.embeds)):
        #         # Compare only the relevant fields instead of the entire dict
        #         before_dict = before.embeds[i].to_dict()
        #         after_dict = after.embeds[i].to_dict()

        #         # Compare only fields that matter for content changes
        #         relevant_fields = [
        #             "title",
        #             "description",
        #             "fields",
        #             "image",
        #             "thumbnail",
        #             "author",
        #             "footer",
        #         ]
        #         for field in relevant_fields:
        #             if before_dict.get(field) != after_dict.get(field):
        #                 embedsChanged = True
        #                 break

        #         if embedsChanged:
        #             break
        # else:
        #     embedsChanged = True  # Different number of embeds means they changed

        # if embedsChanged:
        #     description_parts.append(
        #         tanjunLocalizer.localize(
        #             locale,
        #             "logs.messageEdit.embeds",
        #             before=before.embeds,
        #             after=after.embeds,
        #         )
        #     )

        if len(description_parts) == 1:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        # Ensure the description does not exceed 4000 characters
        if len(description) > 4000:
            description = description[:3000] + f" {truncated_notice}"  # type: ignore[possibly-undefined]

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.messageEdit.title"),
            description=description,
        )
        await log_event_producer(str(after.guild.id), embed)  # type: ignore[union-attr]

        # if embedsChanged:
        #     for i in range(len(before.embeds)):
        #         beforeEmbed = before.embeds[i]
        #         afterEmbed = after.embeds[i]
        #         if beforeEmbed.to_dict() != afterEmbed.to_dict():
        #             embeds[str(after.guild.id)].append(beforeEmbed)
        #             embeds[str(after.guild.id)].append(afterEmbed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        log_enable = message.guild and (await get_log_enable(message.guild.id)).message_delete
        if not log_enable:
            return

        if await is_log_entity_blacklisted(message.guild.id, str(message.author.id), LogBlacklistType.USER):  # type: ignore[union-attr]
            return

        if (
            message.channel is not None
            and message.guild is not None
            and await _is_channel_or_category_blacklisted(str(message.guild.id), message.channel)
        ):  # type: ignore[union-attr]
            return

        blacklisted_roles = await get_log_blacklist(message.guild.id, LogBlacklistType.ROLE)  # type: ignore[union-attr]
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in message.author.roles):  # type: ignore[union-attr]
                return

        locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"  # type: ignore[union-attr]
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.messageDelete.name",
                user=message.author.mention,
                channel=message.channel.mention,  # type: ignore[union-attr]
            )
        )
        deleted_by = None

        send_log = False

        async for log in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):  # type: ignore[union-attr]
            if log.target.id == message.author.id and log.extra.channel.id == message.channel.id:  # type: ignore[union-attr]
                deleted_by = log.user
                break
        if deleted_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.messageDelete.deletedBy",
                    deleted_by=deleted_by.mention,
                )
            )

        if message.content:
            send_log = True
            description_parts.append(tanjunLocalizer.localize(locale, "logs.messageDelete.content", content=message.content))

        if message.attachments:
            send_log = True
            attachment_parts = []
            url_not_available_locale = tanjunLocalizer.localize(locale, "logs.messageDelete.url_not_available_locale")

            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image/"):
                    try:
                        attachment_bytes = await attachment.read()
                        url = await upload_image_to_imgbb(attachment_bytes, attachment.filename.split(".")[-1])
                        if url:
                            url = url["data"]["display_url"]
                    except Exception:
                        url = None
                else:
                    url = None

                attachment_parts.append(f"[{attachment.filename}]({url if url else url_not_available_locale})")

            attachments = "\n- ".join(attachment_parts)
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.messageDelete.attachments", attachments=attachments)
            )

        if message.embeds:
            send_log = True
            description_parts.append(tanjunLocalizer.localize(locale, "logs.messageDelete.embeds"))

        if not send_log:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.messageDelete.title"),
            description=description,
        )
        await log_event_producer(str(message.guild.id), embed)  # type: ignore[union-attr]
        for emb in message.embeds:
            await log_event_producer(str(message.guild.id), emb)  # type: ignore[union-attr]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        log_enable = reaction.guild and (await get_log_enable(reaction.guild.id)).reaction_add
        if not log_enable:
            return

        if await is_log_entity_blacklisted(reaction.guild.id, str(user.id), LogBlacklistType.USER):
            return

        if (
            reaction.message.channel is not None
            and reaction.guild is not None
            and await _is_channel_or_category_blacklisted(str(reaction.guild.id), reaction.message.channel)
        ):
            return

        blacklisted_roles = await get_log_blacklist(reaction.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in user.roles):
                return

        locale = reaction.guild.preferred_locale if hasattr(reaction.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.reactionAdd.name",
                user=user.mention,
                emoji=reaction.emoji,
                message=reaction.message.jump_url,
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.reactionAdd.title"),
            description=description,
        )
        await log_event_producer(str(reaction.guild.id), embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User) -> None:
        log_enable = reaction.guild and (await get_log_enable(reaction.guild.id)).reaction_remove
        if not log_enable:
            return

        if await is_log_entity_blacklisted(reaction.guild.id, str(user.id), LogBlacklistType.USER):
            return

        if (
            reaction.message.channel is not None
            and reaction.guild is not None
            and await _is_channel_or_category_blacklisted(str(reaction.guild.id), reaction.message.channel)
        ):
            return

        blacklisted_roles = await get_log_blacklist(reaction.guild.id, LogBlacklistType.ROLE)
        for blacklisted_role in blacklisted_roles:
            if any(str(role.id) == blacklisted_role for role in user.roles):
                return

        locale = reaction.guild.preferred_locale if hasattr(reaction.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.reactionRemove.name",
                user=user.mention,
                emoji=reaction.emoji,
                message=reaction.message.jump_url,
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.reactionRemove.title"),
            description=description,
        )
        await log_event_producer(str(reaction.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        log_enable = role.guild and (await get_log_enable(role.guild.id)).guild_role_create
        if not log_enable:
            return

        locale = role.guild.preferred_locale if hasattr(role.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.name", role=role.mention))

        created_by = None
        async for log in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_create):
            if log.target.id == role.id:  # type: ignore[union-attr]
                created_by = log.user
                break
        if created_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleCreate.createdBy",
                    created_by=created_by.mention,
                )
            )

        if role.color:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.color", color=role.color))

        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=f"[{url_locale}]({role.display_icon.url})",
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=role.display_icon,
                    )
                )

        if role.hoist:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.hoist"))

        if role.managed:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.managed"))

        if role.mentionable:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.mentionable"))

        if role.permissions:
            permissions_list = [perm for perm, value in role.permissions if value]  # Get only the permissions that are True
            if permissions_list:
                formatted_permissions = ", ".join(
                    [f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`" for perm in permissions_list]
                )
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.permissions",
                        permissions=formatted_permissions,
                    )
                )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleCreate.title"),
            description=description,
        )
        await log_event_producer(str(role.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        log_enable = role.guild and (await get_log_enable(role.guild.id)).guild_role_delete
        if not log_enable:
            return

        locale = role.guild.preferred_locale if hasattr(role.guild, "preferred_locale") else "en_US"
        description_parts = []

        description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleDelete.name", role=role.name))

        deleted_by = None
        async for log in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_delete):
            if log.target.id == role.id:  # type: ignore[union-attr]
                deleted_by = log.user
                break
        if deleted_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleDelete.deletedBy",
                    deleted_by=deleted_by.mention,
                )
            )

        if role.color:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.color", color=role.color))

        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=f"[{url_locale}]({role.display_icon.url})",
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=role.display_icon,
                    )
                )

        if role.hoist:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.hoist"))

        if role.managed:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.managed"))

        if role.mentionable:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleCreate.mentionable"))

        # Format permissions nicely
        if role.permissions:
            permissions_list = [perm for perm, value in role.permissions if value]  # Get only the permissions that are True
            if permissions_list:
                formatted_permissions = ", ".join(
                    [f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`" for perm in permissions_list]
                )
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleDelete.permissions",
                        permissions=formatted_permissions,
                    )
                )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleDelete.title"),
            description=description,
        )
        await log_event_producer(str(role.guild.id), embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        log_enable = after.guild and (await get_log_enable(after.guild.id)).guild_role_update
        if not log_enable:
            return

        locale = after.guild.preferred_locale if hasattr(after.guild, "preferred_locale") else "en_US"
        description_parts = []

        # Check for changes in role attributes
        if before.name != after.name:
            description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.name", role=after.name))

        updated_by = None
        async for log in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
            if log.target.id == after.id:  # type: ignore[union-attr]
                updated_by = log.user
                break
        if updated_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.updatedBy",
                    updated_by=updated_by.mention,
                )
            )

        if before.color != after.color:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.color",
                    before=before.color,
                    after=after.color,
                )
            )

        if before.hoist != after.hoist:
            if after.hoist:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.hoistNow", role=after.name))
            else:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.hoistNoLonger", role=after.name)
                )

        if before.mentionable != after.mentionable:
            if after.mentionable:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.mentionableNow", role=after.name)
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleUpdate.mentionableNoLonger",
                        role=after.name,
                    )
                )

        if before.managed != after.managed:
            if after.managed:
                description_parts.append(tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.managedNow", role=after.name))
            else:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.managedNoLonger", role=after.name)
                )

        before_perms = {perm for perm, value in before.permissions if value}
        after_perms = {perm for perm, value in after.permissions if value}

        added_perms = after_perms - before_perms
        removed_perms = before_perms - after_perms

        if added_perms:
            added_perms_list = ", ".join(
                [f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`" for perm in added_perms]
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.addedPermissions",
                    permissions=added_perms_list,
                )
            )

        if removed_perms:
            removed_perms_list = ", ".join(
                [f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`" for perm in removed_perms]
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.removedPermissions",
                    permissions=removed_perms_list,
                )
            )

        if before.display_icon != after.display_icon:
            url_locale = tanjunLocalizer.localize(locale, "logs.userUpdate.guildAvatarLocales.url")
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.displayIcon",
                    before=(f"[{url_locale}]({before.display_icon.url})" if before.display_icon else "None"),  # type: ignore[union-attr]
                    after=(f"[{url_locale}]({after.display_icon.url})" if after.display_icon else "None"),  # type: ignore[union-attr]
                )
            )

        if before.icon != after.icon:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.icon",
                    before=before.icon,
                    after=after.icon,
                )
            )

        if len(description_parts) == 1:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.title"),
            description=description,
        )
        await log_event_producer(str(after.guild.id), embed)

    async def log_consumer_task(self) -> None:
        """Run the log event consumer as a background task."""
        try:
            await log_event_consumer(self.bot)
        finally:
            self._log_consumer_task = None

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logcmds = LogsCommands(
            name=app_commands.locale_str("logs_name"),
            description=app_commands.locale_str("logs_description"),
        )
        channel_blacklist = ChannelBlacklistCommands(
            name=app_commands.locale_str("logs_blacklist_name"),
            description=app_commands.locale_str("logs_blacklist_description"),
        )
        user_blacklist = UserBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistu_name"),
            description=app_commands.locale_str("logs_blacklistu_description"),
        )
        role_blacklist = RoleBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistr_name"),
            description=app_commands.locale_str("logs_blacklistr_description"),
        )
        voice_blacklist = VoiceBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistv_name"),
            description=app_commands.locale_str("logs_blacklistv_description"),
        )
        category_blacklist = CategoryBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistcat_name"),
            description=app_commands.locale_str("logs_blacklistcat_description"),
        )
        logcmds.add_command(channel_blacklist)
        logcmds.add_command(user_blacklist)
        logcmds.add_command(role_blacklist)
        logcmds.add_command(voice_blacklist)
        logcmds.add_command(category_blacklist)
        self.bot.tree.add_command(logcmds)

        # Only create the log consumer task if it doesn't exist or is done
        if self._log_consumer_task is None or self._log_consumer_task.done():
            self._log_consumer_task = self.bot.loop.create_task(self.log_consumer_task())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LogsCog(bot))
