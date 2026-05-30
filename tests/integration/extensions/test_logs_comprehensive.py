from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from extensions.logs import (
    ChannelBlacklistCommands,
    LogsCog,
    LogsCommands,
    RoleBlacklistCommands,
    UserBlacklistCommands,
    log_event_consumer,
    log_event_producer,
    send_logEmbeds,
)
from tests.helpers.db import make_bot
from tests.helpers.discord import make_guild, make_member, make_role, make_text_channel
from tests.helpers.extensions import (
    async_audit_logs,
    invoke_interaction_command,
    make_audit_log_entry,
    make_automod_rule,
    make_log_enable,
)
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.logs"

IMG_UPLOAD = {"data": {"url": "https://img.example/old.png", "display_url": "https://img.example/display.png"}}


class _PermissionOverwrite:
    def __init__(self, perms: dict[str, bool | None]) -> None:
        self._perms = dict(perms)

    def __iter__(self):
        return iter(self._perms.items())

    def __getitem__(self, key: str) -> bool | None:
        return self._perms[key]

    def items(self):
        return self._perms.items()


def _setup_discord_enums() -> None:
    discord.AutoModRuleActionType = MagicMock()
    discord.AutoModRuleActionType.block_message = 1
    discord.AutoModRuleActionType.send_alert_message = 2
    discord.AutoModRuleActionType.timeout = 3
    discord.AutoModRuleActionType.block_member_interactions = 4
    discord.AuditLogAction = MagicMock()
    discord.AuditLogAction.automod_rule_update = "automod_rule_update"
    discord.AuditLogAction.automod_rule_create = "automod_rule_create"
    discord.AuditLogAction.channel_update = "channel_update"
    discord.AuditLogAction.channel_delete = "channel_delete"
    discord.AuditLogAction.channel_create = "channel_create"
    discord.AuditLogAction.ban = "ban"
    discord.AuditLogAction.unban = "unban"
    discord.AuditLogAction.role_create = "role_create"
    discord.AuditLogAction.role_delete = "role_delete"
    discord.AuditLogAction.role_update = "role_update"
    discord.AuditLogAction.message_delete = "message_delete"
    discord.Asset = type("Asset", (), {})


_setup_discord_enums()


@pytest.fixture
def log_api_mocks():
    with (
        patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=make_log_enable())),
        patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=None)),
        patch("extensions.logs.get_log_channel", new=AsyncMock(return_value="444444444")),
        patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=[])),
        patch("extensions.logs.blacklist_channel", new=AsyncMock()),
        patch("extensions.logs.blacklist_remove_channel", new=AsyncMock()),
        patch("extensions.logs.blacklist_list_channel", new=AsyncMock()),
        patch("extensions.logs.blacklist_user", new=AsyncMock()),
        patch("extensions.logs.blacklist_remove_user", new=AsyncMock()),
        patch("extensions.logs.blacklist_list_user", new=AsyncMock()),
        patch("extensions.logs.blacklist_role", new=AsyncMock()),
        patch("extensions.logs.blacklist_remove_role", new=AsyncMock()),
        patch("extensions.logs.blacklist_list_role", new=AsyncMock()),
        patch("extensions.logs.set_log_channel", new=AsyncMock()),
        patch("extensions.logs.remove_log_channel", new=AsyncMock()),
        patch("extensions.logs.configure_logs", new=AsyncMock()),
        patch("extensions.logs.log_event_producer", new=AsyncMock()) as producer,
        patch("utility.upload_image_to_imgbb", new=AsyncMock(return_value=IMG_UPLOAD)),
        patch("extensions.logs.upload_image_to_imgbb", new=AsyncMock(return_value=IMG_UPLOAD)),
        patch("extensions.logs.upload_to_tanjun_logs", new=AsyncMock(return_value="https://logs.example/diff")),
    ):
        yield producer


def _rich_automod_rule(guild: MagicMock) -> MagicMock:
    rule = make_automod_rule(guild)
    rule.trigger.regex_patterns = [r"bad.*"]
    rule.trigger.allow_list = ["ok"]
    rule.trigger.mention_limit = 5
    rule.trigger.mention_raid_protection = True
    rule.exempt_roles = [make_role()]
    rule.exempt_channels = [make_text_channel(guild=guild)]
    block = MagicMock()
    block.type = discord.AutoModRuleActionType.block_message
    alert = MagicMock()
    alert.type = discord.AutoModRuleActionType.send_alert_message
    alert.channel_id = 444444444
    timeout = MagicMock()
    timeout.type = discord.AutoModRuleActionType.timeout
    timeout.duration = 60
    block_interaction = MagicMock()
    block_interaction.type = discord.AutoModRuleActionType.block_member_interactions
    block_interaction.duration = 120
    rule.actions = [block, alert, timeout, block_interaction]
    guild.audit_logs = MagicMock(return_value=async_audit_logs(make_audit_log_entry(target_id=rule.id)))
    return rule


