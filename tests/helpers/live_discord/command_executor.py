from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from tests.helpers.live_discord.command_registry import CommandRegistry, ResolvedSlashCommand
from tests.helpers.live_discord.discord_api import DiscordBotClient, DiscordUserClient, GuildContext
from tests.helpers.live_discord.interaction_client import invoke_application_command
from tests.helpers.live_discord.interaction_payload import build_fun_interaction_payload
from tests.helpers.live_discord.smoke_payload import build_smoke_interaction_payload
from tests.helpers.live_e2e.attachments import upload_channel_attachment
from tests.helpers.live_e2e.models import CommandLiveCase
from tests.helpers.live_e2e.payloads import PayloadContext, build_command_interaction_payload

if TYPE_CHECKING:
    from tests.helpers.fun_matrix import FunLiveCase
    from tests.helpers.live_discord.config import LiveE2EConfig
    from tests.helpers.live_discord.live_matrix import LiveSmokeCase


class LiveCommandExecutor:
    def __init__(
        self,
        *,
        user_client: DiscordUserClient,
        bot_client: DiscordBotClient,
        guild: GuildContext,
        config: LiveE2EConfig,
        registry: CommandRegistry,
    ) -> None:
        self._user_client = user_client
        self._bot_client = bot_client
        self._guild = guild
        self._config = config
        self._registry = registry
        self._interval_lock = asyncio.Lock()
        self._last_invoke_at: float | None = None

    def _target_user_id(self, case: FunLiveCase) -> str:
        if case.target == "bot":
            return self._config.bot_user_id
        return self._guild.owner_user_id

    async def _throttle(self) -> None:
        async with self._interval_lock:
            if self._last_invoke_at is not None:
                elapsed_ms = (asyncio.get_running_loop().time() - self._last_invoke_at) * 1000
                wait_ms = self._config.command_interval_ms - elapsed_ms
                if wait_ms > 0:
                    await asyncio.sleep(wait_ms / 1000)
            self._last_invoke_at = asyncio.get_running_loop().time()

    def _build_payload(
        self,
        resolved: ResolvedSlashCommand,
        *,
        target_id: str,
        message: str | None,
    ) -> dict:
        return build_fun_interaction_payload(
            resolved,
            application_id=self._config.application_id,
            guild=self._guild,
            target_user_id=target_id,
            message=message,
            user_param_name=self._registry.param_name(resolved, kind="user"),
            message_param_name=self._registry.param_name(resolved, kind="message"),
        )

    async def _resolve_fun(self, case: FunLiveCase) -> tuple[ResolvedSlashCommand, str]:
        resolved = await self._registry.resolve(
            group=self._config.fun_group_name,
            subcommand=case.subcommand_name,
        )
        return resolved, self._target_user_id(case)

    async def invoke_fun(self, case: FunLiveCase) -> None:
        await self._throttle()
        resolved, target_id = await self._resolve_fun(case)
        payload = self._build_payload(resolved, target_id=target_id, message=case.message)
        retry_state = {"resolved": resolved, "target_id": target_id}

        async def _refresh() -> None:
            await self._registry.refresh()
            retry_state["resolved"], retry_state["target_id"] = await self._resolve_fun(case)

        def _rebuild() -> dict:
            return self._build_payload(
                retry_state["resolved"],
                target_id=retry_state["target_id"],
                message=case.message,
            )

        await invoke_application_command(
            self._user_client._token,
            payload,
            preferred_api_version=self._config.interaction_api_version,
            retry_count=self._config.command_retry_count,
            on_refresh=_refresh,
            rebuild_payload=_rebuild,
        )

    async def invoke_smoke(self, case: LiveSmokeCase) -> None:
        await self._throttle()
        resolved = await self._registry.resolve_tree_path(case.tree_path)
        payload = build_smoke_interaction_payload(
            resolved,
            application_id=self._config.application_id,
            guild=self._guild,
            bot_user_id=self._config.bot_user_id,
        )
        retry_state = {"resolved": resolved}

        async def _refresh() -> None:
            await self._registry.refresh()
            retry_state["resolved"] = await self._registry.resolve_tree_path(case.tree_path)

        def _rebuild() -> dict:
            return build_smoke_interaction_payload(
                retry_state["resolved"],
                application_id=self._config.application_id,
                guild=self._guild,
                bot_user_id=self._config.bot_user_id,
            )

        await invoke_application_command(
            self._user_client._token,
            payload,
            preferred_api_version=self._config.interaction_api_version,
            retry_count=self._config.command_retry_count,
            on_refresh=_refresh,
            rebuild_payload=_rebuild,
        )

    def _payload_context(self, *, attachment_id: str | None = None) -> PayloadContext:
        channel_id = self._config.disposable_channel_id or self._guild.channel_id
        guild = GuildContext(
            guild_id=self._guild.guild_id,
            channel_id=channel_id,
            owner_user_id=self._guild.owner_user_id,
        )
        return PayloadContext(
            guild=guild,
            bot_user_id=self._config.bot_user_id,
            secondary_user_id=self._config.secondary_user_id,
            disposable_channel_id=self._config.disposable_channel_id,
            attachment_id=attachment_id,
        )

    async def _needs_attachment(self, case: CommandLiveCase) -> bool:
        resolved = await self._registry.resolve_tree_path(case.tree_path)
        for option in resolved.subcommand.options:
            if int(option.get("type", 0)) == 11 and option.get("required", False):
                return True
        return False

    async def invoke_command(self, case: CommandLiveCase) -> None:
        await self._throttle()
        attachment_id: str | None = None
        if await self._needs_attachment(case):
            attachment_id = await upload_channel_attachment(
                self._user_client,
                channel_id=self._payload_context().guild.channel_id,
            )
        resolved = await self._registry.resolve_tree_path(case.tree_path)
        ctx = self._payload_context(attachment_id=attachment_id)
        payload = build_command_interaction_payload(
            resolved,
            application_id=self._config.application_id,
            case=case,
            ctx=ctx,
        )
        retry_state = {"resolved": resolved, "attachment_id": attachment_id}

        async def _refresh() -> None:
            await self._registry.refresh()
            retry_state["resolved"] = await self._registry.resolve_tree_path(case.tree_path)

        def _rebuild() -> dict:
            return build_command_interaction_payload(
                retry_state["resolved"],
                application_id=self._config.application_id,
                case=case,
                ctx=self._payload_context(attachment_id=retry_state["attachment_id"]),
            )

        await invoke_application_command(
            self._user_client._token,
            payload,
            preferred_api_version=self._config.interaction_api_version,
            retry_count=self._config.command_retry_count,
            on_refresh=_refresh,
            rebuild_payload=_rebuild,
        )

    async def run_command_case(self, case: CommandLiveCase) -> dict:
        last_error: Exception | None = None
        attempts = max(1, self._config.command_retry_count + 1)
        for attempt in range(attempts):
            seen_ids = await self._bot_client.bot_message_ids(
                self._payload_context().guild.channel_id,
                self._config.bot_user_id,
            )
            try:
                await self.invoke_command(case)
                return await self._bot_client.wait_for_new_bot_response(
                    self._payload_context().guild.channel_id,
                    self._config.bot_user_id,
                    exclude_message_ids=seen_ids,
                    timeout_sec=self._config.command_wait_ms / 1000,
                    kind=case.response_kind,
                )
            except Exception as exc:
                last_error = exc
                if attempt + 1 >= attempts:
                    break
                await asyncio.sleep(1.0 + attempt)
        assert last_error is not None
        raise last_error

    async def run_smoke_case(self, case: LiveSmokeCase) -> dict:
        command_case = CommandLiveCase(tree_path=case.tree_path)
        return await self.run_command_case(command_case)

    async def run_fun_case(self, case: FunLiveCase) -> dict:
        last_error: Exception | None = None
        attempts = max(1, self._config.command_retry_count + 1)
        for attempt in range(attempts):
            seen_ids = await self._bot_client.bot_message_ids(
                self._guild.channel_id,
                self._config.bot_user_id,
            )
            try:
                await self.invoke_fun(case)
                result = await self._bot_client.wait_for_new_bot_response(
                    self._guild.channel_id,
                    self._config.bot_user_id,
                    exclude_message_ids=seen_ids,
                    timeout_sec=self._config.command_wait_ms / 1000,
                    kind="embed",
                )
                embed = result.get("embed")
                assert embed is not None
                return embed
            except Exception as exc:
                last_error = exc
                if attempt + 1 >= attempts:
                    break
                await asyncio.sleep(1.0 + attempt)
        assert last_error is not None
        raise last_error
