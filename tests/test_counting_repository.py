"""Tests for CountingRepository from services/counting_repository.py.

Uses mocked api.execute_query / execute_action to avoid database dependency.
"""

from unittest.mock import AsyncMock, patch

import pytest

from services.counting_repository import CountingMode, CountingRepository


def _mode_to_table(mode: CountingMode) -> str:
    """Map CountingMode to the actual table name used in queries."""
    return {
        CountingMode.NORMAL: "counting",
        CountingMode.CHALLENGE: "counting_challenge",
        CountingMode.MODES: "counting_modes",
    }[mode]


@pytest.fixture
def repo() -> CountingRepository:
    return CountingRepository()


class TestCountingRepository:
    """Unit tests for CountingRepository with mocked database layer."""

    # ── set_progress ──────────────────────────────────────────

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mode", list(CountingMode))
    async def test_set_progress_insert(self, repo: CountingRepository, mode: CountingMode) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_progress(mode, "123", 42, "456")
            mock_exec.assert_awaited_once()
            args, kwargs = mock_exec.await_args
            query = args[0]
            expected_table = _mode_to_table(mode)
            assert expected_table in query
            assert "ON DUPLICATE KEY UPDATE" in query
            assert args[1] == ("123", 42, "456", 42)

    @pytest.mark.asyncio
    async def test_set_progress_with_int_ids(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_progress(CountingMode.NORMAL, 123, 42, 456)
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert "counting" in args[0]

    # ── get_progress ──────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_progress_found(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(42,)]
            result = await repo.get_progress(CountingMode.NORMAL, "123")
            assert result == 42
            mock_q.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_progress_none(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_progress(CountingMode.CHALLENGE, "999")
            assert result is None

    # ── get_channel_count ─────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_channel_count(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(5,)]
            result = await repo.get_channel_count(CountingMode.MODES, "456")
            assert result == 5

    @pytest.mark.asyncio
    async def test_get_channel_count_none(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_channel_count(CountingMode.NORMAL, "000")
            assert result == 0

    # ── get_last_counter_id ───────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_last_counter_id_found(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [("user_1",)]
            result = await repo.get_last_counter_id(CountingMode.NORMAL, "123")
            assert result == "user_1"

    @pytest.mark.asyncio
    async def test_get_last_counter_id_none(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_last_counter_id(CountingMode.NORMAL, "999")
            assert result is None

    # ── increment_progress ────────────────────────────────────

    @pytest.mark.asyncio
    async def test_increment_progress(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.increment_progress(CountingMode.NORMAL, "123", "user_1")
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert "progress + 1" in args[0]
            assert "last_counter_id" in args[0]
            assert args[1] == ("user_1", "123")

    # ── clear ─────────────────────────────────────────────────

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mode", list(CountingMode))
    async def test_clear(self, repo: CountingRepository, mode: CountingMode) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.clear(mode, "123")
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert "DELETE FROM" in args[0]
            expected_table = _mode_to_table(mode)
            assert expected_table in args[0]

    # ── get_mode (MODES only) ─────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_mode_found(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(3,)]
            result = await repo.get_mode("123")
            assert result == 3

    @pytest.mark.asyncio
    async def test_get_mode_none(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_mode("999")
            assert result is None

    # ── get_goal ──────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_goal_found(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [(100,)]
            result = await repo.get_goal("123")
            assert result == 100

    @pytest.mark.asyncio
    async def test_get_goal_none(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_goal("999")
            assert result is None

    # ── set_mode_progress ─────────────────────────────────────

    @pytest.mark.asyncio
    async def test_set_mode_progress(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_mode_progress("123", 42, "456", 3, 100, "user_1")
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert "counting_modes" in args[0]
            assert "ON DUPLICATE KEY UPDATE" in args[0]
            expected_params = ("123", 42, "456", 3, 100, "user_1")
            assert args[1] == expected_params

    # ── set_challenge_progress ────────────────────────────────

    @pytest.mark.asyncio
    async def test_set_challenge_progress_challenge(self, repo: CountingRepository) -> None:
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_challenge_progress(CountingMode.CHALLENGE, "123", 10, "456")
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert "counting_challenge" in args[0]
            assert args[1] == ("123", 10, "456", 10)

    # ── get_configs (batch) ───────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_configs_all_none(self, repo: CountingRepository) -> None:
        """When no configs exist, all three should be None."""
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = []
            result = await repo.get_configs("999")
            assert result == (None, None, None)
            assert mock_q.await_count == 3

    @pytest.mark.asyncio
    async def test_get_configs_normal_only(self, repo: CountingRepository) -> None:
        """Only the normal mode config is present."""
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.side_effect = [
                [(42, "user_1", "456")],   # counting
                [],                          # counting_challenge
                [],                          # counting_modes
            ]
            normal, challenge, modes = await repo.get_configs("123")
            assert normal == {"progress": 42, "last_counter_id": "user_1", "guild_id": "456"}
            assert challenge is None
            assert modes is None

    @pytest.mark.asyncio
    async def test_get_configs_all_modes(self, repo: CountingRepository) -> None:
        """All three configs returned for a fully configured channel."""
        with patch("services.counting_repository.execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.side_effect = [
                [(42, "user_1", "456")],                                # counting
                [(99, "user_2", "456")],                                # counting_challenge
                [(10, 3, 100, "user_3", "456")],                        # counting_modes
            ]
            normal, challenge, modes = await repo.get_configs("123")
            assert normal == {"progress": 42, "last_counter_id": "user_1", "guild_id": "456"}
            assert challenge == {"progress": 99, "last_counter_id": "user_2", "guild_id": "456"}
            assert modes == {
                "progress": 10, "mode": 3, "goal": 100,
                "last_counter_id": "user_3", "guild_id": "456",
            }

    # ── TDD for known patterns / edge cases ──────────────────

    @pytest.mark.asyncio
    async def test_set_progress_zero_progress(self, repo: CountingRepository) -> None:
        """Setting progress to 0 should still work (reset case)."""
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_progress(CountingMode.NORMAL, "123", 0, "456")
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert args[1][1] == 0  # progress is 0

    @pytest.mark.asyncio
    async def test_increment_progress_then_get(self, repo: CountingRepository) -> None:
        """Simulate increment+read flow: after increment, get_progress shows +1."""
        calls = []

        async def fake_action(*args, **kwargs):
            calls.append(("action", args))

        async def fake_query_after_increment(*args, **kwargs):
            return [(43,)]  # was 42, now 43

        with patch.multiple(
            "services.counting_repository",
            execute_action=fake_action,
            execute_query=fake_query_after_increment,
        ):
            await repo.increment_progress(CountingMode.NORMAL, "123", "user_2")
            result = await repo.get_progress(CountingMode.NORMAL, "123")

        assert result == 43
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_challenge_progress_with_default_guild_id(self, repo: CountingRepository) -> None:
        """set_challenge_progress should accept guild_id=0 as fallback."""
        with patch("services.counting_repository.execute_action", new_callable=AsyncMock) as mock_exec:
            await repo.set_challenge_progress(CountingMode.CHALLENGE, "123", 5)
            mock_exec.assert_awaited_once()
            args = mock_exec.await_args[0]
            assert args[1] == ("123", 5, 0, 5)
