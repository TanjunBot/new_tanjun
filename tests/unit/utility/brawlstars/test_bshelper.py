from __future__ import annotations

from unittest.mock import mock_open, patch

from commands.utility.brawlstars import bshelper


def test_parse_name():
    assert bshelper.parseName("mario-bros") == "Mario Bros"


def test_get_star_power_emoji_hit():
    with patch.dict(bshelper.star_powerEmojiMap, {"1": "⭐"}, clear=False):
        assert bshelper.getStarPowerEmoji(1) == "⭐"


def test_get_star_power_emoji_miss():
    assert bshelper.getStarPowerEmoji(99999) == ""


def test_get_gadget_emoji_hit():
    with patch.dict(bshelper.gadgetEmojiMap, {"2": "🔧"}, clear=False):
        assert bshelper.getGadgetEmoji(2) == "🔧"


def test_get_gadget_emoji_miss():
    assert bshelper.getGadgetEmoji(99999) == ""


def test_get_gear_emoji_hit():
    with patch.dict(bshelper.gearEmojiMap, {"3": "⚙️"}, clear=False):
        assert bshelper.getGearEmoji(3) == "⚙️"


def test_get_gear_emoji_miss():
    assert bshelper.getGearEmoji(99999) == ""


def test_get_level_emoji_high_level():
    with patch.dict(bshelper.level_emojiMap, {"51": "🏆"}, clear=False):
        assert bshelper.getLevelEmoji(99) == "🏆"


def test_get_level_emoji_normal():
    with patch.dict(bshelper.level_emojiMap, {"5": "5️⃣"}, clear=False):
        assert bshelper.getLevelEmoji(5) == "5️⃣"


def test_get_level_emoji_miss():
    assert bshelper.getLevelEmoji(0) == ""


def test_load_emoji_map_missing_file():
    with patch("commands.utility.brawlstars.bshelper.open", side_effect=FileNotFoundError):
        assert bshelper._load_emoji_map("missing.json") == {}


def test_load_emoji_map_invalid_json():
    with patch("commands.utility.brawlstars.bshelper.open", mock_open(read_data="not json")):
        assert bshelper._load_emoji_map("bad.json") == {}
