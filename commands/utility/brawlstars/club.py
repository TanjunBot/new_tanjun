import aiohttp
import discord

from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import addThousandsSeparator, commandInfo, similar, tanjunEmbed


async def getClubInfo(clubTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/clubs/%23{clubTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


async def club(commandInfo: commandInfo, clubTag: str):
    if not clubTag.startswith("#"):
        clubTag = f"#{clubTag}"
    clubInfo = await getClubInfo(clubTag)
    if not clubInfo:
        return await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.club.error.notFound",
            )
        )

    clubName = clubInfo["name"]
    clubDescription = clubInfo["description"]
    requiredTrophies = clubInfo["requiredTrophies"]
    trophies = clubInfo["trophies"]
    members = clubInfo["members"]
    role_order = {"president": 4, "vicePresident": 3, "senior": 2, "member": 1}
    members = sorted(members, key=lambda x: (role_order[x["role"]], x["trophies"]), reverse=True)

    baseDescription = ""
    baseDescription += tanjunLocalizer.localize(
        commandInfo.locale,
        "commands.utility.brawlstars.club.description.overview",
        name=clubName,
        trophies=addThousandsSeparator(trophies),
        description=clubDescription,
        requiredTrophies=addThousandsSeparator(requiredTrophies),
    )
    pages = []
    for i, member in enumerate(members):
        description = baseDescription
        description += "\n"
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.brawlstars.club.description.member",
            name=member["name"],
            tag=member["tag"],
            trophies=addThousandsSeparator(member["trophies"]),
            role=member["role"],
        )
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.club.title",
                name=clubName,
                tag=clubTag,
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
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
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
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
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
            if not interaction.user.id == commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.events.notYourEmbed",
                    ),
                    ephemeral=True,
                )
                return
            await interaction.response.send_modal(SearchModal(commandInfo))

    class SearchModal(discord.ui.Modal):
        def __init__(self, commandInfo: commandInfo):
            super().__init__(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.brawlstars.club.search.title")
            )
            self.commandInfo = commandInfo
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.club.search.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.utility.brawlstars.club.search.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            try:
                memberName = self.children[0].value

                desiredPage = 0
                bestSimilarity = -100
                for i, member in enumerate(members):
                    similarity = similar(member["name"].lower(), memberName.lower())
                    if similarity > bestSimilarity:
                        bestSimilarity = similarity
                        desiredPage = i
                    similarity = similar(member["tag"].lower(), memberName.lower())
                    if similarity > bestSimilarity:
                        bestSimilarity = similarity
                        desiredPage = i

                view = ClubPaginator(pages, desiredPage)
                page = pages[desiredPage]
                await interaction.response.edit_message(view=view, embed=page)

            except ValueError:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except Exception:
                embed = tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.utility.brawlstars.brawlers.search.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    if len(pages) > 1:
        view = ClubPaginator(pages)
        await commandInfo.reply(embed=pages[0], view=view)
    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.club.titleNoMembers",
                name=clubName,
                tag=clubTag,
            ),
            description=pages[0].description,
        )
        await commandInfo.reply(embed=embed)
