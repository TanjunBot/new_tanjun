from __future__ import annotations

import asyncio
import atexit
import contextlib
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable

from tests.helpers.live_discord.command_executor import LiveCommandExecutor
from tests.helpers.live_discord.command_registry import CommandRegistry
from tests.helpers.live_discord.config import LiveE2EConfig, load_live_e2e_config
from tests.helpers.live_discord.discord_api import DiscordBotClient, DiscordUserClient, GuildContext
from tests.helpers.live_discord.chromium_launch import launch_live_e2e_browser
from tests.helpers.live_discord.discord_api_sync import bot_is_guild_member
from tests.helpers.live_discord.discord_api_sync import create_guild as sync_create_guild
from tests.helpers.live_discord.discord_api_sync import default_text_channel_id
from tests.helpers.live_discord.discord_api_sync import delete_guild as sync_delete_guild
from tests.helpers.live_discord.discord_api_sync import fetch_bot_user
from tests.helpers.live_discord.discord_api_sync import fetch_me as sync_fetch_me
from tests.helpers.live_discord.rate_limit import DiscordRateLimitedError
from tests.helpers.live_discord.playwright_ui import (
    authorize_bot_to_guild,
    create_guild_via_ui,
    open_channel,
)
from tests.helpers.live_discord.token_capture import read_user_token_from_auth_state, resolve_user_token

if TYPE_CHECKING:
    from playwright.sync_api import Page


