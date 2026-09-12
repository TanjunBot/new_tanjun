from __future__ import annotations

import os
import stat

import tests.mock_config as mock_config

mock_config.patch_config_module()

from extensions.administration import _mysql_defaults_file  # noqa: E402


def test_mysql_defaults_file_writes_credentials() -> None:
    path = _mysql_defaults_file('user', 'pass', 'host', 3306)
    try:
        with open(path) as handle:
            content = handle.read()
        assert 'user=user' in content
        assert 'password=pass' in content
        assert 'host=host' in content
        assert 'port=3306' in content
        assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    finally:
        os.unlink(path)


def test_mysql_defaults_file_rejects_newlines() -> None:
    try:
        _mysql_defaults_file('user', 'bad\npassword', 'host', 3306)
    except ValueError as exc:
        assert "newlines" in str(exc)
    else:
        raise AssertionError("newline-containing credentials must be rejected")
