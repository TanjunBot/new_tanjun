from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

if TYPE_CHECKING:
    from aiohttp import web
from activities.base import BaseGame, Player
from activities.games.tictactoe import TicTacToeGame

logger = logging.getLogger(__name__)


class GameSession:
    """Manages an active game instance and its connected WebSockets."""

    def __init__(self, session_id: str, game: BaseGame) -> None:
        self.session_id: str = session_id
        self.game: BaseGame = game
        self.sockets: Dict[str, web.WebSocketResponse] = {}  # user_id -> ws
        self.created_at: float = asyncio.get_event_loop().time()
        self.last_activity: float = self.created_at

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
        state = self.game.get_state()
        await self.broadcast({
            "type": "state_update",
            "state": state
        })


class SessionManager:
    """Central registry and lifecycle manager for all game sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, GameSession] = {}
        self._game_registry: Dict[str, type[BaseGame]] = {
            "tictactoe": TicTacToeGame
        }

    def register_game(self, game_type: str, game_cls: type[BaseGame]) -> None:
        self._game_registry[game_type] = game_cls

    def get_supported_games(self) -> list[Dict[str, str]]:
        return [
            {"type": "tictactoe", "name": "Tic Tac Toe", "min_players": 1, "max_players": 2, "icon": "grid"}
        ]

    def create_session(self, game_type: str, host: Player, session_id: Optional[str] = None) -> GameSession:
        sid = session_id or str(uuid.uuid4())[:8]
        cls = self._game_registry.get(game_type)
        if not cls:
            raise ValueError(f"Unknown game type: {game_type}")

        game_instance = cls(session_id=sid, host=host)
        session = GameSession(session_id=sid, game=game_instance)
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
