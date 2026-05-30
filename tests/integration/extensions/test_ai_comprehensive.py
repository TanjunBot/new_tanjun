from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.ai as ai_ext
from extensions.ai import AiCommands, CustomSituationCommands, aiCustomSituationAutocomplete
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.ai"

PATCH_NAMES = ["add_custom_situation", "delete_custom_situation", "ask_gpt"]


@pytest.fixture
def mock_cmds():
    patches = [patch.object(ai_ext, name, new=AsyncMock()) for name in PATCH_NAMES]
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls,method,extra",
    [
        (
            CustomSituationCommands,
            "add_custom",
            {
                "name": "test",
                "personality": "a" * 10,
                "temperature": 1.0,
                "topp": 1.0,
                "frequencypenalty": 0.0,
                "presencepenalty": 0.0,
            },
        ),
        (CustomSituationCommands, "delete_custom", {}),
        (AiCommands, "ask_gpt_command", {"prompt": "hi", "temperature": 1.0, "topp": 1.0, "frequencypenalty": 0.0, "presencepenalty": 0.0}),
    ],
    ids=["add", "delete", "ask_gpt"],
)
async def test_ai_commands(group_cls, method, extra, mock_cmds) -> None:
    group = group_cls(name="test", description="test")
    await invoke_interaction_command(getattr(group, method), extra_kwargs=extra)


async def test_ai_autocomplete(mock_cmds) -> None:
    interaction = MagicMock()
    interaction.user.id = 1
    with patch.object(ai_ext.AiService, "get_public_situations_iterator") as mock_iter:
        async def gen():
            yield "Friendly"
            yield "Strict"

        mock_iter.return_value = gen()
        choices = await aiCustomSituationAutocomplete(interaction, "fri")
    assert len(choices) >= 1


async def test_ai_cog_on_ready(mock_cmds) -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
