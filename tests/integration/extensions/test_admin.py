from __future__ import annotations

import importlib

import pytest

from tests.helpers.extension_loader import (
    find_nested_group,
    find_tree_group,
    fire_cog_on_ready,
    get_subcommand_names,
    get_tree_command_names,
    get_tree_commands,
    load_extension,
    make_bot_for_extensions,
)
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.admin"
COG_NAME = "AdminCog"

# The admin extension registers 13 top-level groups on on_ready
ADMIN_TOP_LEVEL_GROUPS = [
    "admin_warn_name",
    "admin_role_name",
    "admin_rolemanage_name",
    "admin_report_name",
    "admin_triggermessages_name",
    "admin_jointocreate_name",
    "admin_moderation_name",
    "admin_purgegroup_name",
    "admin_channels_name",
    "admin_messaging_name",
    "admin_emoji_name",
    "admin_setup_name",
    "admin_localegroup_name",
]


async def test_module_exposes_setup():
    module = importlib.import_module(EXTENSION)
    assert hasattr(module, "setup")
    assert callable(module.setup)


async def test_setup_registers_cog():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert COG_NAME in bot.cogs


async def test_setup_calls_add_cog_once():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    bot.add_cog.assert_awaited_once()


async def test_get_cog_returns_registered_instance():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.get_cog(COG_NAME) is bot.cogs[COG_NAME]


async def test_cog_stores_bot_reference():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.cogs[COG_NAME].bot is bot


async def test_on_ready_adds_all_groups_to_tree():
    bot = make_bot_for_extensions()
    await load_extension(bot, EXTENSION)
    assert get_tree_commands(bot) == []
    await fire_cog_on_ready(bot)
    assert len(get_tree_commands(bot)) == len(ADMIN_TOP_LEVEL_GROUPS)


async def test_all_top_level_groups_registered():
    bot = await load_extension_bot(EXTENSION)
    names = get_tree_command_names(bot)
    assert len(names) == len(ADMIN_TOP_LEVEL_GROUPS)
    for expected in ADMIN_TOP_LEVEL_GROUPS:
        assert expected in names, f"Missing top-level group: {expected}"


async def test_admin_warn_group_has_3_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_warn_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 3


async def test_admin_role_group_has_2_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_role_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 2


async def test_admin_rolemanage_group_has_4_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_rolemanage_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 4


async def test_admin_report_group_has_4_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_report_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 4


async def test_admin_triggermessages_group_has_2_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_triggermessages_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 2


async def test_admin_jointocreate_group_has_2_commands():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_jointocreate_name")
    assert group is not None
    assert len(get_subcommand_names(group)) == 2


async def test_admin_moderation_kick_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_kick_name" in get_subcommand_names(group)


async def test_admin_moderation_ban_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_ban_name" in get_subcommand_names(group)


async def test_admin_moderation_unban_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_unban_name" in get_subcommand_names(group)


async def test_admin_moderation_timeout_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_timeout_name" in get_subcommand_names(group)


async def test_admin_moderation_removetimeout_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_removetimeout_name" in get_subcommand_names(group)


async def test_admin_moderation_nickname_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_moderation_name")
    assert group is not None
    assert "admin_nickname_name" in get_subcommand_names(group)


async def test_admin_channels_lock_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_channels_name")
    assert group is not None
    assert "admin_lock_name" in get_subcommand_names(group)


async def test_admin_channels_unlock_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_channels_name")
    assert group is not None
    assert "admin_unlock_name" in get_subcommand_names(group)


async def test_admin_channels_slowmode_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_channels_name")
    assert group is not None
    assert "admin_slowmode_name" in get_subcommand_names(group)


async def test_admin_channels_nuke_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_channels_name")
    assert group is not None
    assert "admin_nuke_name" in get_subcommand_names(group)


async def test_admin_purgegroup_purge_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_purgegroup_name")
    assert group is not None
    assert "admin_purge_name" in get_subcommand_names(group)


async def test_admin_messaging_say_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_messaging_name")
    assert group is not None
    assert "admin_say_name" in get_subcommand_names(group)


async def test_admin_messaging_embed_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_messaging_name")
    assert group is not None
    assert "admin_embed_name" in get_subcommand_names(group)


async def test_admin_emoji_createemoji_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_emoji_name")
    assert group is not None
    assert "admin_createemoji_name" in get_subcommand_names(group)


async def test_admin_emoji_copyemoji_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_emoji_name")
    assert group is not None
    assert "admin_copyemoji_name" in get_subcommand_names(group)


async def test_admin_emoji_boosterrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_emoji_name")
    assert group is not None
    assert "admin_boosterrole_name" in get_subcommand_names(group)


async def test_admin_setup_createticket_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_setup_name")
    assert group is not None
    assert "admin_createticket_name" in get_subcommand_names(group)


async def test_admin_localegroup_setlocale_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_localegroup_name")
    assert group is not None
    assert "admin_setlocale_name" in get_subcommand_names(group)


async def test_admin_warn_add_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_warn_name")
    assert group is not None
    assert "admin_warn_add_name" in get_subcommand_names(group)


async def test_admin_warn_view_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_warn_name")
    assert group is not None
    assert "admin_warn_view_name" in get_subcommand_names(group)


async def test_admin_warn_config_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_warn_name")
    assert group is not None
    assert "admin_warn_config_name" in get_subcommand_names(group)


async def test_admin_role_addrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_role_name")
    assert group is not None
    assert "admin_addrole_name" in get_subcommand_names(group)


async def test_admin_role_removerole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_role_name")
    assert group is not None
    assert "admin_removerole_name" in get_subcommand_names(group)


async def test_admin_rolemanage_createrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_rolemanage_name")
    assert group is not None
    assert "admin_createrole_name" in get_subcommand_names(group)


async def test_admin_rolemanage_deleterole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_rolemanage_name")
    assert group is not None
    assert "admin_deleterole_name" in get_subcommand_names(group)


async def test_admin_rolemanage_moverole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_rolemanage_name")
    assert group is not None
    assert "admin_moverole_name" in get_subcommand_names(group)


async def test_admin_rolemanage_copyrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_rolemanage_name")
    assert group is not None
    assert "admin_copyrole_name" in get_subcommand_names(group)


async def test_admin_report_setchannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_report_name")
    assert group is not None
    assert "admin_rps_setchannel_name" in get_subcommand_names(group)


async def test_admin_report_removechannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_report_name")
    assert group is not None
    assert "admin_rps_removechannel_name" in get_subcommand_names(group)


async def test_admin_report_showreports_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_report_name")
    assert group is not None
    assert "admin_rps_showreports_name" in get_subcommand_names(group)


async def test_admin_report_unblockreporter_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_report_name")
    assert group is not None
    assert "admin_rps_unblockreporter_name" in get_subcommand_names(group)


async def test_admin_triggermessages_configure_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_triggermessages_name")
    assert group is not None
    assert "admin_tm_configure_name" in get_subcommand_names(group)


async def test_admin_triggermessages_add_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_triggermessages_name")
    assert group is not None
    assert "admin_tm_add_name" in get_subcommand_names(group)


async def test_admin_jointocreate_setchannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_jointocreate_name")
    assert group is not None
    assert "admin_jtc_setchannel_name" in get_subcommand_names(group)


async def test_admin_jointocreate_removechannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    group = find_tree_group(bot, "admin_jointocreate_name")
    assert group is not None
    assert "admin_jtc_removechannel_name" in get_subcommand_names(group)
