import json

import discord

from api import get_brawlstars_linked_account
from commands.utility.brawlstars.bshelper import (
    getGadgetEmoji,
    getGearEmoji,
    getLevelEmoji,
    getStarPowerEmoji,
    parseName,
)
from localizer import tanjunLocalizer
from services.brawlstars import get_brawlstars_service
from utility import command_info, similar, tanjunEmbed


async def brawlers(command_info: command_info, player_tag: str = None):
    if not player_tag:
        player_tag = await get_brawlstars_linked_account(command_info.user.id)
    if player_tag and player_tag.startswith("<@"):
        player_tag_user_id = player_tag.split("<@")[1].split(">")[0]
        player_tag = await get_brawlstars_linked_account(player_tag_user_id)
        if not player_tag:
            return await command_info.reply(
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
    if player_tag and not player_tag.startswith("#"):
        player_tag = f"#{player_tag}"
    if not player_tag:
        return await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.error.notLinked.description",
                ),
            )
        )

    service = get_brawlstars_service()
    player_info = await service.get_player(player_tag)
    if not player_info:
        return await command_info.reply(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.error.notFound",
            )
        )

    player_name = player_info.name
    total_brawlers = len(player_info.brawlers)

    async def generate_page(page_number: int) -> discord.Embed:
        brawler = player_info.brawlers[page_number]
        id = brawler.id
        name = parseName(brawler.name)
        power = brawler.power
        rank = brawler.rank
        trophies = brawler.trophies
        highest_trophies = brawler.highest_trophies
        gears = brawler.gears
        gadgets = brawler.gadgets
        star_powers = brawler.star_powers
        level_emoji = getLevelEmoji(rank)

        if rank <= 50:
            description = tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.description.overview",
                name=name,
                power=power,
                rank=rank,
                trophies=trophies,
                highest_trophies=highest_trophies,
                level_emoji=level_emoji,
            )
            description += "\n"
        else:
            description = tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.description.overviewMaxTier",
                name=name,
                power=power,
                rank=rank,
                trophies=trophies,
                highest_trophies=highest_trophies,
                level_emoji=level_emoji,
            )
            description += "\n"

        if len(star_powers) > 0:
            description += tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.description.star_powers",
            )
            description += "\n"

            for star_power in star_powers:
                name = f" {getStarPowerEmoji(star_power.id)} {parseName(star_power.name)}"
                description += tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.description.star_power",
                    name=name,
                )
                description += "\n"
            description += "\n"

        if len(gadgets) > 0:
            description += tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.description.gadgets",
            )
            description += "\n"
            description += "\n"

            for gadget in gadgets:
                name = f" {getGadgetEmoji(gadget.id)} {parseName(gadget.name)}"
                description += tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.description.gadget",
                    name=name,
                )
                description += "\n"
            description += "\n"

        if len(gears) > 0:
            description += tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.description.gears",
            )
            description += "\n"

            for gear in gears:
                name = f" {getGearEmoji(gear.id)} {parseName(gear.name)}"
                description += tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.description.gear",
                    name=name,
                )
                description += "\n"
            description += "\n"
            description += "\n"

        if command_info.user.id == 1295625022454370346 and command_info.guild.id == 947219439764521060:
            description += "\n"
            description += f"raw: \n```json\n{json.dumps(brawler.model_dump(), indent=4)}\n```"

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.title",
                current_page=page_number + 1,
                total_pages=total_brawlers,
                name=player_name,
                tag=player_tag,
            ),
            description=description,
        )
        embed.set_thumbnail(url=f"https://cdn.brawlify.com/brawlers/borderless/{id}.png")
        return embed

    class BrawlersPaginator(discord.ui.View):
        def __init__(self, current_page=0):
            super().__init__(timeout=3600)
            self.current_page = current_page

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return

            if self.current_page == 0:
                self.current_page = total_brawlers - 1
            else:
                self.current_page -= 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return

            if self.current_page == total_brawlers - 1:
                self.current_page = 0
            else:
                self.current_page += 1

            new_page = await generate_page(self.current_page)
            await interaction.response.edit_message(view=self, embed=new_page)

        @discord.ui.button(label="🔍", style=discord.ButtonStyle.primary)
        async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
            await interaction.response.send_modal(SearchModal(command_info))

    class SearchModal(discord.ui.Modal):
        def __init__(self, command_info: command_info):
            super().__init__(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.brawlers.search.title",
                )
            )
            self.command_info = command_info
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            try:
                brawler_name = self.children[0].value

                desired_page = 0
                best_similarity = -100
                for i, brawler in enumerate(player_info.brawlers):
                    similarity = similar(brawler.name.lower(), brawler_name.lower())
                    if similarity > best_similarity:
                        best_similarity = similarity
                        desired_page = i

                view = BrawlersPaginator(desired_page)
                page = await generate_page(desired_page)
                await interaction.response.edit_message(view=view, embed=page)

            except ValueError:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except Exception:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    if total_brawlers > 1:
        first_page = await generate_page(0)
        view = BrawlersPaginator()
        await command_info.reply(embed=first_page, view=view)
    else:
        first_page = await generate_page(0)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.brawlers.titleNoPages",
                player_name=player_name,
                tag=player_tag,
            ),
            description=first_page.description,
        )
        await command_info.reply(embed=embed)
