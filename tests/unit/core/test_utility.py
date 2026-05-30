"""Tests for utility.py helpers, CommandInfo, SafeInteraction, DiscordSafe."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.helpers.discord import make_guild, make_interaction, make_member, make_message, make_text_channel
from tests.helpers.discord_exceptions import Forbidden, HTTPException, NotFound
from utility import (
    CommandInfo,
    DiscordSafe,
    SafeInteraction,
    add_thousands_separator,
    addThousandsSeparator,
    check_if_str_is_hex_color,
    command_info,
    draw_text_with_outline,
    similar,
    tanjunEmbed,
)


class TestMiscHelpers:
    def test_check_if_str_is_hex_color_valid(self):
        assert check_if_str_is_hex_color("FF00FF") is True

    def test_check_if_str_is_hex_color_invalid(self):
        assert check_if_str_is_hex_color("nothex") is False

    def test_similar_identical(self):
        assert similar("hello", "hello") == 1.0

    def test_similar_different(self):
        ratio = similar("hello", "world")
        assert 0 <= ratio < 1

    def test_add_thousands_separator(self):
        assert add_thousands_separator(1000000) == "1 000 000"

    def test_add_thousands_separator_alias(self):
        assert addThousandsSeparator(1234) == "1 234"

    def test_add_thousands_separator_zero(self):
        assert add_thousands_separator(0) == "0"


class TestDrawTextWithOutline:
    def test_draws_outline_and_text(self):
        draw = MagicMock()
        font = MagicMock()
        draw_text_with_outline(draw, (10, 20), "Hi", font, "white", "black")
        assert draw.text.call_count == 5
        fills = [call.kwargs.get("fill") or call.args[4] for call in draw.text.call_args_list]
        assert fills.count("black") == 4
        assert fills.count("white") == 1


class TestUtilityReexports:
    def test_tanjun_embed_reexport(self):
        embed = tanjunEmbed(title="T")
        assert embed.title == "T"

    def test_command_info_type_alias(self):
        assert command_info is CommandInfo


class TestCommandInfo:
    def test_init_with_kwargs(self):
        member = make_member()
        info = CommandInfo(user=member, locale="en-US")
        assert info.user is member
        assert info.locale == "en-US"

    def test_missing_attrs_default_none(self):
        info = CommandInfo()
        assert info.user is None
        assert info.guild is None

    def test_all_kwargs_stored(self):
        client = MagicMock()
        guild = make_guild()
        channel = make_text_channel(guild=guild)
        command = MagicMock()
        message = make_message()
        perms = MagicMock()
        info = CommandInfo(
            user=make_member(),
            channel=channel,
            guild=guild,
            command=command,
            locale="de",
            message=message,
            permissions=perms,
            client=client,
        )
        assert info.channel is channel
        assert info.command is command
        assert info.message is message
        assert info.permissions is perms
        assert info.client is client


class TestSafeInteraction:
    @pytest.mark.asyncio
    async def test_respond_when_not_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        embed = MagicMock()
        await SafeInteraction.respond(interaction, embed=embed)
        interaction.response.send_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_respond_when_already_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = True
        await SafeInteraction.respond(interaction, content="followup")
        interaction.followup.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_defer_when_not_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        await SafeInteraction.defer(interaction)
        interaction.response.defer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_defer_skips_when_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = True
        await SafeInteraction.defer(interaction)
        interaction.response.defer.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_edit_when_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = True
        await SafeInteraction.edit(interaction, content="edited")
        interaction.edit_original_response.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_respond_with_view(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        view = MagicMock()
        await SafeInteraction.respond(interaction, content="hi", view=view, ephemeral=True)
        interaction.response.send_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_respond_interaction_responded_fallback(self):
        import discord

        class InteractionResponded(Exception):
            pass

        discord.InteractionResponded = InteractionResponded
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        interaction.response.send_message = AsyncMock(side_effect=InteractionResponded())
        await SafeInteraction.respond(interaction, content="retry")
        interaction.followup.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_defer_interaction_responded(self):
        import discord

        class InteractionResponded(Exception):
            pass

        discord.InteractionResponded = InteractionResponded
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        interaction.response.defer = AsyncMock(side_effect=InteractionResponded())
        await SafeInteraction.defer(interaction)

    @pytest.mark.asyncio
    async def test_edit_when_not_done(self):
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        embed = MagicMock()
        await SafeInteraction.edit(interaction, embed=embed, view=MagicMock())
        interaction.response.send_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_edit_interaction_responded_fallback(self):
        import discord

        class InteractionResponded(Exception):
            pass

        discord.InteractionResponded = InteractionResponded
        interaction = make_interaction()
        interaction.response.is_done.return_value = False
        interaction.response.send_message = AsyncMock(side_effect=InteractionResponded())
        await SafeInteraction.edit(interaction, content="edited")
        interaction.edit_original_response.assert_awaited_once()


class TestDiscordSafe:
    @pytest.mark.asyncio
    async def test_send_success(self):
        channel = make_text_channel()
        msg = MagicMock()
        channel.send = AsyncMock(return_value=msg)
        result = await DiscordSafe.send(channel, content="hello")
        assert result is msg

    @pytest.mark.asyncio
    async def test_send_forbidden_returns_none(self):
        channel = make_text_channel()
        channel.send = AsyncMock(side_effect=Forbidden("forbidden"))
        result = await DiscordSafe.send(channel, content="hello")
        assert result is None

    @pytest.mark.asyncio
    async def test_send_http_exception_returns_none(self):
        channel = make_text_channel()
        exc = HTTPException("http")
        exc.status = 500
        channel.send = AsyncMock(side_effect=exc)
        result = await DiscordSafe.send(channel, embed=MagicMock())
        assert result is None

    @pytest.mark.asyncio
    async def test_send_dm_success(self):
        user = make_member()
        user.send = AsyncMock()
        assert await DiscordSafe.send_dm(user, "hi") is True

    @pytest.mark.asyncio
    async def test_send_dm_forbidden(self):
        user = make_member()
        user.send = AsyncMock(side_effect=Forbidden("no dm"))
        assert await DiscordSafe.send_dm(user, "hi") is False

    @pytest.mark.asyncio
    async def test_send_dm_http_exception(self):
        user = make_member()
        exc = HTTPException("http")
        exc.status = 429
        user.send = AsyncMock(side_effect=exc)
        assert await DiscordSafe.send_dm(user, "hi") is False

    @pytest.mark.asyncio
    async def test_delete_success(self):
        message = make_message()
        message.delete = AsyncMock()
        assert await DiscordSafe.delete(message) is True

    @pytest.mark.asyncio
    async def test_delete_not_found_returns_true(self):
        message = make_message()
        message.delete = AsyncMock(side_effect=NotFound("gone"))
        assert await DiscordSafe.delete(message) is True

    @pytest.mark.asyncio
    async def test_delete_forbidden(self):
        message = make_message()
        message.delete = AsyncMock(side_effect=Forbidden("no delete"))
        assert await DiscordSafe.delete(message) is False

    @pytest.mark.asyncio
    async def test_delete_http_exception(self):
        message = make_message()
        exc = HTTPException("http")
        exc.status = 500
        message.delete = AsyncMock(side_effect=exc)
        assert await DiscordSafe.delete(message) is False

    @pytest.mark.asyncio
    async def test_reply_success(self):
        message = make_message()
        reply = MagicMock()
        message.reply = AsyncMock(return_value=reply)
        result = await DiscordSafe.reply(message, content="reply")
        assert result is reply

    @pytest.mark.asyncio
    async def test_reply_forbidden(self):
        message = make_message()
        message.reply = AsyncMock(side_effect=Forbidden("no reply"))
        assert await DiscordSafe.reply(message, embed=MagicMock()) is None

    @pytest.mark.asyncio
    async def test_reply_http_exception(self):
        message = make_message()
        exc = HTTPException("http")
        exc.status = 403
        message.reply = AsyncMock(side_effect=exc)
        assert await DiscordSafe.reply(message, content="x") is None

    @pytest.mark.asyncio
    async def test_add_reaction_success(self):
        message = make_message()
        message.add_reaction = AsyncMock()
        assert await DiscordSafe.add_reaction(message, "👍") is True

    @pytest.mark.asyncio
    async def test_add_reaction_forbidden(self):
        message = make_message()
        message.add_reaction = AsyncMock(side_effect=Forbidden("no react"))
        assert await DiscordSafe.add_reaction(message, "👍") is False

    @pytest.mark.asyncio
    async def test_add_reaction_not_found(self):
        message = make_message()
        message.add_reaction = AsyncMock(side_effect=NotFound("gone"))
        assert await DiscordSafe.add_reaction(message, "👍") is False

    @pytest.mark.asyncio
    async def test_add_reaction_http_exception(self):
        message = make_message()
        exc = HTTPException("http")
        exc.status = 400
        exc.text = "bad"
        message.add_reaction = AsyncMock(side_effect=exc)
        assert await DiscordSafe.add_reaction(message, "👍") is False
