"""Hypothesis property tests for models.py validation and from_row roundtrips."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from models import (
    ScheduledMessageModel,
    TicketMessageModel,
    TriggerMessageModel,
    WordleStatsModel,
)
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID

pytestmark = pytest.mark.unit

_snowflake = st.from_regex(r"^\d{17,20}$", fullmatch=True)
_dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)


class TestSnowflakeValidation:
    @given(_snowflake)
    @settings(max_examples=50)
    def test_valid_snowflake_accepted(self, snowflake: str):
        model = TriggerMessageModel(
            id=1,
            guild_id=snowflake,
            trigger="hi",
            response="there",
            case_sensitive=False,
        )
        assert model.guild_id == snowflake

    @given(st.text(min_size=1, max_size=16).filter(lambda s: not s.isdigit() or len(s) < 17))
    @settings(max_examples=30)
    def test_invalid_snowflake_rejected(self, bad_id: str):
        with pytest.raises(ValidationError):
            TriggerMessageModel(
                id=1,
                guild_id=bad_id,
                trigger="hi",
                response="there",
                case_sensitive=False,
            )


class TestFromRowRoundtrip:
    @given(
        games_played=st.integers(min_value=0, max_value=10_000),
        games_won=st.integers(min_value=0, max_value=10_000),
        current_streak=st.integers(min_value=0, max_value=500),
        max_streak=st.integers(min_value=0, max_value=500),
    )
    @settings(max_examples=40)
    def test_wordle_stats_roundtrip(
        self,
        games_played: int,
        games_won: int,
        current_streak: int,
        max_streak: int,
    ):
        original = WordleStatsModel(
            user_id=USER_ID,
            guild_id=GUILD_ID,
            games_played=games_played,
            games_won=games_won,
            current_streak=current_streak,
            max_streak=max_streak,
            guess_distribution="0,0,0,0,0,0",
            hard_mode_games_played=0,
            hard_mode_games_won=0,
        )
        row = tuple(getattr(original, f) for f in WordleStatsModel.model_fields)
        restored = WordleStatsModel.from_row(row)
        assert restored == original

    @given(
        trigger=st.text(min_size=1, max_size=128),
        response=st.text(min_size=1, max_size=1024),
        case_sensitive=st.booleans(),
    )
    @settings(max_examples=40)
    def test_trigger_message_roundtrip(self, trigger: str, response: str, case_sensitive: bool):
        original = TriggerMessageModel(
            id=1,
            guild_id=GUILD_ID,
            trigger=trigger,
            response=response,
            case_sensitive=case_sensitive,
        )
        row = (original.id, original.guild_id, original.trigger, original.response, original.case_sensitive)
        restored = TriggerMessageModel.from_row(row)
        assert restored == original

    @given(content=st.text(min_size=1, max_size=2000))
    @settings(max_examples=30)
    def test_scheduled_message_roundtrip(self, content: str):
        original = ScheduledMessageModel(
            message_id=1,
            guild_id=GUILD_ID,
            channel_id=CHANNEL_ID,
            user_id=USER_ID,
            content=content,
            send_time=_dt,
            repeat_interval=None,
            repeat_amount=None,
            attachments=None,
            discord_message_id=None,
            created_at=_dt,
        )
        row = tuple(getattr(original, f) for f in ScheduledMessageModel.model_fields)
        restored = ScheduledMessageModel.from_row(row)
        assert restored == original


class TestModelValidation:
    @given(st.text(min_size=2001, max_size=2100))
    @settings(max_examples=10)
    def test_scheduled_message_content_max_length(self, content: str):
        with pytest.raises(ValidationError):
            ScheduledMessageModel(
                message_id=1,
                guild_id=GUILD_ID,
                channel_id=CHANNEL_ID,
                user_id=USER_ID,
                content=content,
                send_time=_dt,
                repeat_interval=None,
                repeat_amount=None,
                created_at=_dt,
            )

    @given(st.text(min_size=129, max_size=200))
    @settings(max_examples=10)
    def test_ticket_message_name_max_length(self, name: str):
        with pytest.raises(ValidationError):
            TicketMessageModel(
                id=1,
                guild_id=GUILD_ID,
                channel_id=CHANNEL_ID,
                name=name,
            )

    @given(st.integers(min_value=-100, max_value=-1))
    @settings(max_examples=20)
    def test_wordle_stats_negative_rejected(self, negative: int):
        with pytest.raises(ValidationError):
            WordleStatsModel(
                user_id=USER_ID,
                guild_id=GUILD_ID,
                games_played=negative,
            )
