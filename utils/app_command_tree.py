from __future__ import annotations

from typing import Any

from discord.utils import MISSING


def make_add_command_idempotent(tree: Any) -> None:
    original_add_command = tree.add_command

    def add_command(command: Any, /, **kwargs: Any) -> None:
        if not kwargs.get("override", False):
            root = getattr(command, "root_parent", None) or command
            lookup_guild = kwargs.get("guild", MISSING)
            if lookup_guild is MISSING:
                lookup_guild = None
            if tree.get_command(root.name, guild=lookup_guild) is not None:
                return
        original_add_command(command, **kwargs)

    tree.add_command = add_command
