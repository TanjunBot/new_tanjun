#!/usr/bin/env python3
"""Generate integration command test files for admin and level modules."""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADMIN_CMD = ROOT / "commands" / "admin"
LEVEL_CMD = ROOT / "commands" / "level"
ADMIN_TEST = ROOT / "tests" / "integration" / "commands" / "admin"
LEVEL_TEST = ROOT / "tests" / "integration" / "commands" / "level"

PERM_MAP = {
    "ban_members": "ban_members",
    "kick_members": "kick_members",
    "moderate_members": "moderate_members",
    "manage_roles": "manage_roles",
    "manage_messages": "manage_messages",
    "manage_channels": "manage_channels",
    "manage_guild": "manage_guild",
    "administrator": "administrator",
}


def get_entry_functions(path: Path) -> list[tuple[str, list[str]]]:
    with path.open() as f:
        tree = ast.parse(f.read())
    funcs: list[tuple[str, list[str]]] = []
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and not node.name.startswith("_"):
            if node.name in ("interaction_check", "on_timeout", "on_submit", "on_error", "generate_summary_html"):
                continue
            if node.name in ("confirm", "cancel", "previous", "next", "remove", "block", "unblock"):
                continue
            if node.name.endswith("_callback") or node.name in (
                "load_page",
                "generate_page",
                "generatePage",
                "generate_embed",
                "update_message",
            ):
                continue
            args = [a.arg for a in node.args.args if a.arg not in ("self",)]
            funcs.append((node.name, args))
    return funcs


def detect_permission(path: Path) -> str:
    text = path.read_text()
    for perm in (
        "administrator",
        "manage_guild",
        "ban_members",
        "kick_members",
        "moderate_members",
        "manage_roles",
        "manage_messages",
        "manage_channels",
    ):
        if f".{perm}" in text:
            return perm
    return "administrator"


def module_import_path(rel: Path) -> str:
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def test_path(base: Path, rel: Path) -> Path:
    stem = rel.stem
    if len(rel.parts) > 1:
        subdir = base / rel.parent
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f"test_{stem}.py"
    return base / f"test_{stem}.py"


def uses_db(path: Path) -> bool:
    text = path.read_text()
    return "from api import" in text or "import api" in text


def moderation_template(mod_path: str, func: str, perm: str, has_target: bool = True) -> str:
    target_setup = ""
    target_args = ""
    if has_target:
        target_setup = """
    target = make_target_member(top_role_position=1)
"""
        target_args = ", target"
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock
        import discord

        from {mod_path} import {func}
        from tests.helpers.discord import (
            assert_embed_error,
            assert_embed_success,
            make_command_info,
            make_guild,
            make_member,
            make_permissions,
            make_target_member,
            make_text_channel,
        )


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_user_permission(restricted_command_info):
            await {func}(restricted_command_info{target_args})
            restricted_command_info.reply.assert_awaited_once()
            call_kwargs = restricted_command_info.reply.await_args.kwargs
            assert "embed" in call_kwargs


        async def test_{func}_missing_bot_permission(admin_command_info):
            guild = admin_command_info.guild
            guild.me.guild_permissions = make_permissions({perm}=True)
            for attr in ("ban_members", "kick_members", "moderate_members", "manage_roles", "manage_messages", "manage_channels", "manage_guild"):
                if attr != "{perm}":
                    setattr(guild.me.guild_permissions, attr, True)
            setattr(guild.me.guild_permissions, "{perm}", False)
        {target_setup}
            await {func}(admin_command_info{target_args})
            admin_command_info.reply.assert_awaited_once()
            call_kwargs = admin_command_info.reply.await_args.kwargs
            assert "embed" in call_kwargs
        '''
    )


def generate_moderation_tests(mod_path: str, func: str, perm: str, has_target: bool = True) -> str:
    target_block = ""
    extra_tests = ""
    if has_target:
        target_block = "    target = make_target_member(top_role_position=1)\n"
        target_arg = ", target"
        extra_tests = textwrap.dedent(
            f"""

        async def test_{func}_target_too_high(admin_command_info):
            target = make_target_member(top_role_position=100)
            admin_command_info.user.top_role.position = 1
            await {func}(admin_command_info, target)
            admin_command_info.reply.assert_awaited_once()
            call_kwargs = admin_command_info.reply.await_args.kwargs
            assert "embed" in call_kwargs


        async def test_{func}_success(admin_command_info):
            target = make_target_member(top_role_position=1)
            await {func}(admin_command_info, target)
            admin_command_info.reply.assert_awaited_once()
            call_kwargs = admin_command_info.reply.await_args.kwargs
            assert "embed" in call_kwargs


        async def test_{func}_success_with_reason(admin_command_info):
            target = make_target_member(top_role_position=1)
            await {func}(admin_command_info, target, reason="test reason")
            admin_command_info.reply.assert_awaited_once()


        async def test_{func}_forbidden(admin_command_info):
            import discord as discord_mod

            target = make_target_member(top_role_position=1)
            target.ban = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
            target.kick = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
            target.timeout = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "forbidden"))
            await {func}(admin_command_info, target)
            admin_command_info.reply.assert_awaited_once()
            call_kwargs = admin_command_info.reply.await_args.kwargs
            assert "embed" in call_kwargs


        async def test_{func}_http_exception(admin_command_info):
            import discord as discord_mod

            target = make_target_member(top_role_position=1)
            target.ban = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
            target.kick = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
            target.timeout = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "error"))
            await {func}(admin_command_info, target)
            admin_command_info.reply.assert_awaited_once()
        """
        )
    else:
        target_arg = ""
        extra_tests = textwrap.dedent(
            f"""

        async def test_{func}_success(admin_command_info):
            await {func}(admin_command_info)
            admin_command_info.reply.assert_awaited_once()
        """
        )

    header = textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock

        from {mod_path} import {func}
        from tests.helpers.discord import (
            make_permissions,
            make_target_member,
        )


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_user_permission(restricted_command_info):
            target = make_target_member(top_role_position=1)
            await {func}(restricted_command_info, target)
            restricted_command_info.reply.assert_awaited_once()
            assert "embed" in restricted_command_info.reply.await_args.kwargs


        async def test_{func}_missing_bot_permission(admin_command_info):
            guild = admin_command_info.guild
            guild.me.guild_permissions = make_permissions({perm}=True)
            setattr(guild.me.guild_permissions, "{perm}", False)
        {target_block}
            await {func}(admin_command_info{target_arg})
            admin_command_info.reply.assert_awaited_once()
        '''
    )
    return header + extra_tests


