from __future__ import annotations

import inspect
from typing import Any

from diagnostics.mocks import make_attachment, make_choice, make_member, make_text_channel

_PARAM_DEFAULTS: dict[str, Any] = {
    "user": lambda: make_member(),
    "member": lambda: make_member(),
    "target": lambda: make_member(),
    "opponent": lambda: make_member(),
    "player": lambda: make_member(),
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
    "scaling": lambda: make_choice("linear"),
    "level": 5,
    "cooldown": 60,
    "quality": lambda: make_choice("85"),
    "tag": "#ABC123",
    "messageid": 1,
    "trigger": "test",
    "response": "ok",
    "personality": "default",
    "giveawayid": 1,
}


def _make_role() -> Any:
    role = make_member()
    role.id = 555555555
    role.name = "TestRole"
    role.mention = "<@&555555555>"
    role.position = 5
    return role


def build_kwargs_for_handler(handler: Any) -> dict[str, Any]:
    try:
        sig = inspect.signature(getattr(handler, "callback", handler))
    except (TypeError, ValueError):
        return {}
    kwargs: dict[str, Any] = {}
    for name, param in sig.parameters.items():
        if name in ("self", "interaction", "ctx"):
            continue
        if param.default is not inspect.Parameter.empty and param.default is None:
            continue
        factory = _PARAM_DEFAULTS.get(name)
        if factory is not None:
            kwargs[name] = factory() if callable(factory) else factory
    return kwargs
