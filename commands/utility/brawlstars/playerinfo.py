from typing import Any

import aiohttp
import brawlstats

from api import get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed

bs_client = brawlstats.Client(brawlstarsToken, is_async=True)


async def getAllBrawlers() -> dict[str, dict[str, str]] | None:
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.brawlstars.com/v1/brawlers",
            headers=headers,
        ) as response:
            json_data: Any = await response.json()
            if isinstance(json_data, dict):
                return json_data
            else:
                return None


async def playerInfo(commandInfo: commandInfo, playerTag: str | None = None) -> None:
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
    if "club" in playerInfo and "tag" in playerInfo["club"]:
        description += "\n"
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.club",
            tag=player.club.tag,
            name=player.club.name,
        )
    description += "\n"
    if playerInfo["3vs3Victories"] != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.3v3Victories",
            victories=playerInfo["3vs3Victories"],
        )
    description += "\n"
    if playerInfo["soloVictories"] != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.soloVictories",
            victories=playerInfo["soloVictories"],
        )
    description += "\n"
    if playerInfo["duoVictories"] != 0:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.duoVictories",
            victories=playerInfo["duoVictories"],
        )
    description += "\n"
    description += "\n"
    allBrawlers = await getAllBrawlers()
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.brawlers",
        brawlers=len(allBrawlers["items"]) if allBrawlers is not None else 0,
        owned=len(playerInfo["brawlers"]),
    )
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.title",
            playerName=playerInfo["name"],
            tag=playerTag,
        ),
        description=description,
        color=playerInfo["nameColor"],
    )
    await commandInfo.reply(embed=embed)
