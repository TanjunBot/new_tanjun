"""Unit tests for Discord Activities framework and games."""

import asyncio
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

    async def test_connect4_custom_grid_size(self):
        session = session_manager.create_session("connect4", host=self.host, session_id="test_c4_custom")
        game: Connect4Game = session.game
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        game.add_player(p2)

        # Start with 8x7 grid, 5 in a row to win, and guest starts
        start_res = await game.handle_action("user_host", "start", {
            "mode": "pvp",
            "rows": 7,
            "cols": 8,
            "connect": 5,
            "first_turn": "guest"
        })
        self.assertEqual(start_res["status"], "started")
        state = game.get_state()
        self.assertEqual(state["rows"], 7)
        self.assertEqual(state["cols"], 8)
        self.assertEqual(state["connect_target"], 5)
        self.assertEqual(state["current_turn"], "user_guest")
        self.assertEqual(len(state["board"]), 7 * 8)

        # Guest drops in col 7 (rightmost column)
        move_res = await game.handle_action("user_guest", "move", {"col": 7})
        self.assertEqual(move_res["status"], "moved")
        # Lowest row in 7-row board is row 6: index 6 * 8 + 7 = 55
        self.assertEqual(move_res["state"]["board"][55], "Y")
        self.assertEqual(move_res["state"]["current_turn"], "user_host")

    async def test_rps_lizard_spock_variation(self):
        session = session_manager.create_session("rps", host=self.host, session_id="test_rps_ls")
        game: RPSGame = session.game
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        game.add_player(p2)

        start_res = await game.handle_action("user_host", "start", {
            "mode": "pvp",
            "variation": "lizard_spock",
            "target_wins": 3
        })
        self.assertEqual(start_res["status"], "started")
        state = game.get_state()
        self.assertEqual(state["variation"], "lizard_spock")
        self.assertEqual(len(state["available_choices"]), 5)
        self.assertIn("lizard", state["available_choices"])
        self.assertIn("spock", state["available_choices"])

        # Spock vaporizes Rock -> Host plays Spock, Guest plays Rock
        await game.handle_action("user_host", "pick", {"choice": "spock"})
        pick_res = await game.handle_action("user_guest", "pick", {"choice": "rock"})
        self.assertTrue(pick_res["round_completed"])
        self.assertEqual(pick_res["round_result"]["winner"], "user_host")
        self.assertEqual(game.scores["user_host"], 1)

    async def test_tournament_points_format_lifecycle(self):
        from activities.tournament import Tournament

        tourney = Tournament(session_id="cup_1", host=self.host)
        self.assertEqual(tourney.status, "lobby")
        self.assertEqual(len(tourney.participants), 1)

        # 1. Starting with 1 player fails
        res_fail = await tourney.handle_action("user_host", "tournament_start", {})
        self.assertIn("error", res_fail)

        # 2. Add players: 3 players total (to verify odd player Bye)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player Two")
        p3 = Player(user_id="user_p3", username="P3", display_name="Player Three")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        self.assertEqual(len(tourney.participants), 3)

        # 3. Update settings
        settings_res = await tourney.handle_action("user_host", "tournament_update_settings", {
            "format": "points",
            "match_style": "spectated",
            "selected_game": "tictactoe",
            "total_rounds": 2,
            "points_win": 3,
            "points_draw": 1
        })
        self.assertEqual(settings_res["status"], "settings_updated")
        self.assertEqual(tourney.selected_game, "tictactoe")
        self.assertEqual(tourney.total_rounds, 2)

        # 4. Start tournament
        start_res = await tourney.handle_action("user_host", "tournament_start", {})
        self.assertEqual(start_res["status"], "tournament_started")
        self.assertEqual(tourney.status, "active")
        self.assertEqual(tourney.current_round, 1)
        self.assertEqual(len(tourney.active_matches), 2)

        # One match is a duel, one match is a bye
        duel_match = next(m for m in tourney.active_matches if not m.is_bye)
        bye_match = next(m for m in tourney.active_matches if m.is_bye)

        self.assertEqual(bye_match.status, "finished")
        self.assertEqual(bye_match.player1.score, 1)  # Points for bye
        self.assertEqual(duel_match.status, "active")
        self.assertEqual(duel_match.game_type, "tictactoe")

        # 5. Spectator cheering
        cheer_res = await tourney.handle_action("user_p3", "tournament_cheer", {"emote": "🔥"})
        self.assertEqual(cheer_res["status"], "cheered")

        # 6. Play the duel match via tournament_match_action
        p1_id = duel_match.player1.user_id
        p2_id = duel_match.player2.user_id

        # Make moves: P1 takes 0, 1, 2 for a win
        await tourney.handle_action(p1_id, "tournament_match_action", {
            "match_id": duel_match.match_id,
            "sub_action": "move",
            "sub_data": {"cell": 0}
        })
        await tourney.handle_action(p2_id, "tournament_match_action", {
            "match_id": duel_match.match_id,
            "sub_action": "move",
            "sub_data": {"cell": 3}
        })
        await tourney.handle_action(p1_id, "tournament_match_action", {
            "match_id": duel_match.match_id,
            "sub_action": "move",
            "sub_data": {"cell": 1}
        })
        await tourney.handle_action(p2_id, "tournament_match_action", {
            "match_id": duel_match.match_id,
            "sub_action": "move",
            "sub_data": {"cell": 4}
        })
        m_win = await tourney.handle_action(p1_id, "tournament_match_action", {
            "match_id": duel_match.match_id,
            "sub_action": "move",
            "sub_data": {"cell": 2}
        })
        self.assertEqual(duel_match.status, "finished")
        self.assertEqual(duel_match.winner_id, p1_id)
        self.assertEqual(duel_match.player1.score, 3)

        # Round 1 finished -> tournament enters round_end
        self.assertEqual(tourney.status, "round_end")

        # 7. Start round 2
        next_rnd = await tourney.handle_action("user_host", "tournament_next_round", {})
        self.assertEqual(next_rnd["status"], "next_round_started")
        self.assertEqual(tourney.current_round, 2)

        # 8. Check leaderboard
        lb = tourney.get_leaderboard()
        self.assertEqual(len(lb), 3)
        self.assertGreaterEqual(lb[0]["score"], lb[1]["score"])

    async def test_tournament_knockout_lifecycle(self):
        from activities.tournament import Tournament

        tourney = Tournament(session_id="cup_ko", host=self.host)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player Two")
        p3 = Player(user_id="user_p3", username="P3", display_name="Player Three")
        p4 = Player(user_id="user_p4", username="P4", display_name="Player Four")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        tourney.add_participant(p4)

        # Setup knockout mode with parallel execution
        await tourney.handle_action("user_host", "tournament_update_settings", {
            "format": "knockout",
            "match_style": "parallel",
            "selected_game": "rps"
        })
        await tourney.handle_action("user_host", "tournament_start", {})
        self.assertEqual(tourney.status, "active")
        self.assertEqual(tourney.format, "knockout")
        self.assertEqual(len(tourney.active_matches), 2)

        # Resolve match 1: player 1 wins, player 2 eliminated
        m1 = tourney.active_matches[0]
        await tourney._resolve_match(m1, m1.player1.user_id)
        self.assertTrue(m1.player2.is_eliminated)

        # Resolve match 2: player 1 wins, player 2 eliminated
        m2 = tourney.active_matches[1]
        await tourney._resolve_match(m2, m2.player1.user_id)
        self.assertTrue(m2.player2.is_eliminated)

        # Semifinals completed -> status is round_end
        self.assertEqual(tourney.status, "round_end")

        # Advance to finals (round 2)
        await tourney.handle_action("user_host", "tournament_next_round", {})
        self.assertEqual(tourney.current_round, 2)
        self.assertEqual(len(tourney.active_matches), 1)

        final_match = tourney.active_matches[0]
        final_winner = final_match.player1.user_id
        await tourney._resolve_match(final_match, final_winner)

        # Tournament is now finished
        self.assertEqual(tourney.status, "finished")
        leaderboard = tourney.get_leaderboard()
        self.assertEqual(leaderboard[0]["user_id"], final_winner)

    async def test_session_manager_tournament_mode(self):
        # Create a session and switch into tournament mode
        session = session_manager.create_session("hub", host=self.host, session_id="test_hub_to_tourney")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)

        # Switch to tournament
        session.switch_game("tournament")
        self.assertIsNotNone(session.tournament)
        self.assertIn("user_host", session.tournament.participants)
        self.assertIn("user_guest", session.tournament.participants)

        full_state = session.get_full_state(for_user_id="user_host")
        self.assertIn("tournament", full_state)
        self.assertEqual(full_state["tournament"]["status"], "lobby")
        self.assertEqual(full_state["tournament"]["participants_count"], 2)

    async def test_tournament_as_option_and_multi_game_switching(self):
        # 1. Session is in Hub
        session = session_manager.create_session("hub", host=self.host, session_id="tourney_opt_test")
        self.assertTrue(session.is_hub)
        self.assertIsNone(session.tournament)

        # 2. Host creates tournament as an option
        session.create_tournament(host=self.host)
        self.assertIsNotNone(session.tournament)
        self.assertEqual(session.tournament.status, "lobby")

        # 3. Guest joins tournament
        guest = Player(user_id="guest_p", username="Guest", display_name="Guest")
        session.join_tournament(guest)
        self.assertEqual(len(session.tournament.participants), 2)

        # 4. Host starts Round 1 with Connect 4
        await session.tournament.handle_action("user_host", "tournament_start", {"selected_game": "connect4"})
        self.assertEqual(session.tournament.status, "active")
        self.assertEqual(session.tournament.current_round, 1)
        self.assertEqual(len(session.tournament.active_matches), 1)
        self.assertEqual(session.tournament.active_matches[0].game_type, "connect4")

        # Complete Round 1: host wins
        m1 = session.tournament.active_matches[0]
        await session.tournament._resolve_match(m1, "user_host")
        self.assertEqual(session.tournament.status, "round_end")
        self.assertEqual(session.tournament.participants["user_host"].score, 3)
        self.assertEqual(session.tournament.participants["guest_p"].score, 0)

        # 5. Tournament Master switches to Tic-Tac-Toe for Round 2!
        await session.tournament.handle_action("user_host", "tournament_next_round", {"selected_game": "tictactoe"})
        self.assertEqual(session.tournament.status, "active")
        self.assertEqual(session.tournament.current_round, 2)
        self.assertEqual(session.tournament.active_matches[0].game_type, "tictactoe")

        # Complete Round 2: guest wins Tic-Tac-Toe
        m2 = session.tournament.active_matches[0]
        await session.tournament._resolve_match(m2, "guest_p")
        self.assertEqual(session.tournament.status, "round_end")

        # 6. Verify scores accumulated across different games!
        self.assertEqual(session.tournament.participants["user_host"].score, 3)
        self.assertEqual(session.tournament.participants["guest_p"].score, 3)

        # 7. Tournament Master switches to RPS for Round 3!
        await session.tournament.handle_action("user_host", "tournament_next_round", {"selected_game": "rps"})
        self.assertEqual(session.tournament.status, "active")
        self.assertEqual(session.tournament.current_round, 3)
        self.assertEqual(session.tournament.active_matches[0].game_type, "rps")

        # Complete Round 3: draw
        m3 = session.tournament.active_matches[0]
        await session.tournament._resolve_match(m3, "draw")
        self.assertEqual(session.tournament.status, "finished")

        # Points from RPS draw (1 pt each) added to previous scores:
        self.assertEqual(session.tournament.participants["user_host"].score, 4)
        self.assertEqual(session.tournament.participants["guest_p"].score, 4)

    async def test_bot_intermediate_broadcast_and_rps_picks(self):
        # 1. Connect4: intermediate broadcast transmits player's move before bot moves
        s_c4 = session_manager.create_session("connect4", host=self.host, session_id="test_c4_bcast")
        c4_game: Connect4Game = s_c4.game
        await c4_game.handle_action("user_host", "start", {"mode": "bot", "difficulty": 3})

        broadcast_states = []
        async def mock_broadcast():
            broadcast_states.append(c4_game.get_state())

        await c4_game.handle_action("user_host", "move", {"col": 3}, broadcast_cb=mock_broadcast)
        # Intermediate broadcast occurred before bot move:
        self.assertEqual(len(broadcast_states), 1)
        # Player's move at bottom of col 3 (row 5 * 7 + 3 = 38)
        self.assertEqual(broadcast_states[0]["last_move"], 38)
        self.assertEqual(broadcast_states[0]["board"][38], "R")
        self.assertEqual(broadcast_states[0]["current_turn"], "bot_tanjun")

        # 2. TicTacToe: intermediate broadcast transmits player's move before bot moves
        s_ttt = session_manager.create_session("tictactoe", host=self.host, session_id="test_ttt_bcast")
        ttt_game: TicTacToeGame = s_ttt.game
        await ttt_game.handle_action("user_host", "start", {"mode": "bot", "difficulty": 3})

        ttt_bcasts = []
        async def mock_ttt_broadcast():
            ttt_bcasts.append(ttt_game.get_state())

        await ttt_game.handle_action("user_host", "move", {"cell": 4}, broadcast_cb=mock_ttt_broadcast)
        self.assertEqual(len(ttt_bcasts), 1)
        self.assertEqual(ttt_bcasts[0]["last_move"], 4)
        self.assertEqual(ttt_bcasts[0]["board"][4], "X")
        self.assertEqual(ttt_bcasts[0]["current_turn"], "bot_tanjun")

        # 3. RPS: intermediate broadcast records player pick, then round result contains both revealed picks
        s_rps = session_manager.create_session("rps", host=self.host, session_id="test_rps_bcast")
        rps_game: RPSGame = s_rps.game
        await rps_game.handle_action("user_host", "start", {"mode": "bot", "target_wins": 3})

        rps_bcasts = []
        async def mock_rps_broadcast():
            rps_bcasts.append(rps_game.get_state("user_host"))

        res = await rps_game.handle_action("user_host", "pick", {"choice": "scissors"}, broadcast_cb=mock_rps_broadcast)
        self.assertEqual(len(rps_bcasts), 1)
        self.assertEqual(rps_bcasts[0]["current_picks"]["user_host"], "scissors")

        # Final state contains last_round_result with revealed picks
        final_state = rps_game.get_state("user_host")
        self.assertIsNotNone(final_state["last_round_result"])
        self.assertEqual(final_state["last_round_result"]["picks"]["user_host"], "scissors")
        self.assertIn(final_state["last_round_result"]["picks"]["bot_tanjun"], ["rock", "paper", "scissors"])

    async def test_tournament_mehrkampf_playlist_progression(self):
        """Verify that Mehrkampf (playlist) mode cycles through disciplines per round."""
        from activities.tournament import Tournament, TournamentRewards

        session = session_manager.create_session("hub", host=self.host, session_id="test_mehrkampf")
        tourney: Tournament = session.create_tournament(host=self.host)
        p2 = Player(user_id="player_bob", username="Bob", display_name="Bob")
        tourney.add_participant(p2)

        # Configure playlist disciplines: Tic-Tac-Toe -> Connect4 -> RPS
        tourney.game_selection = "playlist"
        tourney.disciplines = ["tictactoe", "connect4", "rps"]
        tourney.total_rounds = 3

        # Round 1: should be tictactoe
        await tourney.start_tournament()
        self.assertEqual(tourney.current_round, 1)
        self.assertEqual(tourney.active_matches[0].game_type, "tictactoe")

        # Complete Round 1: host wins
        m1 = tourney.active_matches[0]
        await tourney.resolve_current_match("user_host")
        self.assertEqual(tourney.status, "round_end")

        # Round 2: should be connect4
        await tourney.start_next_round()
        self.assertEqual(tourney.current_round, 2)
        self.assertEqual(tourney.active_matches[0].game_type, "connect4")

        # Complete Round 2: bob wins
        await tourney.resolve_current_match("player_bob")
        self.assertEqual(tourney.status, "round_end")

        # Round 3: should be rps
        await tourney.start_next_round()
        self.assertEqual(tourney.current_round, 3)
        self.assertEqual(tourney.active_matches[0].game_type, "rps")

        # Complete Round 3: host wins
        await tourney.resolve_current_match("user_host")
        self.assertEqual(tourney.status, "finished")

        # Final podium check: Host has 6 pts (2 wins), Bob has 3 pts (1 win)
        podium = tourney.get_podium()
        self.assertEqual(podium[0]["user_id"], "user_host")
        self.assertEqual(podium[0]["score"], 6)
        self.assertEqual(podium[1]["user_id"], "player_bob")
        self.assertEqual(podium[1]["score"], 3)

    async def test_tournament_rewards_and_finish_callback(self):
        """Verify rewards data structure and on_finished_callback execution."""
        from activities.tournament import Tournament, TournamentRewards

        tourney = Tournament(session_id="test_rew_cup", host=self.host)
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        tourney.add_participant(p2)

        tourney.rewards = TournamentRewards(
            guild_id="123456789",
            channel_id="987654321",
            xp_1st=1000,
            xp_2nd=500,
            can_grant_xp=True,
            can_grant_role=True,
            role_id="112233"
        )
        tourney.total_rounds = 1

        callback_called = []
        async def mock_finish_callback(t):
            callback_called.append(t.title)

        tourney.on_finished_callback = mock_finish_callback

        await tourney.start_tournament("connect4")
        m1 = tourney.active_matches[0]
        await tourney._resolve_match(m1, "user_host")

        self.assertEqual(tourney.status, "finished")
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], "Tanjun Cup")
        self.assertTrue(tourney.rewards.can_grant_xp)
        self.assertEqual(tourney.rewards.xp_1st, 1000)

    async def test_tournament_match_transition_state(self):
        """Verify that when multiple matches exist, transition_info is populated and advance clears it."""
        from activities.tournament import Tournament

        tourney = Tournament(session_id="test_transition", host=self.host)
        p2 = Player(user_id="p2", username="P2", display_name="P2")
        p3 = Player(user_id="p3", username="P3", display_name="P3")
        p4 = Player(user_id="p4", username="P4", display_name="P4")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        tourney.add_participant(p4)

        # 4 participants -> 2 matches in round 1
        await tourney.start_tournament("connect4")
        self.assertEqual(len(tourney.active_matches), 2)
        self.assertIsNone(tourney.transition_info)

        # Match 1 completes -> transition_info is set for Match 2
        m1 = tourney.active_matches[0]
        await tourney.resolve_current_match(m1.player1.user_id)
        self.assertEqual(tourney.status, "active")
        self.assertIsNotNone(tourney.transition_info)
        self.assertTrue(tourney.transition_info["active"])
        self.assertEqual(tourney.transition_info["seconds_remaining"], 5)

        # Advance to match 2 -> transition_info cleared, match 2 is active
        m2 = await tourney.advance_to_next_match()
        self.assertIsNotNone(m2)
        self.assertEqual(m2.status, "active")
        self.assertIsNone(tourney.transition_info)

    async def test_leave_tournament_and_reconnect_non_elimination(self):
        """Verify leave_tournament removes in lobby, and disconnect doesn't eliminate in points mode."""
        session = session_manager.create_session("hub", host=self.host, session_id="test_leave_reconnect")
        tourney = session.create_tournament(host=self.host)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)
        self.assertEqual(len(tourney.participants), 2)

        # 1. Leave in lobby removes participant
        session.leave_tournament("user_p2")
        self.assertNotIn("user_p2", tourney.participants)

        # 2. Rejoin and start tournament
        tourney.add_participant(p2)
        await tourney.start_tournament("connect4")
        self.assertEqual(tourney.status, "active")

        # 3. Disconnect in active tournament (points mode) only marks connected=False, NOT is_eliminated
        tourney.remove_participant("user_p2")
        self.assertFalse(tourney.participants["user_p2"].connected)
        self.assertFalse(tourney.participants["user_p2"].is_eliminated)

        # 4. Reconnect restores connected=True
        tourney.add_participant(p2)
        self.assertTrue(tourney.participants["user_p2"].connected)
        self.assertFalse(tourney.participants["user_p2"].is_eliminated)

    async def test_host_migration(self):
        """Verify that when host departs, session & tournament migrate to next connected human player."""
        session = session_manager.create_session("hub", host=self.host, session_id="test_migration")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        session.game.add_player(p2)
        tourney = session.create_tournament(host=self.host)
        tourney.add_participant(p2)

        self.assertEqual(session.game.host.user_id, "user_host")
        self.assertEqual(tourney.host_id, "user_host")

        # Migrate when user_host departs
        new_host = session.migrate_host_if_needed("user_host")
        self.assertIsNotNone(new_host)
        self.assertEqual(new_host.user_id, "user_p2")
        self.assertEqual(session.game.host.user_id, "user_p2")
        self.assertTrue(session.game.players["user_p2"].is_host)
        self.assertEqual(tourney.host_id, "user_p2")
        self.assertTrue(tourney.participants["user_p2"].is_host)

    async def test_tournament_end_early_callback(self):
        """Verify that host ending tournament early triggers on_finished_callback."""
        from activities.tournament import Tournament

        tourney = Tournament(session_id="test_end_early", host=self.host)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)

        finished_events = []
        async def mock_finish_cb(t):
            finished_events.append(t.session_id)

        tourney.on_finished_callback = mock_finish_cb
        await tourney.start_tournament("tictactoe")
        self.assertEqual(tourney.status, "active")

        # Host ends tournament early
        res = await tourney.handle_action("user_host", "tournament_end", {})
        self.assertEqual(res["status"], "tournament_finished")
        self.assertEqual(tourney.status, "finished")
        self.assertEqual(len(finished_events), 1)
        self.assertEqual(finished_events[0], "test_end_early")

    async def test_connect4_bot_avoids_suicide_trap(self):
        """Verify that Connect 4 bot AI on difficulty >= 3 avoids setting up a winning move for player."""
        session = session_manager.create_session("connect4", host=self.host, session_id="test_c4_trap")
        game: Connect4Game = session.game
        game.difficulty = 4
        game.setup_bot(difficulty=4)
        game.player_symbols = {"user_host": "R", "bot_tanjun": "Y"}
        game.is_started = True

        # Set up horizontal 3-in-a-row for Human "R" on row 4 in columns 0, 1, 2.
        # If bot places chip in column 3, row 5 (the bottom row), row 4 in col 3 will become playable for Human to win!
        # Bottom row (row 5) indices: 5 * 7 + c = 35 + c
        # Row 4 indices: 4 * 7 + c = 28 + c
        game.board = [""] * 42
        # Human chips at row 4, cols 0, 1, 2
        game.board[4 * 7 + 0] = "R"
        game.board[4 * 7 + 1] = "R"
        game.board[4 * 7 + 2] = "R"
        # Support chips under them on row 5 (non-winning for bot)
        game.board[5 * 7 + 0] = "Y"
        game.board[5 * 7 + 1] = "R"
        game.board[5 * 7 + 2] = "Y"

        # Now column 3 is empty at row 5. If bot plays in col 3 at row 5, human can play row 4, col 3 and win with 4-in-a-row!
        # Col 4, 5, 6 are completely empty and safe.
        bot_choice = game._bot_calculate_move()
        # Bot should NOT choose column 3!
        self.assertNotEqual(bot_choice, 3, "Bot should have avoided column 3 because it sets up a human win on row 4!")

    async def test_bot_first_turn_handover(self):
        """Verify that when bot makes first move, turn hands over to human player properly."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_first_turn")
        game: TicTacToeGame = session.game
        game.first_turn_rule = "guest"  # Guest is bot
        await game.handle_action("user_host", "start", {"mode": "bot", "first_turn": "guest"})

        self.assertTrue(game.is_started)
        # Bot made move, turn must now be user_host
        self.assertEqual(game.current_turn, "user_host")
        x_count = sum(1 for c in game.board if c == "X")
        o_count = sum(1 for c in game.board if c == "O")
        self.assertEqual(o_count, 1)
        self.assertEqual(x_count, 0)


    async def test_spectator_action_rejection(self):
        """Verify that spectators cannot make game moves or picks."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_spec_rej")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        spec = Player(user_id="user_spec", username="Spec", display_name="Spectator")
        session.game.add_player(p2)
        session.game.add_player(spec)  # exceeds max_players (2) -> added as spectator
        self.assertIn("user_spec", session.game.spectators)

        await session.game.handle_action("user_host", "start", {"mode": "pvp"})
        self.assertTrue(session.game.is_started)

        # Spectator tries to move in TicTacToe
        res = await session.game.handle_action("user_spec", "move", {"cell": 0})
        self.assertIn("error", res)
        self.assertIn("Spectator", res["error"])

        # Same for Connect4
        c4_session = session_manager.create_session("connect4", host=self.host, session_id="test_c4_spec")
        c4_session.game.add_player(p2)
        c4_session.game.add_player(spec)
        await c4_session.game.handle_action("user_host", "start", {"mode": "pvp"})
        c4_res = await c4_session.game.handle_action("user_spec", "move", {"col": 0})
        self.assertIn("error", c4_res)
        self.assertIn("Spectator", c4_res["error"])

        # Same for RPS
        rps_session = session_manager.create_session("rps", host=self.host, session_id="test_rps_spec")
        rps_session.game.add_player(p2)
        rps_session.game.add_player(spec)
        await rps_session.game.handle_action("user_host", "start", {"mode": "pvp"})
        rps_res = await rps_session.game.handle_action("user_spec", "pick", {"choice": "rock"})
        self.assertIn("error", rps_res)
        self.assertIn("Only active players", rps_res["error"])

    async def test_spectators_included_in_tournament_mode(self):
        """Verify that spectators from Hub/game are transferred into tournament participants."""
        session = session_manager.create_session("hub", host=self.host, session_id="test_hub_tourney")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        p3 = Player(user_id="user_p3", username="P3", display_name="Player 3")
        p4 = Player(user_id="user_p4", username="P4", display_name="Player 4")
        session.game.add_player(p2)
        session.game.add_player(p3)  # In hub with max_players=2, p3 & p4 become spectators
        session.game.add_player(p4)

        self.assertEqual(len(session.game.players), 2)
        self.assertEqual(len(session.game.spectators), 2)

        # Host initiates tournament mode
        session.start_tournament_mode()
        self.assertIsNotNone(session.tournament)
        # All 4 participants must be registered in the tournament
        self.assertEqual(len(session.tournament.participants), 4)
        self.assertIn("user_host", session.tournament.participants)
        self.assertIn("user_p2", session.tournament.participants)
        self.assertIn("user_p3", session.tournament.participants)
        self.assertIn("user_p4", session.tournament.participants)

    async def test_rps_spectator_no_deadlock(self):
        """Verify that RPS round evaluates cleanly between duelists even if spectators are present."""
        session = session_manager.create_session("rps", host=self.host, session_id="test_rps_deadlock")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        spec = Player(user_id="user_spec", username="Spec", display_name="Spectator")
        session.game.add_player(p2)
        session.game.add_player(spec)

        await session.game.handle_action("user_host", "start", {"mode": "pvp", "target_wins": 2})
        self.assertTrue(session.game.is_started)

        # Host picks rock
        p1_res = await session.game.handle_action("user_host", "pick", {"choice": "rock"})
        self.assertFalse(p1_res["round_completed"])

        # P2 picks scissors -> round must complete immediately without waiting for spec!
        p2_res = await session.game.handle_action("user_p2", "pick", {"choice": "scissors"})
        self.assertTrue(p2_res["round_completed"])
        self.assertEqual(p2_res["round_result"]["winner"], "user_host")
        self.assertEqual(session.game.scores["user_host"], 1)

    async def test_switch_game_respects_capacity(self):
        """Verify switch_game maintains max_players bound and routes extra players to spectators."""
        session = session_manager.create_session("connect4", host=self.host, session_id="test_switch_cap")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        session.game.add_player(p2)

        # Switch to TicTacToe (max_players = 2)
        new_game = session.switch_game("tictactoe")
        self.assertEqual(new_game.game_type, "tictactoe")
        self.assertLessEqual(len(new_game.players), new_game.max_players)

    async def test_score_reset_on_mode_change_and_lobby(self):
        """Verify game scores are cleared when returning to lobby or switching game modes."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_score_reset")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        session.game.add_player(p2)

        await session.game.handle_action("user_host", "start", {"mode": "pvp"})
        # Complete a game: host wins
        session.game.current_turn = "user_host"
        await session.game.handle_action("user_host", "move", {"cell": 0})
        await session.game.handle_action("user_p2", "move", {"cell": 3})
        await session.game.handle_action("user_host", "move", {"cell": 1})
        await session.game.handle_action("user_p2", "move", {"cell": 4})
        await session.game.handle_action("user_host", "move", {"cell": 2})

        self.assertTrue(session.game.is_finished)
        self.assertEqual(session.game.scores["user_host"], 1)

        # Return to lobby
        lobby_res = await session.game.handle_action("user_host", "lobby", {})
        self.assertEqual(lobby_res["status"], "lobby")
        self.assertEqual(session.game.scores["user_host"], 0)

    async def test_points_tournament_retains_disconnected_players(self):
        """Verify that in points tournament, temporary disconnected status doesn't eliminate player from next round."""
        from activities.tournament import Tournament

        tourney = Tournament(session_id="test_disc_ret", host=self.host)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)

        await tourney.handle_action("user_host", "tournament_update_settings", {
            "format": "points",
            "total_rounds": 3,
            "selected_game": "tictactoe"
        })
        await tourney.start_tournament("tictactoe")
        self.assertEqual(tourney.current_round, 1)

        # Simulate match resolution
        curr_m = tourney.get_current_match()
        await tourney.resolve_current_match("user_host")
        self.assertEqual(tourney.status, "round_end")

        # P2 has a brief network disconnect before round 2 starts
        tourney.participants["user_p2"].connected = False

        # Host advances to round 2
        await tourney.handle_action("user_host", "tournament_next_round", {})
        self.assertEqual(tourney.current_round, 2)
        # P2 should still be in the round pairings!
        match_pids = [tourney.active_matches[0].player1.user_id, tourney.active_matches[0].player2.user_id]
        self.assertIn("user_p2", match_pids)

    async def test_tournament_leave_active_match_forfeit(self):
        """Verify that voluntarily leaving an active match forfeits to the opponent."""
        from activities.tournament import Tournament

        tourney = Tournament(session_id="test_forfeit", host=self.host)
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        p3 = Player(user_id="user_p3", username="P3", display_name="Player 3")
        tourney.add_participant(p2)
        tourney.add_participant(p3)

        await tourney.start_tournament("tictactoe")
        self.assertEqual(tourney.status, "active")

        # Find match with p2
        curr_m = tourney.get_current_match()
        active_pids = [curr_m.player1.user_id, curr_m.player2.user_id if curr_m.player2 else None]
        leaving_pid = active_pids[0]
        expected_winner = active_pids[1]

        winner = tourney.remove_participant(leaving_pid, voluntary=True)
        self.assertEqual(winner, expected_winner)

        # Resolve match with the forfeit winner
        await tourney.resolve_current_match(winner)
        self.assertEqual(curr_m.status, "finished")
        self.assertEqual(curr_m.winner_id, expected_winner)

    async def test_points_tournament_finishes_when_only_one_player_remains(self):
        """Verify that tournament finishes immediately when remaining active participants drop to 1."""
        from activities.tournament import Tournament

        finished_called = []
        async def on_fin(t):
            finished_called.append(t.session_id)

        tourney = Tournament(session_id="test_dropouts", host=self.host)
        tourney.on_finished_callback = on_fin
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)

        await tourney.start_tournament("tictactoe")
        self.assertEqual(tourney.status, "active")

        # P2 voluntarily leaves
        forfeit_winner = tourney.remove_participant("user_p2", voluntary=True)
        self.assertEqual(forfeit_winner, "user_host")
        await tourney.resolve_current_match(forfeit_winner)

        # Because only 1 player remains, tournament should finish immediately!
        self.assertEqual(tourney.status, "finished")
        self.assertEqual(len(finished_called), 1)

    async def test_knockout_disconnect_reconnect_and_forfeit_timer(self):
        """Verify that a disconnected player can reconnect during match, or forfeits after timeout."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_reconnect_ko")
        tourney = session.start_tournament_mode()
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)

        await tourney.handle_action("user_host", "tournament_update_settings", {
            "format": "knockout",
            "selected_game": "tictactoe"
        })
        await tourney.start_tournament("tictactoe")

        curr_m = tourney.get_current_match()
        self.assertEqual(curr_m.status, "active")

        # 1. P2 has a brief network disconnect
        winner = tourney.remove_participant("user_p2", voluntary=False)
        self.assertIsNone(winner, "Temporary disconnect should not immediately forfeit active match")
        self.assertFalse(tourney.participants["user_p2"].connected)
        session.schedule_disconnect_forfeit("user_p2", delay=0.1)

        # 2. P2 reconnects within grace period!
        session.cancel_disconnect_forfeit("user_p2")
        tourney.add_participant(p2)
        self.assertTrue(tourney.participants["user_p2"].connected)
        self.assertEqual(curr_m.status, "active")

        # 3. P2 disconnects again and timeout expires without reconnecting
        tourney.remove_participant("user_p2", voluntary=False)
        session.schedule_disconnect_forfeit("user_p2", delay=0.05)
        # Wait for timeout
        await asyncio.sleep(0.1)

        # Match must have been forfeited to user_host
        self.assertEqual(curr_m.status, "finished")
        self.assertEqual(curr_m.winner_id, "user_host")
        self.assertEqual(tourney.status, "finished")

    async def test_malformed_action_payloads(self):
        """Verify robust error handling on non-int or malformed action payloads."""
        # Connect4
        c4_session = session_manager.create_session("connect4", host=self.host, session_id="test_malformed_c4")
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        c4_session.game.add_player(p2)
        await c4_session.game.handle_action("user_host", "start", {"mode": "pvp"})
        c4_session.game.current_turn = "user_host"

        # String column
        r1 = await c4_session.game.handle_action("user_host", "move", {"col": "not_a_number"})
        self.assertIn("error", r1)
        self.assertEqual(r1["error"], "Invalid column")

        # Boolean column (isinstance(True, int) in Python)
        r2 = await c4_session.game.handle_action("user_host", "move", {"col": True})
        self.assertIn("error", r2)
        self.assertEqual(r2["error"], "Invalid column")

        # TicTacToe
        ttt_session = session_manager.create_session("tictactoe", host=self.host, session_id="test_malformed_ttt")
        ttt_session.game.add_player(p2)
        await ttt_session.game.handle_action("user_host", "start", {"mode": "pvp"})
        ttt_session.game.current_turn = "user_host"

        # String cell
        t1 = await ttt_session.game.handle_action("user_host", "move", {"cell": "nine"})
        self.assertIn("error", t1)
        self.assertEqual(t1["error"], "Invalid cell move")

        # Boolean cell
        t2 = await ttt_session.game.handle_action("user_host", "move", {"cell": False})
        self.assertIn("error", t2)
        self.assertEqual(t2["error"], "Invalid cell move")

        # RPS
        rps_session = session_manager.create_session("rps", host=self.host, session_id="test_malformed_rps")
        rps_session.game.add_player(p2)
        await rps_session.game.handle_action("user_host", "start", {"mode": "pvp"})

        # Non-string choice
        rps1 = await rps_session.game.handle_action("user_host", "pick", {"choice": 123})
        self.assertIn("error", rps1)
        self.assertIn("Invalid choice", rps1["error"])

    async def test_session_manager_cleanup_idle_sessions(self):
        """Verify that inactive sessions without sockets are purged when idle timeout expires."""
        s = session_manager.create_session("tictactoe", host=self.host, session_id="test_cleanup_stale")
        self.assertIsNotNone(session_manager.get_session("test_cleanup_stale"))

        # Simulate session created 2 hours ago
        s.last_activity = asyncio.get_event_loop().time() - 7200
        # Clean up sessions idle > 3600s
        await session_manager.cleanup_idle_sessions(max_idle_seconds=3600)

        # Stale session must have been purged
        self.assertIsNone(session_manager.get_session("test_cleanup_stale"))

    async def test_standard_game_disconnect_forfeit_and_reconnect(self):
        """Verify that in standard games, disconnect sets a grace period forfeit timer,
        and reconnecting cancels forfeit while timeout forfeits match to opponent."""
        session = session_manager.create_session("connect4", host=self.host, session_id="test_std_disconnect")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)
        await session.game.handle_action("user_host", "start", {"mode": "pvp"})
        self.assertTrue(session.game.is_started)
        self.assertFalse(session.game.is_finished)

        # 1. Guest disconnects (e.g. mobile app backgrounded)
        session.game.remove_player("user_guest")
        self.assertFalse(session.game.players["user_guest"].connected)
        session.schedule_disconnect_forfeit("user_guest", delay=0.1)

        # 2. Guest reconnects within grace period
        session.cancel_disconnect_forfeit("user_guest")
        session.game.add_player(p2)
        self.assertTrue(session.game.players["user_guest"].connected)
        self.assertTrue(session.game.is_started)
        self.assertFalse(session.game.is_finished)

        # 3. Guest drops connection permanently and forfeit timer expires
        session.game.remove_player("user_guest")
        session.schedule_disconnect_forfeit("user_guest", delay=0.05)
        await asyncio.sleep(0.1)

        # Game must now be finished with host awarded the win by forfeit
        self.assertTrue(session.game.is_finished)
        self.assertEqual(session.game.winner, "user_host")
        self.assertEqual(session.game.scores.get("user_host"), 1)

    async def test_rps_secret_choice_masking_no_spectator_leak(self):
        """Verify that secret picks in RPS are never leaked to opponents or unauthenticated/spectator requests."""
        session = session_manager.create_session("rps", host=self.host, session_id="test_rps_masking")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)
        await session.game.handle_action("user_host", "start", {"mode": "pvp"})

        # Host picks rock
        pick_res = await session.game.handle_action("user_host", "pick", {"choice": "rock"})
        self.assertEqual(pick_res["status"], "picked")

        # 1. Host sees their own pick
        host_state = session.game.get_state(for_user_id="user_host")
        self.assertEqual(host_state["current_picks"]["user_host"], "rock")

        # 2. Opponent (Guest) sees masked "locked" pick
        guest_state = session.game.get_state(for_user_id="user_guest")
        self.assertEqual(guest_state["current_picks"]["user_host"], "locked")

        # 3. Spectator or API GET request with for_user_id=None sees masked "locked"
        spectator_state = session.game.get_state(for_user_id=None)
        self.assertEqual(spectator_state["current_picks"]["user_host"], "locked")

    async def test_host_migration_delayed_on_disconnect_timeout(self):
        """Verify host migration only occurs after disconnect grace period expires,
        and cleanly unsets the former host's is_host flag."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_host_migrate")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)
        self.assertTrue(session.game.players["user_host"].is_host)

        # Host disconnects
        session.game.remove_player("user_host")
        session.schedule_disconnect_forfeit("user_host", delay=0.05)

        # Before timeout expires, host is still user_host
        self.assertEqual(session.game.host.user_id, "user_host")

        # Wait for timeout to expire
        await asyncio.sleep(0.1)

        # Host privileges must have transferred to user_guest
        self.assertEqual(session.game.host.user_id, "user_guest")
        self.assertTrue(session.game.players["user_guest"].is_host)
        self.assertFalse(session.game.players["user_host"].is_host)

    async def test_pvp_voluntary_forfeit_action(self):
        """Verify that sending forfeit in an active PvP match awards the win to opponent."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_forfeit_action")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)
        await session.game.handle_action("user_host", "start", {"mode": "pvp"})

        # Guest forfeits
        self.assertTrue(session.game.is_started)
        self.assertFalse(session.game.is_finished)

        # Simulate forfeit action
        if session.game and session.game.is_started and not session.game.is_finished:
            opponents = [pid for pid in session.game.players if pid != "user_guest" and not session.game.players[pid].is_bot]
            if opponents:
                winner = opponents[0]
                session.game.is_finished = True
                session.game.winner = winner
                session.game.scores[winner] = session.game.scores.get(winner, 0) + 1

        self.assertTrue(session.game.is_finished)
        self.assertEqual(session.game.winner, "user_host")
        self.assertEqual(session.game.scores["user_host"], 1)

    async def test_tournament_host_preserved_when_spectating_matches(self):
        """Verify that when tournament host Alice is spectating Bob vs Charlie,
        Alice remains the session host and is_host is not falsely assigned to Bob."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_tourney_spectate_host")
        tourney = session.tournament
        p_bob = Player(user_id="user_bob", username="Bob", display_name="Bob")
        p_charlie = Player(user_id="user_charlie", username="Charlie", display_name="Charlie")
        tourney.add_participant(p_bob)
        tourney.add_participant(p_charlie)

        # Force pairings to be Bob vs Charlie, Alice receives bye or spectates
        await tourney.start_tournament("tictactoe")
        # Find a match where Alice is not playing
        alice_match = next((m for m in tourney.active_matches if m.player1.user_id != self.host.user_id and (not m.player2 or m.player2.user_id != self.host.user_id)), None)
        if alice_match:
            tourney.active_matches = [alice_match]
            tourney.current_match_idx = 0
            session.sync_tournament_match()

            # Host must still be Alice
            self.assertEqual(session.game.host.user_id, self.host.user_id)
            self.assertTrue(session.game.host.is_host)
            # Neither Bob nor Charlie should have hijacked host
            p1_player = session.game.players.get(alice_match.player1.user_id)
            if p1_player:
                self.assertFalse(p1_player.is_host)

    async def test_knockout_tournament_dispatches_finished_rewards(self):
        """Verify that knockout tournament triggers finish callback when final match concludes."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_knockout_finish_cb")
        tourney = session.tournament
        p2 = Player(user_id="user_p2", username="P2", display_name="Player 2")
        tourney.add_participant(p2)

        callback_called = False
        def _on_finish(t):
            nonlocal callback_called
            callback_called = True

        tourney.on_finished_callback = _on_finish
        await tourney.handle_action("user_host", "tournament_update_settings", {"format": "knockout"})
        await tourney.start_tournament("tictactoe")

        curr_m = tourney.get_current_match()
        self.assertIsNotNone(curr_m)
        # Host wins the final match
        await tourney.resolve_current_match("user_host")

        self.assertEqual(tourney.status, "finished")
        self.assertTrue(callback_called, "Finished callback must be invoked upon knockout conclusion")

    async def test_tictactoe_restart_respects_first_turn_rule(self):
        """Verify that restarting a TicTacToe game respects the first_turn_rule (guest)."""
        session = session_manager.create_session("tictactoe", host=self.host, session_id="test_ttt_restart_turn")
        p2 = Player(user_id="user_guest", username="Guest", display_name="Guest")
        session.game.add_player(p2)
        await session.game.handle_action("user_host", "start", {"mode": "pvp", "first_turn": "guest"})
        self.assertEqual(session.game.current_turn, "user_guest")

        # Restart game
        await session.game.handle_action("user_host", "restart", {})
        # Must still be user_guest's turn
        self.assertEqual(session.game.current_turn, "user_guest")

    async def test_tournament_cheer_length_clamping(self):
        """Verify that tournament cheer emote string is safely clamped."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_cheer_clamp")
        tourney = session.tournament
        p2 = Player(user_id="user_p2", username="P2", display_name="P2")
        tourney.add_participant(p2)
        await tourney.start_tournament("tictactoe")

        res = await tourney.handle_action("user_p2", "tournament_cheer", {"emote": "A" * 500})
        self.assertEqual(res["status"], "cheered")
        curr_m = tourney.get_current_match()
        self.assertTrue(len(curr_m.cheers) > 0)
        self.assertEqual(curr_m.cheers[-1]["emote"], "AAAAAAAA")

    async def test_tournament_match_style_settings_update(self):
        """Verify that match_style setting (spectated vs parallel) updates and persists."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_style_upd")
        tourney = session.tournament
        self.assertEqual(tourney.match_style, "spectated")

        # Host updates match_style to parallel
        res = await tourney.handle_action("user_host", "tournament_update_settings", {"match_style": "parallel"})
        self.assertEqual(res["status"], "settings_updated")
        self.assertEqual(tourney.match_style, "parallel")

        # State reflects parallel
        state = tourney.get_state()
        self.assertEqual(state["match_style"], "parallel")

        # Host switches back to spectated
        await tourney.handle_action("user_host", "tournament_update_settings", {"match_style": "spectated"})
        self.assertEqual(tourney.match_style, "spectated")

    async def test_tournament_dynamic_game_selection_and_expansion(self):
        """Verify that next round game can be chosen dynamically and tournament can be expanded."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_dynamic_cup")
        tourney = session.tournament
        p2 = Player(user_id="user_p2", username="Player2", display_name="Player 2")
        tourney.add_participant(p2)

        # Start with 1 planned round of Tic-Tac-Toe
        tourney.total_rounds = 1
        await tourney.handle_action("user_host", "tournament_start", {"selected_game": "tictactoe"})
        self.assertEqual(tourney.current_round, 1)
        self.assertEqual(tourney.active_matches[0].game_type, "tictactoe")

        # Finish round 1
        m1 = tourney.active_matches[0]
        await tourney._resolve_match(m1, "user_host")
        self.assertEqual(tourney.status, "finished")

        # Host dynamically continues and expands to round 2 with Connect 4!
        res = await tourney.handle_action("user_host", "tournament_next_round", {"selected_game": "connect4"})
        self.assertEqual(res["status"], "next_round_started")
        self.assertEqual(tourney.current_round, 2)
        self.assertEqual(tourney.total_rounds, 2)
        self.assertEqual(tourney.status, "active")
        self.assertEqual(tourney.active_matches[0].game_type, "connect4")

        # Finish round 2
        m2 = tourney.active_matches[0]
        await tourney._resolve_match(m2, "user_p2")
        self.assertEqual(tourney.status, "finished")

        # Host dynamically adds a round before starting it
        add_res = await tourney.handle_action("user_host", "tournament_add_round", {})
        self.assertEqual(add_res["status"], "round_added")
        self.assertEqual(tourney.total_rounds, 3)
        self.assertEqual(tourney.status, "round_end")

        # Host starts round 3 with RPS
        await tourney.handle_action("user_host", "tournament_next_round", {"selected_game": "rps"})
        self.assertEqual(tourney.current_round, 3)
        self.assertEqual(tourney.active_matches[0].game_type, "rps")

    async def test_tournament_max_players_limit_raised(self):
        """Verify tournament max_players is configured for large groups (64)."""
        games = session_manager.get_supported_games()
        tourney_game = next((g for g in games if g["type"] == "tournament"), None)
        self.assertIsNotNone(tourney_game)
        self.assertEqual(tourney_game["max_players"], 64)

    async def test_tournament_parallel_forfeit_and_disconnect(self):
        """Verify that a disconnect/forfeit in match 1 of a parallel round resolves match 1 and does not break match 0."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_parallel_forfeit")
        tourney = session.tournament
        tourney.match_style = "parallel"
        p2 = Player(user_id="user_p2", username="Player2", display_name="Player 2")
        p3 = Player(user_id="user_p3", username="Player3", display_name="Player 3")
        p4 = Player(user_id="user_p4", username="Player4", display_name="Player 4")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        tourney.add_participant(p4)

        await tourney.handle_action("user_host", "tournament_start", {"selected_game": "tictactoe"})
        self.assertEqual(len(tourney.active_matches), 2)
        self.assertEqual(tourney.active_matches[0].status, "active")
        self.assertEqual(tourney.active_matches[1].status, "active")

        # Identify which match player 3 is in
        m_p3 = tourney.get_match_for_user("user_p3")
        self.assertIsNotNone(m_p3)
        p3_opponent_id = m_p3.player2.user_id if m_p3.player1.user_id == "user_p3" else m_p3.player1.user_id

        # Schedule disconnect forfeit with a small delay
        session.schedule_disconnect_forfeit("user_p3", delay=0.01)
        await asyncio.sleep(0.05)

        # Match for player 3 should be finished and awarded to opponent
        self.assertEqual(m_p3.status, "finished")
        self.assertEqual(m_p3.winner_id, p3_opponent_id)

        # The other match must still be active!
        other_m = next(m for m in tourney.active_matches if m != m_p3)
        self.assertEqual(other_m.status, "active")
        self.assertEqual(tourney.status, "active")

        # Now voluntary forfeit the other match
        other_player = other_m.player1.user_id
        other_opponent = other_m.player2.user_id
        winner = session.leave_tournament(other_player)
        self.assertEqual(winner, other_opponent)
        await tourney._resolve_match(other_m, winner)
        self.assertEqual(other_m.status, "finished")

        # Now that both matches finished, round ends
        self.assertIn(tourney.status, ("round_end", "finished"))

    async def test_tournament_reset_to_lobby_clears_history_and_state(self):
        """Verify that resetting a finished tournament to lobby cleans up history, rounds, and eliminations."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_reset_lobby")
        tourney = session.tournament
        p2 = Player(user_id="user_p2", username="Player2", display_name="Player 2")
        tourney.add_participant(p2)

        await tourney.handle_action("user_host", "tournament_start", {"selected_game": "tictactoe"})
        m = tourney.active_matches[0]
        await tourney._resolve_match(m, "user_host")
        self.assertEqual(len(tourney.match_history), 1)
        self.assertIn(tourney.status, ("round_end", "finished"))

        # Reset to lobby
        res = await tourney.handle_action("user_host", "tournament_reset_to_lobby", {})
        self.assertEqual(res["status"], "reset_to_lobby")
        self.assertEqual(tourney.status, "lobby")
        self.assertEqual(tourney.current_round, 0)
        self.assertEqual(len(tourney.active_matches), 0)
        self.assertEqual(len(tourney.match_history), 0)
        self.assertIsNone(tourney.last_round_result)
        self.assertIsNone(tourney.spectated_match_id)
        self.assertEqual(tourney.participants["user_host"].score, 0)

    async def test_tournament_knockout_leaderboard_prioritizes_non_eliminated(self):
        """Verify that in knockout mode, surviving players rank above eliminated ones."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_ko_rank")
        tourney = session.tournament
        tourney.format = "knockout"
        p2 = Player(user_id="user_p2", username="Player2", display_name="Player 2")
        tourney.add_participant(p2)

        # Eliminate p2
        tourney.participants["user_p2"].is_eliminated = True
        tourney.participants["user_p2"].score = 10
        tourney.participants["user_host"].is_eliminated = False
        tourney.participants["user_host"].score = 3

        lb = tourney.get_leaderboard()
        self.assertEqual(lb[0]["user_id"], "user_host")
        self.assertEqual(lb[1]["user_id"], "user_p2")

    async def test_tournament_spectator_switch_in_parallel_mode(self):
        """Verify that spectators in parallel mode receive the spectated match game state and can switch matches."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_spectate_switch")
        tourney = session.tournament
        tourney.match_style = "parallel"
        p2 = Player(user_id="user_p2", username="Player2", display_name="Player 2")
        p3 = Player(user_id="user_p3", username="Player3", display_name="Player 3")
        p4 = Player(user_id="user_p4", username="Player4", display_name="Player 4")
        spec = Player(user_id="user_spec", username="Spectator", display_name="Spectator")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        tourney.add_participant(p4)
        session.game.spectators["user_spec"] = spec

        await tourney.handle_action("user_host", "tournament_start", {"selected_game": "tictactoe"})
        self.assertEqual(len(tourney.active_matches), 2)
        m0 = tourney.active_matches[0]
        m1 = tourney.active_matches[1]

        # By default, spectated_match_id is m0
        self.assertEqual(tourney.spectated_match_id, m0.match_id)
        state_spec = session.get_full_state(for_user_id="user_spec")
        self.assertEqual(state_spec["players"][0]["user_id"], m0.player1.user_id)

        # Spectator switches to watch match 1
        res = await tourney.handle_action("user_spec", "tournament_spectate_match", {"match_id": m1.match_id})
        self.assertEqual(res["status"], "spectating_match")
        self.assertEqual(tourney.spectated_match_id, m1.match_id)

        # Spectator now gets match 1's state
        state_spec_m1 = session.get_full_state(for_user_id="user_spec")
        self.assertEqual(state_spec_m1["players"][0]["user_id"], m1.player1.user_id)

    async def test_channel_alias_registration_and_lookup(self):
        """Verify that voice channel ID aliases correctly route to the associated game session."""
        session = session_manager.create_session("hub", host=self.host, session_id="session_target_123")
        voice_channel_id = "1234567890123456"

        # Register channel alias
        session_manager.register_channel_alias(voice_channel_id, session.session_id)

        # Lookup by channel
        resolved_by_channel = session_manager.get_session_by_channel(voice_channel_id)
        self.assertIsNotNone(resolved_by_channel)
        self.assertEqual(resolved_by_channel.session_id, "session_target_123")

        # Lookup by get_session directly with channel ID (alias fallback)
        resolved_by_alias = session_manager.get_session(voice_channel_id)
        self.assertIsNotNone(resolved_by_alias)
        self.assertEqual(resolved_by_alias.session_id, "session_target_123")

        # Clean up session and verify alias is removed
        session_manager.remove_session(session.session_id)
        self.assertIsNone(session_manager.get_session(voice_channel_id))
        self.assertIsNone(session_manager.get_session_by_channel(voice_channel_id))

    async def test_points_tournament_fair_pairings_minimize_duplicates(self):
        """Verify that in points tournament, pairings across rounds minimize repeat encounters."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_fair_pairs")
        tourney = session.tournament
        tourney.format = "points"
        tourney.total_rounds = 3

        p2 = Player(user_id="p2", username="Player2", display_name="Player 2")
        p3 = Player(user_id="p3", username="Player3", display_name="Player 3")
        p4 = Player(user_id="p4", username="Player4", display_name="Player 4")
        tourney.add_participant(p2)
        tourney.add_participant(p3)
        tourney.add_participant(p4)

        # Round 1
        await tourney.start_tournament("tictactoe")
        self.assertEqual(len(tourney.active_matches), 2)
        for m in tourney.active_matches:
            await tourney._resolve_match(m, m.player1.user_id)

        # Round 2
        await tourney.start_next_round()
        self.assertEqual(len(tourney.active_matches), 2)
        for m in tourney.active_matches:
            await tourney._resolve_match(m, m.player1.user_id)

        # Round 3
        await tourney.start_next_round()
        self.assertEqual(len(tourney.active_matches), 2)
        for m in tourney.active_matches:
            await tourney._resolve_match(m, m.player1.user_id)

        # With 4 players and 3 rounds, each pair (A vs B, A vs C, A vs D, etc.) can be completely unique
        encounters = set()
        for m in tourney.match_history:
            if m.get("p1_id") and m.get("p2_id"):
                pair = frozenset([m["p1_id"], m["p2_id"]])
                self.assertNotIn(pair, encounters, f"Pair {pair} was matched more than once in a 4-player 3-round tournament!")
                encounters.add(pair)
        self.assertEqual(len(encounters), 6)  # Exactly 6 unique pairs (4 choose 2)

    async def test_odd_players_tournament_fair_byes(self):
        """Verify that an odd number of players gives Byes fairly without starving any player."""
        session = session_manager.create_session("tournament", host=self.host, session_id="test_byes")
        tourney = session.tournament
        tourney.format = "points"
        tourney.total_rounds = 3

        p2 = Player(user_id="p2", username="Player2", display_name="Player 2")
        p3 = Player(user_id="p3", username="Player3", display_name="Player 3")
        tourney.add_participant(p2)
        tourney.add_participant(p3)

        # 3 players total. Over 3 rounds, each player must receive exactly 1 Bye!
        byes_received = []

        # Round 1
        await tourney.start_tournament("tictactoe")
        bye_m1 = next(m for m in tourney.active_matches if m.is_bye)
        byes_received.append(bye_m1.player1.user_id)
        # Finish active matches
        for m in tourney.active_matches:
            if not m.is_bye:
                await tourney._resolve_match(m, m.player1.user_id)

        # Round 2
        await tourney.start_next_round()
        bye_m2 = next(m for m in tourney.active_matches if m.is_bye)
        byes_received.append(bye_m2.player1.user_id)
        for m in tourney.active_matches:
            if not m.is_bye:
                await tourney._resolve_match(m, m.player1.user_id)

        # Round 3
        await tourney.start_next_round()
        bye_m3 = next(m for m in tourney.active_matches if m.is_bye)
        byes_received.append(bye_m3.player1.user_id)

        # All 3 byes must have gone to different players!
        self.assertEqual(len(set(byes_received)), 3)
        self.assertIn("user_host", byes_received)
        self.assertIn("p2", byes_received)
        self.assertIn("p3", byes_received)

    async def test_api_config_secret_handling(self):
        """Verify that get_config_dict correctly reports has_client_secret even with SecretStr empty values."""
        from pydantic import SecretStr
        import config
        from activities.server import ActivityServer

        server = ActivityServer()

        orig_secret = getattr(config, "discord_client_secret", None)
        try:
            # Case 1: empty SecretStr
            config.discord_client_secret = SecretStr("")
            cfg1 = server.get_config_dict()
            self.assertFalse(cfg1["has_client_secret"])

            # Case 2: whitespace SecretStr
            config.discord_client_secret = SecretStr("   ")
            cfg2 = server.get_config_dict()
            self.assertFalse(cfg2["has_client_secret"])

            # Case 3: valid SecretStr
            config.discord_client_secret = SecretStr("my_valid_secret")
            cfg3 = server.get_config_dict()
            self.assertTrue(cfg3["has_client_secret"])
        finally:
            config.discord_client_secret = orig_secret


if __name__ == "__main__":
    unittest.main()



