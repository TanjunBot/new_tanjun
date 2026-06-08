from __future__ import annotations

import asyncio
import contextlib
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from tests.helpers.live_discord.config import ROOT, load_live_e2e_config
from tests.helpers.live_discord.discord_api import DiscordBotClient
from tests.helpers.live_discord.discord_api_sync import fetch_bot_user
from tests.helpers.live_discord.e2e_database import (
    apply_test_database_env,
    ensure_test_mariadb_running,
    use_test_database,
)

_READY_POLL_SEC = 2.0


class E2EBotProcess:
    def __init__(
        self,
        *,
        bot_token: str,
        application_id: str,
        fun_group_name: str,
        required_command_roots: tuple[str, ...],
        ready_file: Path,
        startup_timeout_sec: float,
        command_sync_timeout_sec: float,
        guild_id: str | None,
    ) -> None:
        self._bot_token = bot_token
        self._application_id = application_id
        self._fun_group_name = fun_group_name
        self._required_command_roots = required_command_roots
        self._ready_file = ready_file
        self._startup_timeout_sec = startup_timeout_sec
        self._command_sync_timeout_sec = command_sync_timeout_sec
        self._guild_id = guild_id
        self._proc: subprocess.Popen[bytes] | None = None
        self._log_path: Path | None = None
        self._log_handle: object | None = None

    @classmethod
    def from_config(cls) -> E2EBotProcess:
        config = load_live_e2e_config()
        ready = Path(
            os.getenv(
                "TANJUN_E2E_BOT_READY_FILE",
                str(ROOT / ".tanjun-e2e-bot-ready"),
            )
        )
        return cls(
            bot_token=config.bot_token,
            application_id=config.application_id,
            fun_group_name=config.fun_group_name,
            required_command_roots=config.required_command_roots,
            ready_file=ready,
            startup_timeout_sec=float(
                os.getenv("TANJUN_E2E_BOT_STARTUP_TIMEOUT_SEC", "180")
            ),
            command_sync_timeout_sec=float(config.command_sync_timeout_sec),
            guild_id=config.reuse_guild_id,
        )

    async def start(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            return
        self._ready_file.unlink(missing_ok=True)
        if use_test_database():
            await asyncio.to_thread(ensure_test_mariadb_running)
        env = os.environ.copy()
        env["token"] = self._bot_token
        env["applicationId"] = self._application_id
        env["TANJUN_E2E_MINIMAL_STARTUP"] = "1"
        env["SYNC_COMMANDS_ON_STARTUP"] = "true"
        env["BOT_READY_FILE"] = str(self._ready_file)
        env.setdefault("PYTHONUNBUFFERED", "1")
        if use_test_database():
            apply_test_database_env(env)
        log_path = ROOT / ".tanjun-e2e-bot.log"
        log_path.write_text("", encoding="utf-8")
        self._log_path = log_path
        self._log_handle = open(log_path, "w", encoding="utf-8")
        self._proc = subprocess.Popen(
            [sys.executable, str(ROOT / "main.py")],
            cwd=str(ROOT),
            env=env,
            stdout=self._log_handle,
            stderr=subprocess.STDOUT,
        )
        await asyncio.to_thread(self._wait_until_ready)
        await self._wait_for_commands_synced()

    def _wait_until_ready(self) -> None:
        if self._proc is None:
            raise RuntimeError("E2E bot process was not started")
        deadline = time.monotonic() + self._startup_timeout_sec
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                tail = self._read_process_output_tail()
                db_hint = (
                    "Test DB: docker compose -f docker-compose.test.yml up -d "
                    "(TANJUN_E2E_USE_TEST_DB=1 by default)."
                    if use_test_database()
                    else "Check database_* in .env or set TANJUN_E2E_USE_TEST_DB=1."
                )
                raise RuntimeError(
                    f"E2E bot process exited with code {self._proc.returncode} before ready. "
                    f"{db_hint} Last output:\n{tail}"
                )
            if self._ready_file.is_file():
                with contextlib.suppress(RuntimeError):
                    fetch_bot_user(self._bot_token)
                return
            time.sleep(_READY_POLL_SEC)
        tail = self._read_process_output_tail()
        db_hint = (
            "Test DB: docker compose -f docker-compose.test.yml up -d "
            "(TANJUN_E2E_USE_TEST_DB=1 by default)."
            if use_test_database()
            else "Check database_* in .env or set TANJUN_E2E_USE_TEST_DB=1."
        )
        raise RuntimeError(
            f"E2E bot did not become ready within {self._startup_timeout_sec:.0f}s. "
            f"{db_hint} Last output:\n{tail}"
        )

    async def _wait_for_commands_synced(self) -> None:
        client = DiscordBotClient(self._bot_token, self._application_id)
        required = set(self._required_command_roots) or {self._fun_group_name}
        await client.wait_for_application_command_names(
            required,
            guild_id=self._guild_id,
            timeout_sec=self._command_sync_timeout_sec,
        )

    def _read_process_output_tail(self, *, max_chars: int = 4000) -> str:
        log_path = getattr(self, "_log_path", None)
        if log_path is None or not log_path.is_file():
            return ""
        with contextlib.suppress(Exception):
            return log_path.read_text(encoding="utf-8", errors="replace")[-max_chars:]
        return ""

    async def stop(self) -> None:
        if self._proc is None:
            return
        if self._proc.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                self._proc.send_signal(signal.SIGTERM)
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(self._proc.wait),
                    timeout=15,
                )
            except TimeoutError:
                with contextlib.suppress(ProcessLookupError):
                    self._proc.kill()
                await asyncio.to_thread(self._proc.wait)
        self._proc = None
        if self._log_handle is not None:
            with contextlib.suppress(Exception):
                self._log_handle.close()
            self._log_handle = None
        self._ready_file.unlink(missing_ok=True)


def should_manage_bot_process() -> bool:
    raw = os.getenv("TANJUN_E2E_MANAGE_BOT")
    if raw is None:
        return True
    return raw.strip().lower() in {"1", "true", "yes", "on"}


async def ensure_e2e_bot_running() -> E2EBotProcess | None:
    if not should_manage_bot_process():
        return None
    process = E2EBotProcess.from_config()
    await process.start()
    return process
