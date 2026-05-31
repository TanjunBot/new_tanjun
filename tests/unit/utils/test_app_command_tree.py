from __future__ import annotations

from unittest.mock import MagicMock

from utils.app_command_tree import make_add_command_idempotent


def test_add_command_skips_when_already_registered() -> None:
    tree = MagicMock()
    existing = MagicMock()
    tree.get_command.return_value = existing
    calls: list[MagicMock] = []

    def original_add(command, /, *, guild=..., guilds=..., override=False):
        calls.append(command)

    tree.add_command = original_add
    make_add_command_idempotent(tree)

    command = MagicMock()
    command.root_parent = None
    command.name = "levelcommands_name"

    tree.add_command(command)

    tree.get_command.assert_called_once_with("levelcommands_name", guild=None)
    assert calls == []


def test_add_command_registers_when_missing() -> None:
    tree = MagicMock()
    tree.get_command.return_value = None
    calls: list[MagicMock] = []

    def original_add(command, /, *, guild=..., guilds=..., override=False):
        calls.append(command)

    tree.add_command = original_add
    make_add_command_idempotent(tree)

    command = MagicMock()
    command.root_parent = None
    command.name = "levelcommands_name"

    tree.add_command(command)

    assert calls == [command]
