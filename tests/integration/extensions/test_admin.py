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


async def test_on_ready_adds_command_to_tree():
    bot = make_bot_for_extensions()
    await load_extension(bot, EXTENSION)
    assert get_tree_commands(bot) == []
    await fire_cog_on_ready(bot)
    assert len(get_tree_commands(bot)) == 1


async def test_root_command_name_is_admin_name():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_command_names(bot) == ["admin_name"]


async def test_root_group_has_24_entries():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert len(get_subcommand_names(root)) == 24


async def test_subcommand_admin_kick_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_kick_name" in get_subcommand_names(root)


async def test_subcommand_admin_ban_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_ban_name" in get_subcommand_names(root)


async def test_subcommand_admin_unban_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_unban_name" in get_subcommand_names(root)


async def test_subcommand_admin_timeout_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_timeout_name" in get_subcommand_names(root)


async def test_subcommand_admin_removetimeout_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_removetimeout_name" in get_subcommand_names(root)


async def test_subcommand_admin_purge_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_purge_name" in get_subcommand_names(root)


async def test_subcommand_admin_nickname_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_nickname_name" in get_subcommand_names(root)


async def test_subcommand_admin_slowmode_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_slowmode_name" in get_subcommand_names(root)


async def test_subcommand_admin_lock_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_lock_name" in get_subcommand_names(root)


async def test_subcommand_admin_unlock_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_unlock_name" in get_subcommand_names(root)


async def test_subcommand_admin_nuke_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_nuke_name" in get_subcommand_names(root)


async def test_subcommand_admin_say_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_say_name" in get_subcommand_names(root)


async def test_subcommand_admin_embed_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_embed_name" in get_subcommand_names(root)


async def test_subcommand_admin_createemoji_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_createemoji_name" in get_subcommand_names(root)


async def test_subcommand_admin_boosterrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_boosterrole_name" in get_subcommand_names(root)


async def test_subcommand_admin_createticket_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_createticket_name" in get_subcommand_names(root)


async def test_subcommand_admin_setlocale_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_setlocale_name" in get_subcommand_names(root)


async def test_subcommand_admin_copyemoji_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_copyemoji_name" in get_subcommand_names(root)


async def test_subcommand_admin_warn_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_warn_name" in get_subcommand_names(root)


async def test_subcommand_admin_role_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_role_name" in get_subcommand_names(root)


async def test_subcommand_admin_report_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_report_name" in get_subcommand_names(root)


async def test_subcommand_admin_triggermessages_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_triggermessages_name" in get_subcommand_names(root)


async def test_subcommand_admin_jointocreate_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    assert root is not None
    assert "admin_jointocreate_name" in get_subcommand_names(root)


async def test_nested_group_admin_warn_name_has_3_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_warn_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 3


async def test_nested_admin_warn_name_admin_warn_add_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_warn_name")
    assert nested is not None
    assert "admin_warn_add_name" in get_subcommand_names(nested)


async def test_nested_admin_warn_name_admin_warn_view_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_warn_name")
    assert nested is not None
    assert "admin_warn_view_name" in get_subcommand_names(nested)


async def test_nested_admin_warn_name_admin_warn_config_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_warn_name")
    assert nested is not None
    assert "admin_warn_config_name" in get_subcommand_names(nested)


async def test_nested_group_admin_role_name_has_6_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 6


async def test_nested_admin_role_name_admin_addrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_addrole_name" in get_subcommand_names(nested)


async def test_nested_admin_role_name_admin_removerole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_removerole_name" in get_subcommand_names(nested)


async def test_nested_admin_role_name_admin_createrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_createrole_name" in get_subcommand_names(nested)


async def test_nested_admin_role_name_admin_deleterole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_deleterole_name" in get_subcommand_names(nested)


async def test_nested_admin_role_name_admin_moverole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_moverole_name" in get_subcommand_names(nested)


async def test_nested_admin_role_name_admin_copyrole_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_role_name")
    assert nested is not None
    assert "admin_copyrole_name" in get_subcommand_names(nested)


async def test_nested_group_admin_report_name_has_4_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_report_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 4


async def test_nested_admin_report_name_admin_rps_setchannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_report_name")
    assert nested is not None
    assert "admin_rps_setchannel_name" in get_subcommand_names(nested)


async def test_nested_admin_report_name_admin_rps_removechannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_report_name")
    assert nested is not None
    assert "admin_rps_removechannel_name" in get_subcommand_names(nested)


async def test_nested_admin_report_name_admin_rps_showreports_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_report_name")
    assert nested is not None
    assert "admin_rps_showreports_name" in get_subcommand_names(nested)


async def test_nested_admin_report_name_admin_rps_unblockreporter_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_report_name")
    assert nested is not None
    assert "admin_rps_unblockreporter_name" in get_subcommand_names(nested)


async def test_nested_group_admin_triggermessages_name_has_2_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_triggermessages_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 2


async def test_nested_admin_triggermessages_name_admin_tm_configure_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_triggermessages_name")
    assert nested is not None
    assert "admin_tm_configure_name" in get_subcommand_names(nested)


async def test_nested_admin_triggermessages_name_admin_tm_add_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_triggermessages_name")
    assert nested is not None
    assert "admin_tm_add_name" in get_subcommand_names(nested)


async def test_nested_group_admin_jointocreate_name_has_2_commands():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_jointocreate_name")
    assert nested is not None
    assert len(get_subcommand_names(nested)) == 2


async def test_nested_admin_jointocreate_name_admin_jtc_setchannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_jointocreate_name")
    assert nested is not None
    assert "admin_jtc_setchannel_name" in get_subcommand_names(nested)


async def test_nested_admin_jointocreate_name_admin_jtc_removechannel_name_registered():
    bot = await load_extension_bot(EXTENSION)
    root = find_tree_group(bot, "admin_name")
    nested = find_nested_group(root, "admin_jointocreate_name")
    assert nested is not None
    assert "admin_jtc_removechannel_name" in get_subcommand_names(nested)