def _channel_with_overwrites(guild: MagicMock) -> MagicMock:
    channel = make_text_channel(guild=guild)
    channel.type = 0
    channel.created_at = datetime.now(UTC)
    channel.topic = "topic"
    channel.category = MagicMock()
    channel.category.name = "cat"
    target = make_role()
    target.name = "RoleTarget"
    overwrite = _PermissionOverwrite({"send_messages": True, "read_messages": False})
    channel.overwrites = {target: overwrite}
    channel.guild = guild
    return channel


async def _cog(log_api_mocks, *, fire_ready: bool = False) -> LogsCog:
    bot = await load_extension_bot(EXTENSION, fire_ready=fire_ready)
    return bot.cogs["LogsCog"]


@pytest.fixture
def logs_cog(log_api_mocks):
    async def _factory():
        return await _cog(log_api_mocks)

    return _factory


async def test_log_consumer_none_channel_and_wrong_type(log_api_mocks):
    bot = MagicMock()
    bot.get_channel = MagicMock(return_value=MagicMock())
    from extensions import logs

    logs._log_queue = asyncio.Queue()
    await logs._log_queue.put(("1", MagicMock()))
    with patch("extensions.logs.get_log_channel", new=AsyncMock(return_value=None)):
        task = asyncio.create_task(log_event_consumer(bot))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


async def test_log_consumer_send_exception(log_api_mocks):
    bot = MagicMock()
    channel = make_text_channel()
    channel.send = AsyncMock(side_effect=RuntimeError("send failed"))
    bot.get_channel = MagicMock(return_value=channel)
    from extensions import logs

    logs._log_queue = asyncio.Queue()
    await logs._log_queue.put(("123456789", MagicMock()))
    with patch("extensions.logs.get_log_channel", new=AsyncMock(return_value=str(channel.id))):
        task = asyncio.create_task(log_event_consumer(bot))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


async def test_log_consumer_text_channel_send(log_api_mocks):
    bot = MagicMock()
    channel = make_text_channel()
    channel.send = AsyncMock()
    bot.get_channel = MagicMock(return_value=channel)
    from extensions import logs

    logs._log_queue = asyncio.Queue()
    await logs._log_queue.put(("123456789", MagicMock()))
    with patch("extensions.logs.get_log_channel", new=AsyncMock(return_value=str(channel.id))):
        task = asyncio.create_task(log_event_consumer(bot))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    channel.send.assert_awaited()


async def test_blacklist_commands_default_channel(log_api_mocks):
    group = ChannelBlacklistCommands(name="bl", description="bl")
    await invoke_interaction_command(group.add_blacklist_channel_cmd, extra_kwargs={"channel": None})
    await invoke_interaction_command(group.remove_blacklist_channel_cmd, extra_kwargs={"channel": None})


async def test_automod_create_update_delete_full(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    rule = _rich_automod_rule(guild)
    await cog.on_automod_rule_create(rule)
    await cog.on_automod_rule_update(rule)
    await cog.on_automod_rule_delete(rule)


async def test_automod_action_all_types(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    for action_type, duration in (
        (discord.AutoModRuleActionType.block_message, None),
        (discord.AutoModRuleActionType.send_alert_message, None),
        (discord.AutoModRuleActionType.timeout, 60),
        (discord.AutoModRuleActionType.block_member_interactions, 120),
    ):
        execution = MagicMock()
        execution.guild = guild
        execution.member = make_member()
        execution.channel = make_text_channel(guild=guild)
        execution.action = MagicMock()
        execution.action.type = action_type
        execution.action.channel_id = 444444444
        execution.action.duration = duration
        execution.action.content = "x" * 1005
        await cog.on_automod_action(execution)


async def test_automod_blacklisted_and_disabled(log_api_mocks, logs_cog):
    cog = await logs_cog()
    rule = make_automod_rule()
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_automod_rule_create(rule)
    disabled = make_log_enable(automod_rule_create=False)
    with patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=disabled)):
        await cog.on_automod_rule_create(rule)


async def test_channel_create_delete_with_overwrites(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs(make_audit_log_entry(target_id=444444444)))
    channel = _channel_with_overwrites(guild)
    await cog.on_guild_channel_create(channel)
    await cog.on_guild_channel_delete(channel)


