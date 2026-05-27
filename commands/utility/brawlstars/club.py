import aiohttp
import discord
from aiohttp import ClientTimeout

from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import addThousandsSeparator, command_info, similar, tanjunEmbed


async def getClubInfo(club_tag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            f"https://api.brawlstars.com/v1/clubs/%23{club_tag[1:]}",
            headers=headers,
            timeout=ClientTimeout(total=10),
        ) as response,
    ):
        if response.status != 200:
            return None
        return await response.json()


async def club(command_info: command_info, club_tag: str):
    if not club_tag.startswith("#"):
        club_tag = f"#{club_tag}"
    club_info = await getClubInfo(club_tag)
    if not club_info:
        return await command_info.reply(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.club.error.notFound",
            )
        )

    club_name = club_info["name"]
    club_description = club_info["description"]
    required_trophies = club_info["required_trophies"]
    trophies = club_info["trophies"]
    members = club_info["members"]
    role_order = {"president": 4, "vicePresident": 3, "senior": 2, "member": 1}
    members = sorted(members, key=lambda x: (role_order[x["role"]], x["trophies"]), reverse=True)

    base_description = ""
    base_description += tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.brawlstars.club.description.overview",
        name=club_name,
        trophies=addThousandsSeparator(trophies),
        description=club_description,
        required_trophies=addThousandsSeparator(required_trophies),
    )
    pages = []
    for i, member in enumerate(members):
        description = base_description
        description += "\n"
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.brawlstars.club.description.member",
            name=member["name"],
            tag=member["tag"],
            trophies=addThousandsSeparator(member["trophies"]),
            role=member["role"],
        )
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.club.title",
                name=club_name,
                tag=club_tag,
                role=member["role"],
                current_page=i + 1,
                total_pages=len(members),
            ),
            description=description,
        )
        pages.append(embed)

    class ClubPaginator(discord.ui.View):
        def __init__(self, pages: list[tanjunEmbed], current_page=0):
            super().__init__(timeout=3600)
            self.pages = pages
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
                self.current_page = len(self.pages) - 1
            else:
                self.current_page -= 1
            await interaction.response.edit_message(view=self, embed=pages[self.current_page])

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
            if self.current_page == len(self.pages) - 1:
                self.current_page = 0
            else:
                self.current_page += 1
            await interaction.response.edit_message(view=self, embed=pages[self.current_page])

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
                title=tanjunLocalizer.localize(command_info.locale, "commands.utility.brawlstars.club.search.title")
            )
            self.command_info = command_info
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.club.search.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.utility.brawlstars.club.search.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            try:
                member_name = self.children[0].value

                desired_page = 0
                best_similarity = -100
                for i, member in enumerate(members):
                    similarity = similar(member["name"].lower(), member_name.lower())
                    if similarity > best_similarity:
                        best_similarity = similarity
                        desired_page = i
                    similarity = similar(member["tag"].lower(), member_name.lower())
                    if similarity > best_similarity:
                        best_similarity = similarity
                        desired_page = i

                view = ClubPaginator(pages, desired_page)
                page = pages[desired_page]
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

    if len(pages) > 1:
        view = ClubPaginator(pages)
        await command_info.reply(embed=pages[0], view=view)
    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.club.titleNoMembers",
                name=club_name,
                tag=club_tag,
            ),
            description=pages[0].description,
        )
        await command_info.reply(embed=embed)
