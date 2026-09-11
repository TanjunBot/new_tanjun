"""Unit tests for Discord Activities framework and games."""

import unittest
from activities.base import Player
from activities.manager import session_manager
from activities.games.tictactoe import TicTacToeGame
from activities.games.connect4 import Connect4Game
from activities.games.rps import RPSGame


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

    async def test_connect4_gameplay_and_win(self):
        session = session_manager.create_session("connect4", host=self.host, session_id="test_c4")
        game: Connect4Game = session.game
        self.assertIsInstance(game, Connect4Game)

        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        game.add_player(p2)

        start_res = await game.handle_action("user_host", "start", {"mode": "pvp"})
        self.assertEqual(start_res.get("status"), "started")
        self.assertEqual(game.current_turn, "user_host")

        # Drop into col 0: lowest row is 5 -> index 5 * 7 + 0 = 35
        m1 = await game.handle_action("user_host", "move", {"col": 0})
        self.assertEqual(m1["state"]["board"][35], "R")
        self.assertEqual(m1["state"]["current_turn"], "user_guest")

        # Guest drops in col 0: lands at row 4 -> index 4 * 7 + 0 = 28
        m2 = await game.handle_action("user_guest", "move", {"col": 0})
        self.assertEqual(m2["state"]["board"][28], "Y")

        # Horizontal win sequence for host in bottom row (cols 1, 2, 3)
        # Row 5 indices: col 0=35 (R), col 1=36 (R), col 2=37 (R), col 3=38 (R)
        await game.handle_action("user_host", "move", {"col": 1})
        await game.handle_action("user_guest", "move", {"col": 1})
        await game.handle_action("user_host", "move", {"col": 2})
        await game.handle_action("user_guest", "move", {"col": 2})
        win_move = await game.handle_action("user_host", "move", {"col": 3})

        self.assertTrue(win_move["state"]["is_finished"])
        self.assertEqual(win_move["state"]["winner"], "user_host")
        self.assertEqual(win_move["state"]["scores"]["user_host"], 1)

    async def test_connect4_bot(self):
        session = session_manager.create_session("connect4", host=self.host, session_id="test_c4_bot")
        game: Connect4Game = session.game
        await game.handle_action("user_host", "start", {"mode": "bot", "difficulty": 3})
        self.assertTrue(game.is_started)
        self.assertIn("bot_tanjun", game.players)

        move_res = await game.handle_action("user_host", "move", {"col": 3})
        # After player moves, bot should have moved automatically
        yellow_chips = [c for c in move_res["state"]["board"] if c == "Y"]
        self.assertEqual(len(yellow_chips), 1)

    async def test_rps_gameplay_and_masking(self):
        session = session_manager.create_session("rps", host=self.host, session_id="test_rps")
        game: RPSGame = session.game
        self.assertIsInstance(game, RPSGame)

        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        game.add_player(p2)

        start_res = await game.handle_action("user_host", "start", {"mode": "pvp", "target_wins": 2})
        self.assertEqual(start_res.get("status"), "started")

        # Player 1 picks rock
        p1_res = await game.handle_action("user_host", "pick", {"choice": "rock"})
        self.assertFalse(p1_res.get("round_completed"))

        # From Guest's perspective, host's pick is masked ("locked")
        guest_view = game.get_state(for_user_id="user_guest")
        self.assertEqual(guest_view["current_picks"]["user_host"], "locked")

        # From Host's perspective, own pick is visible
        host_view = game.get_state(for_user_id="user_host")
        self.assertEqual(host_view["current_picks"]["user_host"], "rock")

        # Guest picks scissors (Host wins round)
        p2_res = await game.handle_action("user_guest", "pick", {"choice": "scissors"})
        self.assertTrue(p2_res.get("round_completed"))
        self.assertEqual(p2_res["round_result"]["winner"], "user_host")
        self.assertEqual(game.scores["user_host"], 1)
        self.assertEqual(game.current_round, 2)

    async def test_rps_bot(self):
        session = session_manager.create_session("rps", host=self.host, session_id="test_rps_bot")
        game: RPSGame = session.game
        await game.handle_action("user_host", "start", {"mode": "bot", "target_wins": 3})
        self.assertTrue(game.is_started)

        # Picking against bot automatically resolves the round
        pick_res = await game.handle_action("user_host", "pick", {"choice": "rock"})
        self.assertTrue(pick_res.get("round_completed"))
        self.assertIsNotNone(pick_res.get("round_result"))

    async def test_hub_session_and_game_switch(self):
        session = session_manager.create_session("hub", host=self.host, session_id="test_hub")
        self.assertTrue(session.is_hub)

        state = session.get_full_state()
        self.assertTrue(state["is_hub"])
        self.assertGreaterEqual(len(state["available_games"]), 3)

        # Add second player to hub
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)

        # Switch to Connect 4
        switched_game = session.switch_game("connect4")
        self.assertIsInstance(switched_game, Connect4Game)
        self.assertFalse(session.is_hub)
        # Players and host preserved
        self.assertIn("user_host", switched_game.players)
        self.assertIn("user_guest", switched_game.players)
        self.assertEqual(switched_game.host.user_id, "user_host")

        # Switch to RPS
        switched_game2 = session.switch_game("rps")
        self.assertIsInstance(switched_game2, RPSGame)
        self.assertIn("user_host", switched_game2.players)
        self.assertIn("user_guest", switched_game2.players)


if __name__ == "__main__":
    unittest.main()

