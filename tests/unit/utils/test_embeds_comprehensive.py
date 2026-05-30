"""Extended tests for utils/embeds.py."""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import discord
import pytest

from utils.embeds import (
    EMOJI_MAP,
    EmbedAuthor,
    EmbedColor,
    EmbedField,
    EmbedFooter,
    EmbedMedia,
    EmbedProvider,
    EmbedVideo,
    ErrorEmbedCategory,
    StatusIcon,
    TanjunEmbed,
    categorized_error_embed,
    categorized_info_embed,
    categorized_success_embed,
    categorized_warning_embed,
    embed_or_wrap,
    error_embed,
    get_icon_emoji,
    info_embed,
    success_embed,
    tanjunEmbed,
    warning_embed,
)


@pytest.fixture(autouse=True)
def _restore_discord_utils():
    from tests.helpers.discord import _ensure_discord_types, _mock_discord_get

    _ensure_discord_types()
    discord.utils.get = _mock_discord_get
    yield


class TestEmbedColorValues:
    @pytest.mark.parametrize(
        ("member", "value"),
        [
            ("BRAND", 0xCB33F5),
            ("SUCCESS", 0x4BB543),
            ("WARNING", 0xFFBF00),
            ("ERROR", 0xE74C3C),
            ("INFO", 0x3498DB),
            ("TIMEOUT", 0x95A5A6),
        ],
    )
    def test_color_values(self, member: str, value: int):
        assert int(getattr(EmbedColor, member)) == value


class TestStatusIconValues:
    @pytest.mark.parametrize(
        "member",
        ["SUCCESS", "ERROR", "WARNING", "INFO", "LOCK", "PENDING", "DENIED", "ENABLED", "DISABLED"],
    )
    def test_icon_is_string(self, member: str):
        icon = getattr(StatusIcon, member)
        assert isinstance(icon, str)
        assert len(icon) > 0


class TestErrorEmbedCategory:
    @pytest.mark.parametrize(
        "member",
        ["PERMISSION", "NOT_FOUND", "RATE_LIMIT", "VALIDATION", "UNEXPECTED", "TIMEOUT"],
    )
    def test_category_has_color(self, member: str):
        assert isinstance(int(getattr(ErrorEmbedCategory, member)), int)


class TestEmbedSubModels:
    def test_embed_field(self):
        field = EmbedField(name="N", value="V", inline=False)
        assert field.inline is False

    def test_embed_footer_optional_icon(self):
        footer = EmbedFooter(text="text", icon_url="https://x.com/i.png")
        assert footer.icon_url == "https://x.com/i.png"

    def test_embed_media(self):
        media = EmbedMedia(url="https://img.png", width=100, height=50)
        assert media.width == 100

    def test_embed_video(self):
        video = EmbedVideo(url="https://v.mp4")
        assert video.url == "https://v.mp4"

    def test_embed_provider(self):
        provider = EmbedProvider(name="Twitch", url="https://twitch.tv")
        assert provider.name == "Twitch"

    def test_embed_author(self):
        author = EmbedAuthor(name="Bot", url="https://bot.dev", icon_url="https://i.png")
        assert author.name == "Bot"


class TestTanjunEmbedColour:
    def test_default_brand_colour(self):
        embed = TanjunEmbed()
        assert embed.colour == EmbedColor.BRAND

    def test_colour_via_color_kwarg(self):
        embed = TanjunEmbed(color=int(EmbedColor.ERROR))
        assert embed.colour == EmbedColor.ERROR

    def test_colour_none_uses_brand(self):
        embed = TanjunEmbed()
        embed.colour = None
        assert embed.colour == EmbedColor.BRAND

    def test_colour_discord_colour(self):
        embed = TanjunEmbed()
        embed.colour = discord.Colour(0xFF0000)
        assert embed.colour == 0xFF0000

    def test_colour_embed_color_enum(self):
        embed = TanjunEmbed()
        embed.colour = EmbedColor.SUCCESS
        assert embed.colour == EmbedColor.SUCCESS

    def test_color_property_alias(self):
        embed = TanjunEmbed()
        embed.color = int(EmbedColor.WARNING)
        assert embed.color == EmbedColor.WARNING

    def test_invalid_colour_type(self):
        embed = TanjunEmbed()
        with pytest.raises(TypeError):
            embed.colour = "red"


