from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch

import pytest

import extensions.admin as admin_ext
from extensions.admin import (
    AdministrationCommands,
    AdminCog,
    JoinToCreateCommands,
    ReportCommands,
    RoleCommands,
    TriggerMessagesCommands,
    WarnCommands,
)
from tests.helpers.discord import make_member, make_role, make_text_channel
from tests.helpers.extensions import invoke_interaction_command
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.admin"


@pytest.fixture
def mock_all_admin_commands():
    patches = []
    for name in dir(admin_ext):
        if name.endswith("Command"):
            patches.append(patch.object(admin_ext, name, AsyncMock()))
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()


@pytest.mark.parametrize(
    "group_cls",
    [
        WarnCommands,
        RoleCommands,
        ReportCommands,
        TriggerMessagesCommands,
        JoinToCreateCommands,
        AdministrationCommands,
    ],
    ids=["warn", "role", "report", "trigger", "jtc", "admin"],
)
async def test_invoke_all_group_handlers(group_cls, mock_all_admin_commands):
    group = group_cls(name="test", description="test")
    for name, method in inspect.getmembers(group, predicate=inspect.isfunction):
        if not name.startswith("_") and inspect.iscoroutinefunction(method):
            bound = getattr(group, name)
            kwargs = {}
            sig = inspect.signature(bound)
            for pname in sig.parameters:
                if pname in ("self", "interaction", "ctx"):
                    continue
                if "Member" in str(sig.parameters[pname].annotation):
                    kwargs[pname] = make_member()
                elif "Role" in str(sig.parameters[pname].annotation):
                    kwargs[pname] = make_role()
                elif "TextChannel" in str(sig.parameters[pname].annotation) or "VoiceChannel" in str(
                    sig.parameters[pname].annotation
                ):
                    kwargs[pname] = make_text_channel()
            await invoke_interaction_command(bound, extra_kwargs=kwargs)


async def test_admin_cog_on_ready():
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called