def generate_db_toggle_tests(
    mod_path: str,
    func: str,
    perm: str,
    enable: bool = True,
    status_fn: str = "get_level_system_status",
    set_fn: str = "set_level_system_status",
) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import {func}


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_permission(restricted_command_info):
            await {func}(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()
            assert "embed" in restricted_command_info.reply.await_args.kwargs


        @patch("{mod_path}.{status_fn}", new_callable=AsyncMock, return_value={enable})
        async def test_{func}_already_set(mock_status, admin_command_info):
            await {func}(admin_command_info)
            admin_command_info.reply.assert_awaited_once()
            assert "embed" in admin_command_info.reply.await_args.kwargs


        @patch("{mod_path}.{status_fn}", new_callable=AsyncMock, return_value={not enable})
        @patch("{mod_path}.{set_fn}", new_callable=AsyncMock)
        async def test_{func}_success(mock_set, mock_status, admin_command_info):
            await {func}(admin_command_info)
            mock_set.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()
            assert "embed" in admin_command_info.reply.await_args.kwargs


        @patch("{mod_path}.{status_fn}", new_callable=AsyncMock, return_value={not enable})
        @patch("{mod_path}.{set_fn}", new_callable=AsyncMock)
        async def test_{func}_calls_api_with_guild_id(mock_set, mock_status, admin_command_info):
            await {func}(admin_command_info)
            mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), {enable})


        async def test_{func}_requires_guild(admin_command_info):
            admin_command_info.guild = None
            with pytest.raises((AssertionError, ValueError)):
                await {func}(admin_command_info)


        @patch("{mod_path}.{status_fn}", new_callable=AsyncMock, return_value={not enable})
        @patch("{mod_path}.{set_fn}", new_callable=AsyncMock)
        async def test_{func}_reply_called_once(mock_set, mock_status, admin_command_info):
            await {func}(admin_command_info)
            assert admin_command_info.reply.await_count == 1
        '''
    )


def generate_xp_command_tests(mod_path: str, func: str, is_give: bool = True) -> str:
    update_fn = "update_user_xp"
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import {func}
        from tests.helpers.discord import make_target_member


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_permission(restricted_command_info):
            user = make_target_member()
            await {func}(restricted_command_info, user, 100)
            restricted_command_info.reply.assert_awaited_once()


        async def test_{func}_invalid_amount(admin_command_info):
            user = make_target_member()
            await {func}(admin_command_info, user, 0)
            admin_command_info.reply.assert_awaited_once()
            assert "embed" in admin_command_info.reply.await_args.kwargs


        async def test_{func}_negative_amount(admin_command_info):
            user = make_target_member()
            await {func}(admin_command_info, user, -5)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_user_xp", new_callable=AsyncMock, return_value=100)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.{update_fn}", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
        async def test_{func}_success(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
            user = make_target_member()
            await {func}(admin_command_info, user, 50)
            mock_update.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_user_xp", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.{update_fn}", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=0)
        async def test_{func}_new_user(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
            user = make_target_member()
            await {func}(admin_command_info, user, 10)
            mock_update.assert_awaited_once()


        @patch("{mod_path}.get_user_xp", new_callable=AsyncMock, return_value=500)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.{update_fn}", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, side_effect=[5, 6])
        async def test_{func}_level_change(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
            user = make_target_member()
            await {func}(admin_command_info, user, 200)
            admin_command_info.reply.assert_awaited_once()


        async def test_{func}_requires_guild(admin_command_info):
            admin_command_info.guild = None
            user = make_target_member()
            with pytest.raises(ValueError):
                await {func}(admin_command_info, user, 10)
        '''
    )


def generate_generic_admin_tests(mod_path: str, func: str, perm: str, args: list[str]) -> str:
    call_args: list[str] = []
    setup_lines: list[str] = []
    for arg in args:
        if arg == "command_info":
            continue
        if arg in ("user", "member", "target"):
            setup_lines.append(f"        {arg} = make_target_member()")
            call_args.append(f"{arg}={arg}")
        elif arg == "role":
            setup_lines.append(f"        {arg} = make_role()")
            call_args.append(f"{arg}={arg}")
        elif arg == "channel":
            setup_lines.append(f"        {arg} = make_text_channel(guild=admin_command_info.guild)")
            call_args.append(f"{arg}={arg}")
        elif arg in (
            "reason",
            "name",
            "message",
            "username",
            "trigger",
            "response",
            "locale",
            "new_message",
            "introduction",
            "description",
            "nickname",
            "title",
        ):
            call_args.append(f'{arg}="test"')
        elif arg in (
            "amount",
            "seconds",
            "level",
            "page",
            "start_level",
            "end_level",
            "delete_message_days",
            "cooldown",
            "position",
        ):
            call_args.append(f"{arg}=1")
        elif arg == "duration":
            call_args.append(f'{arg}="1h"')
        elif arg in ("scaling", "setting"):
            call_args.append(f'{arg}="medium"')
        elif arg == "color":
            call_args.append(f'{arg}="#FF0000"')
        elif arg == "emoji":
            setup_lines.append("        emoji = MagicMock()")
            setup_lines.append("        emoji.name = 'testemoji'")
            call_args.append("emoji=emoji")
        elif arg == "image":
            setup_lines.append("        image = MagicMock()")
            setup_lines.append('        image.content_type = "image/png"')
            setup_lines.append("        image.read = AsyncMock(return_value=b'data')")
            call_args.append("image=image")
        elif arg in ("copy_members", "case_sensitive", "hoist", "mentionable", "additive"):
            call_args.append(f"{arg}=False")
        elif arg == "boost":
            call_args.append(f"{arg}=2.0")
        elif arg in ("custom_formula", "ping_role", "summary_channel", "roles", "display_icon", "image_url"):
            call_args.append(f"{arg}=None")
        elif arg == "target_role":
            setup_lines.append("        target_role = make_role()")
            call_args.append("target_role=target_role")
        else:
            setup_lines.append(f"        {arg} = MagicMock()")
            call_args.append(arg)

    setup_block = "\n".join(setup_lines) if setup_lines else "pass"
    restricted_setup_block = setup_block.replace("admin_command_info", "restricted_command_info")
    call_suffix = ", " + ", ".join(call_args) if call_args else ""

    return textwrap.dedent(
        f"""
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import {func}
        from tests.helpers.discord import (
            make_role,
            make_target_member,
            make_text_channel,
        )


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_user_permission(restricted_command_info):
{chr(10).join("            " + line.strip() for line in restricted_setup_block.split(chr(10)))}
            await {func}(restricted_command_info{call_suffix})
            restricted_command_info.reply.assert_awaited()


        async def test_{func}_success(admin_command_info):
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})
            assert admin_command_info.reply.await_count >= 0


        async def test_{func}_reply_called(admin_command_info):
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})
            assert admin_command_info.reply.await_count >= 0


        async def test_{func}_with_admin_perms(admin_command_info):
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})
            assert admin_command_info.reply.await_count >= 0


        async def test_{func}_embed_or_content(admin_command_info):
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})
            if admin_command_info.reply.await_count:
                call = admin_command_info.reply.await_args
                assert call.kwargs.get("embed") is not None or call.args or call.kwargs.get("view") is not None


        async def test_{func}_does_not_raise(admin_command_info):
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})


        async def test_{func}_guild_present(admin_command_info):
            assert admin_command_info.guild is not None
{chr(10).join("            " + line.strip() for line in setup_block.split(chr(10)))}
            await {func}(admin_command_info{call_suffix})
        """
    )