@dataclass
class LiveGuildSession:
    config: LiveE2EConfig
    guild: GuildContext
    user_display_name: str
    user_username: str
    bot_display_name: str
    bot_username: str
    _user_client: DiscordUserClient
    _bot_client: DiscordBotClient
    _command_executor: LiveCommandExecutor
    _playwright_page: Page | None = None
    _playwright_cm: object | None = None
    _browser_cm: object | None = None
    _context_cm: object | None = None
    _guild_deleted: bool = False
    _playwright_executor: ThreadPoolExecutor | None = field(default=None, repr=False)

    async def _run_playwright(self, fn: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
        if self._playwright_executor is None:
            raise RuntimeError("Playwright executor is not initialized")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._playwright_executor,
            lambda: fn(*args, **kwargs),
        )

    @classmethod
    async def create(
        cls,
        *,
        skip_api_command_ready_check: bool = False,
    ) -> LiveGuildSession:
        config = load_live_e2e_config()
        if not config.auth_state_path.is_file():
            raise RuntimeError(
                f"Playwright auth state missing at {config.auth_state_path}. "
                "Run: python scripts/e2e_discord_login.py"
            )

        use_api_only = cls._should_use_api_only_bootstrap(config)
        executor: ThreadPoolExecutor | None = None

        try:
            if use_api_only:
                session = await cls._bootstrap_api_only(config)
            else:
                executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="live-e2e-pw")
                loop = asyncio.get_running_loop()
                session = await asyncio.wait_for(
                    loop.run_in_executor(executor, cls._bootstrap_playwright, config),
                    timeout=config.timeouts.bootstrap_sec,
                )
                session._playwright_executor = executor
                if config.debug_screenshots_dir is None:
                    await session._run_playwright(session.close_playwright)
                    session._playwright_executor.shutdown(wait=False, cancel_futures=True)
                    session._playwright_executor = None
        except TimeoutError as exc:
            if executor is not None:
                executor.shutdown(wait=False, cancel_futures=True)
            raise RuntimeError(
                f"Live E2E bootstrap timed out after {config.timeouts.bootstrap_sec:.0f}s. "
                "Increase TANJUN_E2E_BOOTSTRAP_TIMEOUT_SEC or run with TANJUN_E2E_HEADLESS=false."
            ) from exc
        except DiscordRateLimitedError:
            if executor is not None:
                executor.shutdown(wait=False, cancel_futures=True)
            raise
        except Exception:
            if executor is not None:
                executor.shutdown(wait=False, cancel_futures=True)
            raise

        session._register_cleanup_handlers()
        await session._bot_client.wait_for_bot_member(
            session.guild.guild_id,
            config.bot_user_id,
            timeout_sec=90,
        )
        if not skip_api_command_ready_check and not config.skip_command_sync:
            await session._wait_for_fun_commands_api(config)
        await session._command_executor._registry.refresh()
        return session

    @staticmethod
    def _should_use_api_only_bootstrap(config: LiveE2EConfig) -> bool:
        if config.bootstrap_mode == "playwright":
            return False
        if config.bootstrap_mode == "api_only":
            if not config.reuse_guild_id or not config.reuse_channel_id:
                raise RuntimeError(
                    "TANJUN_E2E_BOOTSTRAP_MODE=api_only requires "
                    "TANJUN_E2E_GUILD_ID and TANJUN_E2E_CHANNEL_ID."
                )
            return True
        if not config.reuse_guild_id or not config.reuse_channel_id:
            return False
        token = config.user_token or read_user_token_from_auth_state(config.auth_state_path)
        if not token:
            return False
        return bot_is_guild_member(
            config.bot_token,
            config.reuse_guild_id,
            config.bot_user_id,
        )

    @classmethod
    def _resolve_user_token(cls, config: LiveE2EConfig, page: Page | None = None) -> str:
        if config.user_token.strip():
            return config.user_token.strip()
        from_file = read_user_token_from_auth_state(config.auth_state_path)
        if from_file:
            return from_file.strip()
        if page is None:
            raise RuntimeError(
                "Could not read user token from auth state. "
                "Run: python scripts/e2e_discord_login.py"
            )
        return resolve_user_token(
            page,
            configured_token=config.user_token,
            auth_state_path=config.auth_state_path,
            timeout_ms=config.timeouts.token_capture_ms,
            app_gate_timeout_ms=config.timeouts.app_gate_ms,
        )

    @classmethod
    async def _bootstrap_api_only(cls, config: LiveE2EConfig) -> LiveGuildSession:
        user_token = cls._resolve_user_token(config)
        user_client = DiscordUserClient(user_token)
        me = sync_fetch_me(user_token)
        DiscordUserClient.ensure_human_account(me)

        owner_id = str(me["id"])
        user_username = str(me.get("username") or "e2e")
        display = config.user_display_name or str(me.get("global_name") or user_username)
        bot_me = fetch_bot_user(config.bot_token)
        bot_username = str(bot_me.get("username") or "bot")
        bot_display = str(bot_me.get("global_name") or bot_username)

        guild_id = config.reuse_guild_id
        channel_id = config.reuse_channel_id
        assert guild_id and channel_id

        if not bot_is_guild_member(config.bot_token, guild_id, config.bot_user_id):
            await user_client.authorize_bot_to_guild(
                application_id=config.application_id,
                guild_id=guild_id,
                permissions=config.bot_invite_permissions,
            )

        guild = GuildContext(guild_id=guild_id, channel_id=channel_id, owner_user_id=owner_id)
        bot_client = DiscordBotClient(config.bot_token, config.application_id)
        registry = CommandRegistry(bot_client, guild_id=guild_id)
        command_executor = LiveCommandExecutor(
            user_client=user_client,
            bot_client=bot_client,
            guild=guild,
            config=config,
            registry=registry,
        )
        return cls(
            config=config,
            guild=guild,
            user_display_name=display,
            user_username=user_username,
            bot_display_name=bot_display,
            bot_username=bot_username,
            _user_client=user_client,
            _bot_client=bot_client,
            _command_executor=command_executor,
        )

    @classmethod
    def _bootstrap_playwright(cls, config: LiveE2EConfig) -> LiveGuildSession:
        from playwright.sync_api import sync_playwright

        playwright = sync_playwright().start()
        browser, context = launch_live_e2e_browser(
            playwright,
            headless=config.headless,
            auth_state_path=str(config.auth_state_path),
            timeouts=config.timeouts,
        )
        page = context.new_page()

        user_token = cls._resolve_user_token(config, page)
        user_client = DiscordUserClient(user_token)
        me = sync_fetch_me(user_token)
        DiscordUserClient.ensure_human_account(me)

        owner_id = str(me["id"])
        user_username = str(me.get("username") or "e2e")
        display = config.user_display_name or str(me.get("global_name") or user_username)
        bot_me = fetch_bot_user(config.bot_token)
        bot_username = str(bot_me.get("username") or "bot")
        bot_display = str(bot_me.get("global_name") or bot_username)

        if config.reuse_guild_id and config.reuse_channel_id:
            guild_id, channel_id = config.reuse_guild_id, config.reuse_channel_id
        else:
            stamp = datetime.now(UTC).strftime("%m%d-%H%M")
            guild_name = f"{config.guild_name_prefix}-{stamp}-{uuid.uuid4().hex[:6]}"
            guild_id, channel_id = cls._create_guild(
                browser,
                page,
                user_token=user_token,
                guild_name=guild_name,
                timeouts=config.timeouts,
            )
        guild = GuildContext(guild_id=guild_id, channel_id=channel_id, owner_user_id=owner_id)

        authorize_bot_to_guild(
            page,
            browser=browser,
            auth_state_path=str(config.auth_state_path),
            user_token=user_token,
            bot_token=config.bot_token,
            bot_user_id=config.bot_user_id,
            application_id=config.application_id,
            guild_id=guild_id,
            permissions=config.bot_invite_permissions,
            oauth_headless=config.oauth_headless,
            timeouts=config.timeouts,
        )
        if config.debug_screenshots_dir is not None:
            open_channel(page, guild_id, channel_id, timeouts=config.timeouts)

        bot_client = DiscordBotClient(config.bot_token, config.application_id)
        registry = CommandRegistry(bot_client, guild_id=guild_id)
        command_executor = LiveCommandExecutor(
            user_client=user_client,
            bot_client=bot_client,
            guild=guild,
            config=config,
            registry=registry,
        )
        return cls(
            config=config,
            guild=guild,
            user_display_name=display,
            user_username=user_username,
            bot_display_name=bot_display,
            bot_username=bot_username,
            _user_client=user_client,
            _bot_client=bot_client,
            _command_executor=command_executor,
            _playwright_page=page,
            _playwright_cm=playwright,
            _browser_cm=browser,
            _context_cm=context,
        )

    async def _wait_for_fun_commands_api(self, config: LiveE2EConfig) -> None:
        required = set(config.required_command_roots) or {config.fun_group_name}
        api_timeout = float(config.command_sync_timeout_sec)
        await self._bot_client.wait_for_application_command_names(
            required,
            guild_id=self.guild.guild_id,
            timeout_sec=api_timeout,
        )

    @staticmethod
    def _create_guild(
        browser: object,
        page: Page,
        *,
        user_token: str,
        guild_name: str,
        timeouts,
    ) -> tuple[str, str]:
        with contextlib.suppress(RuntimeError):
            created = sync_create_guild(user_token, guild_name)
            return str(created["id"]), default_text_channel_id(created)

        return create_guild_via_ui(page, guild_name, timeouts=timeouts)

    def _register_cleanup_handlers(self) -> None:
        if self.config.reuse_guild_id:
            return
        token = self._user_client._token
        guild_id = self.guild.guild_id

        def _cleanup() -> None:
            with contextlib.suppress(Exception):
                sync_delete_guild(token, guild_id)

        atexit.register(_cleanup)

    async def run_matrix_case(self, case) -> dict:
        from tests.helpers.command_matrix.harness import build_e2e_live_case
        from tests.helpers.command_matrix.models import MatrixCase

        if not isinstance(case, MatrixCase):
            raise TypeError("run_matrix_case expects MatrixCase")
        command_case = build_e2e_live_case(case)
        result = await self.run_command_case(command_case)
        if self._playwright_page is not None and case.group in {"setup_name", "games_name"}:
            from tests.helpers.live_discord.playwright_components import click_game_button, run_wizard_flow

            if case.group == "setup_name":
                await self._run_playwright(run_wizard_flow, self._playwright_page, steps=2)
            else:
                await self._run_playwright(click_game_button, self._playwright_page)
        return result

    async def run_command_case(self, case) -> dict:
        from tests.helpers.live_e2e.cleanup import run_setup, run_teardown
        from tests.helpers.live_e2e.models import CommandLiveCase
        from tests.helpers.live_e2e.registry import resolve_case_placeholders

        if not isinstance(case, CommandLiveCase):
            case = CommandLiveCase(tree_path=str(getattr(case, "tree_path", case)))
        state: dict[str, Any] = {}
        await run_setup(case.setup, self, state)
        case = resolve_case_placeholders(
            case,
            owner_user_id=self.guild.owner_user_id,
            secondary_user_id=self.config.secondary_user_id,
            bot_user_id=self.config.bot_user_id,
            main_channel_id=self.guild.channel_id,
            disposable_channel_id=self.config.disposable_channel_id,
            temp_role_id=state.get("temp_role_id"),
            attachment_id=state.get("attachment_id"),
        )
        try:
            return await self._command_executor.run_command_case(case)
        finally:
            await run_teardown(case.teardown, self, state)

    async def run_fun_case(self, case) -> dict:
        return await self._command_executor.run_fun_case(case)

    async def run_smoke_case(self, case) -> dict:
        return await self._command_executor.run_smoke_case(case)

    async def delete_guild(self) -> None:
        if self.config.reuse_guild_id or self._guild_deleted or self.guild.guild_id == "0":
            return
        self._guild_deleted = True
        await self._user_client.delete_guild(self.guild.guild_id)

    def close_playwright(self) -> None:
        if self._context_cm is not None:
            self._context_cm.close()
            self._context_cm = None
        if self._browser_cm is not None:
            self._browser_cm.close()
            self._browser_cm = None
        if self._playwright_cm is not None:
            self._playwright_cm.stop()
            self._playwright_cm = None
        self._playwright_page = None

    async def teardown(self) -> None:
        if self._playwright_executor is not None:
            await self._run_playwright(self.close_playwright)
            self._playwright_executor.shutdown(wait=False, cancel_futures=True)
            self._playwright_executor = None
        elif self._playwright_page is not None or self._playwright_cm is not None:
            self.close_playwright()
        await self.delete_guild()
