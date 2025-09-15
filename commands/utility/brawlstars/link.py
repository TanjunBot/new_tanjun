import aiohttp

from api import add_brawlstars_linked_account, get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def getPlayerInfo(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response,
    ):
        if response.status != 200:
            return None
        return await response.json()


async def link(commandInfo: commandInfo, playerTag: str):
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        return await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.notFound.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.notFound.description",
                ),
            )
        )

    if await get_brawlstars_linked_account(commandInfo.user.id):
        return await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.description",
                ),
            )
        )

    await add_brawlstars_linked_account(commandInfo.user.id, playerTag)

    return await commandInfo.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.description",
                tag=playerTag,
            ),
        )
    )