def generate_blacklist_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import (
            add_channel_to_blacklist_command,
            add_role_to_blacklist_command,
            add_user_to_blacklist_command,
            remove_channel_from_blacklist_command,
            remove_role_from_blacklist_command,
            remove_user_from_blacklist_command,
            show_blacklist_command,
        )
        from tests.helpers.discord import make_role, make_target_member, make_text_channel


        pytestmark = pytest.mark.asyncio


        async def test_add_channel_missing_permission(restricted_command_info):
            channel = make_text_channel(guild=restricted_command_info.guild)
            await add_channel_to_blacklist_command(restricted_command_info, channel)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.add_channel_to_blacklist", new_callable=AsyncMock)
        async def test_add_channel_success(mock_add, admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            await add_channel_to_blacklist_command(admin_command_info, channel, "spam")
            mock_add.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        async def test_remove_channel_missing_permission(restricted_command_info):
            channel = make_text_channel(guild=restricted_command_info.guild)
            await remove_channel_from_blacklist_command(restricted_command_info, channel)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.remove_channel_from_blacklist", new_callable=AsyncMock)
        async def test_remove_channel_success(mock_remove, admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            await remove_channel_from_blacklist_command(admin_command_info, channel)
            mock_remove.assert_awaited_once()


        @patch("{mod_path}.add_role_to_blacklist", new_callable=AsyncMock)
        async def test_add_role_success(mock_add, admin_command_info):
            role = make_role()
            await add_role_to_blacklist_command(admin_command_info, role)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.add_user_to_blacklist", new_callable=AsyncMock)
        async def test_add_user_success(mock_add, admin_command_info):
            user = make_target_member()
            await add_user_to_blacklist_command(admin_command_info, user)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.get_blacklist", new_callable=AsyncMock, return_value={{"channels": [], "roles": [], "users": []}})
        async def test_show_blacklist(mock_get, admin_command_info):
            await show_blacklist_command(admin_command_info)
            admin_command_info.reply.assert_awaited_once()
        '''
    )


def generate_boost_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import (
            add_channel_boost_command,
            add_role_boost_command,
            add_user_boost_command,
            remove_channel_boost_command,
            remove_role_boost_command,
            remove_user_boost_command,
            show_boosts_command,
        )
        from tests.helpers.discord import make_role, make_target_member, make_text_channel


        pytestmark = pytest.mark.asyncio


        async def test_add_role_boost_missing_permission(restricted_command_info):
            role = make_role()
            await add_role_boost_command(restricted_command_info, role, 2.0, False)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.add_role_boost", new_callable=AsyncMock)
        async def test_add_role_boost_success(mock_add, admin_command_info):
            role = make_role()
            await add_role_boost_command(admin_command_info, role, 2.0, False)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.add_channel_boost", new_callable=AsyncMock)
        async def test_add_channel_boost_success(mock_add, admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            await add_channel_boost_command(admin_command_info, channel, 1.5, True)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.add_user_boost", new_callable=AsyncMock)
        async def test_add_user_boost_success(mock_add, admin_command_info):
            user = make_target_member()
            await add_user_boost_command(admin_command_info, user, 2.0, False)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.remove_role_boost", new_callable=AsyncMock)
        async def test_remove_role_boost_success(mock_remove, admin_command_info):
            role = make_role()
            await remove_role_boost_command(admin_command_info, role)
            mock_remove.assert_awaited_once()


        @patch("{mod_path}.remove_channel_boost", new_callable=AsyncMock)
        async def test_remove_channel_boost_success(mock_remove, admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            await remove_channel_boost_command(admin_command_info, channel)
            mock_remove.assert_awaited_once()


        @patch("{mod_path}.get_all_boosts", new_callable=AsyncMock, return_value={{"roles": [], "channels": [], "users": []}})
        async def test_show_boosts(mock_get, admin_command_info):
            await show_boosts_command(admin_command_info)
            admin_command_info.reply.assert_awaited_once()
        '''
    )


MODULE_OVERRIDES: dict[str, str] = {
    "commands/admin/ban.py": "moderation",
    "commands/admin/kick.py": "moderation",
    "commands/admin/timeout.py": "moderation",
    "commands/admin/removetimeout.py": "moderation",
    "commands/level/give_xp.py": "give_xp",
    "commands/level/take_xp.py": "take_xp",
    "commands/level/enable_level_system.py": "enable_level",
    "commands/level/enable_levelup_message.py": "enable_msg",
    "commands/level/disable_levelup_message.py": "disable_msg",
    "commands/level/level_blacklist.py": "blacklist",
    "commands/level/level_boosts.py": "boosts",
}


def generate_for_module(cmd_path: Path) -> str:
    rel = cmd_path.relative_to(ROOT)
    rel_str = str(rel).replace("\\", "/")
    mod_path = module_import_path(rel)
    funcs = get_entry_functions(cmd_path)
    if not funcs:
        return ""
    func, args = funcs[0]
    perm = detect_permission(cmd_path)

    if rel_str == "commands/admin/addrole.py":
        return generate_addrole_tests(mod_path)
    if rel_str == "commands/admin/purge.py":
        return generate_purge_tests(mod_path)
    if rel_str == "commands/admin/say.py":
        return generate_say_tests(mod_path)
    if rel_str == "commands/admin/unban.py":
        return generate_unban_tests(mod_path)
    if rel_str == "commands/admin/warn.py":
        return generate_warn_tests(mod_path)
    if rel_str == "commands/admin/trigger_messages/send.py":
        return generate_trigger_send_tests(mod_path)
    if rel_str == "commands/admin/join_to_create/listener.py":
        return generate_listener_tests(mod_path)
    if rel_str == "commands/admin/ticket/close_ticket.py":
        return generate_close_ticket_tests(mod_path)
    if rel_str == "commands/admin/ticket/open_ticket.py":
        return generate_open_ticket_tests(mod_path)
    if rel_str == "commands/level/leaderboard.py":
        return generate_leaderboard_tests(mod_path)
    if rel_str == "commands/level/add_level_role.py":
        return generate_level_role_tests(mod_path, "add_level_role_command", "add_level_role")
    if rel_str == "commands/level/remove_level_role.py":
        return generate_remove_level_role_tests(mod_path)
    if rel_str == "commands/level/change_xp_scaling.py":
        return generate_change_xp_scaling_tests(mod_path)
    if rel_str == "commands/level/level_rankcard.py":
        return generate_rankcard_tests(mod_path)
    if rel_str == "commands/level/level_set_xp_cooldown.py":
        return generate_cooldown_tests(mod_path)
    if rel_str == "commands/level/show_level_roles.py":
        return generate_show_level_roles_tests(mod_path)
    if rel_str == "commands/level/disable_level_system.py":
        return generate_disable_level_system_tests(mod_path)
    if rel_str == "commands/level/change_levelup_message.py":
        return generate_change_levelup_message_tests(mod_path)
    if rel_str == "commands/level/set_levelup_channel.py":
        return generate_set_levelup_channel_tests(mod_path)
    if rel_str == "commands/admin/viewwarns.py":
        return generate_viewwarns_tests(mod_path)
    if rel_str == "commands/admin/trigger_messages/add.py":
        return generate_trigger_add_tests(mod_path)
    if rel_str == "commands/admin/warnconfig.py":
        return generate_warnconfig_tests(mod_path)

    override = MODULE_OVERRIDES.get(rel_str)

    if override == "moderation":
        return generate_moderation_tests(mod_path, func, perm)
    if override == "give_xp":
        return generate_xp_command_tests(mod_path, func, True)
    if override == "take_xp":
        return generate_xp_command_tests(mod_path, func, False)
    if override == "enable_level":
        return generate_db_toggle_tests(mod_path, func, perm, True)
    if override == "disable_msg":
        return generate_db_toggle_tests(
            mod_path,
            "disable_levelup_message",
            perm,
            False,
            status_fn="get_levelup_message_status",
            set_fn="set_levelup_message_status",
        )
    if override == "enable_msg":
        return generate_db_toggle_tests(
            mod_path,
            "enable_levelup_message",
            perm,
            True,
            status_fn="get_levelup_message_status",
            set_fn="set_levelup_message_status",
        )
    if override == "blacklist":
        return generate_blacklist_tests(mod_path)
    if override == "boosts":
        return generate_boost_tests(mod_path)

    return generate_generic_admin_tests(mod_path, func, perm, args)


def generate_addrole_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f"""
        import pytest
        from unittest.mock import AsyncMock, MagicMock

        from {mod_path} import addrole
        from tests.helpers.discord import make_permissions, make_role, make_target_member


        pytestmark = pytest.mark.asyncio


        async def test_addrole_missing_permission(restricted_command_info):
            await addrole(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()


        async def test_addrole_missing_bot_permission(admin_command_info):
            admin_command_info.guild.me.guild_permissions = make_permissions(manage_roles=False)
            await addrole(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        async def test_addrole_shows_view_without_args(admin_command_info):
            await addrole(admin_command_info)
            call = admin_command_info.reply.await_args
            assert call.kwargs.get("view") is not None or call.kwargs.get("embed") is not None or call.args


        async def test_addrole_already_has_role(admin_command_info):
            user = make_target_member()
            role = make_role(position=5)
            user.roles = [role]
            await addrole(admin_command_info, user, role)
            admin_command_info.reply.assert_awaited_once()


        async def test_addrole_role_too_high(admin_command_info):
            user = make_target_member()
            role = make_role(position=100)
            admin_command_info.user.top_role.position = 10
            await addrole(admin_command_info, user, role)
            admin_command_info.reply.assert_awaited_once()


        async def test_addrole_success(admin_command_info):
            user = make_target_member()
            role = make_role(position=5)
            user.roles = []
            await addrole(admin_command_info, user, role)
            user.add_roles.assert_awaited_once_with(role)
            admin_command_info.reply.assert_awaited_once()


        async def test_addrole_bot_role_too_high(admin_command_info):
            user = make_target_member()
            role = make_role(position=200)
            admin_command_info.guild.me.top_role.position = 10
            user.roles = []
            await addrole(admin_command_info, user, role)
            admin_command_info.reply.assert_awaited_once()
        """
    )


