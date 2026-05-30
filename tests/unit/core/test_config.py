"""Tests for config.py Settings and compatibility aliases."""

from __future__ import annotations

import config


class TestSettings:
    def test_mock_config_module_available(self):
        assert config.token == "mock_test_token"
        assert config.applicationId == "1234567890_mock"
        assert config.prefix == "?mock?"

    def test_admin_ids_parsed(self):
        assert config.adminIds == [1001, 1002, 1003]

    def test_database_settings(self):
        assert config.database_ip == "mock.db.ip.here"
        assert config.database_port == 3306
        assert config.database_user == "mock_db_user"
        assert config.database_schema == "mock_db_schema"

    def test_external_api_keys(self):
        assert config.giphyAPIKey == "mock_giphy_api_key"
        assert str(config.openAiKey) == "mock_openai_key" or config.openAiKey == "mock_openai_key"
        assert config.twitchId == "mock_twitch_id_123"
        assert config.GithubAuthToken == "mock_github_token"

    def test_version_string(self):
        assert config.version == "1.0.5-test"

    def test_calc_emoji_defaults(self):
        assert config.CALC_ADD

    def test_bytebin_config(self):
        assert config.bytebin_url == "https://mock.bytebin.url"
        assert config.bytebin_username == "mock_bytebin_user"

    def test_activity_template(self):
        assert "{version}" in config.activity

    def test_prefix_alias(self):
        assert config.prefix == "?mock?"

    def test_github_token(self):
        assert config.GithubAuthToken == "mock_github_token"