async def test_channel_update_permission_branches(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs(make_audit_log_entry(target_id=444444444)))
    before = make_text_channel(guild=guild)
    before.mention = "<#before>"
    before.name = "old"
    before.type = 0
    before.category = None
    before.topic = "old topic"
    before.nsfw = False
    before.slowmode_delay = 0
    before.default_auto_archive_duration = 60
    before.default_thread_auto_archive_duration = 1440
    role_target = make_role()
    role_target.mention = "<@&1>"
    removed_target = make_role(role_id=777)
    removed_target.name = "gone"
    old_only = _PermissionOverwrite({"send_messages": True})
    new_target = make_role(role_id=888)
    new_target.mention = "<@&888>"
    new_overwrite = _PermissionOverwrite({"send_messages": True, "attach_files": False, "embed_links": None})
    modified_old = _PermissionOverwrite({"send_messages": True, "manage_messages": False, "read_messages": True})
    modified_new = _PermissionOverwrite({"send_messages": False, "manage_messages": None, "read_messages": None})
    before.overwrites = {role_target: modified_old, removed_target: old_only}
    after = make_text_channel(guild=guild)
    after.mention = "<#after>"
    after.name = "new"
    after.type = 1
    after.category = MagicMock()
    after.topic = "new topic"
    after.nsfw = True
    after.slowmode_delay = 5
    after.default_auto_archive_duration = 120
    after.default_thread_auto_archive_duration = 2880
    after.overwrites = {role_target: modified_new, new_target: new_overwrite}
    after.guild = guild
    before.guild = guild
    await cog.on_guild_channel_update(before, after)


async def test_guild_update_comprehensive(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before = make_guild()
    after = make_guild()
    after.guild = after
    ch = make_text_channel(guild=after)
    before.afk_channel = None
    after.afk_channel = ch
    before.afk_timeout = 300
    after.afk_timeout = 600
    before.banner = None
    after.banner = "https://banner"
    before.default_notifications = True
    after.default_notifications = False
    before.description = "a"
    after.description = "b"
    splash = MagicMock()
    splash.url = "https://splash"
    before.discovery_splash = None
    after.discovery_splash = splash
    before.emoji_limit = 50
    after.emoji_limit = 100
    emoji = MagicMock()
    emoji.name = "e"
    before.emojis = []
    after.emojis = [emoji]
    before.explicit_content_filter = MagicMock(disabled=True, no_role=False)
    after.explicit_content_filter = MagicMock(disabled=False, no_role=True)
    before.features = []
    after.features = ["COMMUNITY"]
    before.icon = None
    after.icon = "https://icon"
    before.filesize_limit = 8
    after.filesize_limit = 25
    before.invites_paused_until = None
    after.invites_paused_until = datetime.now(UTC)
    before.max_members = 100
    after.max_members = 200
    before.max_presences = None
    after.max_presences = 50
    before.max_video_channel_users = None
    after.max_video_channel_users = 25
    before.name = "old guild"
    after.name = "new guild"
    before.nsfw_level = MagicMock(default=True, explicit=False, safe=False, age_restricted=False)
    after.nsfw_level = MagicMock(default=False, explicit=True, safe=False, age_restricted=False)
    before.owner = make_member()
    after.owner = make_member(user_id=333)
    before.preferred_locale = "en-US"
    after.preferred_locale = "de"
    before.premium_progress_bar_enabled = False
    after.premium_progress_bar_enabled = True
    before.premium_subscriber_role = None
    after.premium_subscriber_role = make_role()
    before.premium_subscribers = 0
    after.premium_subscribers = 5
    before.premium_tier = 0
    after.premium_tier = 2
    before.public_updates_channel = None
    after.public_updates_channel = ch
    before.rules_channel = None
    after.rules_channel = ch
    before.safety_alerts_channel = None
    after.safety_alerts_channel = ch
    before.unavailable = True
    after.unavailable = False
    before.verification_level = MagicMock(none=True, low=False, medium=False, high=False)
    after.verification_level = MagicMock(none=False, low=True, medium=False, high=False)
    removed_emoji = MagicMock()
    removed_emoji.name = "gone"
    before.emojis = [removed_emoji]
    after.emojis = []
    before.features = ["NEWS"]
    after.features = []
    await cog.on_guild_update(before, after)


async def test_invite_create_delete(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    invite = MagicMock()
    invite.guild = guild
    invite.channel = make_text_channel(guild=guild)
    invite.inviter = make_member()
    invite.inviter.roles = []
    invite.code = "xyz"
    invite.max_age = 3600
    invite.max_uses = 10
    invite.max_uses = None
    invite.expires_at = datetime.now(UTC)
    invite.temporary = True
    invite.url = "https://discord.gg/xyz"
    invite.scheduled_event = MagicMock(url="https://event")
    invite.target_application = MagicMock(name="App")
    invite.target_type = "InviteTarget.stream"
    invite.target_user = make_member()
    invite.target_user.mention = "<@222>"
    await cog.on_invite_create(invite)
    invite.expires_at = None
    invite.max_uses = 0
    invite.channel = None
    invite.scheduled_event = None
    invite.target_application = None
    invite.target_type = "InviteTarget.unknown"
    invite.target_user = None
    invite.temporary = False
    await cog.on_invite_create(invite)
    await cog.on_invite_delete(invite)
    with patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=["555555555"])):
        invite.inviter.roles = [make_role(role_id=555555555)]
        await cog.on_invite_create(invite)


