from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from api import get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def fetch_player_data(player_tag: str) -> dict[str, Any] | None:
    """Fetch player data directly from Brawl Stars API."""
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    url = "https://api.brawlstars.com/v1/players"
    params = {"tag": player_tag}
    async with (
        aiohttp.ClientSession() as session,
        session.get(url, headers=headers, params=params, timeout=ClientTimeout(total=10)) as response,
    ):
        if response.status != 200:
            return None
        return await response.json()


async def getAllBrawlers() -> dict[str, Any] | None:
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            "https://api.brawlstars.com/v1/brawlers",
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response,
    ):
        if response.status != 200:
            return None
        json_data: Any = await response.json()
        if isinstance(json_data, dict):
            return json_data
        return None


async def player_info(command_info: CommandInfo, player_tag: str | None = None) -> None:
    if not player_tag:
        player_tag = await get_brawlstars_linked_account(command_info.user.id)
    if player_tag and player_tag.startswith("<@"):
        player_tag_user_id = player_tag.split("<@")[1].split(">")[0]
        player_tag = await get_brawlstars_linked_account(player_tag_user_id)
        if not player_tag:
            await command_info.reply(
                embed=tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.title",
                    ),
                    description=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.description",
                    ),
                )
            )
            return

    if player_tag and not player_tag.startswith("#"):
        player_tag = f"#{player_tag}"
    if not player_tag:
        await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.playerinfo.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.playerinfo.error.notLinked.description",
                ),
            )
        )
        return

    player_data = await fetch_player_data(player_tag)
    if not player_data or "items" not in player_data or not player_data["items"]:
        await command_info.reply(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.playerinfo.error.notFound",
            )
        )
        return

    player = player_data["items"][0]

    description = ""
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.trophies",
        trophies=player.get("trophies", 0),
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.highest_trophies",
        highest_trophies=player.get("highest_trophies", 0),
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.expLevel",
        expLevel=player.get("expLevel", 0),
    )

    club = player.get("club", {})
    if club:
        description += "\n"
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.club",
            tag=club.get("tag", "N/A"),
            name=club.get("name", "N/A"),
        )
    description += "\n"
    victories_3v3 = player.get("x3vs3_victories", 0)
    if victories_3v3 != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.3v3Victories",
            victories=victories_3v3,
        )
    description += "\n"
    solo_victories = player.get("solo_victories", 0)
    if solo_victories != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.soloVictories",
            victories=solo_victories,
        )
    description += "\n"
    duo_victories = player.get("duo_victories", 0)
    if duo_victories != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.duoVictories",
            victories=duo_victories,
        )
    description += "\n"
    description += "\n"
    all_brawlers = await getAllBrawlers()
    brawlers_count = 0
    if all_brawlers and "items" in all_brawlers:
        brawlers_count = len(all_brawlers["items"])

    owned_count = len(player.get("brawlers", []))
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.brawlers",
        brawlers=brawlers_count,
        owned=owned_count,
    )
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.title",
            player_name=player.get("name", "Unknown"),
            tag=player_tag,
        ),
        description=description,
        color=player.get("nameColor", 0xFFFFFF),
    )
    await command_info.reply(embed=embed)