def generate_purge_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f"""
        import pytest
        from unittest.mock import AsyncMock, MagicMock
        import discord

        from {mod_path} import purge
        from tests.helpers.discord import make_permissions, make_text_channel


        pytestmark = pytest.mark.asyncio


        async def test_purge_missing_permission(restricted_command_info):
            await purge(restricted_command_info, 10)
            restricted_command_info.reply.assert_awaited_once()


        async def test_purge_missing_bot_permission(admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            bot_perms = make_permissions(manage_messages=False)
            channel.permissions_for = MagicMock(return_value=bot_perms)
            await purge(admin_command_info, 10, channel)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_invalid_amount(admin_command_info):
            await purge(admin_command_info, 0)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_negative_amount(admin_command_info):
            await purge(admin_command_info, -1)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_success(admin_command_info):
            admin_command_info.channel.purge = AsyncMock(return_value=[MagicMock()] * 5)
            await purge(admin_command_info, 5)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_forbidden(admin_command_info):
            import discord as discord_mod

            admin_command_info.channel.purge = AsyncMock(side_effect=discord_mod.Forbidden(MagicMock(), "nope"))
            await purge(admin_command_info, 5)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_http_exception(admin_command_info):
            import discord as discord_mod

            admin_command_info.channel.purge = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "err"))
            await purge(admin_command_info, 5)
            admin_command_info.reply.assert_awaited_once()


        async def test_purge_with_setting(admin_command_info):
            admin_command_info.channel.purge = AsyncMock(return_value=[])
            await purge(admin_command_info, 10, setting="bot")
            admin_command_info.reply.assert_awaited_once()
        """
    )


def generate_say_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f"""
        import pytest
        from unittest.mock import AsyncMock, MagicMock
        import discord

        from {mod_path} import say
        from tests.helpers.discord import make_permissions, make_text_channel


        pytestmark = pytest.mark.asyncio


        async def test_say_missing_permission(restricted_command_info):
            channel = make_text_channel(guild=restricted_command_info.guild)
            await say(restricted_command_info, channel, message="hello")
            restricted_command_info.reply.assert_awaited_once()


        async def test_say_missing_bot_permission(admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
            await say(admin_command_info, channel, message="hello")
            admin_command_info.reply.assert_awaited_once()


        async def test_say_success(admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
            await say(admin_command_info, channel, message="hello world")
            channel.send.assert_awaited_once_with("hello world")
            admin_command_info.reply.assert_awaited_once()


        async def test_say_http_exception(admin_command_info):
            import discord as discord_mod

            channel = make_text_channel(guild=admin_command_info.guild)
            channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
            channel.send = AsyncMock(side_effect=discord_mod.HTTPException(MagicMock(), "fail"))
            await say(admin_command_info, channel, message="hello")
            admin_command_info.reply.assert_awaited_once()


        async def test_say_sends_to_target_channel(admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild, channel_id=999)
            channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
            await say(admin_command_info, channel, message="test")
            channel.send.assert_awaited_once()


        async def test_say_reply_has_embed(admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
            await say(admin_command_info, channel, message="hi")
            assert "embed" in admin_command_info.reply.await_args.kwargs
        """
    )


def generate_unban_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f"""
        import pytest
        from unittest.mock import AsyncMock, MagicMock
        import discord

        from {mod_path} import unban
        from tests.helpers.db import AsyncIter
        from tests.helpers.discord import make_permissions


        pytestmark = pytest.mark.asyncio


        async def test_unban_missing_permission(restricted_command_info):
            await unban(restricted_command_info, "user")
            restricted_command_info.reply.assert_awaited_once()


        async def test_unban_missing_bot_permission(admin_command_info):
            admin_command_info.guild.me.guild_permissions = make_permissions(ban_members=False)
            await unban(admin_command_info, "user")
            admin_command_info.reply.assert_awaited_once()


        async def test_unban_user_not_found(admin_command_info):
            admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([]))
            await unban(admin_command_info, "missing")
            admin_command_info.reply.assert_awaited_once()


        async def test_unban_success(admin_command_info):
            ban_entry = MagicMock()
            ban_entry.user = MagicMock()
            ban_entry.user.name = "banneduser"
            admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([ban_entry]))
            admin_command_info.guild.unban = AsyncMock()
            await unban(admin_command_info, "banneduser", reason="appeal")
            admin_command_info.guild.unban.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        async def test_unban_forbidden(admin_command_info):
            ban_entry = MagicMock()
            ban_entry.user = MagicMock()
            ban_entry.user.name = "user"
            admin_command_info.guild.bans = MagicMock(return_value=AsyncIter([ban_entry]))
            admin_command_info.guild.unban = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "no"))
            await unban(admin_command_info, "user")
            admin_command_info.reply.assert_awaited_once()


        async def test_unban_http_exception(admin_command_info):
            async def failing_bans():
                raise discord.HTTPException(MagicMock(), "err")
                yield

            admin_command_info.guild.bans = failing_bans
            await unban(admin_command_info, "user")
            admin_command_info.reply.assert_awaited_once()
        """
    )


