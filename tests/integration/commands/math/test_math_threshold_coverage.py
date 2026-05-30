from __future__ import annotations

import pytest

from commands.math.faculty import faculty_command
from commands.math.randomnumber import random_number_command


pytestmark = pytest.mark.asyncio


async def test_faculty_negative(admin_command_info):
    await faculty_command(admin_command_info, -1)
    admin_command_info.reply.assert_awaited_once()


async def test_faculty_too_large(admin_command_info):
    await faculty_command(admin_command_info, 101)
    admin_command_info.reply.assert_awaited_once()


async def test_faculty_zero(admin_command_info):
    await faculty_command(admin_command_info, 0)
    admin_command_info.reply.assert_awaited_once()


async def test_faculty_success(admin_command_info):
    await faculty_command(admin_command_info, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_randomnumber_success(admin_command_info):
    await random_number_command(admin_command_info, 1, 10, 3)
    admin_command_info.reply.assert_awaited_once()


async def test_randomnumber_invalid_range(admin_command_info):
    await random_number_command(admin_command_info, 10, 1, 1)
    admin_command_info.reply.assert_awaited_once()
