from __future__ import annotations

from api import get_brawlstars_linked_account
from localizer import tanjunLocalizer
from services.brawlstars import get_brawlstars_service
from utility import CommandInfo, tanjunEmbed


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

    service = get_brawlstars_service()
    player = await service.get_player(player_tag)
    if not player:
        await command_info.reply(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.playerinfo.error.notFound",
            )
        )
        return

    description = ""
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.trophies",
        trophies=player.trophies,
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.highest_trophies",
        highest_trophies=player.highest_trophies,
    )
    description += "\n"
    description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.playerinfo.description.expLevel",
        expLevel=player.exp_level,
    )

    if player.club:
        description += "\n"
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.club",
            tag=player.club.tag,
            name=player.club.name,
        )
    description += "\n"
    if player.x3vs3_victories != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.3v3Victories",
            victories=player.x3vs3_victories,
        )
    description += "\n"
    if player.solo_victories != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.soloVictories",
            victories=player.solo_victories,
        )
    description += "\n"
    if player.duo_victories != 0:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.playerinfo.description.duoVictories",
            victories=player.duo_victories,
        )
    description += "\n"
    description += "\n"
    all_brawlers = await service.get_brawler_list()
    brawlers_count = len(all_brawlers)
    owned_count = len(player.brawlers)
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
            player_name=player.name,
            tag=player_tag,
        ),
        description=description,
        color=player.name_color or 0xFFFFFF,
    )
    await command_info.reply(embed=embed)