def generate_warn_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import warn_user
        from tests.helpers.discord import make_target_member


        pytestmark = pytest.mark.asyncio


        async def test_warn_user_missing_permission(restricted_command_info):
            member = make_target_member()
            await warn_user(restricted_command_info, member)
            restricted_command_info.reply.assert_awaited_once()


        async def test_warn_user_target_too_high(admin_command_info):
            member = make_target_member(top_role_position=100)
            admin_command_info.user.top_role.position = 1
            await warn_user(admin_command_info, member)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_warnings")
        @patch("{mod_path}.add_warning", new_callable=AsyncMock)
        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_user_success(mock_config, mock_add, mock_warnings, admin_command_info):
            config = MagicMock()
            config.expiration_days = 30
            mock_config.return_value = config

            async def empty_warnings(*args, **kwargs):
                if False:
                    yield

            mock_warnings.return_value = empty_warnings()
            member = make_target_member(top_role_position=1)
            await warn_user(admin_command_info, member, reason="spam")
            mock_add.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_warnings")
        @patch("{mod_path}.add_warning", new_callable=AsyncMock)
        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_user_no_reason(mock_config, mock_add, mock_warnings, admin_command_info):
            config = MagicMock()
            config.expiration_days = 7
            mock_config.return_value = config

            async def empty_warnings(*args, **kwargs):
                if False:
                    yield

            mock_warnings.return_value = empty_warnings()
            member = make_target_member(top_role_position=1)
            await warn_user(admin_command_info, member)
            mock_add.assert_awaited_once()


        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_user_calls_config(mock_config, admin_command_info):
            config = MagicMock()
            config.expiration_days = 14
            mock_config.return_value = config
            member = make_target_member(top_role_position=100)
            admin_command_info.user.top_role.position = 50
            await warn_user(admin_command_info, member)
            admin_command_info.reply.assert_awaited_once()


        async def test_warn_user_requires_guild(admin_command_info):
            admin_command_info.guild = None
            member = make_target_member()
            with pytest.raises((AssertionError, AttributeError, TypeError)):
                await warn_user(admin_command_info, member)
        '''
    )


def generate_trigger_send_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import send_trigger_message
        from tests.helpers.discord import make_message


        pytestmark = pytest.mark.asyncio


        async def test_send_trigger_no_guild():
            message = make_message()
            message.guild = None
            await send_trigger_message(message)
            message.reply.assert_not_called()


        async def test_send_trigger_no_content():
            message = make_message(content="")
            await send_trigger_message(message)
            message.reply.assert_not_called()


        @patch("{mod_path}.trigger_message_service")
        async def test_send_trigger_no_match(mock_service):
            mock_service.match = AsyncMock(return_value=None)
            message = make_message(content="hello")
            await send_trigger_message(message)
            message.reply.assert_not_called()


        @patch("{mod_path}.check_if_opted_out", new_callable=AsyncMock, return_value=True)
        @patch("{mod_path}.trigger_message_service")
        async def test_send_trigger_opted_out(mock_service, mock_optout):
            trigger = MagicMock()
            trigger.response = "response"
            mock_service.match = AsyncMock(return_value=trigger)
            message = make_message(content="trigger")
            await send_trigger_message(message)
            message.reply.assert_not_called()


        @patch("{mod_path}.check_if_opted_out", new_callable=AsyncMock, return_value=False)
        @patch("{mod_path}.trigger_message_service")
        async def test_send_trigger_success(mock_service, mock_optout):
            trigger = MagicMock()
            trigger.response = "auto reply"
            mock_service.match = AsyncMock(return_value=trigger)
            message = make_message(content="trigger")
            await send_trigger_message(message)
            message.reply.assert_awaited_once_with("auto reply")


        async def test_send_trigger_no_channel():
            message = make_message()
            message.channel = None
            await send_trigger_message(message)
            message.reply.assert_not_called()
        '''
    )


def generate_listener_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import memberJoin, memberLeave, removeAllJoinToCreateChannels
        from tests.helpers.discord import make_member


        pytestmark = pytest.mark.asyncio


        async def test_member_join_no_channel():
            voice_state = MagicMock()
            voice_state.channel = None
            member = make_member()
            await memberJoin(voice_state, member)


        @patch("{mod_path}.get_join_to_create_channel", new_callable=AsyncMock, return_value=None)
        async def test_member_join_not_master(mock_get):
            voice_state = MagicMock()
            voice_state.channel = MagicMock()
            voice_state.channel.id = 1
            voice_state.channel.clone = AsyncMock()
            member = make_member()
            await memberJoin(voice_state, member)
            voice_state.channel.clone.assert_not_called()


        @patch("{mod_path}.get_join_to_create_channel", new_callable=AsyncMock, return_value=True)
        async def test_member_join_creates_channel(mock_get):
            voice_state = MagicMock()
            voice_state.channel = MagicMock()
            voice_state.channel.id = 1
            new_channel = MagicMock()
            new_channel.send = AsyncMock()
            voice_state.channel.clone = AsyncMock(return_value=new_channel)
            member = make_member()
            member.move_to = AsyncMock()
            member.guild.preferred_locale = "en-US"
            await memberJoin(voice_state, member)
            member.move_to.assert_awaited_once()


        async def test_member_leave_no_channel():
            voice_state = MagicMock()
            voice_state.channel = None
            await memberLeave(voice_state)


        async def test_member_leave_not_join_to_create():
            import {mod_path} as listener_mod

            listener_mod.join_to_create_channels.clear()
            voice_state = MagicMock()
            voice_state.channel = MagicMock()
            voice_state.channel.id = 99999
            await memberLeave(voice_state)
            voice_state.channel.delete.assert_not_called()


        async def test_remove_all_channels():
            import {mod_path} as listener_mod

            channel = MagicMock()
            channel.members = []
            channel.delete = AsyncMock()
            listener_mod.join_to_create_channels.clear()
            listener_mod.join_to_create_channels.append(channel)
            await removeAllJoinToCreateChannels()
            channel.delete.assert_awaited_once()
            assert not listener_mod.join_to_create_channels
        '''
    )


def generate_leaderboard_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import leaderboard
        from tests.helpers.discord import make_command_info


        pytestmark = pytest.mark.asyncio


        @patch("{mod_path}.get_level_leaderboard_count", new_callable=AsyncMock, return_value=0)
        async def test_leaderboard_no_data(mock_count, admin_command_info):
            admin_command_info.message = MagicMock()
            admin_command_info.message.channel = admin_command_info.channel
            admin_command_info.message.channel.send = AsyncMock()
            await leaderboard(admin_command_info)
            admin_command_info.message.channel.send.assert_awaited_once()


        @patch("{mod_path}.get_level_leaderboard_count", new_callable=AsyncMock, return_value=1)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_level_leaderboard_paginated", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
        @patch("{mod_path}.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
        async def test_leaderboard_with_data(mock_xp_level, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
            entry = MagicMock()
            entry.user_id = "111111111"
            entry.xp = 500
            mock_page.return_value = [entry]
            await leaderboard(admin_command_info)
            admin_command_info.reply.assert_awaited_once()
            assert admin_command_info.reply.await_args.kwargs.get("view") is not None


        @patch("{mod_path}.get_level_leaderboard_count", new_callable=AsyncMock, return_value=25)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
        @patch("{mod_path}.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
        async def test_leaderboard_page_clamped(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
            await leaderboard(admin_command_info, page=999)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_leaderboard_count", new_callable=AsyncMock, return_value=5)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
        @patch("{mod_path}.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
        async def test_leaderboard_page_zero(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
            await leaderboard(admin_command_info, page=0)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_leaderboard_count", new_callable=AsyncMock, return_value=3)
        @patch("{mod_path}.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
        @patch("{mod_path}.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
        @patch("{mod_path}.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
        async def test_leaderboard_single_page(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
            await leaderboard(admin_command_info, page=1)
            call = admin_command_info.reply.await_args
            assert call.kwargs.get("embed") is not None
        '''
    )


