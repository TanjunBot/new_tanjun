from __future__ import annotations

from unittest.mock import MagicMock

from PIL import Image

from commands.level.level_rankcard import _process_image_sync


def test_process_image_sync_basic():
    bg = [Image.new("RGBA", (1000, 300), (30, 30, 30, 255))]
    avatar = [Image.new("RGBA", (200, 200), (100, 100, 100, 255))]
    user = MagicMock()
    user.name = "Tester"
    user_info = MagicMock(level=10, xp=50, xp_needed=100)
    command_info = MagicMock()
    command_info.locale = "en_US"
    result = _process_image_sync(bg, avatar, None, user, user_info, command_info, 100)
    assert result.getvalue()


def test_process_image_sync_with_decoration():
    bg = [Image.new("RGBA", (1000, 300), (30, 30, 30, 255))]
    avatar = [Image.new("RGBA", (200, 200), (100, 100, 100, 255))]
    decoration = [Image.new("RGBA", (240, 240), (200, 50, 50, 255))]
    user = MagicMock()
    user.name = "Tester"
    user_info = MagicMock(level=1, xp=5, xp_needed=10)
    command_info = MagicMock()
    command_info.locale = "en_US"
    result = _process_image_sync(bg, avatar, decoration, user, user_info, command_info, 100)
    assert result.getvalue()


def test_process_image_sync_low_xp_bar():
    bg = [Image.new("RGBA", (1000, 300), (30, 30, 30, 255))]
    avatar = [Image.new("RGBA", (200, 200), (100, 100, 100, 255))]
    user = MagicMock()
    user.name = "Tester"
    user_info = MagicMock(level=1, xp=1, xp_needed=1000)
    command_info = MagicMock()
    command_info.locale = "en_US"
    result = _process_image_sync(bg, avatar, None, user, user_info, command_info, 100)
    assert result.getvalue()
