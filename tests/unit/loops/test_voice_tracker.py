from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from loops._voice_tracker import VoiceUserManager


def test_voice_manager_add_remove_clear():
    mgr = VoiceUserManager()
    mgr.add(1, 10)
    mgr.add(2, 10)
    assert (1, 10) in mgr.user_ids
    mgr.remove(1, 10)
    assert (1, 10) not in mgr.user_ids
    assert mgr.get_active_users() == [(2, 10)]
    mgr.clear()
    assert mgr.get_active_users() == []


def test_voice_manager_synchronize():
    mgr = VoiceUserManager()
    mgr.add(1, 10)
    mgr.add(2, 20)
    mgr._synchronize([(2, 20), (3, 30)])
    active = set(mgr.get_active_users())
    assert active == {(2, 20), (3, 30)}


def _member(mid: int, gid: int, *, self_mute: bool = False, self_deaf: bool = False):
    m = MagicMock(id=mid)
    m.guild.id = gid
    m.voice = MagicMock(self_mute=self_mute, self_deaf=self_deaf)
    return m


async def test_handle_voice_change_two_active():
    mgr = VoiceUserManager()
    m1 = _member(1, 10)
    m2 = _member(2, 10)
    channel = MagicMock()
    channel.members = [m1, m2]
    before = MagicMock(channel=None)
    after = MagicMock(channel=channel)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await mgr.handle_voice_change(m1, before, after)
    assert (1, 10) in mgr.user_ids and (2, 10) in mgr.user_ids


async def test_handle_voice_change_opted_out():
    mgr = VoiceUserManager()
    mgr.add(5, 99)
    member = _member(5, 99)
    before = MagicMock(channel=None)
    after = MagicMock(channel=MagicMock(members=[]))
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=True):
        await mgr.handle_voice_change(member, before, after)
    assert (5, 99) not in mgr.user_ids


async def test_module_level_aliases():
    from loops import _voice_tracker as vt

    vt.add_voice_user(1, 2)
    vt.remove_voice_user(1, 2)
    vt.update_voice_users([(3, 4)])
    assert (3, 4) in vt.voice_user_manager.user_ids
    member = _member(1, 10)
    before = MagicMock(channel=None)
    after = MagicMock(channel=None)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=True):
        await vt.handle_voice_change(member, before, after)
