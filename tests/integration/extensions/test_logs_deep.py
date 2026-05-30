from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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
from tests.helpers.discord import make_guild, make_member, make_role, make_text_channel
from tests.helpers.extensions import (
    async_audit_logs,
    invoke_interaction_command,
    make_automod_rule,
    make_log_enable,
)
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.logs"


@pytest.fixture
def log_api_mocks():
    with (
        patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=make_log_enable())),
        patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=None)),
        patch("extensions.logs.get_log_channel", new=AsyncMock(return_value="444444444")),
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
    ):
        yield producer


async def test_log_event_producer_enqueues():
    from extensions import logs

    logs._log_queue = asyncio.Queue(maxsize=200)
    embed = MagicMock()
    await log_event_producer("123", embed)
    assert logs._log_queue.qsize() == 1


async def test_log_event_producer_drops_when_full():
    from extensions import logs

    logs._log_queue = asyncio.Queue(maxsize=1)
    logs._log_queue.put_nowait(("1", MagicMock()))
    await log_event_producer("123", MagicMock())
    assert logs._log_queue.qsize() == 1


async def test_send_logEmbeds_delegates():
    with patch("extensions.logs.log_event_producer", new=AsyncMock()) as prod:
        await send_logEmbeds("123", MagicMock())
    prod.assert_awaited_once()


async def test_log_event_consumer_sends_to_channel():
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
        try:
            await task
        except asyncio.CancelledError:
            pass
    channel.send.assert_awaited()


async def test_log_event_consumer_skips_missing_channel():
    bot = MagicMock()
    bot.get_channel = MagicMock(return_value=None)
    from extensions import logs

    logs._log_queue = asyncio.Queue()
    await logs._log_queue.put(("123", MagicMock()))
    with patch("extensions.logs.get_log_channel", new=AsyncMock(return_value="999")):
        task = asyncio.create_task(log_event_consumer(bot))
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def test_channel_blacklist_commands(log_api_mocks):
    group = ChannelBlacklistCommands(name="bl", description="bl")
    for name in ("add_blacklist_channel_cmd", "remove_blacklist_channel_cmd", "show_blacklist_channel_cmd"):
        await invoke_interaction_command(
            getattr(group, name), extra_kwargs={"channel": make_text_channel()}
        )


async def test_user_blacklist_commands(log_api_mocks):
    group = UserBlacklistCommands(name="bl", description="bl")
    for name in ("add_blacklist_user_cmd", "remove_blacklist_user_cmd", "show_blacklist_user_cmd"):
        await invoke_interaction_command(getattr(group, name), extra_kwargs={"user": make_member()})


async def test_role_blacklist_commands(log_api_mocks):
    group = RoleBlacklistCommands(name="bl", description="bl")
    for name in ("add_blacklist_role_cmd", "remove_blacklist_role_cmd", "show_blacklist_role_cmd"):
        await invoke_interaction_command(getattr(group, name), extra_kwargs={"role": make_role()})


async def test_logs_commands(log_api_mocks):
    group = LogsCommands(name="logs", description="logs")
    await invoke_interaction_command(group.set_log_channel_cmd, extra_kwargs={"channel": make_text_channel()})
    await invoke_interaction_command(group.remove_log_channel_cmd)
    await invoke_interaction_command(group.configure_logs_cmd)


