from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from aiohttp import web
from activities.base import BaseGame, Player
from activities.games.tictactoe import TicTacToeGame
from activities.games.connect4 import Connect4Game
from activities.games.rps import RPSGame

logger = logging.getLogger(__name__)


class GameSession:
    """Manages an active game instance, its connected WebSockets, and Hub navigation."""

    def __init__(self, session_id: str, game: BaseGame, is_hub: bool = False) -> None:
        self.session_id: str = session_id
        self.game: BaseGame = game
        self.is_hub: bool = is_hub
        self.tournament: Any = None
        self.sockets: Dict[str, web.WebSocketResponse] = {}  # user_id -> ws
        self.created_at: float = asyncio.get_event_loop().time()
        self.last_activity: float = self.created_at
        self.lobby_settings: Dict[str, Any] = {
            "mode": "pvp",
            "first_turn": "host",
            "difficulty": 3,
            "rows": 6,
            "cols": 7,
            "connect": 4,
            "target_wins": 3,
            "variation": "classic"
        }

    def create_tournament(self, host: Player) -> Any:
        from activities.tournament import Tournament
        self.tournament = Tournament(session_id=self.session_id, host=host)
        return self.tournament

    def start_tournament_mode(self) -> Any:
        from activities.tournament import Tournament
        self.tournament = Tournament(session_id=self.session_id, host=self.game.host)
        for pid, player in self.game.players.items():
            if not player.is_bot:
                self.tournament.add_participant(player)
        return self.tournament

    def join_tournament(self, player: Player) -> Any:
        if not self.tournament:
            return None
        return self.tournament.add_participant(player)

    def sync_tournament_match(self) -> None:
        if not self.tournament or self.tournament.status not in ("active", "round_end"):
            return
        curr_m = self.tournament.get_current_match()
        if not curr_m:
            return

        # Ensure session game matches current tournament match game type
        if self.game.game_type != curr_m.game_type:
            self.switch_game(curr_m.game_type)

        # Collect all known players
        all_known: Dict[str, Player] = {}
        for p in self.game.players.values():
            all_known[p.user_id] = p
        for p in self.game.spectators.values():
            all_known[p.user_id] = p
        for tp in self.tournament.participants.values():
            if tp.user_id not in all_known:
                all_known[tp.user_id] = Player(
                    user_id=tp.user_id,
                    username=tp.username,
                    display_name=tp.display_name,
                    avatar_url=tp.avatar_url,
                    is_host=tp.is_host
                )

        p1_id = curr_m.player1.user_id
        p2_id = curr_m.player2.user_id if curr_m.player2 else None

        new_players: Dict[str, Player] = {}
        new_spectators: Dict[str, Player] = {}

        for uid, p in all_known.items():
            if uid == p1_id:
                p.is_host = True
                new_players[uid] = p
            elif p2_id and uid == p2_id:
                p.is_host = False
                new_players[uid] = p
            else:
                new_spectators[uid] = p

        self.game.players = new_players
        self.game.spectators = new_spectators
        self.is_hub = False
        if not self.game.is_started or self.game.is_finished:
            self.game.start_game()

    def switch_game(self, game_type: str) -> BaseGame:
        if game_type == "tournament":
            self.start_tournament_mode()
            return self.game

        cls = session_manager.get_game_class(game_type)
        if not cls:
            raise ValueError(f"Unknown game type: {game_type}")

        # Preserve players and host across games
        new_game = cls(session_id=self.session_id, host=self.game.host)
        for pid, player in self.game.players.items():
            if not player.is_bot:
                new_game.players[pid] = player
        new_game.spectators = dict(self.game.spectators)
        self.game = new_game
        self.is_hub = False
        return new_game

    def get_full_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        state = self.game.get_state(for_user_id=for_user_id)
        state["is_hub"] = self.is_hub
        state["available_games"] = session_manager.get_supported_games()
        state["lobby_settings"] = self.lobby_settings
        state["tournament"] = self.tournament.get_state(for_user_id=for_user_id) if self.tournament else None
        return state

    async def broadcast(self, message: Dict[str, Any]) -> None:
        payload = json.dumps(message)
        dead_sockets: list[str] = []
        for user_id, ws in list(self.sockets.items()):
            if ws.closed:
                dead_sockets.append(user_id)
                continue
            try:
                await ws.send_str(payload)
            except Exception as e:
                logger.warning("Error broadcasting to user %s: %s", user_id, e)
                dead_sockets.append(user_id)

        for uid in dead_sockets:
            if uid in self.sockets:
                del self.sockets[uid]

    async def broadcast_state(self) -> None:
        dead_sockets: list[str] = []
        for user_id, ws in list(self.sockets.items()):
            if ws.closed:
                dead_sockets.append(user_id)
                continue
            try:
                state = self.get_full_state(for_user_id=user_id)
                await ws.send_json({
                    "type": "state_update",
                    "state": state
                })
            except Exception as e:
                logger.warning("Error broadcasting state to user %s: %s", user_id, e)
                dead_sockets.append(user_id)

        for uid in dead_sockets:
            if uid in self.sockets:
                del self.sockets[uid]


