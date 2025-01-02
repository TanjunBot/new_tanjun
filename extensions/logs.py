# Unused imports:
# from typing import List
# import os
import discord
from discord.ext import commands
from discord import app_commands
import utility
from api import (
    get_log_enable,
    get_log_channel,
    is_log_channel_blacklisted,
    is_log_user_blacklisted,
    get_log_role_blacklist,
)
from localizer import tanjunLocalizer
import difflib
from utility import upload_to_tanjun_logs, upload_image_to_imgbb

from commands.logs.set_log_channel import set_log_channel
from commands.logs.remove_log_channel import remove_log_channel
from commands.logs.configure_logs import configure_logs

from commands.logs.blacklist_channel.blacklist_channel import blacklist_channel
from commands.logs.blacklist_channel.blacklist_remove_channel import (
    blacklist_remove_channel,
)
from commands.logs.blacklist_channel.blacklist_list_channel import (
    blacklist_list_channel,
)

from commands.logs.blacklist_user.blacklist_user import blacklist_user
from commands.logs.blacklist_user.blacklist_remove_user import blacklist_remove_user
from commands.logs.blacklist_role.blacklist_role import blacklist_role
from commands.logs.blacklist_role.blacklist_remove_role import blacklist_remove_role
from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user
from commands.logs.blacklist_role.blacklist_list_role import blacklist_list_role

embeds = {}


class EmbedColors:
    green = 0x4BB543
    yellow = 0xFFBF00
    red = 0xFF0000


async def sendLogEmbeds(bot):
    global embeds
    for guildId, ems in embeds.items():
        try:
            print("Sending log embeds for guild", guildId)
            destination = await get_log_channel(guildId)
            print("Destination: ", destination)
            if destination is None:
                continue
            destinationChannel = bot.get_channel(int(destination))
            print("Destination Channel: ", destinationChannel)
            if destinationChannel is None:
                continue
            for i in range(0, len(ems), 10):
                chunk = ems[i: i + 10]
                print("Sending chunk of embeds to destination channel")
                await destinationChannel.send(embeds=chunk)
            embeds[guildId] = []
            print("Successfully sent log embeds for guild", guildId)
        except Exception as e:
            print("Error sending log embeds: ", e)

    embeds = {}


class ChannelBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_add_name"),
        description=app_commands.locale_str("logs_blacklistc_add_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "logs_blacklistc_add_params_channel_description"
        )
    )
    async def add_blacklist_channel_cmd(
        self, ctx: discord.Interaction, channel: discord.TextChannel = None
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel

        await blacklist_channel(commandInfo=commandInfo, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_remove_name"),
        description=app_commands.locale_str("logs_blacklistc_remove_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "logs_blacklistc_remove_params_channel_description"
        )
    )
    async def remove_blacklist_channel_cmd(
        self, ctx: discord.Interaction, channel: discord.TextChannel = None
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel

        await blacklist_remove_channel(commandInfo=commandInfo, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistc_show_name"),
        description=app_commands.locale_str("logs_blacklistc_show_description"),
    )
    async def show_blacklist_channel_cmd(self, ctx: discord.Interaction):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await blacklist_list_channel(commandInfo=commandInfo)


class UserBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_add_name"),
        description=app_commands.locale_str("logs_blacklistu_add_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("logs_blacklistu_add_params_user_description")
    )
    async def add_blacklist_user_cmd(
        self, ctx: discord.Interaction, user: discord.Member
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_user(commandInfo=commandInfo, user=user)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_remove_name"),
        description=app_commands.locale_str("logs_blacklistu_remove_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("logs_blacklistu_remove_params_user_description")
    )
    async def remove_blacklist_user_cmd(
        self, ctx: discord.Interaction, user: discord.Member
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_remove_user(commandInfo=commandInfo, user=user)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistu_show_name"),
        description=app_commands.locale_str("logs_blacklistu_show_description"),
    )
    async def show_blacklist_user_cmd(self, ctx: discord.Interaction):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_user(commandInfo=commandInfo)


class RoleBlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_add_name"),
        description=app_commands.locale_str("logs_blacklistr_add_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("logs_blacklistr_add_params_role_description")
    )
    async def add_blacklist_role_cmd(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_role(commandInfo=commandInfo, role=role)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_remove_name"),
        description=app_commands.locale_str("logs_blacklistr_remove_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("logs_blacklistr_remove_params_role_description")
    )
    async def remove_blacklist_role_cmd(
        self, ctx: discord.Interaction, role: discord.Role
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_remove_role(commandInfo=commandInfo, role=role)

    @app_commands.command(
        name=app_commands.locale_str("logs_blacklistr_show_name"),
        description=app_commands.locale_str("logs_blacklistr_show_description"),
    )
    async def show_blacklist_role_cmd(self, ctx: discord.Interaction):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )
        await blacklist_list_role(commandInfo=commandInfo)


class LogsCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("logs_set_name"),
        description=app_commands.locale_str("logs_set_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("logs_set_params_channel_description")
    )
    async def set_log_channel_cmd(
        self, ctx: discord.Interaction, channel: discord.TextChannel = None
    ):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if channel is None:
            channel = ctx.channel

        await set_log_channel(commandInfo=commandInfo, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("logs_remove_name"),
        description=app_commands.locale_str("logs_remove_description"),
    )
    async def remove_log_channel_cmd(self, ctx: discord.Interaction):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await remove_log_channel(commandInfo=commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("logs_configure_name"),
        description=app_commands.locale_str("logs_configure_description"),
    )
    async def configure_logs_cmd(self, ctx: discord.Interaction):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await configure_logs(commandInfo=commandInfo)


class LogsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_automod_rule_create(self, rule: discord.AutoModRule):
        logEnable = rule.guild and (await get_log_enable(rule.guild.id))[1]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(rule.guild.id, str(rule.channel_id)):
            return

        locale = (
            rule.guild.preferred_locale
            if hasattr(rule.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        # Basic info
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.created_by",
                creator=rule.creator.mention,
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.automodRuleCreate.name", name=rule.name
            )
        )

        # Trigger information
        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger")
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(
                    tanjunLocalizer.localize(
                        locale, "logs.automodRuleCreate." + str(rule.trigger.type)
                    )
                ),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(
                f"- {keyword}" for keyword in rule.trigger.keyword_filter
            )
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
                sexualContentFilter=(
                    "✅" if rule.trigger.presets.sexual_content else "❌"
                ),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.allow_list", allow_list=allows
                )
            )

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
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.mentionSpamProtection"
                )
            )

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
            channels = "\n".join(
                f"- {excluded.mention}" for excluded in rule.exempt_channels
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions")
            )

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale, "logs.automodRuleCreate.block_message"
                        )
                    )

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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleCreate.title"),
            description=description,
        )
        if not str(rule.guild.id) in embeds:
            embeds[str(rule.guild.id)] = []
        embeds[str(rule.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_automod_rule_update(self, rule: discord.AutoModRule):
        logEnable = rule.guild and (await get_log_enable(rule.guild.id))[2]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(rule.guild.id, str(rule.channel_id)):
            return

        locale = (
            rule.guild.preferred_locale
            if hasattr(rule.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        updater = None

        async for entry in rule.guild.audit_logs(
            action=discord.AuditLogAction.automod_rule_update
        ):
            updater = entry.user.mention
            break

        # Basic info
        if updater:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleUpdate.updated_by", updater=updater
                )
            )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.automodRuleCreate.name", name=rule.name
            )
        )

        # Trigger information
        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger")
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(
                    tanjunLocalizer.localize(
                        locale, "logs.automodRuleCreate." + str(rule.trigger.type)
                    )
                ),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(
                f"- {keyword}" for keyword in rule.trigger.keyword_filter
            )
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
                sexualContentFilter=(
                    "✅" if rule.trigger.presets.sexual_content else "❌"
                ),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.allow_list", allow_list=allows
                )
            )

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
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.mentionSpamProtection"
                )
            )

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
            channels = "\n".join(
                f"- {excluded.mention}" for excluded in rule.exempt_channels
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions")
            )

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale, "logs.automodRuleCreate.block_message"
                        )
                    )

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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleUpdate.title"),
            description=description,
        )
        embed.set_footer(
            text=tanjunLocalizer.localize(locale, "logs.automodRuleUpdate.footer")
        )
        if not str(rule.guild.id) in embeds:
            embeds[str(rule.guild.id)] = []
        embeds[str(rule.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_automod_rule_delete(self, rule: discord.AutoModRule):
        logEnable = rule.guild and (await get_log_enable(rule.guild.id))[3]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(rule.guild.id, str(rule.channel_id)):
            return

        locale = (
            rule.guild.preferred_locale
            if hasattr(rule.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        updater = None

        async for entry in rule.guild.audit_logs(
            action=discord.AuditLogAction.automod_rule_delete
        ):
            updater = entry.user.mention
            break

        # Basic info
        if updater:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleDelete.deleted_by", updater=updater
                )
            )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.enabled",
                enabled=("✅" if rule.enabled else "❌"),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.automodRuleCreate.name", name=rule.name
            )
        )

        # Trigger information
        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.automodRuleCreate.trigger")
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodRuleCreate.triggerType",
                triggerType=str(
                    tanjunLocalizer.localize(
                        locale, "logs.automodRuleCreate." + str(rule.trigger.type)
                    )
                ),
            )
        )

        # Keyword filters
        if rule.trigger.keyword_filter:
            filters = "\n".join(
                f"- {keyword}" for keyword in rule.trigger.keyword_filter
            )
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
                sexualContentFilter=(
                    "✅" if rule.trigger.presets.sexual_content else "❌"
                ),
                slurFilter="✅" if rule.trigger.presets.slurs else "❌",
            )
        )

        # Allow list
        if rule.trigger.allow_list:
            allows = "\n".join(f"- {allow}" for allow in rule.trigger.allow_list)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.allow_list", allow_list=allows
                )
            )

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
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.automodRuleCreate.mentionSpamProtection"
                )
            )

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
            channels = "\n".join(
                f"- {excluded.mention}" for excluded in rule.exempt_channels
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.excluded_channels",
                    excluded_channels=channels or "-",
                )
            )

        # Actions
        if len(rule.actions) > 0:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.automodRuleCreate.actions")
            )

            for r in rule.actions:
                if r.type == discord.AutoModRuleActionType.block_message:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale, "logs.automodRuleCreate.block_message"
                        )
                    )

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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
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
                                    "logs.automodRuleCreate.timeout_duration."
                                    + str(r.duration),
                                )
                            ),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleDelete.title"),
            description=description,
        )
        if not str(rule.guild.id) in embeds:
            embeds[str(rule.guild.id)] = []
        embeds[str(rule.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction):
        logEnable = execution.guild and (await get_log_enable(execution.guild.id))[4]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(
            execution.guild.id, str(execution.channel.id)
        ):
            return

        locale = (
            execution.guild.preferred_locale
            if hasattr(execution.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.automodAction.actionWasTaken",
                user=execution.member.mention,
                channel=execution.channel.mention,
            )
        )
        # Actions
        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.automodAction.action")
        )

        if execution.action.type == discord.AutoModRuleActionType.block_message:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.automodRuleCreate.block_message")
            )

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
                            "logs.automodRuleCreate.timeout_duration."
                            + str(execution.action.duration),
                        )
                    ),
                )
            )

        elif (
            execution.action.type
            == discord.AutoModRuleActionType.block_member_interactions
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.automodRuleCreate.block_member_interaction",
                    duration=str(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.automodRuleCreate.timeout_duration."
                            + str(execution.action.duration),
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
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.automodRuleDelete.title"),
            description=description,
        )
        if not str(execution.guild.id) in embeds:
            embeds[str(execution.guild.id)] = []
        embeds[str(execution.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        logEnable = channel.guild and (await get_log_enable(channel.guild.id))[5]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(channel.guild.id, str(channel.id)):
            return

        locale = (
            channel.guild.preferred_locale
            if hasattr(channel.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        deleter = None
        async for entry in channel.guild.audit_logs(
            action=discord.AuditLogAction.channel_delete
        ):
            deleter = entry.user.mention
            break

        if deleter:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelDelete.deleted_by", deleter=deleter
                )
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.guildChannelDelete.name", channel=channel.name
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guildChannelDelete.type",
                type=str(
                    tanjunLocalizer.localize(
                        locale, "logs.guildChannelDelete.types." + str(channel.type)
                    )
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guildChannelDelete.created_at",
                created_at=utility.date_time_to_timestamp(channel.created_at),
            )
        )
        if channel.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelDelete.category",
                    category=channel.category,
                )
            )

        if channel.topic:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelDelete.topic", topic=channel.topic
                )
            )

        if len(channel.overwrites.keys()) > 0:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelDelete.permissionOverwrites"
                )
            )
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    localPerm = tanjunLocalizer.localize(
                        locale, "logs.permissions." + perm
                    )
                    if value is True:
                        allowed.append(f"`{localPerm}`")
                    elif value is False:
                        denied.append(f"`{localPerm}`")

                target_str = (
                    target.mention if hasattr(target, "mention") else target.name
                )
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildChannelDelete.permissionOverwriteTarget",
                        target=target_str,
                    )
                )
                if allowed:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guildChannelDelete.permissionOverwriteAllowed",
                            permissions=", ".join(allowed),
                        )
                    )
                if denied:
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guildChannelDelete.permissionOverwriteDenied",
                            permissions=", ".join(denied),
                        )
                    )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.guildChannelDelete.title"),
            description=description,
        )
        if not str(channel.guild.id) in embeds:
            embeds[str(channel.guild.id)] = []
        embeds[str(channel.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        logEnable = channel.guild and (await get_log_enable(channel.guild.id))[6]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(channel.guild.id, str(channel.id)):
            return

        locale = (
            channel.guild.preferred_locale
            if hasattr(channel.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []
        creator = None
        async for entry in channel.guild.audit_logs(
            action=discord.AuditLogAction.channel_create
        ):
            creator = entry.user.mention
            break

        if creator:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelCreate.created_by", creator=creator
                )
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.guildChannelCreate.name", name=channel.name
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guildChannelCreate.type",
                type=str(
                    tanjunLocalizer.localize(
                        locale, "logs.guildChannelCreate.types." + str(channel.type)
                    )
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.guildChannelCreate.created_at",
                created_at=utility.date_time_to_timestamp(channel.created_at),
            )
        )
        if channel.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelCreate.category",
                    category=channel.category,
                )
            )

        if channel.topic:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelCreate.topic", topic=channel.topic
                )
            )

        if len(channel.overwrites.keys()) > 0:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelCreate.permissionOverwrites"
                )
            )
            for target, overwrite in channel.overwrites.items():
                allowed = []
                denied = []
                for perm, value in overwrite:
                    localPerm = tanjunLocalizer.localize(
                        locale, "logs.permissions." + perm
                    )
                    if value is True:
                        allowed.append(f"`{localPerm}`")
                    elif value is False:
                        denied.append(f"`{localPerm}`")

                target_str = (
                    target.mention if hasattr(target, "mention") else target.name
                )
                description_parts.append(f"### {target_str}")
                if allowed:
                    description_parts.append("✅ " + ", ".join(allowed))
                if denied:
                    description_parts.append("❌ " + ", ".join(denied))

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.guildChannelCreate.title"),
            description=description,
        )
        if not str(channel.guild.id) in embeds:
            embeds[str(channel.guild.id)] = []
        embeds[str(channel.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel
    ):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[7]
        if not logEnable:
            return

        if await is_log_channel_blacklisted(after.guild.id, str(after.id)):
            return

        locale = (
            after.guild.preferred_locale
            if hasattr(after.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        updater = None
        async for entry in after.guild.audit_logs(
            action=discord.AuditLogAction.channel_update
        ):
            updater = entry.user.mention
            break

        if updater:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildChannelUpdate.updated_by", updater=updater
                )
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.guildChannelUpdate.mention", mention=before.mention
            )
        )

        if before.name != after.name:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.name",
                    before=before.name,
                    after=after.name,
                )
            )

        if hasattr(before, "type") and before.type != after.type:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.type",
                    before=str(
                        tanjunLocalizer.localize(
                            locale, "logs.guildChannelUpdate.types." + str(before.type)
                        )
                    ),
                    after=str(
                        tanjunLocalizer.localize(
                            locale, "logs.guildChannelUpdate.types." + str(after.type)
                        )
                    ),
                )
            )

        if hasattr(before, "category") and before.category != after.category:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.category",
                    before=before.category,
                    after=after.category,
                )
            )

        if hasattr(before, "topic") and before.topic != after.topic:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.topic",
                    before=before.topic,
                    after=after.topic,
                )
            )

        if before.overwrites != after.overwrites:
            # Track removed targets
            for target in before.overwrites:
                if target not in after.overwrites:
                    target_str = (
                        target.mention if hasattr(target, "mention") else target.name
                    )
                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guildChannelUpdate.permissionOverwriteRemoved",
                            target=target_str,
                        )
                    )

            # Track added/modified targets
            for target, new_overwrite in after.overwrites.items():
                old_overwrite = before.overwrites.get(target, None)
                target_str = (
                    target.mention if hasattr(target, "mention") else target.name
                )

                if old_overwrite is None:
                    # New target - show all permissions
                    allowed = []
                    denied = []
                    neutral = []
                    for perm, value in new_overwrite:
                        localPerm = tanjunLocalizer.localize(
                            locale, "logs.permissions." + perm
                        )
                        if value is True:
                            allowed.append(f"`{localPerm}`")
                        elif value is False:
                            denied.append(f"`{localPerm}`")
                        else:
                            neutral.append(f"`{localPerm}`")

                    description_parts.append(
                        tanjunLocalizer.localize(
                            locale,
                            "logs.guildChannelUpdate.permissionOverwriteNew",
                            target=target_str,
                        )
                    )
                    if allowed:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guildChannelUpdate.permissionOverwriteAllowed",
                                permissions=", ".join(allowed),
                            )
                        )
                    if denied:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guildChannelUpdate.permissionOverwriteDenied",
                                permissions=", ".join(denied),
                            )
                        )
                    if neutral:
                        description_parts.append(
                            tanjunLocalizer.localize(
                                locale,
                                "logs.guildChannelUpdate.permissionOverwriteNeutral",
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
                            localPerm = tanjunLocalizer.localize(
                                locale, "logs.permissions." + perm
                            )
                            if new_value is True:
                                added_allow.append(f"`{localPerm}`")
                            elif new_value is False:
                                added_deny.append(f"`{localPerm}`")
                            elif new_value is None:
                                added_neutral.append(f"`{localPerm}`")

                            if old_value is True:
                                removed_allow.append(f"`{localPerm}`")
                            elif old_value is False:
                                removed_deny.append(f"`{localPerm}`")
                            elif old_value is None:
                                removed_neutral.append(f"`{localPerm}`")

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
                                "logs.guildChannelUpdate.permissionOverwriteModified",
                                target=target_str,
                            )
                        )
                        if added_allow:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteAddedAllow",
                                    permissions=", ".join(added_allow),
                                )
                            )
                        if added_deny:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteAddedDeny",
                                    permissions=", ".join(added_deny),
                                )
                            )
                        if added_neutral:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteAddedNeutral",
                                    permissions=", ".join(added_neutral),
                                )
                            )
                        if removed_allow:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteRemovedAllow",
                                    permissions=", ".join(removed_allow),
                                )
                            )
                        if removed_deny:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteRemovedDeny",
                                    permissions=", ".join(removed_deny),
                                )
                            )
                        if removed_neutral:
                            description_parts.append(
                                tanjunLocalizer.localize(
                                    locale,
                                    "logs.guildChannelUpdate.permissionOverwriteRemovedNeutral",
                                    permissions=", ".join(removed_neutral),
                                )
                            )

        if (
            hasattr(after, "default_auto_archive_duration")
            and after.default_auto_archive_duration
            != before.default_auto_archive_duration
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.defaultAutoArchiveDuration",
                    before=before.default_auto_archive_duration,
                    after=after.default_auto_archive_duration,
                )
            )

        if (
            hasattr(after, "default_thread_auto_archive_duration")
            and after.default_thread_auto_archive_duration
            != before.default_thread_auto_archive_duration
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.defaultThreadAutoArchiveDuration",
                    before=before.default_thread_auto_archive_duration,
                    after=after.default_thread_auto_archive_duration,
                )
            )

        if hasattr(after, "nsfw") and after.nsfw != before.nsfw:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.nsfw",
                    before=(
                        str(
                            tanjunLocalizer.localize(
                                locale, "logs.guildChannelUpdate.yes"
                            )
                        )
                        if before.nsfw
                        else str(
                            tanjunLocalizer.localize(
                                locale, "logs.guildChannelUpdate.no"
                            )
                        )
                    ),
                    after=(
                        str(
                            tanjunLocalizer.localize(
                                locale, "logs.guildChannelUpdate.yes"
                            )
                        )
                        if after.nsfw
                        else str(
                            tanjunLocalizer.localize(
                                locale, "logs.guildChannelUpdate.no"
                            )
                        )
                    ),
                )
            )

        if (
            hasattr(after, "slowmode_delay")
            and after.slowmode_delay != before.slowmode_delay
        ):
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildChannelUpdate.slowmodeDelay",
                    before=before.slowmode_delay,
                    after=after.slowmode_delay,
                )
            )

        if len(description_parts) == 2:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.guildChannelUpdate.title"),
            description=description,
        )
        if not str(after.guild.id) in embeds:
            embeds[str(after.guild.id)] = []
        embeds[str(after.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[8]
        if not logEnable:
            return

        locale = after.locale if hasattr(after, "preferred_locale") else "en_US"
        description_parts = []

        keinerLocale = tanjunLocalizer.localize(locale, "logs.guildUpdate.none")

        if before.afk_channel != after.afk_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.afkChannel",
                    before=(
                        before.afk_channel.mention
                        if before.afk_channel
                        else keinerLocale
                    ),
                    after=(
                        after.afk_channel.mention if after.afk_channel else keinerLocale
                    ),
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
                    before=before.banner if before.banner else keinerLocale,
                    after=after.banner if after.banner else keinerLocale,
                )
            )

        if before.default_notifications != after.default_notifications:
            allMembersLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.defaultNotificationsLocales.allMembers"
            )
            only_mentions = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.defaultNotificationsLocales.onlyMentions"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.defaultNotifications",
                    before=(
                        allMembersLocale
                        if before.default_notifications
                        else only_mentions
                    ),
                    after=(
                        allMembersLocale
                        if after.default_notifications
                        else only_mentions
                    ),
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
            urlLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.discoverySplashLocales.url"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.discoverySplash",
                    before=(
                        "[" + urlLocale + "](" + before.discovery_splash.url + ")"
                        if before.discovery_splash
                        else keinerLocale
                    ),
                    after=(
                        "[" + urlLocale + "](" + after.discovery_splash.url + ")"
                        if after.discovery_splash
                        else keinerLocale
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
            added_list = "\n".join(
                f"- {emoji} : {emoji.name}" for emoji in added_emojis
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildUpdate.addedEmojis", added_emojis=added_list
                )
            )

        if removed_emojis:
            removed_list = "\n".join(
                f"- {emoji} : {emoji.name}" for emoji in removed_emojis
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.removedEmojis",
                    removed_emojis=removed_list,
                )
            )

        if before.explicit_content_filter != after.explicit_content_filter:
            disabled = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.explicitContentFilterLocales.disabled"
            )
            noRole = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.explicitContentFilterLocales.noRole"
            )
            allMembers = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.explicitContentFilterLocales.allMembers"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.explicitContentFilter",
                    before=(
                        disabled
                        if before.explicit_content_filter.disabled
                        else (
                            noRole
                            if before.explicit_content_filter.no_role
                            else allMembers
                        )
                    ),
                    after=(
                        disabled
                        if after.explicit_content_filter.disabled
                        else (
                            noRole
                            if after.explicit_content_filter.no_role
                            else allMembers
                        )
                    ),
                )
            )

        added_features = [
            feature for feature in after.features if feature not in before.features
        ]
        removed_features = [
            feature for feature in before.features if feature not in after.features
        ]

        if added_features:
            added_list = "\n".join(
                f"- {tanjunLocalizer.localize(locale, 'logs.guildUpdate.featuresLocales.' + feature)}"
                for feature in added_features
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildUpdate.addedFeatures", added_features=added_list
                )
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
            urlLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.iconLocales.url"
            )
            noIconLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.iconLocales.noIcon"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.icon",
                    before=(
                        "[" + urlLocale + "](" + before.icon + ")"
                        if before.icon
                        else noIconLocale
                    ),
                    after=(
                        "[" + urlLocale + "](" + after.icon + ")"
                        if after.icon
                        else noIconLocale
                    ),
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
            notPausedLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.invitesPausedUntilLocales.notPaused"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.invitesPausedUntil",
                    before=(
                        "<t:"
                        + str(
                            utility.date_time_to_timestamp(before.invites_paused_until)
                        )
                        + ":R>"
                        if before.invites_paused_until
                        else notPausedLocale
                    ),
                    after=(
                        "<t:"
                        + str(
                            utility.date_time_to_timestamp(after.invites_paused_until)
                        )
                        + ":R>"
                        if after.invites_paused_until
                        else notPausedLocale
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
                    before=(
                        before.max_presences if before.max_presences else keinerLocale
                    ),
                    after=after.max_presences if after.max_presences else keinerLocale,
                )
            )

        if before.max_video_channel_users != after.max_video_channel_users:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.maxVideoChannelUsers",
                    before=(
                        before.max_video_channel_users
                        if before.max_video_channel_users
                        else keinerLocale
                    ),
                    after=(
                        after.max_video_channel_users
                        if after.max_video_channel_users
                        else keinerLocale
                    ),
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
            defaultLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.nsfwLevelLocales.default"
            )
            explicitLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.nsfwLevelLocales.explicit"
            )
            safeLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.nsfwLevelLocales.safe"
            )
            ageRegisteredLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.nsfwLevelLocales.ageRegistered"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.nsfwLevel",
                    before=(
                        defaultLocale
                        if before.nsfw_level.default
                        else (
                            explicitLocale
                            if before.nsfw_level.explicit
                            else (
                                safeLocale
                                if before.nsfw_level.safe
                                else (
                                    ageRegisteredLocale
                                    if before.nsfw_level.age_restricted
                                    else keinerLocale
                                )
                            )
                        )
                    ),
                    after=(
                        defaultLocale
                        if after.nsfw_level.default
                        else (
                            explicitLocale
                            if after.nsfw_level.explicit
                            else (
                                safeLocale
                                if after.nsfw_level.safe
                                else (
                                    ageRegisteredLocale
                                    if after.nsfw_level.age_restricted
                                    else keinerLocale
                                )
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
                    before=before.owner.mention if before.owner else keinerLocale,
                    after=after.owner.mention if after.owner else keinerLocale,
                )
            )

        if before.preferred_locale != after.preferred_locale:
            beforeLocale = tanjunLocalizer.localize(
                locale,
                "logs.guildUpdate.preferredLocaleLocales."
                + str(before.preferred_locale),
            )
            afterLocale = tanjunLocalizer.localize(
                locale,
                "logs.guildUpdate.preferredLocaleLocales."
                + str(after.preferred_locale),
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.preferredLocale",
                    before=beforeLocale,
                    after=afterLocale,
                )
            )

        if before.premium_progress_bar_enabled != after.premium_progress_bar_enabled:
            if before.premium_progress_bar_enabled:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildUpdate.premiumProgressBarEnabled.activated"
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildUpdate.premiumProgressBarEnabled.deactivated"
                    )
                )

        if before.premium_subscriber_role != after.premium_subscriber_role:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.premiumSubscriberRole",
                    before=(
                        before.premium_subscriber_role.mention
                        if before.premium_subscriber_role
                        else keinerLocale
                    ),
                    after=(
                        after.premium_subscriber_role.mention
                        if after.premium_subscriber_role
                        else keinerLocale
                    ),
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
                    before=(
                        before.public_updates_channel.mention
                        if before.public_updates_channel
                        else keinerLocale
                    ),
                    after=(
                        after.public_updates_channel.mention
                        if after.public_updates_channel
                        else keinerLocale
                    ),
                )
            )

        if before.rules_channel != after.rules_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.rulesChannel",
                    before=(
                        before.rules_channel.mention
                        if before.rules_channel
                        else keinerLocale
                    ),
                    after=(
                        after.rules_channel.mention
                        if after.rules_channel
                        else keinerLocale
                    ),
                )
            )

        if before.safety_alerts_channel != after.safety_alerts_channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.safetyAlertsChannel",
                    before=(
                        before.safety_alerts_channel.mention
                        if before.safety_alerts_channel
                        else keinerLocale
                    ),
                    after=(
                        after.safety_alerts_channel.mention
                        if after.safety_alerts_channel
                        else keinerLocale
                    ),
                )
            )

        if before.unavailable != after.unavailable:
            if before.unavailable:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildUpdate.unavailableLocales.available"
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildUpdate.unavailableLocales.unavailable"
                    )
                )

        if before.verification_level != after.verification_level:
            noneLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.verificationLevelLocales.none"
            )
            lowLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.verificationLevelLocales.low"
            )
            mediumLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.verificationLevelLocales.medium"
            )
            highLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.verificationLevelLocales.high"
            )
            highestLocale = tanjunLocalizer.localize(
                locale, "logs.guildUpdate.verificationLevelLocales.highest"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildUpdate.verificationLevel",
                    before=(
                        noneLocale
                        if before.verification_level.none
                        else (
                            lowLocale
                            if before.verification_level.low
                            else (
                                mediumLocale
                                if before.verification_level.medium
                                else (
                                    highLocale
                                    if before.verification_level.high
                                    else highestLocale
                                )
                            )
                        )
                    ),
                    after=(
                        noneLocale
                        if after.verification_level.none
                        else (
                            lowLocale
                            if after.verification_level.low
                            else (
                                mediumLocale
                                if after.verification_level.medium
                                else (
                                    highLocale
                                    if after.verification_level.high
                                    else highestLocale
                                )
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
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.guildUpdate.title"),
            description=description,
        )
        if not str(after.id) in embeds:
            embeds[str(after.id)] = []
        embeds[str(after.id)].append(embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        logEnable = invite.guild and (await get_log_enable(invite.guild.id))[9]
        if not logEnable:
            return

        if await is_log_user_blacklisted(invite.guild.id, str(invite.inviter.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(invite.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in invite.inviter.roles:
                return

        locale = (
            invite.guild.preferred_locale
            if hasattr(invite.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        neverLocale = tanjunLocalizer.localize(
            locale, "logs.inviteCreate.expiresLocales.never"
        )
        infiniteLocale = tanjunLocalizer.localize(
            locale, "logs.inviteCreate.maxUsesLocales.infinite"
        )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.inviteCreate.createdBy", created_by=invite.inviter.mention
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.expires",
                expires=(
                    neverLocale
                    if invite.expires_at is None
                    else "<t:"
                    + str(utility.date_time_to_timestamp(invite.expires_at))
                    + ":R>"
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.max_uses",
                max_uses=infiniteLocale if invite.max_uses is None else invite.max_uses,
            )
        )

        if invite.channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.inviteCreate.channel", channel=invite.channel.mention
                )
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
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.inviteCreate.temporary")
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.inviteCreate.invite", invite=invite.url
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.inviteCreate.title"),
            description=description,
        )
        if not str(invite.guild.id) in embeds:
            embeds[str(invite.guild.id)] = []
        embeds[str(invite.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        logEnable = invite.guild and (await get_log_enable(invite.guild.id))[10]
        if not logEnable:
            return

        if await is_log_user_blacklisted(invite.guild.id, str(invite.inviter.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(invite.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in invite.inviter.roles:
                return

        locale = (
            invite.guild.preferred_locale
            if hasattr(invite.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        neverLocale = tanjunLocalizer.localize(
            locale, "logs.inviteCreate.expiresLocales.never"
        )
        infiniteLocale = tanjunLocalizer.localize(
            locale, "logs.inviteCreate.maxUsesLocales.infinite"
        )

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.expires",
                expires=(
                    neverLocale
                    if invite.expires_at is None
                    else "<t:"
                    + str(utility.date_time_to_timestamp(invite.expires_at))
                    + ":R>"
                ),
            )
        )
        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.inviteCreate.max_uses",
                max_uses=infiniteLocale if invite.max_uses is None else invite.max_uses,
            )
        )

        if invite.channel:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.inviteCreate.channel", channel=invite.channel.mention
                )
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
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.inviteCreate.temporary")
            )

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.inviteDelete.invite", invite=invite.url
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.inviteDelete.title"),
            description=description,
        )
        if not str(invite.guild.id) in embeds:
            embeds[str(invite.guild.id)] = []
        embeds[str(invite.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logEnable = member.guild and (await get_log_enable(member.guild.id))[11]
        if not logEnable:
            return

        if await is_log_user_blacklisted(member.guild.id, str(member.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(member.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in member.roles:
                return

        locale = (
            member.guild.preferred_locale
            if hasattr(member.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.memberJoin.name", joined=member.mention
            )
        )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.memberJoin.title"),
            description=description,
        )
        if not str(member.guild.id) in embeds:
            embeds[str(member.guild.id)] = []
        embeds[str(member.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        logEnable = member.guild and (await get_log_enable(member.guild.id))[12]
        if not logEnable:
            return

        if await is_log_user_blacklisted(member.guild.id, str(member.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(member.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in member.roles:
                return

        locale = (
            member.guild.preferred_locale
            if hasattr(member.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.memberRemove.name", left=member.mention
            )
        )
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
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.memberJoin.title"),
            description=description,
        )
        if not str(member.guild.id) in embeds:
            embeds[str(member.guild.id)] = []
        embeds[str(member.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[13]
        if not logEnable:
            return

        if await is_log_user_blacklisted(after.guild.id, str(after.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(after.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in after.roles:
                return

        locale = (
            after.guild.preferred_locale
            if hasattr(after.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.memberUpdate.name", member=after.mention
            )
        )

        # Check for avatar change
        if before.display_avatar != after.display_avatar:
            defaultAvatarUrl = "https://cdn.discordapp.com/embed/avatars/0.png"
            urlLocale = tanjunLocalizer.localize(
                locale, "logs.userUpdate.guildAvatarLocales.url"
            )
            # Upload old avatar to ImgBB
            avatar_bytes = (
                await before.display_avatar.read() if before.display_avatar else None
            )  # Read the old avatar as bytes
            avatar_upload_response = (
                await utility.upload_image_to_imgbb(avatar_bytes, "png")
                if avatar_bytes
                else {}
            )
            avatar_url_before = avatar_upload_response.get("data", {}).get(
                "url", defaultAvatarUrl
            )

            # Upload new avatar to ImgBB
            new_avatar_bytes = (
                await after.display_avatar.read() if after.display_avatar else None
            )  # Read the new avatar as bytes
            new_avatar_upload_response = (
                await utility.upload_image_to_imgbb(new_avatar_bytes, "png")
                if new_avatar_bytes
                else {}
            )
            new_avatar_url = new_avatar_upload_response.get("data", {}).get(
                "url", defaultAvatarUrl
            )

            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.userUpdate.avatar",
                    before=f"[{urlLocale}]({avatar_url_before})",
                    after=f"[{urlLocale}]({new_avatar_url})",
                )
            )

        # Check for banner change
        if before.banner != after.banner:
            noneLocale = tanjunLocalizer.localize(
                locale, "logs.userUpdate.guildAvatarLocales.none"
            )
            urlLocale = tanjunLocalizer.localize(
                locale, "logs.userUpdate.guildAvatarLocales.url"
            )
            # Upload old banner to ImgBB
            banner_bytes = (
                await before.banner.read() if before.banner else None
            )  # Read the old banner as bytes
            banner_upload_response = (
                await utility.upload_image_to_imgbb(banner_bytes, "png")
                if banner_bytes
                else {}
            )
            banner_url_before = banner_upload_response.get("data", {}).get(
                "url", noneLocale
            )

            # Upload new banner to ImgBB
            if after.banner:
                new_banner_bytes = (
                    await after.banner.read()
                )  # Read the new banner as bytes
                new_banner_upload_response = await utility.upload_image_to_imgbb(
                    new_banner_bytes, "png"
                )
                new_banner_url = new_banner_upload_response.get("data", {}).get(
                    "url", noneLocale
                )
            else:
                new_banner_url = noneLocale

            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.userUpdate.banner",
                    before=f"[{urlLocale}]({banner_url_before})",
                    after=f"[{urlLocale}]({new_banner_url})",
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
        removed_roles = [
            role.mention for role in before.roles if role not in after.roles
        ]

        if added_roles:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.memberUpdate.addedRoles", roles=", ".join(added_roles)
                )
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
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.memberUpdate.pending")
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.memberUpdate.pendingRemoved")
                )

        if before.timed_out_until != after.timed_out_until:
            if before.timed_out_until is None:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.memberUpdate.timeout",
                        timeout=utility.date_time_to_timestamp(after.timed_out_until),
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(locale, "logs.memberUpdate.timeoutRemoved")
                )

        if len(description_parts) >= 2:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.memberUpdate.title"),
            description=description,
        )
        if not str(after.guild.id) in embeds:
            embeds[str(after.guild.id)] = []
        embeds[str(after.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        for guild in self.bot.guilds:
            user = guild.get_member(before.id)
            if not user:
                continue

            logEnable = guild and (await get_log_enable(guild.id))[14]
            if not logEnable:
                continue

            if await is_log_user_blacklisted(guild.id, str(before.id)):
                continue

            blacklistedRoles = await get_log_role_blacklist(guild.id)
            for blacklistedRole in blacklistedRoles:
                if blacklistedRole in user.roles:
                    continue

            locale = (
                guild.preferred_locale
                if hasattr(guild, "preferred_locale")
                else "en_US"
            )
            description_parts = []

            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.userUpdate.name", user=before.mention
                )
            )

            if before.avatar != after.avatar:
                # defaultAvatarUrl = "https://cdn.discordapp.com/embed/avatars/0.png"
                # urlLocale = tanjunLocalizer.localize(
                #     locale, "logs.userUpdate.guildAvatarLocales.url"
                # )
                # Upload old avatar to ImgBB
                # avatar_bytes = (
                #     await before.display_avatar.read()
                #     if before.display_avatar
                #     else None
                # )  # Read the old avatar as bytes
                # avatar_upload_response = (
                #     await utility.upload_image_to_imgbb(avatar_bytes, "png")
                #     if avatar_bytes
                #     else {}
                # )
                # avatar_url_before = avatar_upload_response.get("data", {}).get(
                #     "url", defaultAvatarUrl
                # )
                # # Upload new avatar to ImgBB
                # new_avatar_bytes = (
                #     await after.display_avatar.read() if after.display_avatar else None
                # )  # Read the new avatar as bytes
                # new_avatar_upload_response = (
                #     await utility.upload_image_to_imgbb(new_avatar_bytes, "png")
                #     if new_avatar_bytes
                #     else {}
                # )
                # new_avatar_url = new_avatar_upload_response.get("data", {}).get(
                #     "url", defaultAvatarUrl
                # )

                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.userUpdate.avatar",
                        # before=f"[{urlLocale}]({avatar_url_before})",
                        # after=f"[{urlLocale}]({new_avatar_url})",
                    )
                )

            if before.banner != after.banner:
                noneLocale = tanjunLocalizer.localize(
                    locale, "logs.userUpdate.guildAvatarLocales.none"
                )
                urlLocale = tanjunLocalizer.localize(
                    locale, "logs.userUpdate.guildAvatarLocales.url"
                )
                # Upload old banner to ImgBB
                banner_bytes = (
                    await before.banner.read() if before.banner else None
                )  # Read the old banner as bytes
                banner_upload_response = (
                    await utility.upload_image_to_imgbb(banner_bytes, "png")
                    if banner_bytes
                    else {}
                )
                banner_url_before = banner_upload_response.get("data", {}).get(
                    "url", noneLocale
                )
                """ Unused:
                banner_url_after = (
                    after.banner.url if after.banner else noneLocale
                )  # New banner URL
                """

                # Upload new banner to ImgBB
                if after.banner:
                    new_banner_bytes = (
                        await after.banner.read()
                    )  # Read the new banner as bytes
                    new_banner_upload_response = await utility.upload_image_to_imgbb(
                        new_banner_bytes, "png"
                    )
                    new_banner_url = new_banner_upload_response.get("data", {}).get(
                        "url", noneLocale
                    )
                else:
                    new_banner_url = noneLocale

                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.userUpdate.banner",
                        before=f"[{urlLocale}]({banner_url_before})",
                        after=f"[{urlLocale}]({new_banner_url})",
                    )
                )

            if len(description_parts) == 1:
                return

            # Join all parts with newlines
            description = "\n".join(description_parts)

            embed = discord.Embed(
                color=EmbedColors.yellow,
                title=tanjunLocalizer.localize(locale, "logs.userUpdate.title"),
                description=description,
            )
            if not str(guild.id) in embeds:
                embeds[str(guild.id)] = []
            embeds[str(guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_member_ban(self, user: discord.Member):
        logEnable = user.guild and (await get_log_enable(user.guild.id))[15]
        if not logEnable:
            return

        if await is_log_user_blacklisted(user.guild.id, str(user.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(user.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in user.roles:
                return

        locale = (
            user.guild.preferred_locale
            if hasattr(user.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.memberBan.name", user=user.mention)
        )

        banner = None
        async for log in user.guild.audit_logs(limit=1, user=user):
            banner = log.banner

        if banner:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.memberBan.banned_by", banner=banner.mention
                )
            )

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.memberBan.title"),
            description=description,
        )
        if not str(user.guild.id) in embeds:
            embeds[str(user.guild.id)] = []
        embeds[str(user.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        logEnable = guild and (await get_log_enable(guild.id))[16]
        if not logEnable:
            return

        if await is_log_user_blacklisted(guild.id, str(user.id)):
            return

        locale = (
            guild.preferred_locale if hasattr(guild, "preferred_locale") else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(locale, "logs.memberUnban.name", user=user.mention)
        )

        unbanned_by = None
        async for log in guild.audit_logs(limit=1, user=user):
            unbanned_by = log.user

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
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.memberUnban.title"),
            description=description,
        )
        if not str(guild.id) in embeds:
            embeds[str(guild.id)] = []
        embeds[str(guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[17]
        if not logEnable:
            return

        if await is_log_user_blacklisted(after.guild.id, str(after.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(after.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in after.roles:
                return

        locale = (
            after.guild.preferred_locale
            if hasattr(after.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.presenceUpdate.name", user=after.mention
            )
        )

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
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.presenceUpdate.title"),
            description=description,
        )
        if not str(after.guild.id) in embeds:
            embeds[str(after.guild.id)] = []
        embeds[str(after.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[18]
        if not logEnable:
            return

        if await is_log_user_blacklisted(after.guild.id, str(after.author.id)):
            return

        if await is_log_channel_blacklisted(after.guild.id, str(after.channel.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(after.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in after.author.roles:
                return

        locale = (
            after.guild.preferred_locale
            if hasattr(after, "preferred_locale")
            else "en_US"
        )
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

            truncated_notice = tanjunLocalizer.localize(
                locale, "logs.messageEdit.truncatedNotice"
            )

            if len(diff_summary) > 1500:
                diff_summary_url = await upload_to_tanjun_logs(
                    tanjunLocalizer.localize(
                        locale, "logs.messageEdit.diff", diff=diff_summary
                    )
                )

                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.messageEdit.tooLongNotice", url=diff_summary_url
                    )
                )

            else:
                # Append the diff summary
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.messageEdit.diff", diff=diff_summary
                    )
                )

        if before.attachments != after.attachments:
            added_attachments = [
                f"[{attachment.filename}]({attachment.url})"
                for attachment in after.attachments
                if attachment not in before.attachments
            ]

            removed_attachments = []
            urlNotAvaiableLocale = tanjunLocalizer.localize(
                locale, "logs.messageEdit.urlNotAvaiableLocale"
            )
            for attachment in before.attachments:
                if attachment not in after.attachments:
                    if attachment.content_type and attachment.content_type.startswith(
                        "image/"
                    ):
                        attachmentBytes = await attachment.read()
                        url = await upload_image_to_imgbb(
                            attachmentBytes, attachment.filename.split(".")[-1]
                        )
                        if url:
                            url = url["data"]["display_url"]
                    else:
                        url = None
                    removed_attachments.append(
                        f"[{attachment.filename}]({url if url else urlNotAvaiableLocale})"
                    )

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
            description = description[:3000] + f" {truncated_notice}"

        embed = discord.Embed(
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.messageEdit.title"),
            description=description,
        )
        if not str(after.guild.id) in embeds:
            embeds[str(after.guild.id)] = []
        embeds[str(after.guild.id)].append(embed)

        # if embedsChanged:
        #     for i in range(len(before.embeds)):
        #         beforeEmbed = before.embeds[i]
        #         afterEmbed = after.embeds[i]
        #         if beforeEmbed.to_dict() != afterEmbed.to_dict():
        #             embeds[str(after.guild.id)].append(beforeEmbed)
        #             embeds[str(after.guild.id)].append(afterEmbed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        print(
            "message delete called on Server",
            message.guild.name,
            "Checking if log is enabled...",
        )
        logEnable = message.guild and (await get_log_enable(message.guild.id))[19]
        print("logEnable Result: ", logEnable)
        if not logEnable:
            return

        if await is_log_user_blacklisted(message.guild.id, str(message.author.id)):
            return

        if await is_log_channel_blacklisted(message.guild.id, str(message.channel.id)):
            return

        blacklistedRoles = await get_log_role_blacklist(message.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in message.author.roles:
                return

        print("so far so good.")

        locale = (
            message.guild.preferred_locale
            if hasattr(message.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale,
                "logs.messageDelete.name",
                user=message.author.mention,
                channel=message.channel.mention,
            )
        )
        deleted_by = None

        sendLog = False

        async for log in message.guild.audit_logs(limit=1, user=message.author):
            deleted_by = log.user
        if deleted_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.messageDelete.deletedBy",
                    deleted_by=deleted_by.mention,
                )
            )

        if message.content:
            sendLog = True
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.messageDelete.content", content=message.content
                )
            )

        if message.attachments:
            sendLog = True
            attachment_parts = []
            urlNotAvaiableLocale = tanjunLocalizer.localize(
                locale, "logs.messageDelete.urlNotAvaiableLocale"
            )

            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith(
                    "image/"
                ):
                    try:
                        attachmentBytes = await attachment.read()
                        url = await upload_image_to_imgbb(
                            attachmentBytes, attachment.filename.split(".")[-1]
                        )
                        if url:
                            url = url["data"]["display_url"]
                    except Exception:
                        url = None
                else:
                    url = None

                attachment_parts.append(
                    f"[{attachment.filename}]({url if url else urlNotAvaiableLocale})"
                )

            attachments = "\n- ".join(attachment_parts)
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.messageDelete.attachments", attachments=attachments
                )
            )

        if message.embeds:
            sendLog = True
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.messageDelete.embeds")
            )

        if not sendLog:
            return

        # Join all parts with newlines
        description = "\n".join(description_parts)

        embed = discord.Embed(
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.messageDelete.title"),
            description=description,
        )
        if not str(message.guild.id) in embeds:
            embeds[str(message.guild.id)] = []
        embeds[str(message.guild.id)].append(embed)
        print("added delete embed to embeds.")
        for emb in message.embeds:
            embeds[str(message.guild.id)].append(emb)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        logEnable = reaction.guild and (await get_log_enable(reaction.guild.id))[20]
        if not logEnable:
            return

        if await is_log_user_blacklisted(reaction.guild.id, str(user.id)):
            return

        if await is_log_channel_blacklisted(
            reaction.guild.id, str(reaction.message.channel.id)
        ):
            return

        blacklistedRoles = await get_log_role_blacklist(reaction.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in user.roles:
                return

        locale = (
            reaction.guild.preferred_locale
            if hasattr(reaction.guild, "preferred_locale")
            else "en_US"
        )
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
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.reactionAdd.title"),
            description=description,
        )
        if not str(reaction.guild.id) in embeds:
            embeds[str(reaction.guild.id)] = []
        embeds[str(reaction.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        logEnable = reaction.guild and (await get_log_enable(reaction.guild.id))[21]
        if not logEnable:
            return

        if await is_log_user_blacklisted(reaction.guild.id, str(user.id)):
            return

        if await is_log_channel_blacklisted(
            reaction.guild.id, str(reaction.message.channel.id)
        ):
            return

        blacklistedRoles = await get_log_role_blacklist(reaction.guild.id)
        for blacklistedRole in blacklistedRoles:
            if blacklistedRole in user.roles:
                return

        locale = (
            reaction.guild.preferred_locale
            if hasattr(reaction.guild, "preferred_locale")
            else "en_US"
        )
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
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.reactionRemove.title"),
            description=description,
        )
        if not str(reaction.guild.id) in embeds:
            embeds[str(reaction.guild.id)] = []
        embeds[str(reaction.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        logEnable = role.guild and (await get_log_enable(role.guild.id))[22]
        if not logEnable:
            return

        locale = (
            role.guild.preferred_locale
            if hasattr(role.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.guildRoleCreate.name", role=role.mention
            )
        )

        created_by = None
        async for log in role.guild.audit_logs(limit=1, user=role.guild.owner):
            created_by = log.user
        if created_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleCreate.createdBy",
                    created_by=created_by.mention,
                )
            )

        if role.color:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildRoleCreate.color", color=role.color
                )
            )

        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                urlLocale = tanjunLocalizer.localize(
                    locale, "logs.userUpdate.guildAvatarLocales.url"
                )
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=f"[{urlLocale}]({role.display_icon.url})",
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
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.hoist")
            )

        if role.managed:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.managed")
            )

        if role.mentionable:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.mentionable")
            )

        if role.permissions:
            permissions_list = [
                perm for perm, value in role.permissions if value
            ]  # Get only the permissions that are True
            if permissions_list:
                formatted_permissions = ", ".join(
                    [
                        f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`"
                        for perm in permissions_list
                    ]
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
            color=EmbedColors.green,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleCreate.title"),
            description=description,
        )
        if not str(role.guild.id) in embeds:
            embeds[str(role.guild.id)] = []
        embeds[str(role.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        logEnable = role.guild and (await get_log_enable(role.guild.id))[23]
        if not logEnable:
            return

        locale = (
            role.guild.preferred_locale
            if hasattr(role.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        description_parts.append(
            tanjunLocalizer.localize(
                locale, "logs.guildRoleDelete.name", role=role.name
            )
        )

        deleted_by = None
        async for log in role.guild.audit_logs(limit=1, user=role.guild.owner):
            deleted_by = log.user
        if deleted_by:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleDelete.deletedBy",
                    deleted_by=deleted_by.mention,
                )
            )

        if role.color:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildRoleCreate.color", color=role.color
                )
            )

        if role.display_icon:
            if isinstance(role.display_icon, discord.Asset):
                urlLocale = tanjunLocalizer.localize(
                    locale, "logs.userUpdate.guildAvatarLocales.url"
                )
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale,
                        "logs.guildRoleCreate.displayIcon",
                        displayIcon=f"[{urlLocale}]({role.display_icon.url})",
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
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.hoist")
            )

        if role.managed:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.managed")
            )

        if role.mentionable:
            description_parts.append(
                tanjunLocalizer.localize(locale, "logs.guildRoleCreate.mentionable")
            )

        # Format permissions nicely
        if role.permissions:
            permissions_list = [
                perm for perm, value in role.permissions if value
            ]  # Get only the permissions that are True
            if permissions_list:
                formatted_permissions = ", ".join(
                    [
                        f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`"
                        for perm in permissions_list
                    ]
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
            color=EmbedColors.red,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleDelete.title"),
            description=description,
        )
        if not str(role.guild.id) in embeds:
            embeds[str(role.guild.id)] = []
        embeds[str(role.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        logEnable = after.guild and (await get_log_enable(after.guild.id))[24]
        if not logEnable:
            return

        locale = (
            after.guild.preferred_locale
            if hasattr(after.guild, "preferred_locale")
            else "en_US"
        )
        description_parts = []

        # Check for changes in role attributes
        if before.name != after.name:
            description_parts.append(
                tanjunLocalizer.localize(
                    locale, "logs.guildRoleUpdate.name", role=after.name
                )
            )

        updated_by = None
        async for log in after.guild.audit_logs(limit=1, user=after.guild.owner):
            updated_by = log.user
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
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildRoleUpdate.hoistNow", role=after.name
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildRoleUpdate.hoistNoLonger", role=after.name
                    )
                )

        if before.mentionable != after.mentionable:
            if after.mentionable:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildRoleUpdate.mentionableNow", role=after.name
                    )
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
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildRoleUpdate.managedNow", role=after.name
                    )
                )
            else:
                description_parts.append(
                    tanjunLocalizer.localize(
                        locale, "logs.guildRoleUpdate.managedNoLonger", role=after.name
                    )
                )

        before_perms = {perm for perm, value in before.permissions if value}
        after_perms = {perm for perm, value in after.permissions if value}

        added_perms = after_perms - before_perms
        removed_perms = before_perms - after_perms

        if added_perms:
            added_perms_list = ", ".join(
                [
                    f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`"
                    for perm in added_perms
                ]
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
                [
                    f"`{tanjunLocalizer.localize(locale, f'logs.permissions.{perm}')}`"
                    for perm in removed_perms
                ]
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.removedPermissions",
                    permissions=removed_perms_list,
                )
            )

        if before.display_icon != after.display_icon:
            urlLocale = tanjunLocalizer.localize(
                locale, "logs.userUpdate.guildAvatarLocales.url"
            )
            description_parts.append(
                tanjunLocalizer.localize(
                    locale,
                    "logs.guildRoleUpdate.displayIcon",
                    before=(
                        f"[{urlLocale}]({before.display_icon.url})"
                        if before.display_icon
                        else "None"
                    ),
                    after=(
                        f"[{urlLocale}]({after.display_icon.url})"
                        if after.display_icon
                        else "None"
                    ),
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
            color=EmbedColors.yellow,
            title=tanjunLocalizer.localize(locale, "logs.guildRoleUpdate.title"),
            description=description,
        )
        if not str(after.guild.id) in embeds:
            embeds[str(after.guild.id)] = []
        embeds[str(after.guild.id)].append(embed)

    @commands.Cog.listener()
    async def on_ready(self):
        logcmds = LogsCommands(
            name=app_commands.locale_str("logs_name"),
            description=app_commands.locale_str("logs_description"),
        )
        channelBlacklist = ChannelBlacklistCommands(
            name=app_commands.locale_str("logs_blacklist_name"),
            description=app_commands.locale_str("logs_blacklist_description"),
        )
        userBlacklist = UserBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistu_name"),
            description=app_commands.locale_str("logs_blacklistu_description"),
        )
        roleBlacklist = RoleBlacklistCommands(
            name=app_commands.locale_str("logs_blacklistr_name"),
            description=app_commands.locale_str("logs_blacklistr_description"),
        )
        logcmds.add_command(channelBlacklist)
        logcmds.add_command(userBlacklist)
        logcmds.add_command(roleBlacklist)
        self.bot.tree.add_command(logcmds)


async def setup(bot):
    await bot.add_cog(LogsCog(bot))
