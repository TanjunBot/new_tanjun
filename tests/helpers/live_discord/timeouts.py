from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiveE2ETimeouts:
    playwright_default_ms: int
    playwright_navigation_ms: int
    bootstrap_sec: float
    token_capture_ms: int
    app_gate_ms: int
    guild_create_ms: int
    oauth_ui_ms: int
    oauth_scroll_ms: int
    open_channel_ms: int

    @classmethod
    def from_env(
        cls,
        *,
        playwright_default_ms: int,
        playwright_navigation_ms: int,
        bootstrap_sec: float,
        token_capture_ms: int,
        app_gate_ms: int,
        guild_create_ms: int,
        oauth_ui_ms: int,
        oauth_scroll_ms: int,
        open_channel_ms: int,
    ) -> LiveE2ETimeouts:
        return cls(
            playwright_default_ms=playwright_default_ms,
            playwright_navigation_ms=playwright_navigation_ms,
            bootstrap_sec=bootstrap_sec,
            token_capture_ms=token_capture_ms,
            app_gate_ms=app_gate_ms,
            guild_create_ms=guild_create_ms,
            oauth_ui_ms=oauth_ui_ms,
            oauth_scroll_ms=oauth_scroll_ms,
            open_channel_ms=open_channel_ms,
        )
