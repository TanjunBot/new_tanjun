from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from loops import create_database_backup


def test_write_defaults_file():
    path = create_database_backup._write_defaults_file("user", "pass", "host", 3306)
    try:
        with open(path) as f:
            content = f.read()
        assert "user=user" in content
        assert "password=pass" in content
    finally:
        os.unlink(path)


pytestmark = pytest.mark.asyncio


@patch("loops.create_database_backup.platform.system", return_value="Windows")
async def test_dump_database_schema_non_linux(mock_sys, capsys):
    await create_database_backup.dump_database_schema("u", "p", "h", 3306, "out.sql")
    assert "non Linux" in capsys.readouterr().out


@patch("loops.create_database_backup.asyncio.create_subprocess_exec")
@patch("loops.create_database_backup.platform.system", return_value="Linux")
async def test_dump_database_schema_success(mock_sys, mock_exec, tmp_path):
    out = tmp_path / "backup.sql"
    proc = MagicMock()
    proc.communicate = AsyncMock(return_value=(b"", b""))
    proc.returncode = 0
    mock_exec.return_value = proc
    await create_database_backup.dump_database_schema("u", "p", "h", 3306, str(out))
    mock_exec.assert_awaited_once()


@patch("loops.create_database_backup.asyncio.create_subprocess_exec", side_effect=FileNotFoundError)
@patch("loops.create_database_backup.platform.system", return_value="Linux")
async def test_dump_database_schema_mysqldump_missing(mock_sys, mock_exec, capsys, tmp_path):
    out = tmp_path / "backup.sql"
    await create_database_backup.dump_database_schema("u", "p", "h", 3306, str(out))
    assert "not found" in capsys.readouterr().out


@patch("loops.create_database_backup.asyncio.create_subprocess_exec")
@patch("loops.create_database_backup.platform.system", return_value="Linux")
async def test_dump_database_schema_error(mock_sys, mock_exec, tmp_path):
    out = tmp_path / "backup.sql"
    proc = MagicMock()
    proc.communicate = AsyncMock(return_value=(b"", b"fail"))
    proc.returncode = 1
    mock_exec.return_value = proc
    with pytest.raises(RuntimeError):
        await create_database_backup.dump_database_schema("u", "p", "h", 3306, str(out))


@patch("loops.create_database_backup.dump_database_schema", new_callable=AsyncMock)
async def test_create_database_backup_no_channel(mock_dump):
    client = MagicMock()
    client.get_channel = MagicMock(return_value=None)
    await create_database_backup.create_database_backup(client)
    mock_dump.assert_awaited_once()
    client.get_channel.assert_called_once()


@patch("loops.create_database_backup.dump_database_schema", new_callable=AsyncMock)
async def test_create_database_backup_sends_file(mock_dump):
    channel = MagicMock()
    channel.send = AsyncMock()
    client = MagicMock()
    client.get_channel = MagicMock(return_value=channel)
    await create_database_backup.create_database_backup(client)
    channel.send.assert_awaited_once()
