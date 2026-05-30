from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.brawlstars.brawlers import brawlers
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


def _brawler(**kwargs):
    b = MagicMock()
    b.id = kwargs.get("id", 1)
    b.name = kwargs.get("name", "Shelly")
    b.power = 11
    b.rank = kwargs.get("rank", 25)
    b.trophies = 500
    b.highest_trophies = 600
    b.gears = kwargs.get("gears", [])
    b.gadgets = kwargs.get("gadgets", [])
    b.star_powers = kwargs.get("star_powers", [])
    b.model_dump = MagicMock(return_value={"id": b.id})
    return b


def _player(brawlers_list=None):
    p = MagicMock()
    p.name = "Player"
    p.brawlers = brawlers_list or [
        _brawler(
            star_powers=[MagicMock(id=1, name="power-one")],
            gadgets=[MagicMock(id=2, name="gadget-one")],
            gears=[MagicMock(id=3, name="gear-one")],
        ),
        _brawler(name="Colt", id=2),
    ]
    return p


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_linked_account", new_callable=AsyncMock, return_value=None)
async def test_brawlers_not_linked(mock_link, admin_command_info):
    await brawlers(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_linked_account", new_callable=AsyncMock, side_effect=["<@123>", None])
async def test_brawlers_mention_not_linked(mock_link, admin_command_info):
    await brawlers(admin_command_info, "<@123>")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_player_not_found(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_player = AsyncMock(return_value=None)
    mock_get_service.return_value = service
    await brawlers(admin_command_info, "TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_single_brawler(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_player = AsyncMock(return_value=_player([_brawler(rank=55)]))
    mock_get_service.return_value = service
    await brawlers(admin_command_info, "TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_pagination_and_search(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_player = AsyncMock(return_value=_player())
    mock_get_service.return_value = service
    await brawlers(admin_command_info, "#TAG")
    view = admin_command_info.reply.await_args.kwargs["view"]

    next_i = make_view_interaction(admin_command_info.user)
    next_i.response.edit_message = AsyncMock()
    await view.next(next_i, MagicMock())
    next_i.response.edit_message.assert_awaited_once()

    prev_i = make_view_interaction(admin_command_info.user)
    prev_i.response.edit_message = AsyncMock()
    await view.previous(prev_i, MagicMock())

    search_i = make_view_interaction(admin_command_info.user)
    search_i.response.send_modal = AsyncMock()
    await view.search(search_i, MagicMock())
    search_i.response.send_modal.assert_awaited_once()

    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.send_message = AsyncMock()
    await view.next(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.brawlstars.brawlers.get_brawlstars_service")
async def test_brawlers_search_modal_submit(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_player = AsyncMock(return_value=_player())
    mock_get_service.return_value = service
    await brawlers(admin_command_info, "#TAG")
    view = admin_command_info.reply.await_args.kwargs["view"]
    search_i = make_view_interaction(admin_command_info.user)
    search_i.response.send_modal = AsyncMock()
    await view.search(search_i, MagicMock())
    modal = search_i.response.send_modal.await_args.args[0]
    submit = make_view_interaction(admin_command_info.user)
    submit.response.edit_message = AsyncMock()
    modal.children[0].value = "Colt"
    await modal.on_submit(submit)
    submit.response.edit_message.assert_awaited_once()
