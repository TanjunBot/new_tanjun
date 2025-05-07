import sys
from unittest.mock import MagicMock

def patch_config_module():
    mock_config_module_instance = MagicMock()

    mock_config_module_instance.version = "1.0.5-test"
    mock_config_module_instance.token = "mock_test_token"
    mock_config_module_instance.applicationId = "1234567890_mock"
    mock_config_module_instance.adminIds = [1001, 1002, 1003]
    mock_config_module_instance.activity = "Testing Tanjun {version}"
    mock_config_module_instance.database_ip = "mock.db.ip.here"
    mock_config_module_instance.database_password = "mock_db_password"
    mock_config_module_instance.database_user = "mock_db_user"
    mock_config_module_instance.database_schema = "mock_db_schema"
    mock_config_module_instance.tenorAPIKey = "mock_tenor_api_key"
    mock_config_module_instance.tenorCKey = "mock_tenor_ckey"
    mock_config_module_instance.GithubAuthToken = "mock_github_token"
    mock_config_module_instance.ImgBBApiKey = "mock_imgbb_key"
    mock_config_module_instance.openAIKey = "mock_openai_key"
    mock_config_module_instance.bytebin_url = "https://mock.bytebin.url"
    mock_config_module_instance.bytebin_password = "mock_bytebin_password"
    mock_config_module_instance.bytebin_username = "mock_bytebin_user"
    mock_config_module_instance.brawlstarsToken = "mock_brawlstars_token"
    mock_config_module_instance.twitchSecret = "mock_twitch_secret"
    mock_config_module_instance.twitchId = "mock_twitch_id_123"
    mock_config_module_instance.prefix = "?mock?"

    mock_env_dict = {
        "token": mock_config_module_instance.token,
        "applicationId": mock_config_module_instance.applicationId,
        "adminIds": ",".join(map(str, mock_config_module_instance.adminIds)),
        "database_ip": mock_config_module_instance.database_ip,
        "database_password": mock_config_module_instance.database_password,
        "database_user": mock_config_module_instance.database_user,
        "database_schema": mock_config_module_instance.database_schema,
        "tenorAPIKey": mock_config_module_instance.tenorAPIKey,
        "tenorCKey": mock_config_module_instance.tenorCKey,
        "GithubAuthToken": mock_config_module_instance.GithubAuthToken,
        "ImgBBApiKey": mock_config_module_instance.ImgBBApiKey,
        "openAIKey": mock_config_module_instance.openAIKey,
        "bytebin_url": mock_config_module_instance.bytebin_url,
        "bytebin_password": mock_config_module_instance.bytebin_password,
        "bytebin_username": mock_config_module_instance.bytebin_username,
        "brawlstarsToken": mock_config_module_instance.brawlstarsToken,
        "twitchSecret": mock_config_module_instance.twitchSecret,
        "twitchId": mock_config_module_instance.twitchId,
        "prefix": mock_config_module_instance.prefix
    }
    mock_config_module_instance.config = mock_env_dict

    sys.modules['config'] = mock_config_module_instance
    return mock_config_module_instance