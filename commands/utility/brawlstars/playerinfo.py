from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_brawlstars_linked_account


async def getPlayerInfo(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


async def playerInfo(commandInfo: commandInfo, playerTag: str = None):
    if not playerTag:
        playerTag = await get_brawlstars_linked_account(commandInfo.user.id)
    if playerTag and not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    if not playerTag:
        return await commandInfo.reply(
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
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        return await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.playerinfo.error.notFound",
            )
        )
    description = ""
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.trophies",
        trophies=playerInfo["trophies"],
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.highestTrophies",
        highestTrophies=playerInfo["highestTrophies"],
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.playerinfo.description.expLevel",
        expLevel=playerInfo["expLevel"],
    )
    description += "\n"
    if "club" in playerInfo:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.playerinfo.description.club",
            tag=playerInfo["club"]["tag"],
            name=playerInfo["club"]["name"],
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