class TestTanjunEmbedBuilders:
    def test_set_footer_with_icon(self):
        embed = TanjunEmbed().set_footer(text="Footer", icon_url="https://i.png")
        assert embed.footer is not None
        assert embed.footer.icon_url == "https://i.png"

    def test_set_footer_none_clears(self):
        embed = TanjunEmbed().set_footer(text="x").set_footer()
        assert embed.footer is None

    def test_remove_footer(self):
        embed = TanjunEmbed().set_footer(text="x").remove_footer()
        assert embed.footer is None

    def test_set_image(self):
        embed = TanjunEmbed().set_image(url="https://img.png")
        assert embed.image is not None
        assert embed.image.url == "https://img.png"

    def test_set_image_none_clears(self):
        embed = TanjunEmbed().set_image(url="https://img.png").set_image(url=None)
        assert embed.image is None

    def test_set_thumbnail(self):
        embed = TanjunEmbed().set_thumbnail(url="https://thumb.png")
        assert embed.thumbnail.url == "https://thumb.png"

    def test_set_author(self):
        embed = TanjunEmbed().set_author(name="Author", url="https://a.com", icon_url="https://i.png")
        assert embed.author.name == "Author"
        assert embed.author.url == "https://a.com"

    def test_remove_author(self):
        embed = TanjunEmbed().set_author(name="A").remove_author()
        assert embed.author is None

    def test_insert_field_at(self):
        embed = TanjunEmbed().add_field(name="B", value="2").insert_field_at(0, name="A", value="1")
        assert embed.fields[0].name == "A"

    def test_clear_fields(self):
        embed = TanjunEmbed().add_field(name="A", value="1").clear_fields()
        assert embed.fields == []

    def test_remove_field_valid(self):
        embed = TanjunEmbed().add_field(name="A", value="1").add_field(name="B", value="2")
        embed.remove_field(0)
        assert len(embed.fields) == 1
        assert embed.fields[0].name == "B"

    def test_remove_field_out_of_range(self):
        embed = TanjunEmbed().add_field(name="A", value="1")
        embed.remove_field(5)
        assert len(embed.fields) == 1

    def test_set_field_at(self):
        embed = TanjunEmbed().add_field(name="A", value="1")
        embed.set_field_at(0, name="B", value="2", inline=False)
        assert embed.fields[0].name == "B"
        assert embed.fields[0].inline is False

    def test_set_field_at_out_of_range(self):
        embed = TanjunEmbed()
        with pytest.raises(IndexError):
            embed.set_field_at(0, name="X", value="Y")


class TestTanjunEmbedSerialization:
    def test_from_dict_full(self):
        data = {
            "title": "T",
            "description": "D",
            "url": "https://x.com",
            "color": int(EmbedColor.INFO),
            "timestamp": "2024-06-15T12:00:00+00:00",
            "footer": {"text": "foot"},
            "image": {"url": "https://img.png"},
            "thumbnail": {"url": "https://thumb.png"},
            "video": {"url": "https://vid.mp4"},
            "provider": {"name": "P"},
            "author": {"name": "A"},
            "fields": [{"name": "F", "value": "V", "inline": True}],
        }
        embed = TanjunEmbed.from_dict(data)
        assert embed.title == "T"
        assert embed.footer is not None
        assert len(embed.fields) == 1

    def test_to_dict_with_aware_timestamp(self):
        ts = datetime.datetime(2024, 6, 15, 12, 0, tzinfo=datetime.UTC)
        embed = TanjunEmbed(title="T", timestamp=ts)
        d = embed.to_dict()
        assert "timestamp" in d
        assert d["timestamp"].endswith("+00:00")

    def test_to_dict_with_naive_timestamp(self):
        ts = datetime.datetime(2024, 6, 15, 12, 0)
        embed = TanjunEmbed(title="T", timestamp=ts)
        d = embed.to_dict()
        assert "timestamp" in d

    def test_to_dict_includes_optional_sections(self):
        embed = (
            TanjunEmbed(title="T", description="D", url="https://x.com")
            .set_footer(text="f")
            .set_image(url="https://img.png")
            .set_thumbnail(url="https://thumb.png")
            .add_field(name="N", value="V")
        )
        embed.video = EmbedVideo(url="https://v.mp4")
        embed.provider = EmbedProvider(name="P")
        embed.author = EmbedAuthor(name="A")
        d = embed.to_dict()
        assert "footer" in d
        assert "image" in d
        assert "thumbnail" in d
        assert "video" in d
        assert "provider" in d
        assert "author" in d
        assert "fields" in d

    def test_to_discord_embed(self):
        embed = (
            TanjunEmbed(title="T", description="D", colour=int(EmbedColor.SUCCESS))
            .set_footer(text="f", icon_url="https://i.png")
            .set_image(url="https://img.png")
            .set_thumbnail(url="https://thumb.png")
            .set_author(name="A", url="https://a.com", icon_url="https://i.png")
            .add_field(name="N", value="V")
        )
        discord_embed = embed.to_discord_embed()
        assert discord_embed.title == "T"


