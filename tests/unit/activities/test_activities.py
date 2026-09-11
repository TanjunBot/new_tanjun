"""Unit tests for Discord Activities framework and games."""

import unittest
from activities.base import Player
from activities.manager import session_manager
from activities.games.tictactoe import TicTacToeGame


class TestActivities(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.host = Player(
            user_id="user_host",
            username="HostPlayer",
            display_name="Host Player",
            is_host=True
        )

    async def test_session_lifecycle_and_gameplay(self):
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_lifecycle")
        game: TicTacToeGame = session.game

        # 1. Starting PvP with only 1 player returns waiting_for_players
        res = await game.handle_action("user_host", "start", {"mode": "pvp"})
        self.assertEqual(res.get("status"), "waiting_for_players")
        self.assertFalse(game.is_started)

        # 2. Player 2 joins
        p2 = Player(
            user_id="user_guest",
            username="GuestPlayer",
            display_name="Guest Player",
            is_host=False
        )
        self.assertTrue(game.add_player(p2))
        self.assertEqual(len(game.players), 2)

        # 3. Starting PvP now succeeds
        res = await game.handle_action("user_host", "start", {"mode": "pvp"})
        self.assertEqual(res.get("status"), "started")
        self.assertTrue(game.is_started)
        self.assertEqual(game.current_turn, "user_host")

        # 4. Player 1 makes a move
        m1 = await game.handle_action("user_host", "move", {"cell": 0})
        self.assertEqual(m1["state"]["board"][0], "X")
        self.assertEqual(m1["state"]["current_turn"], "user_guest")

        # 5. Player 2 reconnects without being demoted to spectator
        self.assertTrue(game.add_player(p2))
        self.assertIn("user_guest", game.players)
        self.assertNotIn("user_guest", game.spectators)

    async def test_bot_mode(self):
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_bot")
        game: TicTacToeGame = session.game

        res = await game.handle_action("user_host", "start", {"mode": "bot", "difficulty": 4})
        self.assertEqual(res.get("status"), "started")
        self.assertIn("bot_tanjun", game.players)

        # Move against bot triggers bot calculation
        m = await game.handle_action("user_host", "move", {"cell": 4})
        self.assertEqual(m["state"]["board"][4], "X")
        bot_moves = [i for i, c in enumerate(m["state"]["board"]) if c == "O"]
        self.assertEqual(len(bot_moves), 1)

        # Returning to lobby resets state
        lob = await game.handle_action("user_host", "lobby", {})
        self.assertFalse(lob["state"]["is_started"])
        self.assertNotIn("bot_tanjun", game.players)


if __name__ == "__main__":
    unittest.main()
