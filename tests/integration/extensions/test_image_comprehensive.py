from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.image as image_ext
from extensions.image import ImageCommands
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.image"

PATCH_NAMES = ["apply_filter", "background", "compress", "mirror", "rescale", "resize"]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(image_ext, name, new=AsyncMock()) for name in PATCH_NAMES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


def _attachment() -> MagicMock:
    att = MagicMock()
    att.url = "https://example.com/img.png"
    att.filename = "img.png"
    return att


@pytest.mark.parametrize(
    "method,extra",
    [
        ("blurimage", {"image": _attachment(), "type": "gaussian", "radius": 3}),
        ("contourimage", {"image": _attachment()}),
        ("detailimage", {"image": _attachment()}),
        ("edgeenhance", {"image": _attachment()}),
        ("emboss", {"image": _attachment()}),
        ("sharpen", {"image": _attachment()}),
        ("smooth", {"image": _attachment()}),
        ("findedges", {"image": _attachment()}),
        ("mirror", {"image": _attachment(), "direction": "x"}),
        ("rescale", {"image": _attachment(), "factor": 0.5}),
        ("resize", {"image": _attachment(), "width": 100, "height": 100}),
    ],
    ids=[f"img{i}" for i in range(11)],
)
async def test_image_commands(method, extra, mock_cmds) -> None:
    group = ImageCommands(name="image", description="image")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_image_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
