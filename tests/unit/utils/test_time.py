"""Tests for utils/time.py relative time helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from utils.time import (
    date_time_to_timestamp,
    dateToRelativeTimeStr,
    isoTimeToDate,
    relative_time_str_to_date,
    relative_time_to_seconds,
    relativeTimeStrToDate,
    relativeTimeToSeconds,
)


class TestRelativeTimeToSeconds:
    def test_empty_string(self):
        assert relative_time_to_seconds("") == 0

    def test_seconds(self):
        assert relative_time_to_seconds("30s") == 30

    def test_minutes(self):
        assert relative_time_to_seconds("5m") == 300

    def test_hours(self):
        assert relative_time_to_seconds("2h") == 7200

    def test_days(self):
        assert relative_time_to_seconds("1d") == 86400

    def test_combined(self):
        assert relative_time_to_seconds("1d2h3m4s") == 86400 + 7200 + 180 + 4

    def test_invalid_returns_zero(self):
        assert relative_time_to_seconds("invalid") == 0

    def test_alias(self):
        assert relativeTimeToSeconds("10s") == 10


class TestRelativeTimeStrToDate:
    def test_empty_returns_now(self):
        before = datetime.now()
        result = relative_time_str_to_date("")
        after = datetime.now()
        assert before <= result <= after

    def test_one_hour_future(self):
        result = relative_time_str_to_date("1h")
        expected = datetime.now() + timedelta(hours=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_alias(self):
        result = relativeTimeStrToDate("30s")
        expected = datetime.now() + timedelta(seconds=30)
        assert abs((result - expected).total_seconds()) < 2


class TestDateToRelativeTimeStr:
    def test_future_date(self):
        future = datetime.now() + timedelta(days=1, hours=2, minutes=3, seconds=4)
        result = dateToRelativeTimeStr(future)
        assert "1d" in result
        assert "2h" in result

    def test_past_date_negative(self):
        past = datetime.now() - timedelta(hours=1)
        result = dateToRelativeTimeStr(past)
        assert result.startswith("-")

    def test_zero_components_omitted(self):
        future = datetime.now() + timedelta(seconds=5)
        result = dateToRelativeTimeStr(future)
        assert "s" in result


class TestDateTimeToTimestamp:
    def test_returns_int(self):
        dt = datetime(2024, 1, 1, 12, 0, 0)
        ts = date_time_to_timestamp(dt)
        assert isinstance(ts, int)
        assert ts == int(dt.timestamp())


class TestIsoTimeToDate:
    def test_parses_iso(self):
        dt = isoTimeToDate("2024-06-15T12:00:00")
        assert dt.year == 2024
        assert dt.month == 6
        assert dt.day == 15
