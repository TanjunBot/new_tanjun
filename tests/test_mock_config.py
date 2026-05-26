"""Tests for the mock_config module."""

import sys

from tests.mock_config import patch_config_module


class TestMockConfig:
    def test_patch_config_module_sets_sys_modules(self):
        mock = patch_config_module()
        assert "config" in sys.modules
        assert sys.modules["config"] is mock

    def test_mock_config_has_required_attributes(self):
        mock = patch_config_module()
        assert mock.version == "1.0.5-test"
        assert mock.token == "mock_test_token"
        assert mock.applicationId == "1234567890_mock"
        assert mock.adminIds == [1001, 1002, 1003]
        assert mock.database_ip == "mock.db.ip.here"
        assert mock.database_port == 3306

    def test_mock_config_env_dict(self):
        mock = patch_config_module()
        assert mock.config["token"] == "mock_test_token"
        assert mock.config["prefix"] == "?mock?"

    def test_patch_overwrites_module(self):
        mock = patch_config_module()
        assert "config" in sys.modules
        assert sys.modules["config"] is mock
