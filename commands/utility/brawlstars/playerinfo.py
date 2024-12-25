from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed, isoTimeToDate, date_time_to_timestamp
import discord
from localizer import tanjunLocalizer
import json
from commands.utility.brawlstars.bshelper import getLevelEmoji


async def getPlayerInfo(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                respo = await response.json()
                return None
            return await response.json()


async def playerInfo(commandInfo: commandInfo, playerTag: str):
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
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
    levelEmoji = getLevelEmoji(playerInfo["expLevel"])
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

