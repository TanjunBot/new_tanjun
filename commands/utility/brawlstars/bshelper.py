"""Brawl Stars helper utilities — emoji lookups and name formatting.

Emoji maps are loaded from JSON files in the data/ directory so that
they can be updated without changing Python source code.
"""

import json
import os
from typing import Final, cast

_DATA_DIR: Final[str] = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


def _load_emoji_map(filename: str) -> dict[str, str]:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if not (isinstance(data, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in data.items())):
                raise TypeError(f"Expected dict[str, str] in {filename}, got invalid structure")
            return cast(dict[str, str], data)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


STAR_POWER_EMOJI_MAP: dict[str, str] = _load_emoji_map("star_powerEmojiMap.json")
GADGET_EMOJI_MAP: dict[str, str] = _load_emoji_map("gadgetEmojiMap.json")
GEAR_EMOJI_MAP: dict[str, str] = _load_emoji_map("gearEmojiMap.json")
LEVEL_EMOJI_MAP: dict[str, str] = _load_emoji_map("level_emojiMap.json")


def getStarPowerEmoji(star_power_id: int) -> str:
    try:
        return STAR_POWER_EMOJI_MAP[str(star_power_id)]
    except KeyError:
        return ""


def getGadgetEmoji(gadget: int) -> str:
    try:
        return GADGET_EMOJI_MAP[str(gadget)]
    except KeyError:
        return ""


def getGearEmoji(gear: int) -> str:
    try:
        return GEAR_EMOJI_MAP[str(gear)]
    except KeyError:
        return ""


def getLevelEmoji(level: int) -> str:
    if level > 50:
        return LEVEL_EMOJI_MAP.get("51", "")
    try:
        return LEVEL_EMOJI_MAP[str(level)]
    except (KeyError, ValueError):
        return ""


def parseName(name: str) -> str:
    name = name.replace("-", " ")
    name = name.title()
    name = name.replace("'S", "'s")
    return name
