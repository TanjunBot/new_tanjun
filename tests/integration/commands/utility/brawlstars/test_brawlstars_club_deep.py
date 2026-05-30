from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.brawlstars.club import club
from tests.helpers.discord import make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _member(name="Player", role="member", trophies=1000):
    m = MagicMock()
    m.name = name
    m.tag = "#ABC"
    m.trophies = trophies
    m.role = role
    return m


def _club_info(members=None):
    info = MagicMock()
    info.name = "Club"
    info.description = "Desc"
    info.required_trophies = 500
    info.trophies = 50000
    info.members = members or [_member("A", "president", 5000), _member("B", "member", 1000)]
    return info


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_not_found(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=None)
    mock_get_service.return_value = service
    await club(admin_command_info, "TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_adds_hash_prefix(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info())
    mock_get_service.return_value = service
    await club(admin_command_info, "TAG")
    service.get_club.assert_awaited_once_with("#TAG")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_pagination(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member(f"P{i}") for i in range(3)]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    next_i = make_view_interaction(admin_command_info.user)
    next_i.response.edit_message = AsyncMock()
    await view.next(next_i, MagicMock())
    next_i.response.edit_message.assert_awaited_once()

    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.send_message = AsyncMock()
    await view.previous(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_single_member(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member("Solo")]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    admin_command_info.reply.assert_awaited_once()
    assert "view" not in (admin_command_info.reply.await_args.kwargs or {})


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_search_modal(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member("Alpha"), _member("Beta")]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    search = make_view_interaction(admin_command_info.user)
    search.response.send_modal = AsyncMock()
    await view.search(search, MagicMock())
    search.response.send_modal.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_previous_page(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member(f"P{i}") for i in range(2)]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.current_page = 0
    prev = make_view_interaction(admin_command_info.user)
    prev.response.edit_message = AsyncMock()
    await view.previous(prev, MagicMock())
    prev.response.edit_message.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_search_submit(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member("Alpha"), _member("Beta")]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    search = make_view_interaction(admin_command_info.user)
    search.response.send_modal = AsyncMock()
    await view.search(search, MagicMock())
    modal = search.response.send_modal.await_args[0][0]
    modal.children[0].value = "Alpha"
    submit = make_view_interaction(admin_command_info.user)
    submit.response.edit_message = AsyncMock()
    await modal.on_submit(submit)
    submit.response.edit_message.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_search_wrong_user(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member("Alpha"), _member("Beta")]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.send_message = AsyncMock()
    await view.search(wrong, MagicMock())
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.brawlstars.club.get_brawlstars_service")
async def test_club_next_wraps(mock_get_service, admin_command_info):
    service = MagicMock()
    service.get_club = AsyncMock(return_value=_club_info([_member("A"), _member("B")]))
    mock_get_service.return_value = service
    await club(admin_command_info, "#CLUB")
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.current_page = 1
    nxt = make_view_interaction(admin_command_info.user)
    nxt.response.edit_message = AsyncMock()
    await view.next(nxt, MagicMock())
    assert view.current_page == 0
    nxt.response.edit_message.assert_awaited_once()
