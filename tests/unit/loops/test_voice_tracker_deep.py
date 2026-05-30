from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from loops._voice_tracker import VoiceUserManager


pytestmark = pytest.mark.asyncio


def _member(mid: int, gid: int, *, mute: bool = False, deaf: bool = False):
    m = MagicMock(id=mid)
    m.guild.id = gid
    m.voice = MagicMock(self_mute=mute, self_deaf=deaf)
    return m


async def test_before_channel_drops_below_two_removes():
    mgr = VoiceUserManager()
    mgr.add(1, 10)
    mgr.add(2, 10)
    m1 = _member(1, 10)
    before_ch = MagicMock()
    before_ch.members = [m1]
    after_ch = MagicMock()
    after_ch.members = []
    before = MagicMock(channel=before_ch)
    after = MagicMock(channel=after_ch)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await mgr.handle_voice_change(m1, before, after)
    assert (1, 10) not in mgr.user_ids


async def test_two_active_in_after_synchronizes():
    mgr = VoiceUserManager()
    m1 = _member(1, 10)
    m2 = _member(2, 10)
    ch = MagicMock(members=[m1, m2])
    before = MagicMock(channel=None)
    after = MagicMock(channel=ch)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await mgr.handle_voice_change(m1, before, after)
    assert (1, 10) in mgr.user_ids and (2, 10) in mgr.user_ids


async def test_muted_members_excluded():
    mgr = VoiceUserManager()
    m1 = _member(1, 10, mute=True)
    m2 = _member(2, 10)
    ch = MagicMock(members=[m1, m2])
    before = MagicMock(channel=None)
    after = MagicMock(channel=ch)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await mgr.handle_voice_change(m1, before, after)
    assert mgr.get_active_users() == []


async def test_both_channels_active_merge():
    mgr = VoiceUserManager()
    m1 = _member(1, 10)
    m2 = _member(2, 10)
    m3 = _member(3, 20)
    m4 = _member(4, 20)
    before_ch = MagicMock(members=[m1, m2])
    after_ch = MagicMock(members=[m3, m4])
    before = MagicMock(channel=before_ch)
    after = MagicMock(channel=after_ch)
    with patch("loops._voice_tracker.check_if_opted_out", new_callable=AsyncMock, return_value=False):
        await mgr.handle_voice_change(m1, before, after)
    assert (1, 10) in mgr.user_ids and (3, 20) in mgr.user_ids