async def test_logs_cog_listeners_automod(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    rule = make_automod_rule(guild)
    await cog.on_automod_rule_create(rule)
    await cog.on_automod_rule_update(rule)
    await cog.on_automod_rule_delete(rule)


async def test_logs_cog_listener_automod_action(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    execution = MagicMock()
    execution.guild = guild
    execution.rule_id = 1
    execution.action = MagicMock()
    execution.action.type = 1
    execution.content = "bad"
    execution.member = make_member()
    execution.channel = make_text_channel(guild=guild)
    await cog.on_automod_action(execution)


async def test_logs_cog_channel_listeners(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    channel = make_text_channel(guild=guild)
    channel.guild = guild
    channel.category = None
    channel.position = 1
    channel.overwrites = {}
    before = make_text_channel(guild=guild)
    before.name = "old"
    after = make_text_channel(guild=guild)
    after.name = "new"
    await cog.on_guild_channel_create(channel)
    await cog.on_guild_channel_delete(channel)
    await cog.on_guild_channel_update(before, after)


async def test_logs_cog_guild_and_invite_listeners(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    before = make_guild()
    before.name = "old"
    after = make_guild()
    after.name = "new"
    invite = MagicMock()
    invite.guild = guild
    invite.channel = make_text_channel(guild=guild)
    invite.inviter = make_member()
    invite.code = "abc"
    invite.max_age = 0
    invite.max_uses = 0
    invite.temporary = False
    await cog.on_guild_update(before, after)
    await cog.on_invite_create(invite)
    await cog.on_invite_delete(invite)


async def test_logs_cog_member_listeners(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    member = make_member()
    member.guild = guild
    member.joined_at = None
    member.display_avatar = MagicMock(url="http://example.com/a.png")
    member.guild_avatar = None
    member.avatar = None
    before = make_member()
    before.guild = guild
    before.display_name = "a"
    before.display_avatar = MagicMock()
    before.display_avatar.read = AsyncMock(return_value=b"")
    before.roles = []
    after = make_member()
    after.guild = guild
    after.display_name = "b"
    after.display_avatar = MagicMock()
    after.display_avatar.read = AsyncMock(return_value=b"")
    after.roles = []
    user_before = MagicMock()
    user_before.id = 111
    user_before.name = "a"
    user_after = MagicMock()
    user_after.id = 111
    user_after.name = "b"
    await cog.on_member_join(member)
    await cog.on_member_remove(member)
    await cog.on_member_update(before, after)
    await cog.on_user_update(user_before, user_after)
    await cog.on_member_ban(member)
    await cog.on_member_unban(guild, user_after)
    await cog.on_presence_update(before, after)


async def test_logs_cog_message_and_reaction_listeners(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    before = MagicMock()
    before.guild = guild
    before.channel = channel
    before.author = make_member()
    before.content = "old"
    before.attachments = []
    before.embeds = []
    after = MagicMock()
    after.guild = guild
    after.channel = channel
    after.author = make_member()
    after.content = "new"
    after.attachments = []
    after.embeds = []
    message = MagicMock()
    message.guild = guild
    message.channel = channel
    message.author = make_member()
    message.content = "hi"
    message.attachments = []
    message.embeds = []
    reaction = MagicMock()
    reaction.message = message
    reaction.emoji = "👍"
    user = make_member()
    await cog.on_message_edit(before, after)
    await cog.on_message_delete(message)
    await cog.on_reaction_add(reaction, user)
    await cog.on_reaction_remove(reaction, user)


async def test_logs_cog_role_listeners(log_api_mocks):
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild()
    guild.audit_logs = MagicMock(return_value=async_audit_logs())
    role = make_role()
    role.guild = guild
    role.color = MagicMock()
    role.display_icon = None
    role.hoist = False
    role.managed = False
    role.mentionable = False
    role.permissions = []
    before = make_role()
    before.guild = guild
    before.name = "old"
    before.color = MagicMock()
    before.hoist = False
    before.mentionable = False
    before.managed = False
    before.display_icon = None
    before.icon = None
    before.permissions = []
    after = make_role()
    after.guild = guild
    after.name = "new"
    after.color = MagicMock()
    after.hoist = True
    after.mentionable = True
    after.managed = False
    after.display_icon = None
    after.icon = None
    after.permissions = []
    await cog.on_guild_role_create(role)
    await cog.on_guild_role_delete(role)
    await cog.on_guild_role_update(before, after)


async def test_logs_cog_on_ready_registers_tree():
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called


async def test_log_enable_disabled_skips_listener():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    disabled = make_log_enable(automod_rule_create=False)
    with patch("extensions.logs.get_log_enable", new=AsyncMock(return_value=disabled)):
        rule = make_automod_rule()
        await cog.on_automod_rule_create(rule)
