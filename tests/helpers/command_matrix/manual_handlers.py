from __future__ import annotations

from typing import Any

import utility
from locale_keys import locale
from utility import EmbedColor


async def booster_channel_info(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        colour=EmbedColor.INFO,
        title=locale.commands.utility.boosterchannelinfo.info.title(str(command_info.locale)),
        description=locale.commands.utility.boosterchannelinfo.info.description(command_info.locale),
    )
    await command_info.reply(embed=embed)


async def booster_role_info(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        colour=EmbedColor.INFO,
        title=locale.commands.utility.boosterroleinfo.info.title(str(command_info.locale)),
        description=locale.commands.utility.boosterroleinfo.info.description(command_info.locale),
    )
    await command_info.reply(embed=embed)


async def ask_custom_situation(
    command_info: utility.CommandInfo,
    prompt: str = "hello",
    personality: str = "test",
    **_kwargs: Any,
) -> None:
    from commands.ai.ask_gpt import ask_gpt
    from services.ai_service import AiService

    situation = await AiService.get_situation(personality, require_unlocked=True)
    await ask_gpt(
        command_info,
        name=personality,
        situation=situation.situation if situation else "",
        prompt=prompt,
        temperature=situation.temperature if situation else 1.0,
        top_p=situation.top_p if situation else 1.0,
        frequency_penalty=situation.frequency_penalty if situation else 0.0,
        presence_penalty=situation.presence_penalty if situation else 0.0,
    )


async def setup_logs_wizard(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        title="Log Setup Wizard",
        description="Welcome! Let's get logging configured.",
    )
    await command_info.reply(embed=embed)


async def setup_level_wizard(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        title="Level Setup Wizard",
        description="Let's set up the leveling system!",
    )
    await command_info.reply(embed=embed)


async def setup_giveaway_wizard(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        title="Giveaway Wizard Opened",
        description="The giveaway builder has opened.",
    )
    await command_info.reply(embed=embed)


async def feedback_command(command_info: utility.CommandInfo, ctx: Any = None, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(title="Feedback", description="Feedback received")
    await command_info.reply(embed=embed)


async def setup_booster_wizard(command_info: utility.CommandInfo, **_kwargs: Any) -> None:
    embed = utility.tanjunEmbed(
        title="Booster Setup Wizard",
        description="Configure perks for server boosters.",
    )
    await command_info.reply(embed=embed)
