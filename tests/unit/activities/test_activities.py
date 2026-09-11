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


if __name__ == "__main__":
    unittest.main()



