from __future__ import annotations

from tests.helpers.fun_matrix import FunLiveCase, iter_fun_live_cases
from tests.helpers.live_discord.command_registry import ResolvedSlashCommand
from tests.helpers.live_discord.discord_api import GuildContext
from tests.helpers.live_discord.interaction_payload import (
    APPLICATION_COMMAND_TYPE,
    CHAT_INPUT_COMMAND_TYPE,
    STRING_OPTION_TYPE,
    SUB_COMMAND_TYPE,
    USER_OPTION_TYPE,
    build_fun_interaction_payload,
)


def _resolved() -> ResolvedSlashCommand:
    group_command = {
        "id": "111",
        "version": "222",
        "name": "funcmd_name",
        "type": CHAT_INPUT_COMMAND_TYPE,
        "options": [
            {
                "type": SUB_COMMAND_TYPE,
                "name": "fun_hug_name",
                "options": [
                    {"type": USER_OPTION_TYPE, "name": "user"},
                    {"type": STRING_OPTION_TYPE, "name": "message"},
                ],
            },
        ],
    }
    sub_option = group_command["options"][0]
    return ResolvedSlashCommand(
        command_id="111",
        version="222",
        name="funcmd_name",
        option_chain=(sub_option,),
        group_command=group_command,
    )


def _guild() -> GuildContext:
    return GuildContext(guild_id="900", channel_id="800", owner_user_id="100")


def test_build_fun_interaction_payload_without_message() -> None:
    payload = build_fun_interaction_payload(
        _resolved(),
        application_id="app",
        guild=_guild(),
        target_user_id="100",
        message=None,
    )
    assert payload["type"] == APPLICATION_COMMAND_TYPE
    assert payload["application_id"] == "app"
    assert payload["guild_id"] == "900"
    assert payload["channel_id"] == "800"
    assert payload["session_id"]
    assert payload["nonce"].isdigit()
    assert int(payload["nonce"]) > 0
    data = payload["data"]
    assert data["version"] == "222"
    assert data["id"] == "111"
    assert data["name"] == "funcmd_name"
    assert data["type"] == CHAT_INPUT_COMMAND_TYPE
    assert data["application_command"]["name"] == "funcmd_name"
    sub = data["options"][0]
    assert sub["type"] == SUB_COMMAND_TYPE
    assert sub["name"] == "fun_hug_name"
    assert sub["options"] == [{"type": USER_OPTION_TYPE, "name": "user", "value": "100"}]


def test_build_fun_interaction_payload_with_message() -> None:
    payload = build_fun_interaction_payload(
        _resolved(),
        application_id="app",
        guild=_guild(),
        target_user_id="200",
        message="e2e check",
    )
    sub_options = payload["data"]["options"][0]["options"]
    assert sub_options[0]["value"] == "200"
    assert sub_options[1] == {
        "type": STRING_OPTION_TYPE,
        "name": "message",
        "value": "e2e check",
    }


def test_live_cases_target_mapping() -> None:
    guild = _guild()
    resolved = _resolved()
    for case in iter_fun_live_cases():
        target_id = "100" if case.target == "self" else "bot-id"
        payload = build_fun_interaction_payload(
            resolved,
            application_id="app",
            guild=guild,
            target_user_id=target_id,
            message=case.message,
        )
        sub_options = payload["data"]["options"][0]["options"]
        assert sub_options[0]["value"] == target_id
        if case.message is None:
            assert len(sub_options) == 1
        else:
            assert sub_options[1]["value"] == case.message


def test_fun_live_case_ids() -> None:
    cases = iter_fun_live_cases()
    assert len(cases) == 72
    assert FunLiveCase(action="hug", message_kind="short", target="self").id == "hug-short-self"