class SessionManager:
    """Central registry and lifecycle manager for all game sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, GameSession] = {}
        self._game_registry: Dict[str, type[BaseGame]] = {
            "tictactoe": TicTacToeGame,
            "connect4": Connect4Game,
            "rps": RPSGame
        }

    def register_game(self, game_type: str, game_cls: type[BaseGame]) -> None:
        self._game_registry[game_type] = game_cls

    def get_game_class(self, game_type: str) -> Optional[type[BaseGame]]:
        return self._game_registry.get(game_type)

    def get_supported_games(self) -> list[Dict[str, Any]]:
        return [
            {
                "type": "tictactoe",
                "name": "Tic-Tac-Toe",
                "description": "Klassisches 3x3 Duell. Wer zuerst drei Symbole in einer Reihe hat, gewinnt!",
                "icon": "❌⭕",
                "min_players": 1,
                "max_players": 2,
                "badge": "Klassiker"
            },
            {
                "type": "connect4",
                "name": "Vier Gewinnt",
                "description": "Taktisches 7x6 Raster. Wirf deine Chips ein und bilde eine 4er-Reihe!",
                "icon": "🔴🟡",
                "min_players": 1,
                "max_players": 2,
                "badge": "Taktik"
            },
            {
                "type": "rps",
                "name": "Schere Stein Papier",
                "description": "Schnelles Duell mit verdeckter Wahl im Best-of-5 Modus.",
                "icon": "✊✋✌️",
                "min_players": 1,
                "max_players": 2,
                "badge": "Action"
            },
            {
                "type": "tournament",
                "name": "Voice-Turnier",
                "description": "Episches Turnier für den Sprachkanal! Punkte-Mehrkampf oder K.O.-Modus mit Live-Zuschauern & Jubel.",
                "icon": "🏆",
                "min_players": 2,
                "max_players": 16,
                "badge": "Turnier / Party"
            }
        ]

    def create_session(self, game_type: str = "hub", host: Optional[Player] = None, session_id: Optional[str] = None) -> GameSession:
        sid = session_id or str(uuid.uuid4())[:8]
        if host is None:
            host = Player(
                user_id="guest_host",
                username="Host",
                display_name="Host",
                is_host=True
            )

        is_hub = (game_type == "hub")
        is_tournament = (game_type == "tournament")
        actual_game_type = "tictactoe" if (is_hub or is_tournament) else game_type

        cls = self.get_game_class(actual_game_type)
        if not cls:
            raise ValueError(f"Unknown game type: {actual_game_type}")

        game_instance = cls(session_id=sid, host=host)
        session = GameSession(session_id=sid, game=game_instance, is_hub=is_hub)
        if is_tournament:
            session.start_tournament_mode()
        self._sessions[sid] = session
        return session

    def get_session(self, session_id: str) -> Optional[GameSession]:
        return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

    async def cleanup_idle_sessions(self, max_idle_seconds: float = 3600) -> None:
        now = asyncio.get_event_loop().time()
        to_delete = [
            sid for sid, s in self._sessions.items()
            if not s.sockets and (now - s.last_activity > max_idle_seconds)
        ]
        for sid in to_delete:
            logger.info("Cleaning up idle game session %s", sid)
            self.remove_session(sid)


session_manager = SessionManager()
