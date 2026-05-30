"""Brawl Stars helper utilities — emoji lookups and name formatting.

Emoji maps are loaded from JSON files in the data/ directory so that
they can be updated without changing Python source code.
"""

import json
import os
from typing import Final

_DATA_DIR: Final[str] = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


def _load_emoji_map(filename: str) -> dict[str, str]:
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)  # type: ignore[no-any-return]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


star_powerEmojiMap: dict[str, str] = _load_emoji_map("star_powerEmojiMap.json")
gadgetEmojiMap: dict[str, str] = _load_emoji_map("gadgetEmojiMap.json")
gearEmojiMap: dict[str, str] = _load_emoji_map("gearEmojiMap.json")
level_emojiMap: dict[str, str] = _load_emoji_map("level_emojiMap.json")


def getStarPowerEmoji(id: int) -> str:
    try:
        return star_powerEmojiMap[str(id)]
    except KeyError:
        return ""


def getGadgetEmoji(gadget: int) -> str:
    try:
        return gadgetEmojiMap[str(gadget)]
    except KeyError:
        return ""


def getGearEmoji(gear: int) -> str:
    try:
        return gearEmojiMap[str(gear)]
    except KeyError:
        return ""


def getLevelEmoji(level: int) -> str:
    if level > 50:
        return level_emojiMap.get("51", "")
    try:
        return level_emojiMap[str(level)]
    except (KeyError, ValueError):
        return ""


def parseName(name: str) -> str:
    name = name.replace("-", " ")
    name = name.title()
    name = name.replace("'S", "'s")
    return name
