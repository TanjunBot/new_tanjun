import math
from datetime import datetime

import discord
from discord.ui import Button, View

import utility
from api import get_detailed_warnings, remove_warning
from localizer import tanjunLocalizer

WARNINGS_PER_PAGE = 5


class WarningView(View):
    def __init__(self, warnings, member, commandInfo):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.warnings = warnings
        self.member = member
        self.commandInfo = commandInfo
        self.page = 0
        self.message = None
        self.update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.viewwarns.unauthorizedUser"),
                ephemeral=True,
            )
            return False
        return True

    def update_buttons(self):
        self.clear_items()
        start = self.page * WARNINGS_PER_PAGE
        end = start + WARNINGS_PER_PAGE

        if self.page > 0:
            prev_button = Button(
                label=tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.viewwarns.prevButton"),
                style=discord.ButtonStyle.primary,
            )
            prev_button.callback = self.prev_page
            self.add_item(prev_button)
        for i, (warning_id, _, _, expires_at, _) in enumerate(self.warnings[start:end], start=start + 1):
            button = Button(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.viewwarns.removeButton",
                    number=i,
                ),
                custom_id=f"remove_{warning_id}",
                style=discord.ButtonStyle.danger,
                disabled=expires_at is not None and datetime.now() > expires_at,
            )
            button.callback = self.remove_warning_callback
            self.add_item(button)

        if (self.page + 1) * WARNINGS_PER_PAGE < len(self.warnings):
            next_button = Button(
                label=tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.viewwarns.nextButton"),
                style=discord.ButtonStyle.primary,
            )
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def remove_warning_callback(self, interaction: discord.Interaction):
        warning_id = int(interaction.data["custom_id"].split("_")[1])
        await remove_warning(warning_id)
        self.warnings = [w for w in self.warnings if w[0] != warning_id]

        if not self.warnings:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.viewwarns.noWarnings.title"),
                description=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.viewwarns.noWarnings.description",
                    user=self.member.name,
                ),
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        self.page = min(self.page, math.ceil(len(self.warnings) / WARNINGS_PER_PAGE) - 1)
        embed = create_warnings_embed(self.commandInfo, self.member, self.warnings, self.page)
        self.update_buttons()

        await interaction.response.edit_message(embed=embed, view=self)

    async def prev_page(self, interaction: discord.Interaction):
        self.page = max(0, self.page - 1)
        embed = create_warnings_embed(self.commandInfo, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.page = min(math.ceil(len(self.warnings) / WARNINGS_PER_PAGE) - 1, self.page + 1)
        embed = create_warnings_embed(self.commandInfo, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)


def create_warnings_embed(commandInfo, member, warnings, page):
    start = page * WARNINGS_PER_PAGE
    end = start + WARNINGS_PER_PAGE
    current_warnings = warnings[start:end]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.title", user=member.name),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.viewwarns.description",
            count=len(warnings),
        ),
    )

    for i, (_, reason, created_at, expires_at, created_by) in enumerate(current_warnings, start=start + 1):
        expired = expires_at is not None and datetime.now() > expires_at
        expiration_str = (
            f"<t:{int(expires_at.timestamp())}:D>"
            if expires_at
            else tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.viewwarns.never",
            )
        )
        expiration_str = f"~~{expiration_str}~~" if expired else expiration_str

        embed.add_field(
            name=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.warningEntry", number=i),
            value=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.viewwarns.warningDetails",
                reason=(
                    reason if reason else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.noReason")
                ),
                date=f"<t:{int(created_at.timestamp())}:D>",
                expiration=expiration_str,
                created_by=created_by,
            ),
            inline=False,
        )

    if len(warnings) > WARNINGS_PER_PAGE > 1:
        embed.set_footer(
            text=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.viewwarns.pageFooter",
                current=page + 1,
                total=math.ceil(len(warnings) / WARNINGS_PER_PAGE),
            )
        )

    return embed


async def view_warnings(commandInfo: utility.commandInfo, member: discord.Member):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).kick_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.viewwarns.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    guild_id = commandInfo.guild.id
    user_id = member.id

    warnings = await get_detailed_warnings(guild_id, user_id)

    if not warnings:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.noWarnings.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.viewwarns.noWarnings.description",
                user=member.name,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    embed = create_warnings_embed(commandInfo, member, warnings, 0)
    view = WarningView(warnings, member, commandInfo)

    view.message = await commandInfo.reply(embed=embed, view=view)