async def test_member_join_remove_blacklist(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.guild = guild
    member.roles = [make_role()]
    member.joined_at = datetime.now(UTC)
    await cog.on_member_join(member)
    await cog.on_member_remove(member)
    with patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=["555555555"])):
        member.roles = [make_role(role_id=555555555)]
        await cog.on_member_join(member)


async def test_member_update_branches(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = guild
    after.guild = guild
    before.display_name = "a"
    after.display_name = "b"
    before.display_avatar = MagicMock()
    before.display_avatar.read = AsyncMock(return_value=b"old")
    after.display_avatar = MagicMock()
    after.display_avatar.read = AsyncMock(return_value=b"new")
    before.banner = MagicMock()
    before.banner.read = AsyncMock(return_value=b"banner")
    after.banner = None
    role_added = make_role(role_id=100)
    role_added.mention = "<@&100>"
    before.roles = []
    after.roles = [role_added]
    before.pending = True
    after.pending = False
    before.timed_out_until = None
    after.timed_out_until = datetime.now(UTC)
    await cog.on_member_update(before, after)
    before.timed_out_until = datetime.now(UTC)
    after.timed_out_until = None
    await cog.on_member_update(before, after)


async def test_user_update_with_guild_member(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.roles = []
    guild.get_member = MagicMock(return_value=member)
    cog.bot.guilds = [guild]
    user_before = MagicMock()
    user_before.id = member.id
    user_before.name = "a"
    user_before.mention = member.mention
    user_before.avatar = MagicMock()
    user_after = MagicMock()
    user_after.id = member.id
    user_after.name = "b"
    user_after.avatar = MagicMock()
    user_after.banner = MagicMock()
    user_after.banner.read = AsyncMock(return_value=b"banner")
    user_before.banner = None
    await cog.on_user_update(user_before, user_after)


async def test_member_ban_unban(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.guild = guild
    member.roles = []
    ban_entry = MagicMock()
    ban_entry.target = member
    ban_entry.user = make_member(user_id=999)
    ban_entry.user.mention = "<@999>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(ban_entry))
    await cog.on_member_ban(member)
    user = MagicMock()
    user.id = 111
    user.mention = "<@111>"
    unban_entry = MagicMock()
    unban_entry.target = user
    unban_entry.user = make_member(user_id=888)
    unban_entry.user.mention = "<@888>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(unban_entry))
    await cog.on_member_unban(guild, user)


async def test_presence_update(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = guild
    after.guild = guild
    before.activity = "playing"
    after.activity = "streaming"
    await cog.on_presence_update(before, after)


async def test_message_edit_content_attachments_long_diff(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = []
    before = MagicMock()
    before.guild = guild
    before.channel = channel
    before.author = author
    before.content = "line\n" * 800
    before.attachments = []
    after = MagicMock()
    after.guild = guild
    after.channel = channel
    after.author = author
    after.content = "changed\n" * 800
    after.attachments = []
    after.jump_url = "https://discord.com/channels/1/2/3"
    await cog.on_message_edit(before, after)

    att_before = MagicMock()
    att_before.filename = "pic.png"
    att_before.content_type = "image/png"
    att_before.read = AsyncMock(return_value=b"img")
    att_after = MagicMock()
    att_after.filename = "doc.txt"
    att_after.url = "https://file"
    before.content = "same"
    after.content = "same"
    before.attachments = [att_before]
    after.attachments = [att_after]
    await cog.on_message_edit(before, after)

    before.content = "a"
    after.content = "b"
    before.attachments = []
    after.attachments = []
    huge = "x" * 5000
    with patch("extensions.logs.upload_to_tanjun_logs", new=AsyncMock(return_value="https://diff")):
        description = "\n".join([huge, huge])
        with patch.object(cog, "on_message_edit", wraps=cog.on_message_edit):
            await cog.on_message_edit(before, after)


async def test_message_delete_variants(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = []
    message = MagicMock()
    message.guild = guild
    message.channel = channel
    message.author = author
    message.content = ""
    message.attachments = []
    message.embeds = []
    await cog.on_message_delete(message)

    audit = MagicMock()
    audit.target = MagicMock(id=author.id)
    audit.extra = MagicMock(channel=channel)
    audit.user = make_member()
    audit.user.mention = "<@mod>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(audit))
    message.content = "deleted text"
    att = MagicMock()
    att.filename = "img.png"
    att.content_type = "image/png"
    att.read = AsyncMock(return_value=b"bytes")
    message.attachments = [att]
    message.embeds = [MagicMock()]
    await cog.on_message_delete(message)

    att.read = AsyncMock(side_effect=RuntimeError("read fail"))
    await cog.on_message_delete(message)


async def test_reactions(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.guild = guild
    message.channel = channel
    message.jump_url = "https://discord.com/ch/1/2"
    message.author = make_member()
    reaction = MagicMock()
    reaction.guild = guild
    reaction.message = message
    reaction.emoji = "👍"
    user = make_member()
    user.roles = []
    await cog.on_reaction_add(reaction, user)
    await cog.on_reaction_remove(reaction, user)
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_reaction_add(reaction, user)


async def test_role_create_delete_update(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs(make_audit_log_entry(target_id=555555555)))
    role = make_role()
    role.guild = guild
    role.color = MagicMock()
    role.hoist = True
    role.managed = True
    role.mentionable = True
    role.permissions = [("send_messages", True), ("administrator", True)]
    asset = discord.Asset()
    asset.url = "https://icon"
    role.display_icon = asset
    await cog.on_guild_role_create(role)
    await cog.on_guild_role_delete(role)

    before = make_role()
    after = make_role()
    before.guild = guild
    after.guild = guild
    before.name = "old"
    after.name = "new"
    before.color = MagicMock()
    after.color = MagicMock()
    before.hoist = False
    after.hoist = True
    before.mentionable = False
    after.mentionable = True
    before.managed = False
    after.managed = True
    before.permissions = [("send_messages", False)]
    after.permissions = [("send_messages", True), ("ban_members", True)]
    before.display_icon = None
    after.display_icon = asset
    before.icon = "old-icon"
    after.icon = "new-icon"
    await cog.on_guild_role_update(before, after)

    before.hoist = True
    after.hoist = False
    before.mentionable = True
    after.mentionable = False
    before.managed = True
    after.managed = False
    await cog.on_guild_role_update(before, after)

    role.display_icon = "emoji-icon"
    await cog.on_guild_role_create(role)


async def test_on_ready_starts_consumer(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    cog = bot.cogs["LogsCog"]
    assert bot.tree.add_command.called
    assert bot.loop.create_task.called
    assert cog._log_consumer_task is not None or bot.loop.create_task.called


async def test_entity_blacklist_early_returns(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        channel = make_text_channel(guild=guild)
        await cog.on_guild_channel_create(channel)
        member = make_member()
        member.guild = guild
        await cog.on_member_join(member)


async def test_logs_commands_group(log_api_mocks):
    group = LogsCommands(name="logs", description="logs")
    await invoke_interaction_command(group.set_log_channel_cmd, extra_kwargs={"channel": make_text_channel()})
    await invoke_interaction_command(group.set_log_channel_cmd, extra_kwargs={"channel": None})
    await invoke_interaction_command(group.remove_log_channel_cmd)
    await invoke_interaction_command(group.configure_logs_cmd)


async def test_user_and_role_blacklist_commands(log_api_mocks):
    user_group = UserBlacklistCommands(name="blu", description="blu")
    for name in ("add_blacklist_user_cmd", "remove_blacklist_user_cmd", "show_blacklist_user_cmd"):
        await invoke_interaction_command(getattr(user_group, name), extra_kwargs={"user": make_member()})
    role_group = RoleBlacklistCommands(name="blr", description="blr")
    for name in ("add_blacklist_role_cmd", "remove_blacklist_role_cmd", "show_blacklist_role_cmd"):
        await invoke_interaction_command(getattr(role_group, name), extra_kwargs={"role": make_role()})


async def test_log_consumer_task_finally(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    with patch("extensions.logs.log_event_consumer", new=AsyncMock()) as consumer:
        await cog.log_consumer_task()
        consumer.assert_awaited_once()
    assert cog._log_consumer_task is None


async def test_producer_queue_integration():
    from extensions import logs

    logs._log_queue = asyncio.Queue(maxsize=200)
    await log_event_producer("1", MagicMock())
    assert logs._log_queue.qsize() == 1


async def test_automod_without_keyword_filter(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    rule = make_automod_rule(guild)
    rule.trigger.keyword_filter = []
    rule.trigger.regex_patterns = []
    rule.trigger.allow_list = []
    rule.trigger.mention_limit = None
    rule.trigger.mention_raid_protection = False
    rule.exempt_roles = []
    rule.exempt_channels = []
    rule.actions = []
    await cog.on_automod_rule_create(rule)


async def test_guild_update_extra_branches(log_api_mocks, logs_cog):
    cog = await logs_cog()
    before = make_guild()
    after = make_guild()
    before.verification_level = MagicMock(none=False, low=False, medium=True, high=False)
    after.verification_level = MagicMock(none=False, low=False, medium=False, high=True)
    before.nsfw_level = MagicMock(default=False, explicit=False, safe=True, age_restricted=False)
    after.nsfw_level = MagicMock(default=False, explicit=False, safe=False, age_restricted=True)
    before.explicit_content_filter = MagicMock(disabled=False, no_role=False)
    after.explicit_content_filter = MagicMock(disabled=False, no_role=False)
    before.premium_progress_bar_enabled = True
    after.premium_progress_bar_enabled = False
    before.unavailable = False
    after.unavailable = True
    before.invites_paused_until = datetime.now(UTC)
    after.invites_paused_until = None
    await cog.on_guild_update(before, after)


async def test_channel_update_no_extra_changes_early_return(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before = make_text_channel(guild=guild)
    after = make_text_channel(guild=guild)
    before.mention = after.mention = "<#x>"
    before.name = after.name = "same"
    before.type = after.type = 0
    before.category = after.category = None
    before.topic = after.topic = None
    before.overwrites = after.overwrites = {}
    before.nsfw = after.nsfw = False
    before.slowmode_delay = after.slowmode_delay = 0
    before.default_auto_archive_duration = after.default_auto_archive_duration = 60
    before.default_thread_auto_archive_duration = after.default_thread_auto_archive_duration = 1440
    await cog.on_guild_channel_update(before, after)


async def test_channel_delete_neutral_overwrite(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    channel.type = 0
    channel.created_at = datetime.now(UTC)
    channel.topic = "t"
    target = make_role()
    channel.overwrites = {target: _PermissionOverwrite({"send_messages": None})}
    await cog.on_guild_channel_delete(channel)


async def test_message_edit_truncated_description(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = []
    before = MagicMock()
    after = MagicMock()
    before.guild = after.guild = guild
    before.channel = after.channel = channel
    before.author = after.author = author
    before.content = "a"
    after.content = "b" + "x" * 5000
    before.attachments = after.attachments = []
    after.jump_url = "https://discord.com/1"
    with patch("extensions.logs.tanjunLocalizer.localize", side_effect=lambda _l, _k, **kw: kw.get("diff", "d") * 500):
        await cog.on_message_edit(before, after)


async def test_message_delete_audit_match(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = []
    message = MagicMock()
    message.guild = guild
    message.channel = channel
    message.author = author
    message.content = "hi"
    message.attachments = []
    message.embeds = []
    audit = MagicMock()
    audit.target = MagicMock(id=author.id)
    audit.extra = MagicMock()
    audit.extra.channel = channel
    audit.user = make_member()
    audit.user.mention = "<@mod>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(audit))
    await cog.on_message_delete(message)


async def test_member_update_only_name_emits(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = after.guild = guild
    before.display_name = after.display_name = "same"
    before.display_avatar = after.display_avatar
    before.banner = after.banner
    before.roles = after.roles = []
    before.pending = after.pending = False
    before.timed_out_until = after.timed_out_until = None
    await cog.on_member_update(before, after)


async def test_user_update_skips_blacklisted_role(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.roles = [make_role(role_id=555555555)]
    guild.get_member = MagicMock(return_value=member)
    cog.bot.guilds = [guild]
    user_before = MagicMock()
    user_before.id = member.id
    user_before.mention = member.mention
    user_before.avatar = MagicMock()
    user_before.banner = None
    user_after = MagicMock()
    user_after.id = member.id
    user_after.avatar = MagicMock()
    user_after.banner = None
    with patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=["555555555"])):
        await cog.on_user_update(user_before, user_after)


async def test_on_ready_skips_consumer_if_running(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    running = MagicMock()
    running.done.return_value = False
    cog._log_consumer_task = running
    await cog.on_ready()
    bot.loop.create_task.assert_not_called()


async def test_make_bot_sets_api_pool():
    bot, pool = make_bot()
    from api import set_bot

    set_bot(bot)
    assert bot._pool is pool
    set_bot(None)


async def test_send_log_embeds_and_queue_full():
    from extensions import logs

    with patch("extensions.logs.log_event_producer", new=AsyncMock()) as prod:
        await send_logEmbeds("1", MagicMock())
        prod.assert_awaited_once()
    logs._log_queue = asyncio.Queue(maxsize=1)
    logs._log_queue.put_nowait(("x", MagicMock()))
    await log_event_producer("2", MagicMock())
    assert logs._log_queue.qsize() == 1


async def test_log_consumer_skips_non_messageable_channel(log_api_mocks):
    bot = MagicMock()
    bot.get_channel = MagicMock(return_value=object())
    from extensions import logs

    logs._log_queue = asyncio.Queue()
    await logs._log_queue.put(("1", MagicMock()))
    with patch("extensions.logs.get_log_channel", new=AsyncMock(return_value="1")):
        task = asyncio.create_task(log_event_consumer(bot))
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


async def test_show_blacklist_channel_cmd(log_api_mocks):
    group = ChannelBlacklistCommands(name="bl", description="bl")
    await invoke_interaction_command(group.show_blacklist_channel_cmd)


async def test_invite_delete_full_payload(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    invite = MagicMock()
    invite.guild = guild
    invite.inviter = make_member()
    invite.inviter.roles = []
    invite.expires_at = datetime.now(UTC)
    invite.max_uses = 5
    invite.channel = make_text_channel(guild=guild)
    invite.scheduled_event = MagicMock(url="https://ev")
    invite.target_application = MagicMock(name="app")
    invite.target_type = "InviteTarget.embedded_application"
    invite.target_user = make_member()
    invite.target_user.mention = "<@u>"
    invite.temporary = True
    invite.url = "https://discord.gg/x"
    await cog.on_invite_delete(invite)


async def test_automod_update_delete_with_updater(log_api_mocks, logs_cog):
    cog = await logs_cog()
    rule = _rich_automod_rule(make_guild())
    entry = make_audit_log_entry(target_id=rule.id)
    rule.guild.audit_logs = MagicMock(return_value=async_audit_logs(entry))
    await cog.on_automod_rule_update(rule)
    rule.guild.audit_logs = MagicMock(return_value=async_audit_logs(make_audit_log_entry(target_id=rule.id)))
    await cog.on_automod_rule_delete(rule)


async def test_member_ban_unban_audit_trail(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.guild = guild
    member.roles = []
    ban_log = MagicMock()
    ban_log.target = member
    ban_log.user = make_member(user_id=900)
    ban_log.user.mention = "<@900>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(ban_log))
    await cog.on_member_ban(member)
    user = MagicMock()
    user.id = 111
    user.mention = "<@111>"
    unban_log = MagicMock()
    unban_log.target = user
    unban_log.user = make_member(user_id=901)
    unban_log.user.mention = "<@901>"
    guild.audit_logs = MagicMock(return_value=async_audit_logs(unban_log))
    await cog.on_member_unban(guild, user)


async def test_member_join_remove_user_blacklist(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    member = make_member()
    member.guild = guild
    member.roles = []
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_member_join(member)
        await cog.on_member_remove(member)


async def test_reaction_blacklist_paths(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    message = MagicMock()
    message.channel = channel
    message.jump_url = "https://discord.com/1"
    reaction = MagicMock()
    reaction.guild = guild
    reaction.message = message
    reaction.emoji = "x"
    user = make_member()
    user.roles = [make_role(role_id=555555555)]
    with patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=["555555555"])):
        await cog.on_reaction_add(reaction, user)
        await cog.on_reaction_remove(reaction, user)
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_reaction_add(reaction, user)


async def test_message_edit_long_diff_upload(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = []
    before = MagicMock()
    after = MagicMock()
    before.guild = after.guild = guild
    before.channel = after.channel = channel
    before.author = after.author = author
    before.content = "\n".join(["old"] * 500)
    after.content = "\n".join(["new"] * 500)
    before.attachments = after.attachments = []
    after.jump_url = "https://discord.com/1"
    await cog.on_message_edit(before, after)


async def test_guild_update_verification_and_nsfw_matrix(log_api_mocks, logs_cog):
    cog = await logs_cog()
    before = make_guild()
    after = make_guild()
    before.verification_level = MagicMock(none=False, low=False, medium=False, high=False)
    before.verification_level.highest = True
    after.verification_level = MagicMock(none=True, low=False, medium=False, high=False)
    after.verification_level.highest = False
    before.nsfw_level = MagicMock(default=False, explicit=False, safe=False, age_restricted=False)
    before.nsfw_level.explicit = False
    after.nsfw_level = MagicMock(default=True, explicit=False, safe=False, age_restricted=False)
    before.explicit_content_filter = MagicMock(disabled=False, no_role=False)
    after.explicit_content_filter = MagicMock(disabled=False, no_role=False)
    after.explicit_content_filter.all_members = True
    before.name = "n1"
    after.name = "n2"
    await cog.on_guild_update(before, after)


async def test_listeners_disabled_early_return(log_api_mocks, logs_cog):
    cog = await logs_cog()
    disabled = make_log_enable(
        automod_rule_create=False,
        automod_rule_update=False,
        automod_rule_delete=False,
        automod_action=False,
        guild_channel_delete=False,
        guild_channel_create=False,
        guild_channel_update=False,
        guild_update=False,
        invite_create=False,
        invite_delete=False,
        member_join=False,
        member_remove=False,
        member_update=False,
        user_update=False,
        member_ban=False,
        member_unban=False,
        presence_update=False,
        message_edit=False,
        message_delete=False,
        reaction_add=False,
        reaction_remove=False,
        guild_role_create=False,
        guild_role_delete=False,
        guild_role_update=False,
    )
    disabled.member_leave = False
    guild = make_guild()
    rule = make_automod_rule(guild)
    channel = make_text_channel(guild=guild)
    member = make_member()
    member.guild = guild
    invite = MagicMock(guild=guild, inviter=member)
    invite.inviter.roles = []
    with patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=disabled)):
        await cog.on_automod_rule_create(rule)
        await cog.on_automod_rule_update(rule)
        await cog.on_automod_rule_delete(rule)
        execution = MagicMock(guild=guild, member=member, channel=channel, action=MagicMock(type=1, content="x"))
        await cog.on_automod_action(execution)
        await cog.on_guild_channel_delete(channel)
        await cog.on_guild_channel_create(channel)
        await cog.on_guild_channel_update(channel, channel)
        await cog.on_guild_update(guild, guild)
        await cog.on_invite_create(invite)
        await cog.on_invite_delete(invite)
        await cog.on_member_join(member)
        await cog.on_member_remove(member)
        await cog.on_member_update(member, member)
        await cog.on_member_ban(member)
        await cog.on_member_unban(guild, member)
        await cog.on_presence_update(member, member)
        msg = MagicMock(guild=guild, channel=channel, author=member, content="", attachments=[], embeds=[])
        await cog.on_message_edit(msg, msg)
        await cog.on_message_delete(msg)
        reaction = MagicMock(guild=guild, message=msg, emoji="e")
        await cog.on_reaction_add(reaction, member)
        await cog.on_reaction_remove(reaction, member)
        role = make_role()
        role.guild = guild
        await cog.on_guild_role_create(role)
        await cog.on_guild_role_delete(role)
        await cog.on_guild_role_update(role, role)


async def test_automod_and_channel_blacklisted(log_api_mocks, logs_cog):
    cog = await logs_cog()
    rule = make_automod_rule()
    channel = make_text_channel()
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_automod_rule_update(rule)
        await cog.on_automod_rule_delete(rule)
        execution = MagicMock(
            guild=channel.guild,
            member=make_member(),
            channel=channel,
            action=MagicMock(type=1, content="c"),
        )
        await cog.on_automod_action(execution)
        await cog.on_guild_channel_delete(channel)
        await cog.on_guild_channel_create(channel)
        before, after = channel, make_text_channel(guild=channel.guild)
        await cog.on_guild_channel_update(before, after)


async def test_member_update_banner_with_after_banner(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = after.guild = guild
    before.display_name = after.display_name = "n"
    av = MagicMock()
    av.read = AsyncMock(return_value=b"x")
    before.display_avatar = av
    after.display_avatar = av
    before.banner = None
    after.banner = MagicMock()
    after.banner.read = AsyncMock(return_value=b"newbanner")
    before.roles = after.roles = []
    before.pending = after.pending = False
    before.timed_out_until = after.timed_out_until = None
    await cog.on_member_update(before, after)


async def test_member_update_roles_and_timeout_removed(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    before = make_member()
    after = make_member()
    before.guild = after.guild = guild
    before.display_name = after.display_name = "n"
    before.display_avatar = after.display_avatar
    before.banner = after.banner = None
    r = make_role()
    r.mention = "<@&r>"
    before.roles = [r]
    after.roles = []
    before.pending = after.pending = False
    before.timed_out_until = datetime.now(UTC)
    after.timed_out_until = None
    await cog.on_member_update(before, after)


async def test_user_update_no_guild_member(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.get_member = MagicMock(return_value=None)
    cog.bot.guilds = [guild]
    user_before = MagicMock(id=1, avatar=MagicMock(), banner=None)
    user_after = MagicMock(id=1, avatar=MagicMock(), banner=None)
    await cog.on_user_update(user_before, user_after)


async def test_message_edit_and_delete_blacklists(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member()
    author.roles = [make_role(role_id=555555555)]
    before = MagicMock(guild=guild, channel=channel, author=author, content="a", attachments=[])
    after = MagicMock(guild=guild, channel=channel, author=author, content="b", attachments=[], jump_url="https://d/1")
    with patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=True)):
        await cog.on_message_edit(before, after)
    message = MagicMock(guild=guild, channel=channel, author=author, content="x", attachments=[], embeds=[])
    with patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=["555555555"])):
        await cog.on_message_delete(message)


async def test_guild_update_empty_changes(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    await cog.on_guild_update(guild, guild)


async def test_channel_update_only_neutral_removed(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before = make_text_channel(guild=guild)
    after = make_text_channel(guild=guild)
    before.mention = after.mention = "<#m>"
    before.name = after.name = "n"
    before.type = after.type = 0
    before.category = after.category = None
    before.topic = after.topic = None
    before.nsfw = after.nsfw = False
    before.slowmode_delay = after.slowmode_delay = 0
    before.default_auto_archive_duration = after.default_auto_archive_duration = 60
    before.default_thread_auto_archive_duration = after.default_thread_auto_archive_duration = 1440
    t = make_role()
    t.mention = "<@&t>"
    old = _PermissionOverwrite({"embed_links": None})
    new = _PermissionOverwrite({"embed_links": True})
    before.overwrites = {t: old}
    after.overwrites = {t: new}
    await cog.on_guild_channel_update(before, after)


async def test_role_without_color_or_permissions(log_api_mocks, logs_cog):
    cog = await logs_cog()
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    role = make_role()
    role.guild = guild
    role.color = None
    role.display_icon = None
    role.hoist = False
    role.managed = False
    role.mentionable = False
    role.permissions = []
    await cog.on_guild_role_create(role)
    await cog.on_guild_role_delete(role)
