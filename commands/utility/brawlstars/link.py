from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from api import add_brawlstars_linked_account, get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def getPlayerInfo(player_tag: str) -> dict[str, str] | None:
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            f"https://api.brawlstars.com/v1/players/%23{player_tag[1:]}",
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response,
    ):
        if response.status != 200:
            return None
        json_data: Any = await response.json()
        if isinstance(json_data, dict):
            return json_data
        else:
            return None


async def link(command_info: CommandInfo, player_tag: str) -> None:
    if not player_tag.startswith("#"):
        player_tag = f"#{player_tag}"
    player_info = await getPlayerInfo(player_tag)
    if not player_info:
        await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.link.error.notFound.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.link.error.notFound.description",
                ),
            )
        )
        return

    if await get_brawlstars_linked_account(command_info.user.id):
        await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.description",
                ),
            )
        )
        return

    await add_brawlstars_linked_account(command_info.user.id, player_tag)

    await command_info.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.link.success.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.link.success.description",
                tag=player_tag,
            ),
        )
    )
    return
