"""Validation, edge cases, and iter_rows coverage for models.py."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from models import (
    AISituationModel,
    CountingMode,
    CountingConfigModel,
    CountingModesConfigModel,
    GiveawayChannelRequirementModel,
    GiveawayModel,
    LevelConfig,
    LevelRolesGroupModel,
    LogEnableModel,
    TwitchUserModel,
    UserLevelInfoModel,
    WarnConfigModel,
    XpBoostModel,
    _from_row,
    _from_row_partial,
)
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, MESSAGE_ID, ROLE_ID, USER_ID, _dt, giveaway_row


class TestFromRowHelpers:
    def test_from_row_success(self):
        model = _from_row(XpBoostModel, (2.0, True))
        assert model.boost == 2.0

    def test_from_row_wrong_length(self):
        with pytest.raises(ValueError, match="expected 2 columns"):
            _from_row(XpBoostModel, (1.0,))

    def test_from_row_partial_success(self):
        model = _from_row_partial(WarnConfigModel, (GUILD_ID, 7, 2, 300, 4, 8), skip=1)
        assert model.expiration_days == 7

    def test_from_row_partial_wrong_length(self):
        with pytest.raises(ValueError, match="expected 5 mapped columns"):
            _from_row_partial(WarnConfigModel, (GUILD_ID, 7), skip=1)


class TestGiveawayModelValidation:
    def test_winners_minimum(self):
        with pytest.raises(ValidationError):
            GiveawayModel(
                giveaway_id=1,
                guild_id=GUILD_ID,
                title="t",
                winners=0,
                with_button=True,
                end_time=None,
                started=False,
                ended=False,
                send_failed=False,
                message_id=MESSAGE_ID,
                created_at=None,
            )

    def test_title_max_length(self):
        with pytest.raises(ValidationError):
            GiveawayModel(
                giveaway_id=1,
                guild_id=GUILD_ID,
                title="x" * 129,
                winners=1,
                with_button=True,
                end_time=None,
                started=False,
                ended=False,
                send_failed=False,
                message_id=MESSAGE_ID,
                created_at=None,
            )

    def test_defaults_optional_fields(self):
        model = GiveawayModel.from_row(giveaway_row())
        assert model.new_message_requirement == 0
        assert model.day_requirement == 0

    def test_description_none_allowed(self):
        row = list(giveaway_row())
        row[3] = None
        model = GiveawayModel.from_row(tuple(row))
        assert model.description is None

    def test_from_row_wrong_column_count(self):
        with pytest.raises(ValueError):
            GiveawayModel.from_row((1, GUILD_ID))


class TestGiveawayChannelRequirementValidation:
    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            GiveawayChannelRequirementModel(channel_id=CHANNEL_ID, amount=0)

    def test_amount_negative_rejected(self):
        with pytest.raises(ValidationError):
            GiveawayChannelRequirementModel(channel_id=CHANNEL_ID, amount=-1)


class TestXpBoostValidation:
    def test_negative_boost_rejected(self):
        with pytest.raises(ValidationError):
            XpBoostModel(boost=-0.1, additive=False)

    def test_zero_boost_allowed(self):
        model = XpBoostModel(boost=0.0, additive=True)
        assert model.boost == 0.0


class TestAISituationValidation:
    def test_temperature_bounds(self):
        dt = _dt()
        with pytest.raises(ValidationError):
            AISituationModel(
                user_id=USER_ID,
                created_at=dt,
                unlocked=True,
                temperature=3.0,
            )

    def test_top_p_bounds(self):
        dt = _dt()
        with pytest.raises(ValidationError):
            AISituationModel(
                user_id=USER_ID,
                created_at=dt,
                unlocked=True,
                top_p=1.5,
            )

    def test_penalty_bounds(self):
        dt = _dt()
        with pytest.raises(ValidationError):
            AISituationModel(
                user_id=USER_ID,
                created_at=dt,
                unlocked=True,
                frequency_penalty=3.0,
            )

    def test_name_max_length(self):
        dt = _dt()
        with pytest.raises(ValidationError):
            AISituationModel(
                user_id=USER_ID,
                name="x" * 16,
                created_at=dt,
                unlocked=True,
            )


class TestLevelConfigValidation:
    def test_invalid_difficulty_rejected(self):
        with pytest.raises(ValidationError):
            LevelConfig(guild_id=GUILD_ID, difficulty="impossible")

    def test_valid_difficulties(self):
        for diff in ("easy", "medium", "hard", "extreme", "custom"):
            cfg = LevelConfig(guild_id=GUILD_ID, difficulty=diff)
            assert cfg.difficulty == diff

    def test_negative_cooldown_rejected(self):
        with pytest.raises(ValidationError):
            LevelConfig(guild_id=GUILD_ID, text_cooldown=-1)

    def test_from_row_non_sequence_raises(self):
        with pytest.raises(ValueError, match="non-sequence"):
            LevelConfig.from_row("not-a-row")


class TestLogEnableModelAdvanced:
    def test_known_db_columns(self):
        cols = LogEnableModel.known_db_columns()
        assert "memberJoin" in cols
        assert "automodRuleCreate" in cols

    def test_db_field_map_covers_options(self):
        assert LogEnableModel._DB_FIELD_MAP["memberJoin"] == "member_join"
        assert LogEnableModel._FIELD_DB_MAP["member_join"] == "memberJoin"

    def test_default_boolean_values(self):
        model = LogEnableModel(guild_id=GUILD_ID)
        assert model.member_join is True
        assert model.invite_delete is False
        assert model.reaction_add is False

    def test_coerce_preserves_guild_id(self):
        model = LogEnableModel(guild_id=GUILD_ID, member_join=1)
        assert model.guild_id == GUILD_ID
        assert model.member_join is True

    def test_set_option_updates_field(self):
        model = LogEnableModel(guild_id=GUILD_ID)
        idx = LogEnableModel._OPTION_KEYS.index("message_delete")
        model.set_option(idx, False)
        assert model.message_delete is False

    def test_get_option_reads_field(self):
        model = LogEnableModel(guild_id=GUILD_ID, message_edit=False)
        idx = LogEnableModel._OPTION_KEYS.index("message_edit")
        assert model.get_option(idx) is False


class TestCountingMode:
    def test_enum_values(self):
        assert CountingMode.NORMAL == 1
        assert CountingMode.ROMEAN == 12
        assert CountingMode.CUBE == 14

    def test_enum_is_intenum(self):
        assert isinstance(CountingMode.PRIME, int)
        assert CountingMode.PRIME.value == 4


class TestCountingConfigModels:
    def test_counting_config_negative_progress_rejected(self):
        with pytest.raises(ValidationError):
            CountingConfigModel(progress=-1, last_counter_id=USER_ID, guild_id=GUILD_ID)

    def test_counting_modes_goal_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            CountingModesConfigModel(
                progress=0, mode=1, goal=-1, last_counter_id=USER_ID, guild_id=GUILD_ID
            )


class TestUserLevelInfoModel:
    def test_defaults(self):
        info = UserLevelInfoModel(xp=100, level=5, xp_needed=200)
        assert info.custom_background is None

    def test_xp_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            UserLevelInfoModel(xp=-1, level=0, xp_needed=0)


class TestLevelRolesGroupModel:
    def test_role_ids_list(self):
        group = LevelRolesGroupModel(level=10, role_ids=[ROLE_ID, "88888888888888888"])
        assert len(group.role_ids) == 2

    def test_level_must_be_non_negative(self):
        with pytest.raises(ValidationError):
            LevelRolesGroupModel(level=-1, role_ids=[ROLE_ID])


class TestTwitchUserModel:
    def test_from_api_response_minimal(self):
        model = TwitchUserModel.from_api_response({"id": "1", "login": "a", "display_name": "A"})
        assert model.view_count == 0
        assert model.type == ""

    def test_from_api_response_full(self):
        data = {
            "id": "99",
            "login": "streamer",
            "display_name": "Streamer",
            "type": "staff",
            "broadcaster_type": "partner",
            "description": "desc",
            "profile_image_url": "http://img",
            "offline_image_url": "http://off",
            "view_count": 1000,
            "created_at": "2020-01-01T00:00:00Z",
        }
        model = TwitchUserModel.from_api_response(data)
        assert model.broadcaster_type == "partner"
        assert model.view_count == 1000


class TestModelIterRows:
    @pytest.mark.asyncio
    async def test_giveaway_iter_rows(self):
        row = giveaway_row()

        async def fake_iter(_query, _params=None):
            yield row

        with patch("api.execute_query_iter", side_effect=fake_iter):
            models = [m async for m in GiveawayModel.iter_rows("SELECT 1")]

        assert len(models) == 1
        assert models[0].giveaway_id == 1

    @pytest.mark.asyncio
    async def test_xp_boost_iter_rows_multiple(self):
        async def fake_iter(_query, _params=None):
            yield (1.0, False)
            yield (2.5, True)

        with patch("api.execute_query_iter", side_effect=fake_iter):
            models = [m async for m in XpBoostModel.iter_rows("SELECT 1")]

        assert len(models) == 2
        assert models[1].additive is True

    @pytest.mark.asyncio
    async def test_log_enable_iter_rows(self):
        flags = [True] * 24
        row = (GUILD_ID, *flags)

        async def fake_iter(_query, _params=None):
            yield row

        with patch("api.execute_query_iter", side_effect=fake_iter):
            models = [m async for m in LogEnableModel.iter_rows("SELECT 1")]

        assert models[0].guild_id == GUILD_ID

    @pytest.mark.asyncio
    async def test_warn_config_iter_rows(self):
        async def fake_iter(_query, _params=None):
            yield (GUILD_ID, 30, 3, 600, 5, 10)

        with patch("api.execute_query_iter", side_effect=fake_iter):
            models = [m async for m in WarnConfigModel.iter_rows("SELECT 1")]

        assert models[0].timeout_threshold == 3
