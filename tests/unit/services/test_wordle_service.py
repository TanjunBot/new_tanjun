from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services import wordle_service
from tests.helpers.factories import GUILD_ID, USER_ID


class TestWordleServiceHelpers:
    def test_validate_hard_mode_first_guess_allowed(self):
        assert wordle_service.validate_hard_mode_guess("about", [], "about") is None

    def test_validate_hard_mode_green_constraint(self):
        err = wordle_service.validate_hard_mode_guess("apple", ["about"], "about")
        assert err is not None
        assert "position" in err.lower()

    def test_validate_hard_mode_empty_last_guess(self):
        assert wordle_service.validate_hard_mode_guess("apple", [""], "apple") is None

    def test_validate_hard_mode_letter_count_at_least(self):
        err = wordle_service.validate_hard_mode_guess("aaaab", ["baaab"], "aabbb")
        assert err is not None
        assert "at least" in err.lower()

    def test_validate_hard_mode_letter_must_be_used(self):
        err = wordle_service.validate_hard_mode_guess("bbbbb", ["bcdea"], "abcde")
        assert err is not None
        assert "must be used" in err.lower()

    def test_api_to_model_none(self):
        assert wordle_service._api_to_model(None) is None

    def test_generate_share_text_win_exact_match_shortcut(self):
        text = wordle_service.generate_share_text(["about"], "about", won=True)
        assert "🟩🟩🟩🟩🟩" in text

    def test_generate_share_text_partial_yellow_green(self):
        text = wordle_service.generate_share_text(["crane"], "apple", won=False)
        assert "🟨" in text or "🟩" in text
        assert "⬛" in text

    def test_generate_share_text_win(self):
        text = wordle_service.generate_share_text(["about"], "about", won=True)
        assert "Wordle" in text
        assert "🟩" in text

    def test_generate_share_text_loss(self):
        text = wordle_service.generate_share_text(["apple", "grape"], "about", won=False, hard_mode=True)
        assert "X/6" in text
        assert "Hard" in text


class TestWordleServiceApi:
    @pytest.mark.asyncio
    async def test_get_wordle_stats(self):
        with patch(
            "api.get_wordle_stats",
            AsyncMock(
                return_value={
                    "user_id": USER_ID,
                    "guild_id": GUILD_ID,
                    "games_played": 1,
                    "games_won": 1,
                    "current_streak": 1,
                    "max_streak": 1,
                    "guess_distribution": "1,0,0,0,0,0",
                    "hard_mode_games_played": 0,
                    "hard_mode_games_won": 0,
                }
            ),
        ):
            result = await wordle_service.get_wordle_stats(USER_ID, GUILD_ID)
        assert result is not None
        assert result.games_won == 1

    @pytest.mark.asyncio
    async def test_upsert_wordle_stats(self):
        with patch(
            "api.upsert_wordle_stats",
            AsyncMock(
                return_value={
                    "user_id": USER_ID,
                    "guild_id": GUILD_ID,
                    "games_played": 2,
                    "games_won": 2,
                    "current_streak": 2,
                    "max_streak": 2,
                    "guess_distribution": "0,1,0,0,0,0",
                    "hard_mode_games_played": 1,
                    "hard_mode_games_won": 1,
                }
            ),
        ):
            result = await wordle_service.upsert_wordle_stats(USER_ID, GUILD_ID, True, 3, hard_mode=True)
        assert result is not None
        assert result.games_won == 2
