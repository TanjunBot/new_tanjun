import math
from datetime import datetime
from typing import Any, cast

import discord  # type: ignore[import-not-found]
from discord.ui import Button, View  # type: ignore[import-not-found]

import utility
from api import get_detailed_warnings, remove_warning
from localizer import tanjunLocalizer

WARNINGS_PER_PAGE = 5


class WarningView(View):  # type: ignore[misc,no-any-unimported]
    def __init__(  # type: ignore[no-any-unimported]
        self,
        warnings: list[tuple[int, str, datetime, datetime | None, str]],
        member: discord.Member,
        commandInfo: utility.CommandInfo,
    ) -> None:
        super().__init__(timeout=300)  # 5 minutes timeout
        self.warnings: list[tuple[int, str, datetime, datetime | None, str]] = warnings
        self.member: discord.Member = member  # type: ignore[no-any-unimported]
        self.commandInfo: utility.CommandInfo = CommandInfo  # type: ignore[name-defined]
        self.page: int = 0
        self.message: discord.Message | None = None  # type: ignore[no-any-unimported]
        self.update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:  # type: ignore[no-any-unimported]
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(str(self.commandInfo.locale), "commands.admin.viewwarns.unauthorizedUser"),
                ephemeral=True,
            )
            return False
        return True

    def update_buttons(self) -> None:
        self.clear_items()
        start = self.page * WARNINGS_PER_PAGE
        end = start + WARNINGS_PER_PAGE

        if self.page > 0:
            prev_button = Button(
                label=tanjunLocalizer.localize(str(self.commandInfo.locale), "commands.admin.viewwarns.prevButton"),
                style=discord.ButtonStyle.primary,
            )
            prev_button.callback = self.prev_page
            self.add_item(prev_button)
        for i, (warning_id, _, _, expires_at, _) in enumerate(self.warnings[start:end], start=start + 1):
            button = Button(
                label=tanjunLocalizer.localize(
                    str(self.commandInfo.locale),
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
                label=tanjunLocalizer.localize(str(self.commandInfo.locale), "commands.admin.viewwarns.nextButton"),
                style=discord.ButtonStyle.primary,
            )
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def remove_warning_callback(self, interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
        data = cast(dict[str, Any], interaction.data)
        warning_id = int(str(data["custom_id"]).split("_")[1])
        await remove_warning(warning_id)
        self.warnings = [w for w in self.warnings if w[0] != warning_id]

        if len(self.warnings) == 0:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(self.commandInfo.locale), "commands.admin.viewwarns.noWarnings.title"),
                description=tanjunLocalizer.localize(
                    str(self.commandInfo.locale),
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

    async def prev_page(self, interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
        self.page = max(0, self.page - 1)
        embed = create_warnings_embed(self.commandInfo, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
        self.page = min(math.ceil(len(self.warnings) / WARNINGS_PER_PAGE) - 1, self.page + 1)
        embed = create_warnings_embed(self.commandInfo, self.member, self.warnings, self.page)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)


def create_warnings_embed(  # type: ignore[no-any-unimported]
    commandInfo: utility.CommandInfo,
    member: discord.Member,
    warnings: list[tuple[int, str, datetime, datetime | None, str]],
    page: int,
) -> utility.tanjunEmbed:
    start = page * WARNINGS_PER_PAGE
    end = start + WARNINGS_PER_PAGE
    current_warnings = warnings[start:end]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.title", user=member.name),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.admin.viewwarns.description",
            count=len(warnings),
        ),
    )

    for i, (_, reason, created_at, expires_at, created_by) in enumerate(current_warnings, start=start + 1):
        expired = expires_at is not None and datetime.now() > expires_at
        expiration_str = (
            f"<t:{int(expires_at.timestamp())}:D>"
            if expires_at is not None
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
                    reason
                    if reason is not None and len(reason.strip()) > 0  # type: ignore[redundant-expr]
                    else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.noReason")
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


async def view_warnings(commandInfo: utility.CommandInfo, member: discord.Member) -> None:  # type: ignore[no-any-unimported]
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).kick_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.viewwarns.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    guild_id = CommandInfo.guild.id  # type: ignore[name-defined]
    user_id = member.id

    warnings = await get_detailed_warnings(guild_id, user_id)

    if warnings is None or len(warnings) == 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.viewwarns.noWarnings.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.viewwarns.noWarnings.description",
                user=member.name,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    embed = create_warnings_embed(commandInfo, member, warnings, 0)
    view = WarningView(warnings, member, commandInfo)

    view.message = await commandInfo.reply(embed=embed, view=view)