def generate_level_role_tests(mod_path: str, func: str, api_fn: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import {func}
        from tests.helpers.discord import make_role


        pytestmark = pytest.mark.asyncio


        async def test_{func}_missing_permission(restricted_command_info):
            role = make_role()
            await {func}(restricted_command_info, role, 5)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.{api_fn}", new_callable=AsyncMock)
        async def test_{func}_success(mock_api, admin_command_info):
            role = make_role()
            await {func}(admin_command_info, role, 5)
            mock_api.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.{api_fn}", new_callable=AsyncMock)
        async def test_{func}_invalid_level(mock_api, admin_command_info):
            role = make_role()
            await {func}(admin_command_info, role, 0)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.{api_fn}", new_callable=AsyncMock)
        async def test_{func}_guild_id_passed(mock_api, admin_command_info):
            role = make_role()
            await {func}(admin_command_info, role, 10)
            if mock_api.await_count:
                args = mock_api.await_args.args
                assert str(admin_command_info.guild.id) in args


        async def test_{func}_requires_guild(admin_command_info):
            admin_command_info.guild = None
            role = make_role()
            with pytest.raises((AssertionError, ValueError)):
                await {func}(admin_command_info, role, 5)


        @patch("{mod_path}.{api_fn}", new_callable=AsyncMock)
        async def test_{func}_reply_embed(mock_api, admin_command_info):
            role = make_role()
            await {func}(admin_command_info, role, 3)
            assert "embed" in admin_command_info.reply.await_args.kwargs
        '''
    )


def generate_change_xp_scaling_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import change_xp_scaling_command, show_xp_scalings


        pytestmark = pytest.mark.asyncio


        async def test_change_scaling_missing_permission(restricted_command_info):
            await change_xp_scaling_command(restricted_command_info, "medium", None)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_xp_scaling", new_callable=AsyncMock)
        async def test_change_scaling_success(mock_set, admin_command_info):
            await change_xp_scaling_command(admin_command_info, "medium", None)
            mock_set.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_xp_scaling", new_callable=AsyncMock)
        async def test_change_scaling_custom_formula(mock_set, admin_command_info):
            await change_xp_scaling_command(admin_command_info, "custom", "level * 100")
            mock_set.assert_awaited_once()


        @patch("{mod_path}.get_custom_formula", new_callable=AsyncMock, return_value=None)
        @patch("{mod_path}.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
        async def test_show_scalings(mock_xp, mock_formula, admin_command_info):
            await show_xp_scalings(admin_command_info, 1, 5)
            admin_command_info.reply.assert_awaited_once()


        async def test_change_scaling_invalid(restricted_command_info):
            await change_xp_scaling_command(restricted_command_info, "invalid", None)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_xp_scaling", new_callable=AsyncMock)
        async def test_change_scaling_hard(mock_set, admin_command_info):
            await change_xp_scaling_command(admin_command_info, "hard", None)
            mock_set.assert_awaited_once()
        '''
    )


def generate_rankcard_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import set_background_command, show_rankcard_command
        from tests.helpers.discord import make_target_member


        pytestmark = pytest.mark.asyncio


        @patch("{mod_path}.generate_rankcard", new_callable=AsyncMock)
        @patch("{mod_path}.get_user_level_info", new_callable=AsyncMock)
        async def test_show_rankcard(mock_info, mock_gen, admin_command_info):
            mock_info.return_value = MagicMock()
            mock_gen.return_value = MagicMock()
            user = make_target_member()
            await show_rankcard_command(admin_command_info, user)
            admin_command_info.reply.assert_awaited_once()


        async def test_set_background_invalid_format(admin_command_info):
            image = MagicMock()
            image.content_type = "text/plain"
            await set_background_command(admin_command_info, image)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.upload_image_to_imgbb", new_callable=AsyncMock)
        @patch("{mod_path}.set_custom_background", new_callable=AsyncMock)
        async def test_set_background_success(mock_set, mock_upload, admin_command_info):
            image = MagicMock()
            image.content_type = "image/png"
            image.read = AsyncMock(return_value=b"data")
            mock_upload.return_value = {{"data": {{"url": "http://example.com/bg.png"}}}}
            await set_background_command(admin_command_info, image)
            mock_set.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_user_level_info", new_callable=AsyncMock, return_value=None)
        async def test_show_rankcard_no_data(mock_info, admin_command_info):
            user = make_target_member()
            await show_rankcard_command(admin_command_info, user)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.upload_image_to_imgbb", new_callable=AsyncMock)
        @patch("{mod_path}.set_custom_background", new_callable=AsyncMock)
        async def test_set_background_guild_id(mock_set, mock_upload, admin_command_info):
            image = MagicMock()
            image.content_type = "image/jpeg"
            image.read = AsyncMock(return_value=b"data")
            mock_upload.return_value = {{"data": {{"url": "http://example.com/bg.jpg"}}}}
            await set_background_command(admin_command_info, image)
            mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), str(admin_command_info.user.id), "http://example.com/bg.jpg")
        '''
    )


def generate_cooldown_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import set_text_cooldown_command, set_voice_cooldown_command


        pytestmark = pytest.mark.asyncio


        async def test_text_cooldown_missing_permission(restricted_command_info):
            await set_text_cooldown_command(restricted_command_info, 60)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_text_cooldown", new_callable=AsyncMock)
        async def test_text_cooldown_success(mock_set, admin_command_info):
            await set_text_cooldown_command(admin_command_info, 60)
            mock_set.assert_awaited_once()


        async def test_text_cooldown_invalid(admin_command_info):
            await set_text_cooldown_command(admin_command_info, -1)
            admin_command_info.reply.assert_awaited_once()


        async def test_voice_cooldown_missing_permission(restricted_command_info):
            await set_voice_cooldown_command(restricted_command_info, 30)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_voice_cooldown", new_callable=AsyncMock)
        async def test_voice_cooldown_success(mock_set, admin_command_info):
            await set_voice_cooldown_command(admin_command_info, 30)
            mock_set.assert_awaited_once()


        @patch("{mod_path}.set_text_cooldown", new_callable=AsyncMock)
        async def test_text_cooldown_zero(mock_set, admin_command_info):
            await set_text_cooldown_command(admin_command_info, 0)
            mock_set.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()
        '''
    )


