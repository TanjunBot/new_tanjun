from __future__ import annotations

import inspect
import typing
from typing import Any, get_args, get_origin

from unittest.mock import AsyncMock, MagicMock

from diagnostics.mocks import make_attachment, make_choice, make_member, make_text_channel

_PARAM_DEFAULTS: dict[str, Any] = {
    "user": lambda: make_member(),
    "member": lambda: make_member(),
    "target": lambda: make_member(),
    "opponent": lambda: make_member(),
    "player": lambda: make_member(),
    "player1": lambda: make_member(),
    "player2": lambda: make_member(),
    "channel": lambda: make_text_channel(),
    "category": lambda: make_text_channel(),
    "role": lambda: _make_role(),
    "language": lambda: make_choice("en"),
    "theme": lambda: make_choice("characters"),
    "size": lambda: make_choice("7,6"),
    "locale": lambda: make_choice("en"),
    "image": lambda: make_attachment(),
    "attachment": lambda: make_attachment(),
    "reason": "test reason",
    "progress": 5,
    "number": 5,
    "name": "Test",
    "content": "hello",
    "message_id": 1,
    "equation": "2+2",
    "expression": "2+2",
    "giveaway_id": 1,
    "title": "Prize",
    "min": 1,
    "max": 10,
    "amount": 1,
    "messages": 5,
    "per": 60,
    "resetafter": 30,
    "situation": "test",
    "prompt": "hi",
    "twitchname": "streamer",
    "notificationmessage": "live",
    "sendin": "1h",
    "axis": "x",
    "type": "gaussian",
    "radius": 3,
    "width": 100,
    "height": 100,
    "scale": 50,
    "factor": 1.0,
    "func": "x",
    "imageurl": "https://example.com/x.png",
    "emoji": "😀",
    "twitch_username": "streamer",
    "username": "user#1234",
    "duration": 60,
    "seconds": 10,
    "description": "ticket",
    "message": "hello",
    "limit": 100,
    "mode": 1,
    "target_role": lambda: _make_role(),
    "position": lambda: make_choice("1"),
    "copymembers": lambda: make_choice("true"),
    "boost": 2.0,
    "additive": False,
    "scaling": lambda: make_choice("medium"),
    "level": 5,
    "cooldown": 60,
    "quality": lambda: make_choice("85"),
    "tag": "#ABC123",
    "messageid": 1,
    "trigger": "test",
    "response": "ok",
    "personality": "default",
    "giveawayid": 1,
    "temperature": 1.0,
    "topp": 1.0,
    "frequencypenalty": 0.0,
    "presencepenalty": 0.0,
    "setting": lambda: make_choice("all"),
    "imageurl": "https://example.com/x.png",
}


def _make_role() -> Any:
    role = MagicMock()
    role.id = 555555555555555555
    role.name = "TestRole"
    role.mention = "<@&555555555555555555>"
    role.position = 5
    role.color = MagicMock()
    role.hoist = False
    role.mentionable = False
    role.permissions = MagicMock()
    role.icon = None
    role.unicode_emoji = None
    role.members = []
    role.delete = AsyncMock()
    role.edit = AsyncMock()
    return role


def _default_from_annotation(annotation: Any) -> Any:
    if annotation is inspect.Parameter.empty:
        return "test"
    origin = get_origin(annotation)
    if origin is typing.Union or str(origin) == "typing.Union":
        args = [a for a in get_args(annotation) if a is not type(None)]
        if args:
            return _default_from_annotation(args[0])
        return None
    if annotation in (int, "int"):
        return 1
    if annotation in (float, "float"):
        return 1.0
    if annotation in (bool, "bool"):
        return False
    if annotation in (str, "str"):
        return "test"
    return "test"


def build_kwargs_for_handler(handler: Any) -> dict[str, Any]:
    try:
        sig = inspect.signature(getattr(handler, "callback", handler))
    except (TypeError, ValueError):
        return {}
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name in ("self", "interaction", "ctx", "command_info", "info"):
            continue
        if name == "language" and param.annotation in (str, "str"):
            if param.default is not inspect.Parameter.empty:
                continue
        if name in _PARAM_DEFAULTS:
            factory = _PARAM_DEFAULTS[name]
            kwargs[name] = factory() if callable(factory) else factory
            continue
        if param.default is not inspect.Parameter.empty:
            continue
        kwargs[name] = _default_from_annotation(param.annotation)
    return kwargs
