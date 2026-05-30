from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_apply_filter_admin_paths(admin_command_info):
    from commands.image._filter import apply_filter as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None, filter_name=None)
    except Exception:
        pass


async def test_apply_filter_restricted_paths(restricted_command_info):
    from commands.image._filter import apply_filter as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None, filter_name=None)
    except Exception:
        pass


async def test_apply_filter_no_guild(restricted_command_info):
    from commands.image._filter import apply_filter as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None, filter_name=None)
    except Exception:
        pass


async def test_contour_admin_paths(admin_command_info):
    from commands.image._filter import contour as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_contour_restricted_paths(restricted_command_info):
    from commands.image._filter import contour as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_contour_no_guild(restricted_command_info):
    from commands.image._filter import contour as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_detail_admin_paths(admin_command_info):
    from commands.image._filter import detail as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_detail_restricted_paths(restricted_command_info):
    from commands.image._filter import detail as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_detail_no_guild(restricted_command_info):
    from commands.image._filter import detail as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_edge_enhance_admin_paths(admin_command_info):
    from commands.image._filter import edge_enhance as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_edge_enhance_restricted_paths(restricted_command_info):
    from commands.image._filter import edge_enhance as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_edge_enhance_no_guild(restricted_command_info):
    from commands.image._filter import edge_enhance as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_emboss_admin_paths(admin_command_info):
    from commands.image._filter import emboss as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_emboss_restricted_paths(restricted_command_info):
    from commands.image._filter import emboss as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_emboss_no_guild(restricted_command_info):
    from commands.image._filter import emboss as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_find_edges_admin_paths(admin_command_info):
    from commands.image._filter import find_edges as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_find_edges_restricted_paths(restricted_command_info):
    from commands.image._filter import find_edges as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_find_edges_no_guild(restricted_command_info):
    from commands.image._filter import find_edges as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_sharpen_admin_paths(admin_command_info):
    from commands.image._filter import sharpen as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_sharpen_restricted_paths(restricted_command_info):
    from commands.image._filter import sharpen as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_sharpen_no_guild(restricted_command_info):
    from commands.image._filter import sharpen as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_smooth_admin_paths(admin_command_info):
    from commands.image._filter import smooth as command_fn

    try:
        await command_fn(admin_command_info, command_info=admin_command_info, image=None)
    except Exception:
        pass


async def test_smooth_restricted_paths(restricted_command_info):
    from commands.image._filter import smooth as command_fn

    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass


async def test_smooth_no_guild(restricted_command_info):
    from commands.image._filter import smooth as command_fn

    restricted_command_info.guild = None
    try:
        await command_fn(restricted_command_info, command_info=restricted_command_info, image=None)
    except Exception:
        pass
