"""Tests for utils/embeds.py embed builders and TanjunEmbed."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from utils.embeds import (
    EMOJI_MAP,
    EmbedColor,
    StatusIcon,
    TanjunEmbed,
    get_icon_emoji,
)


@pytest.fixture(autouse=True)
def _restore_discord_utils():
    from tests.helpers.discord import _ensure_discord_types, _mock_discord_get

    _ensure_discord_types()
    import discord

    discord.utils.get = _mock_discord_get
    yield


class TestEmbedColor:
    def test_brand_color(self):
        assert EmbedColor.BRAND == 0xCB33F5

    def test_success_color(self):
        assert EmbedColor.SUCCESS == 0x4BB543

    def test_error_color(self):
        assert EmbedColor.ERROR == 0xE74C3C


class TestStatusIcon:
    def test_success_icon(self):
        assert StatusIcon.SUCCESS == "✅"

    def test_error_icon(self):
        assert StatusIcon.ERROR == "❌"


class TestEmojiMap:
    def test_checkmark_mapping(self):
        assert EMOJI_MAP["checkmark"] == "check"


class TestTanjunEmbed:
    def test_default_colour(self):
        embed = TanjunEmbed()
        assert embed.colour == EmbedColor.BRAND

    def test_set_title_and_description(self):
        embed = TanjunEmbed(title="Title", description="Desc")
        assert embed.title == "Title"
        assert embed.description == "Desc"

    def test_set_colour_via_int(self):
        embed = TanjunEmbed(colour=int(EmbedColor.SUCCESS))
        assert embed.colour == EmbedColor.SUCCESS

    def test_add_field(self):
        embed = TanjunEmbed()
        embed.add_field(name="Field", value="Value", inline=False)
        assert len(embed.fields) == 1
        assert embed.fields[0].name == "Field"

    def test_set_footer(self):
        embed = TanjunEmbed()
        embed.set_footer(text="Footer text")
        assert embed.footer is not None
        assert embed.footer.text == "Footer text"

    def test_to_dict(self):
        embed = TanjunEmbed(title="T", description="D", colour=int(EmbedColor.ERROR))
        d = embed.to_dict()
        assert d["title"] == "T"
        assert d["description"] == "D"
        assert d["color"] == EmbedColor.ERROR

    def test_from_dict_roundtrip(self):
        original = TanjunEmbed(title="Test", description="Body")
        original.add_field(name="F", value="V")
        restored = TanjunEmbed.from_dict(original.to_dict())
        assert restored.title == "Test"
        assert len(restored.fields) == 1

    def test_len(self):
        embed = TanjunEmbed(title="Hi", description="There")
        assert len(embed) == 7

    def test_bool_empty(self):
        embed = TanjunEmbed()
        assert bool(embed) is False

    def test_bool_with_content(self):
        embed = TanjunEmbed(title="X")
        assert bool(embed) is True

    def test_copy(self):
        embed = TanjunEmbed(title="Original")
        copy = embed.copy()
        copy.title = "Modified"
        assert embed.title == "Original"


class TestEmbedBuilders:
    def test_success_colour_via_int(self):
        embed = TanjunEmbed(title="Done", description="OK", colour=int(EmbedColor.SUCCESS))
        assert embed.colour == EmbedColor.SUCCESS

    def test_error_colour_via_int(self):
        embed = TanjunEmbed(title="Fail", description="Err", colour=int(EmbedColor.ERROR))
        assert embed.colour == EmbedColor.ERROR


class TestGetIconEmoji:
    @pytest.mark.asyncio
    async def test_returns_fallback_when_not_found(self):
        bot = MagicMock()
        bot.emojis = []
        with patch("utils.embeds.discord.utils.get", return_value=None):
            result = await get_icon_emoji(bot, "nonexistent", fallback="🔧")
        assert result == "🔧"

    @pytest.mark.asyncio
    async def test_returns_info_icon_by_default(self):
        bot = MagicMock()
        bot.emojis = []
        with patch("utils.embeds.discord.utils.get", return_value=None):
            result = await get_icon_emoji(bot, "nonexistent")
        assert result == StatusIcon.INFO.value
