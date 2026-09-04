from __future__ import annotations

import abc
import asyncio
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Player(BaseModel):
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    is_bot: bool = False
    is_host: bool = False
    connected: bool = True


class BaseGame(abc.ABC):
    """Abstract base class for Activity games in the Tanjun framework."""

    def __init__(self, session_id: str, host: Player, max_players: int = 2) -> None:
        self.session_id: str = session_id
        self.host: Player = host
        self.max_players: int = max_players
        self.players: Dict[str, Player] = {host.user_id: host}
        self.spectators: Dict[str, Player] = {}
        self.is_started: bool = False
        self.is_finished: bool = False
        self.winner: Optional[str] = None
        self.game_mode: str = "pvp"  # pvp or bot

    @property
    @abc.abstractmethod
    def game_type(self) -> str:
        """Unique key of the game (e.g. 'tictactoe')."""
        pass

    @property
    @abc.abstractmethod
    def display_name(self) -> str:
        """Human-readable name of the game."""
        pass

    @abc.abstractmethod
    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        """Serialize game state for client transmission."""
        pass

    @abc.abstractmethod
    async def handle_action(self, player_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming player action. Return a dict with results/events."""
        pass

    @abc.abstractmethod
    async def reset(self) -> None:
        """Reset the game board/state for a new round."""
        pass

    def add_player(self, player: Player) -> bool:
        if len(self.players) >= self.max_players or self.is_started:
            self.spectators[player.user_id] = player
            return False
        self.players[player.user_id] = player
        return True

    def remove_player(self, user_id: str) -> None:
        if user_id in self.players:
            self.players[user_id].connected = False
        if user_id in self.spectators:
            del self.spectators[user_id]
