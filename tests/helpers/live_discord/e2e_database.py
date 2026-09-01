from __future__ import annotations

import os
import socket
import subprocess
import time
from pathlib import Path

from tests.helpers.live_discord.config import ROOT

_COMPOSE_FILE = ROOT / "docker-compose.test.yml"
_DEFAULT_HOST = "127.0.0.1"
_DEFAULT_PORT = 3307
_DEFAULT_USER = "test_user"
_DEFAULT_PASSWORD = "test_password"
_DEFAULT_SCHEMA = "tanjun_test"


def use_test_database() -> bool:
    raw = os.getenv("TANJUN_E2E_USE_TEST_DB")
    if raw is None:
        return True
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def test_database_settings() -> dict[str, str]:
    return {
        "database_ip": os.getenv("TANJUN_E2E_DB_HOST", os.getenv("TANJUN_TEST_DB_HOST", _DEFAULT_HOST)),
        "database_port": os.getenv(
            "TANJUN_E2E_DB_PORT",
            os.getenv("TANJUN_TEST_DB_PORT", str(_DEFAULT_PORT)),
        ),
        "database_user": os.getenv(
            "TANJUN_E2E_DB_USER",
            os.getenv("TANJUN_TEST_DB_USER", _DEFAULT_USER),
        ),
        "database_password": os.getenv(
            "TANJUN_E2E_DB_PASSWORD",
            os.getenv("TANJUN_TEST_DB_PASSWORD", _DEFAULT_PASSWORD),
        ),
        "database_schema": os.getenv(
            "TANJUN_E2E_DB_NAME",
            os.getenv("TANJUN_TEST_DB_NAME", _DEFAULT_SCHEMA),
        ),
    }


def apply_test_database_env(env: dict[str, str]) -> dict[str, str]:
    settings = test_database_settings()
    env["database_ip"] = settings["database_ip"]
    env["database_port"] = settings["database_port"]
    env["database_user"] = settings["database_user"]
    env["database_password"] = settings["database_password"]
    env["database_schema"] = settings["database_schema"]
    env["MARIADB_HOST"] = settings["database_ip"]
    env["MARIADB_PORT"] = settings["database_port"]
    env["MARIADB_USER"] = settings["database_user"]
    env["MARIADB_PASSWORD"] = settings["database_password"]
    env["MARIADB_DATABASE"] = settings["database_schema"]
    return env


def _port_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except OSError:
        return False


def _database_accepts_credentials(settings: dict[str, str]) -> bool:
    try:
        import asyncmy
    except ImportError:
        return _port_open(settings["database_ip"], int(settings["database_port"]))

    async def _probe() -> bool:
        conn = await asyncmy.connect(
            host=settings["database_ip"],
            port=int(settings["database_port"]),
            user=settings["database_user"],
            password=settings["database_password"],
            db=settings["database_schema"],
            connect_timeout=3,
        )
        try:
            await conn.ensure_closed()
        finally:
            conn.close()
        return True

    try:
        import asyncio

        return asyncio.run(_probe())
    except Exception:
        return False


def ensure_test_mariadb_running(*, timeout_sec: float = 90.0) -> None:
    settings = test_database_settings()
    host = settings["database_ip"]
    port = int(settings["database_port"])
    if _database_accepts_credentials(settings):
        return
    if not _COMPOSE_FILE.is_file():
        raise RuntimeError(
            f"MariaDB is not reachable at {host}:{port} and {_COMPOSE_FILE} is missing. "
            "Start your DB or set TANJUN_E2E_USE_TEST_DB=0 with working database_* in .env."
        )
    subprocess.run(
        ["docker", "compose", "-f", str(_COMPOSE_FILE), "up", "-d", "mariadb-test"],
        cwd=str(ROOT),
        check=True,
    )
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _port_open(host, port):
            time.sleep(2)
            return
        time.sleep(2)
    raise RuntimeError(
        f"Timed out waiting for test MariaDB at {host}:{port}. "
        f"Try: docker compose -f docker-compose.test.yml up -d"
    )
