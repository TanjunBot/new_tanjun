from typing import Any

import aiohttp
import brawlstats  # type: ignore[import-untyped,import-not-found]

from api import get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

bs_client = brawlstats.Client(brawlstarsToken, is_async=True)


async def getAllBrawlers() -> dict[str, Any] | None:
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            "https://api.brawlstars.com/v1/brawlers",
            headers=headers,
        ) as response,
    ):
        if response.status != 200:
            return None
        json_data: Any = await response.json()
        if isinstance(json_data, dict):
            return json_data
        return None


async def playerInfo(commandInfo: CommandInfo, playerTag: str | None = None) -> None:
    if not playerTag:
        playerTag = await get_brawlstars_linked_account(commandInfo.user.id)
    if playerTag and playerTag.startswith("<@"):
        playerTagUserID = playerTag.split("<@")[1].split(">")[0]
        playerTag = await get_brawlstars_linked_account(playerTagUserID)
        if not playerTag:
            await commandInfo.reply(
                embed=tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.battlelog.error.userNotLinked.description",
                    ),
                )
            )
            return

    if playerTag and not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    if not playerTag:
        await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.playerinfo.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.playerinfo.error.notLinked.description",
                ),
            )
        )
        return

    player: brawlstats.Player = await bs_client.get_player(playerTag)
    if player is None or not isinstance(player, brawlstats.Player):
        await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.playerinfo.error.notFound",
            )
        )
        return

    description = ""
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.trophies",
        trophies=player.trophies,
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.highestTrophies",
        highestTrophies=player.highest_trophies,
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.expLevel",
        expLevel=player.exp_level,
    )

    if hasattr(player, "club") and player.club:
        description += "\n"
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.club",
            tag=getattr(player.club, "tag", "N/A"),
            name=getattr(player.club, "name", "N/A"),
        )
    description += "\n"
    victories_3v3 = getattr(player, "x3vs3_victories", 0)
    if victories_3v3 != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.3v3Victories",
            victories=victories_3v3,
        )
    description += "\n"
    solo_victories = getattr(player, "solo_victories", 0)
    if solo_victories != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.soloVictories",
            victories=solo_victories,
        )
    description += "\n"
    duo_victories = getattr(player, "duo_victories", 0)
    if duo_victories != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.duoVictories",
            victories=duo_victories,
        )
    description += "\n"
    description += "\n"
    allBrawlers = await getAllBrawlers()
    brawlers_count = 0
    if allBrawlers and "items" in allBrawlers:
        brawlers_count = len(allBrawlers["items"])

    owned_count = len(getattr(player, "brawlers", []))
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.brawlers",
        brawlers=brawlers_count,
        owned=owned_count,
    )
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.title",
            playerName=getattr(player, "name", "Unknown"),
            tag=playerTag,
        ),
        description=description,
        color=getattr(player, "name_color", 0xFFFFFF),
    )
    await commandInfo.reply(embed=embed)
