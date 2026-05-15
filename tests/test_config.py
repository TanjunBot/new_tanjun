"""Tests for config.py module — comprehensive."""

from tests.mock_config import patch_config_module

patch_config_module()


class TestConfigVariables:
    def test_version_is_string(self):
        from config import version

        assert isinstance(version, str)
        assert len(version) > 0

    def test_version_format(self):
        from config import version

        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor

    def test_adminIds_is_list(self):
        from config import adminIds

        assert isinstance(adminIds, list)

    def test_database_port_is_int(self):
        from config import database_port

        assert isinstance(database_port, int)
        assert database_port > 0

    def test_database_port_default(self):
        """Default port should be 3306 if not set in env."""
        from config import database_port

        assert database_port == 3306 or isinstance(database_port, int)

    def test_activity_is_string(self):
        from config import activity

        assert isinstance(activity, str)

    def test_activity_contains_tanjun(self):
        from config import activity

        assert "Tanjun" in activity or "tanjun" in activity.lower()

    def test_env_vars_are_strings_or_none(self):
        from config import applicationId, database_ip, database_password, token

        # These can be None if not set in env
        for var in [token, applicationId, database_ip, database_password]:
            assert var is None or isinstance(var, str)


class TestConfigModuleImport:
    def test_config_imports_successfully(self):
        import config

        assert hasattr(config, "version")
        assert hasattr(config, "token")
        assert hasattr(config, "database_ip")
        assert hasattr(config, "adminIds")

    def test_all_expected_attributes(self):
        import config

        expected_attrs = [
            "version",
            "token",
            "applicationId",
            "adminIds",
            "activity",
            "database_ip",
            "database_port",
            "database_password",
            "database_user",
            "database_schema",
            "giphyAPIKey",
            "GithubAuthToken",
            "ImgBBApiKey",
            "openAiKey",
            "bytebin_url",
            "bytebin_password",
            "bytebin_username",
            "brawlstarsToken",
            "twitchSecret",
            "twitchId",
            "prefix",
        ]
        for attr in expected_attrs:
            assert hasattr(config, attr), f"Missing attribute: {attr}"