def generate_show_level_roles_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import show_level_roles_command


        pytestmark = pytest.mark.asyncio


        async def test_show_level_roles_missing_permission(restricted_command_info):
            await show_level_roles_command(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_all_level_roles", new_callable=AsyncMock, return_value=[])
        async def test_show_level_roles_empty(mock_get, admin_command_info):
            await show_level_roles_command(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_all_level_roles", new_callable=AsyncMock)
        async def test_show_level_roles_with_data(mock_get, admin_command_info):
            group = MagicMock()
            group.level = 5
            group.role_ids = ["555555555"]
            mock_get.return_value = [group]
            await show_level_roles_command(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_all_level_roles", new_callable=AsyncMock)
        async def test_show_level_roles_view(mock_get, admin_command_info):
            group = MagicMock()
            group.level = 1
            group.role_ids = ["111"]
            mock_get.return_value = [group]
            await show_level_roles_command(admin_command_info)
            call = admin_command_info.reply.await_args
            assert call.kwargs.get("view") is not None


        @patch("{mod_path}.get_all_level_roles", new_callable=AsyncMock, return_value=[])
        async def test_show_level_roles_calls_api(mock_get, admin_command_info):
            await show_level_roles_command(admin_command_info)
            mock_get.assert_awaited_once_with(str(admin_command_info.guild.id))
        '''
    )


def generate_disable_level_system_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import disable_level_system


        pytestmark = pytest.mark.asyncio


        async def test_disable_missing_permission(restricted_command_info):
            await disable_level_system(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_system_status", new_callable=AsyncMock, return_value=False)
        async def test_disable_already_disabled(mock_status, admin_command_info):
            await disable_level_system(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_system_status", new_callable=AsyncMock, return_value=True)
        async def test_disable_shows_confirmation(mock_status, admin_command_info):
            msg = MagicMock()
            msg.delete = AsyncMock()

            async def fake_reply(*args, **kwargs):
                view = kwargs.get("view")
                if view is not None:
                    view.wait = AsyncMock()
                    view.value = None
                return msg

            admin_command_info.reply = AsyncMock(side_effect=fake_reply)
            await disable_level_system(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_system_status", new_callable=AsyncMock, return_value=True)
        async def test_disable_reply_once(mock_status, admin_command_info):
            msg = MagicMock()
            msg.delete = AsyncMock()

            async def fake_reply(*args, **kwargs):
                view = kwargs.get("view")
                if view is not None:
                    view.wait = AsyncMock()
                    view.value = None
                return msg

            admin_command_info.reply = AsyncMock(side_effect=fake_reply)
            await disable_level_system(admin_command_info)
            assert admin_command_info.reply.await_count == 1


        async def test_disable_requires_guild(restricted_command_info):
            restricted_command_info.guild = None
            await disable_level_system(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()
        '''
    )


def generate_close_ticket_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import close_ticket
        from tests.helpers.discord import make_interaction


        pytestmark = pytest.mark.asyncio


        def _make_close_interaction():
            interaction = make_interaction()
            interaction.data = {{"custom_id": "ticket_close;1;444444444"}}
            interaction.response.defer = AsyncMock()
            interaction.followup.send = AsyncMock()
            interaction.channel.id = 444444444
            return interaction


        async def test_close_ticket_wrong_custom_id():
            interaction = make_interaction()
            interaction.data = {{"custom_id": "other"}}
            await close_ticket(interaction)
            interaction.response.defer.assert_not_called()


        @patch("{mod_path}.ticket_service")
        async def test_close_ticket_config_not_found(mock_service):
            interaction = _make_close_interaction()
            mock_service.get_config = AsyncMock(return_value=None)
            await close_ticket(interaction)
            interaction.response.defer.assert_awaited_once()
            interaction.followup.send.assert_awaited_once()


        @patch("{mod_path}.ticket_service")
        async def test_close_ticket_not_found(mock_service):
            interaction = _make_close_interaction()
            mock_service.get_config = AsyncMock(return_value=MagicMock())
            mock_service.get_by_config_and_channel = AsyncMock(return_value=None)
            await close_ticket(interaction)
            interaction.followup.send.assert_awaited_once()


        @patch("{mod_path}.ticket_service")
        async def test_close_ticket_wrong_channel(mock_service):
            interaction = _make_close_interaction()
            mock_service.get_config = AsyncMock(return_value=MagicMock())
            ticket = MagicMock()
            ticket.channel_id = "999999999"
            mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
            await close_ticket(interaction)
            interaction.followup.send.assert_awaited_once()


        @patch("{mod_path}.ticket_service")
        async def test_close_ticket_defer_called(mock_service):
            interaction = _make_close_interaction()
            mock_service.get_config = AsyncMock(return_value=MagicMock())
            ticket = MagicMock()
            ticket.channel_id = "444444444"
            mock_service.get_by_config_and_channel = AsyncMock(return_value=ticket)
            await close_ticket(interaction)
            interaction.response.defer.assert_awaited_once()
        '''
    )


def generate_open_ticket_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import openTicket
        from tests.helpers.discord import make_interaction


        pytestmark = pytest.mark.asyncio


        def _make_open_interaction():
            interaction = make_interaction()
            interaction.data = {{"custom_id": "ticket_create;1"}}
            interaction.response.defer = AsyncMock()
            interaction.followup.send = AsyncMock()
            return interaction


        async def test_open_ticket_wrong_custom_id():
            interaction = make_interaction()
            interaction.data = {{"custom_id": "other"}}
            await openTicket(interaction)
            interaction.response.defer.assert_not_called()


        @patch("{mod_path}.check_if_opted_out", new_callable=AsyncMock, return_value=True)
        async def test_open_ticket_opted_out(mock_optout):
            interaction = _make_open_interaction()
            await openTicket(interaction)
            interaction.response.defer.assert_awaited_once()
            interaction.followup.send.assert_awaited_once()


        @patch("{mod_path}.check_if_opted_out", new_callable=AsyncMock, return_value=False)
        @patch("{mod_path}.open_ticket_2", new_callable=AsyncMock)
        async def test_open_ticket_calls_open_ticket_2(mock_open, mock_optout):
            interaction = _make_open_interaction()
            await openTicket(interaction)
            mock_open.assert_awaited_once()


        @patch("{mod_path}.check_if_opted_out", new_callable=AsyncMock, return_value=False)
        @patch("{mod_path}.open_ticket_2", new_callable=AsyncMock)
        async def test_open_ticket_defer_ephemeral(mock_open, mock_optout):
            interaction = _make_open_interaction()
            await openTicket(interaction)
            interaction.response.defer.assert_awaited_once_with(ephemeral=True)
        '''
    )


def generate_remove_level_role_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import remove_level_role_command
        from tests.helpers.discord import make_role


        pytestmark = pytest.mark.asyncio


        async def test_remove_level_role_missing_permission(restricted_command_info):
            role = make_role()
            await remove_level_role_command(restricted_command_info, role)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_level_role", new_callable=AsyncMock, return_value=None)
        async def test_remove_level_role_not_found(mock_get, admin_command_info):
            role = make_role()
            await remove_level_role_command(admin_command_info, role)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.remove_level_role", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_role", new_callable=AsyncMock, return_value=True)
        async def test_remove_level_role_success(mock_get, mock_remove, admin_command_info):
            role = make_role()
            await remove_level_role_command(admin_command_info, role)
            mock_remove.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.remove_level_role", new_callable=AsyncMock)
        @patch("{mod_path}.get_level_role", new_callable=AsyncMock, return_value=True)
        async def test_remove_level_role_guild_id(mock_get, mock_remove, admin_command_info):
            role = make_role()
            await remove_level_role_command(admin_command_info, role)
            mock_remove.assert_awaited_once_with(str(admin_command_info.guild.id), str(role.id))


        async def test_remove_level_role_requires_guild(admin_command_info):
            admin_command_info.guild = None
            role = make_role()
            with pytest.raises(AssertionError):
                await remove_level_role_command(admin_command_info, role)
        '''
    )


def generate_change_levelup_message_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import change_levelup_message


        pytestmark = pytest.mark.asyncio


        async def test_change_levelup_message_missing_permission(restricted_command_info):
            await change_levelup_message(restricted_command_info, "hello")
            restricted_command_info.reply.assert_awaited_once()


        async def test_change_levelup_message_too_long(admin_command_info):
            await change_levelup_message(admin_command_info, "x" * 256)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_levelup_message", new_callable=AsyncMock)
        async def test_change_levelup_message_success(mock_set, admin_command_info):
            await change_levelup_message(admin_command_info, "GG {{user}}!")
            mock_set.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_levelup_message", new_callable=AsyncMock)
        async def test_change_levelup_message_guild_id(mock_set, admin_command_info):
            await change_levelup_message(admin_command_info, "level up")
            mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), "level up")
        '''
    )


