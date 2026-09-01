from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LINT_SCRIPT = ROOT / "scripts" / "lint_view_initial_embed.py"


def _run_lint_on_snippet(snippet: str) -> int:
    path = ROOT / "extensions" / "_lint_view_initial_embed_fixture.py"
    path.write_text(snippet)
    try:
        result = subprocess.run(
            [sys.executable, str(LINT_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )
        return result.returncode
    finally:
        if path.exists():
            path.unlink()


def test_lint_flags_static_embed_with_new_paginated_view() -> None:
    snippet = '''
import utility
from discord.ui import View

class LogEventConfigView(View):
    async def _render_embed(self):
        return utility.tanjunEmbed(title="x", description="y")

class LogChannelSelectView(View):
    async def on_channel_select(self, interaction):
        event_view = LogEventConfigView("en", None)
        embed = utility.tanjunEmbed(title="bad", description="static")
        await interaction.response.edit_message(embed=embed, view=event_view)
'''
    assert _run_lint_on_snippet(snippet) == 1


def test_lint_passes_when_render_for_message_used() -> None:
    snippet = '''
import utility
from discord.ui import View

class LogEventConfigView(View):
    async def _render_embed(self):
        return utility.tanjunEmbed(title="x", description="y")

    async def render_for_message(self, *, prefix=None):
        embed = await self._render_embed()
        return embed

class LogChannelSelectView(View):
    async def on_channel_select(self, interaction):
        event_view = LogEventConfigView("en", None)
        embed = await event_view.render_for_message(prefix="ok")
        await interaction.response.edit_message(embed=embed, view=event_view)
'''
    assert _run_lint_on_snippet(snippet) == 0
