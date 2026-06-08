from __future__ import annotations

from contextlib import ExitStack, contextmanager
from typing import Any, Iterator
from unittest.mock import AsyncMock, MagicMock, patch

from diagnostics.patches import api_patches, ui_patches
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.discord import make_guild


def _needs_db(case: MatrixCase) -> bool:
    group = case.group
    return (
        group.startswith("admin_")
        or group.startswith("utility")
        or group.startswith("level")
        or group in {"giveaway_name", "logs_name", "minigame_name", "channel_name", "setup_name"}
    )


def _needs_ui(case: MatrixCase) -> bool:
    group = case.group
    if group == "setup_name":
        return True
    if group.startswith("admin_") and case.tree_path.rsplit(" ", 1)[-1] in {
        "admin_embed_name",
        "admin_triggermessages_name",
    }:
        return True
    return False


def _ai_mocks() -> dict[str, Any]:
    situation = MagicMock()
    situation.situation = "test personality"
    situation.temperature = 1.0
    situation.top_p = 1.0
    situation.frequency_penalty = 0.0
    situation.presence_penalty = 0.0

    token_overview = MagicMock()
    token_overview.free_token = 100
    token_overview.plus_token = 0
    token_overview.paid_token = 0

    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content="test ai response"))]
    completion.usage = MagicMock(total_tokens=10)

    completions = MagicMock()
    completions.create = AsyncMock(return_value=completion)
    client = MagicMock()
    client.chat.completions = completions

    mocks: dict[str, Any] = {
        "situation": situation,
        "token_overview": token_overview,
        "client": client,
    }
    return mocks


@contextmanager
def matrix_patches(case: MatrixCase) -> Iterator[dict[str, Any]]:
    mocks: dict[str, Any] = {}
    group = case.group
    stack = ExitStack()

    try:
        if group == "funcmd_name":
            gif = stack.enter_context(
                patch("commands.fun.funcommands.utility.getGif", new_callable=AsyncMock)
            )
            gif.return_value = ["https://example.com/gif.gif"]
            mocks["getGif"] = gif

        if _needs_db(case):
            stack.enter_context(api_patches())

        if _needs_ui(case):
            stack.enter_context(ui_patches())

        if group == "ai_name":
            ai = _ai_mocks()
            for target in (
                "services.openrouter_client.get_openrouter_client",
                "commands.ai.ask_gpt.get_openrouter_client",
                "commands.ai.ask_gpt.client",
            ):
                stack.enter_context(patch(target, ai["client"]))
            stack.enter_context(
                patch(
                    "services.ai_service.AiService.get_available_tokens",
                    new_callable=AsyncMock,
                    return_value=100,
                )
            )
            stack.enter_context(
                patch(
                    "services.ai_service.AiService.initialize_user",
                    new_callable=AsyncMock,
                )
            )
            stack.enter_context(
                patch(
                    "services.ai_service.AiService.consume",
                    new_callable=AsyncMock,
                    return_value=True,
                )
            )
            stack.enter_context(
                patch(
                    "services.ai_service.AiService.get_token_overview",
                    new_callable=AsyncMock,
                    return_value=ai["token_overview"],
                )
            )
            stack.enter_context(
                patch(
                    "services.ai_service.AiService.get_situation",
                    new_callable=AsyncMock,
                    return_value=ai["situation"],
                )
            )
            mocks.update(ai)

        if group == "image_name":
            for target in (
                "services.image_service.ImageService.validate_attachment",
                "services.image_service.ImageService.process",
                "commands.image._filter.ImageService.validate_attachment",
                "commands.image._filter.ImageService.process",
            ):
                if "validate" in target:
                    stack.enter_context(patch(target, return_value=None))
                else:
                    stack.enter_context(patch(target, new_callable=AsyncMock, return_value=b"\x89PNG\r\n\x1a\n"))

        if group == "math_name" and case.dimension("command") == "plotfunction":
            stack.enter_context(patch("matplotlib.pyplot.savefig"))
            stack.enter_context(patch("matplotlib.pyplot.close"))

        if group == "games_name":
            stack.enter_context(patch("commands.games.hangman_words.words.words", return_value=["test"]))
            stack.enter_context(patch("commands.games.wordle_words.words.allowed_words", return_value=["tests"]))
            stack.enter_context(patch("commands.games.wordle_words.words.possible_words", return_value=["tests"]))
            mock_aki = MagicMock()
            mock_aki.start_game = MagicMock()
            mock_aki.question = "Is it a test?"
            mock_aki.progression = 50
            stack.enter_context(patch("commands.games.akinator.Akinator", return_value=mock_aki))

        if group == "minigame_name":
            stack.enter_context(
                patch(
                    "services.counting_repository.CountingRepository.set_progress",
                    new_callable=AsyncMock,
                )
            )

        if group == "giveaway_name":
            giveaway = MagicMock()
            giveaway.guild_id = str(make_guild().id)
            giveaway.ended = False
            giveaway.started = True
            stack.enter_context(
                patch(
                    "services.giveaway_service.giveaway_service.get",
                    new_callable=AsyncMock,
                    return_value=giveaway,
                )
            )
            stack.enter_context(
                patch(
                    "services.giveaway_service.giveaway_service.delete",
                    new_callable=AsyncMock,
                )
            )

        if group.startswith("utility"):
            bs_player = MagicMock()
            bs_player.trophies = 100
            bs_player.name = "Test"
            bs_player.tag = "#TEST"
            bs_player.role = "member"
            bs_club = MagicMock()
            bs_club.name = "Club"
            bs_club.description = "Test club"
            bs_club.required_trophies = 0
            bs_club.trophies = 1000
            bs_club.members = [bs_player]
            bs_service = MagicMock()
            bs_service.get_player = AsyncMock(return_value=bs_player)
            bs_service.get_club = AsyncMock(return_value=bs_club)
            bs_service.get_battle_log = AsyncMock(return_value=[])
            bs_service.get_events = AsyncMock(return_value=[])
            stack.enter_context(
                patch("services.brawlstars.get_brawlstars_service", return_value=bs_service)
            )
            stack.enter_context(
                patch("api.get_brawlstars_linked_account", new_callable=AsyncMock, return_value="#ABC")
            )
            stack.enter_context(
                patch("api.feedbackIsBlocked", new_callable=AsyncMock, return_value=False)
            )

        if group.startswith("admin_"):
            stack.enter_context(
                patch(
                    "api.clear_channel_overwrites",
                    new_callable=AsyncMock,
                    return_value=None,
                )
            )
            stack.enter_context(
                patch(
                    "api.save_channel_overwrites",
                    new_callable=AsyncMock,
                    return_value=None,
                )
            )
            stack.enter_context(
                patch("api.get_reports", new_callable=AsyncMock, return_value=[])
            )
            stack.enter_context(
                patch(
                    "commands.admin.reports.show_reports.get_reports",
                    new_callable=AsyncMock,
                    return_value=[],
                )
            )
            stack.enter_context(
                patch("api.get_warn_config", new_callable=AsyncMock, return_value=None)
            )
            stack.enter_context(
                patch(
                    "services.trigger_message_service.trigger_message_service.create",
                    new_callable=AsyncMock,
                )
            )

        yield mocks
    finally:
        stack.close()