class TestTanjunEmbedMagicMethods:
    def test_len_includes_footer_and_author(self):
        embed = TanjunEmbed(title="Hi", description="There")
        embed.set_footer(text="foot")
        embed.set_author(name="auth")
        assert len(embed) == len("Hi") + len("There") + len("foot") + len("auth")

    def test_bool_colour_change(self):
        embed = TanjunEmbed()
        embed.colour = int(EmbedColor.ERROR)
        assert bool(embed) is True

    def test_bool_with_url(self):
        embed = TanjunEmbed(url="https://x.com")
        assert bool(embed) is True

    def test_bool_with_timestamp(self):
        embed = TanjunEmbed(timestamp=datetime.datetime.now(tz=datetime.UTC))
        assert bool(embed) is True

    def test_tanjun_embed_alias(self):
        assert tanjunEmbed is TanjunEmbed


class TestSimpleEmbedBuilders:
    def test_error_embed_default_title(self):
        embed = error_embed("something failed")
        assert embed.title == "Error"
        assert embed.colour == EmbedColor.ERROR

    def test_error_embed_custom_title(self):
        embed = error_embed("msg", title="Oops")
        assert embed.title == "Oops"

    def test_success_embed_default_title(self):
        embed = success_embed("done")
        assert embed.title == "Success"

    def test_warning_embed_default_title(self):
        embed = warning_embed("careful")
        assert embed.title == "Warning"

    def test_info_embed_default_title(self):
        embed = info_embed("note")
        assert embed.title == "Info"

    def test_embed_or_wrap_default_colour(self):
        embed = embed_or_wrap("plain text")
        assert embed.colour == EmbedColor.BRAND
        assert embed.description == "plain text"

    def test_embed_or_wrap_custom_colour(self):
        embed = embed_or_wrap("text", title="T", colour=int(EmbedColor.INFO))
        assert embed.title == "T"


class TestCategorizedEmbedBuilders:
    @pytest.mark.parametrize(
        ("builder", "category", "expected_colour"),
        [
            (categorized_error_embed, ErrorEmbedCategory.PERMISSION, ErrorEmbedCategory.PERMISSION),
            (categorized_success_embed, None, EmbedColor.SUCCESS),
            (categorized_warning_embed, None, EmbedColor.WARNING),
            (categorized_info_embed, None, EmbedColor.INFO),
        ],
    )
    def test_categorized_builders(self, builder, category, expected_colour):
        if category is not None:
            embed = builder(category, "Title", "Desc")
            assert embed.colour == category.value
        else:
            embed = builder("Title", "Desc")
            assert embed.colour == expected_colour


class TestGetIconEmojiExtended:
    @pytest.mark.asyncio
    async def test_returns_guild_emoji(self):
        bot = MagicMock()
        emoji = MagicMock()
        emoji.__str__ = lambda self: "<:check:1>"
        with patch("utils.embeds.discord.utils.get", return_value=emoji):
            result = await get_icon_emoji(bot, "checkmark")
        assert result == "<:check:1>"

    @pytest.mark.asyncio
    async def test_uses_emoji_map(self):
        bot = MagicMock()
        with patch("utils.embeds.discord.utils.get") as mock_get:
            mock_get.return_value = None
            await get_icon_emoji(bot, "checkmark", fallback="x")
        mock_get.assert_called_once()
        assert mock_get.call_args.kwargs["name"] == EMOJI_MAP["checkmark"]

    @pytest.mark.asyncio
    async def test_direct_emoji_name(self):
        bot = MagicMock()
        with patch("utils.embeds.discord.utils.get") as mock_get:
            mock_get.return_value = None
            await get_icon_emoji(bot, "customname", fallback="fb")
        assert mock_get.call_args.kwargs["name"] == "customname"
