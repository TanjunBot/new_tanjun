"""Tests for real config.Settings loaded from environment variables."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

import tests.mock_config as mock_config

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config.py"


def _base_env() -> dict[str, str]:
    mock = mock_config.patch_config_module()
    return {
        "token": mock.token,
        "applicationId": mock.applicationId,
        "adminIds": mock.config["adminIds"],
        "prefix": mock.prefix,
        "database_ip": mock.database_ip,
        "database_port": str(mock.database_port),
        "database_password": mock.database_password,
        "database_user": mock.database_user,
        "database_schema": mock.database_schema,
        "giphyAPIKey": mock.giphyAPIKey,
        "GithubAuthToken": mock.GithubAuthToken,
        "ImgBBApiKey": mock.ImgBBApiKey,
        "openAIKey": mock.openAIKey,
        "bytebin_url": mock.bytebin_url,
        "bytebin_password": mock.bytebin_password,
        "bytebin_username": mock.bytebin_username,
        "brawlstarsToken": mock.brawlstarsToken,
        "twitchSecret": mock.twitchSecret,
        "twitchId": mock.twitchId,
    }


def _load_config_module(env: dict[str, str]):
    saved_config = sys.modules.get("config")
    sys.modules.pop("config", None)
    known_keys = {
        "token",
        "applicationId",
        "adminIds",
        "prefix",
        "database_ip",
        "database_port",
        "database_password",
        "database_user",
        "database_schema",
        "giphyAPIKey",
        "GithubAuthToken",
        "ImgBBApiKey",
        "openAIKey",
        "bytebin_url",
        "bytebin_password",
        "bytebin_username",
        "brawlstarsToken",
        "twitchSecret",
        "twitchId",
        "WELCOME_EMOJI_ID",
        "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL",
        "sentry_dsn",
        "SENTRY_TRACES_SAMPLE_RATE",
        "SENTRY_ENVIRONMENT",
    }
    for key in known_keys:
        if key in env:
            os.environ[key] = env[key]
        else:
            os.environ.pop(key, None)

    spec = importlib.util.spec_from_file_location("config", CONFIG_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["config"] = module
    with patch("dotenv.load_dotenv"), tempfile.TemporaryDirectory() as tmpdir:
        previous_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            spec.loader.exec_module(module)
        finally:
            os.chdir(previous_cwd)
    return module, saved_config


def _restore_config(saved):
    sys.modules.pop("config", None)
    if saved is not None:
        sys.modules["config"] = saved
    else:
        mock_config.patch_config_module()


@pytest.fixture
def real_config_module(monkeypatch):
    env = _base_env()
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    module, saved = _load_config_module(env)
    yield module
    _restore_config(saved)


def _reload_with_env(env: dict[str, str]):
    return _load_config_module(env)


class TestSettingsClass:
    def test_settings_loads_required_fields(self, real_config_module):
        s = real_config_module.settings
        assert s.token.get_secret_value() == "mock_test_token"
        assert s.application_id == "1234567890_mock"
        assert s.prefix == "?mock?"

    def test_admin_ids_computed_from_csv(self, real_config_module):
        assert real_config_module.settings.admin_ids == [1001, 1002, 1003]

    def test_admin_ids_empty_when_blank(self, monkeypatch):
        env = _base_env()
        env["adminIds"] = "  "
        module, saved = _reload_with_env(env)
        try:
            assert module.settings.admin_ids == []
        finally:
            _restore_config(saved)

    def test_admin_ids_skips_empty_segments(self, monkeypatch):
        env = _base_env()
        env["adminIds"] = "1001,,1002, "
        module, saved = _reload_with_env(env)
        try:
            assert module.settings.admin_ids == [1001, 1002]
        finally:
            _restore_config(saved)

    def test_welcome_emoji_id_parsed(self, real_config_module):
        assert real_config_module.settings.welcome_emoji_id == 1266369876524666920

    def test_welcome_emoji_id_invalid_returns_none(self, monkeypatch):
        env = _base_env()
        env["WELCOME_EMOJI_ID"] = "not-a-number"
        module, saved = _reload_with_env(env)
        try:
            assert module.settings.welcome_emoji_id is None
        finally:
            _restore_config(saved)

    def test_database_port_default(self, monkeypatch):
        env = _base_env()
        del env["database_port"]
        module, saved = _reload_with_env(env)
        try:
            assert module.settings.database_port == 3306
        finally:
            _restore_config(saved)

    def test_openrouter_defaults(self, real_config_module):
        assert real_config_module.settings.openrouter_model == "deepseek/deepseek-v4-flash:free"

    def test_sentry_defaults_empty(self, real_config_module):
        assert real_config_module.settings.sentry_dsn == ""
        assert real_config_module.settings.sentry_traces_sample_rate == 0.0

    def test_calc_emoji_defaults(self, real_config_module):
        assert "math_add" in real_config_module.settings.calc_add

    def test_compatibility_aliases(self, real_config_module):
        assert real_config_module.token == "mock_test_token"
        assert real_config_module.applicationId == "1234567890_mock"
        assert real_config_module.adminIds == [1001, 1002, 1003]
        assert real_config_module.CALC_ADD == real_config_module.settings.calc_add
        assert real_config_module.WELCOME_EMOJI_ID == 1266369876524666920

    def test_version_constant(self, real_config_module):
        assert real_config_module.version == "1.1.4"

    def test_missing_token_exits(self, monkeypatch):
        env = _base_env()
        del env["token"]
        with pytest.raises(SystemExit) as exc:
            _reload_with_env(env)
        assert exc.value.code == 1
        _restore_config(mock_config.patch_config_module())

    def test_invalid_database_port_raises(self, monkeypatch):
        env = _base_env()
        env["database_port"] = "not-a-port"
        with pytest.raises(SystemExit):
            _reload_with_env(env)
        _restore_config(mock_config.patch_config_module())

    def test_settings_validation_error_on_missing_required(self, monkeypatch):
        env = _base_env()
        del env["prefix"]
        with pytest.raises(SystemExit):
            _reload_with_env(env)
        _restore_config(mock_config.patch_config_module())

    def test_secret_str_fields(self, real_config_module):
        s = real_config_module.settings
        assert s.database_password.get_secret_value() == "mock_db_password"
        assert s.giphy_api_key.get_secret_value() == "mock_giphy_api_key"

    def test_extra_env_ignored(self, monkeypatch):
        env = _base_env()
        env["TOTALLY_UNKNOWN_CONFIG_KEY"] = "ignored"
        module, saved = _reload_with_env(env)
        try:
            assert not hasattr(module.settings, "totally_unknown_config_key")
        finally:
            _restore_config(saved)

    def test_missing_required_attr_exits_after_settings(self, monkeypatch):
        env = _base_env()
        env["applicationId"] = ""
        with pytest.raises(SystemExit):
            _reload_with_env(env)
        _restore_config(mock_config.patch_config_module())