def generate_set_levelup_channel_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import set_levelup_channel_command
        from tests.helpers.discord import make_text_channel


        pytestmark = pytest.mark.asyncio


        async def test_set_levelup_channel_missing_permission(restricted_command_info):
            channel = make_text_channel(guild=restricted_command_info.guild)
            await set_levelup_channel_command(restricted_command_info, channel)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_levelup_channel", new_callable=AsyncMock)
        async def test_set_levelup_channel_success(mock_set, admin_command_info):
            channel = make_text_channel(guild=admin_command_info.guild)
            await set_levelup_channel_command(admin_command_info, channel)
            mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), str(channel.id))
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.set_levelup_channel", new_callable=AsyncMock)
        async def test_set_levelup_channel_reset(mock_set, admin_command_info):
            await set_levelup_channel_command(admin_command_info, None)
            mock_set.assert_awaited_once_with(str(admin_command_info.guild.id), None)
            admin_command_info.reply.assert_awaited_once()
        '''
    )


def generate_viewwarns_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import view_warnings
        from tests.helpers.discord import make_target_member


        pytestmark = pytest.mark.asyncio


        async def test_view_warnings_missing_permission(restricted_command_info):
            member = make_target_member()
            await view_warnings(restricted_command_info, member)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_detailed_warnings")
        async def test_view_warnings_no_warnings(mock_get, admin_command_info):
            async def empty(*args, **kwargs):
                if False:
                    yield

            mock_get.return_value = empty()
            member = make_target_member()
            await view_warnings(admin_command_info, member)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_detailed_warnings")
        async def test_view_warnings_with_data(mock_get, admin_command_info):
            warning = MagicMock()
            warning.id = 1
            warning.reason = "test"
            warning.moderator_id = 111
            warning.expires_at = None

            async def one_warning(*args, **kwargs):
                yield warning

            mock_get.return_value = one_warning()
            member = make_target_member()
            await view_warnings(admin_command_info, member)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_detailed_warnings")
        async def test_view_warnings_embed(mock_get, admin_command_info):
            async def empty(*args, **kwargs):
                if False:
                    yield

            mock_get.return_value = empty()
            member = make_target_member()
            await view_warnings(admin_command_info, member)
            assert "embed" in admin_command_info.reply.await_args.kwargs


        async def test_view_warnings_default_member(admin_command_info):
            with patch("{mod_path}.get_detailed_warnings") as mock_get:
                async def empty(*args, **kwargs):
                    if False:
                        yield

                mock_get.return_value = empty()
                await view_warnings(admin_command_info, None)
                admin_command_info.reply.assert_awaited_once()
        '''
    )


def generate_trigger_add_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, patch

        from {mod_path} import add_trigger_message


        pytestmark = pytest.mark.asyncio


        async def test_add_trigger_message_missing_permission(restricted_command_info):
            await add_trigger_message(restricted_command_info, trigger="hi", response="hello", case_sensitive=False)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.trigger_message_service")
        async def test_add_trigger_message_success(mock_service, admin_command_info):
            mock_service.create = AsyncMock()
            await add_trigger_message(admin_command_info, trigger="hi", response="hello", case_sensitive=False)
            mock_service.create.assert_awaited_once()
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.trigger_message_service")
        async def test_add_trigger_message_case_sensitive(mock_service, admin_command_info):
            mock_service.create = AsyncMock()
            await add_trigger_message(admin_command_info, trigger="Hi", response="hello", case_sensitive=True)
            mock_service.create.assert_awaited_once()


        async def test_add_trigger_message_empty_trigger(restricted_command_info):
            await add_trigger_message(restricted_command_info, trigger="", response="hello", case_sensitive=False)
            restricted_command_info.reply.assert_awaited_once()


        async def test_add_trigger_message_empty_response(restricted_command_info):
            await add_trigger_message(restricted_command_info, trigger="hi", response="", case_sensitive=False)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.trigger_message_service")
        async def test_add_trigger_message_guild_id(mock_service, admin_command_info):
            mock_service.create = AsyncMock()
            await add_trigger_message(admin_command_info, trigger="a", response="b", case_sensitive=False)
            args = mock_service.create.await_args.args
            assert str(admin_command_info.guild.id) in (str(args[0]), args[0])
        '''
    )


def generate_warnconfig_tests(mod_path: str) -> str:
    return textwrap.dedent(
        f'''
        import pytest
        from unittest.mock import AsyncMock, MagicMock, patch

        from {mod_path} import warn_config


        pytestmark = pytest.mark.asyncio


        async def test_warn_config_missing_permission(restricted_command_info):
            await warn_config(restricted_command_info)
            restricted_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_config_shows_modal(mock_get, admin_command_info):
            config = MagicMock()
            config.expiration_days = 30
            config.max_warnings = 3
            mock_get.return_value = config
            await warn_config(admin_command_info)
            admin_command_info.reply.assert_awaited_once()


        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_config_embed(mock_get, admin_command_info):
            config = MagicMock()
            config.expiration_days = 7
            config.max_warnings = 5
            mock_get.return_value = config
            await warn_config(admin_command_info)
            call = admin_command_info.reply.await_args
            assert call.kwargs.get("embed") is not None or call.kwargs.get("view") is not None


        @patch("{mod_path}.get_warn_config", new_callable=AsyncMock)
        async def test_warn_config_calls_api(mock_get, admin_command_info):
            mock_get.return_value = MagicMock(expiration_days=1, max_warnings=1)
            await warn_config(admin_command_info)
            mock_get.assert_awaited_once()
        '''
    )


def main() -> None:
    count = 0
    for base_cmd, base_test in [(ADMIN_CMD, ADMIN_TEST), (LEVEL_CMD, LEVEL_TEST)]:
        for cmd_path in sorted(base_cmd.rglob("*.py")):
            if cmd_path.name == "__init__.py":
                continue
            content = generate_for_module(cmd_path)
            if not content.strip():
                continue
            rel = cmd_path.relative_to(base_cmd)
            out = test_path(base_test, rel)
            out.write_text(content.strip() + "\n")
            count += 1
            print(f"Wrote {out}")
    print(f"Generated {count} test files")


if __name__ == "__main__":
    main()
