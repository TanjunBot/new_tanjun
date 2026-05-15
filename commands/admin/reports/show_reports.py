import discord

import utility
from api import (
    block_reporter,
    check_if_reporter_is_blocked,
    delete_report,
    get_reports,
    unblock_reporter,
)
from localizer import tanjunLocalizer
from models import ReportModel


async def show_reports(commandInfo: utility.CommandInfo, user: discord.Member | None = None) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.reports.show_reports.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.reports.show_reports.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    reports = await get_reports(commandInfo.guild.id, user.id if user else None)

    if not reports:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.reports.show_reports.noReports.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.reports.show_reports.noReports.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    async def checkIfCurrentReporterIsBlocked(reports: list[ReportModel], page: int) -> bool:
        assert commandInfo.guild is not None
        return bool(await check_if_reporter_is_blocked(commandInfo.guild.id, str(reports[page].reporter_id)))

    currentReporterIsBlocked = await checkIfCurrentReporterIsBlocked(reports, 0)

    class reportsView(discord.ui.View):
        def __init__(self, reports: list[ReportModel], page: int = 0) -> None:
            super().__init__()
            self.reports = reports
            self.page = page
            self.update_buttons()

        def update_buttons(self) -> None:
            self.previous.disabled = len(self.reports) <= 1
            self.next.disabled = len(self.reports) <= 1

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.show_reports.previous.label"),
            style=discord.ButtonStyle.secondary,
            emoji="⬅️",
        )
        async def previous(  # type: ignore[misc]
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != commandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.not_your_reports",
                    ),
                    ephemeral=True,
                )
                return

            self.page -= 1
            if self.page < 0:
                self.page = len(self.reports) - 1
            await interaction.response.edit_message(view=self, embed=self.get_embed())

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.show_reports.remove.label"),
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
        )
        async def remove(  # type: ignore[misc]
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != commandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.not_your_reports",
                    ),
                    ephemeral=True,
                )
                return

            await delete_report(commandInfo.guild.id, self.reports[self.page].id)  # type: ignore[union-attr]
            self.reports.pop(self.page)
            if len(self.reports) == 0:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.noReports.title",
                    ),
                    description=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.noReports.description",
                    ),
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            if self.page >= len(self.reports):
                self.page = len(self.reports) - 1
            await interaction.response.edit_message(view=self, embed=self.get_embed())

        if not currentReporterIsBlocked:

            @discord.ui.button(
                label=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.show_reports.block.label",
                ),
                style=discord.ButtonStyle.danger,
                emoji="🚫",
            )
            async def block(  # type: ignore[misc]
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button[Any],
            ) -> None:
                if interaction.user.id != commandInfo.user.id:  # type: ignore[misc]
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.admin.reports.show_reports.not_your_reports",
                        ),
                        ephemeral=True,
                    )
                    return
                await block_reporter(commandInfo.guild.id, self.reports[self.page].reporter_id)  # type: ignore[union-attr]
                await interaction.response.edit_message(view=reportsView(reports, self.page), embed=self.get_embed())

        else:

            @discord.ui.button(
                label=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.show_reports.unblock.label",
                ),
                style=discord.ButtonStyle.success,
                emoji="🔓",
            )
            async def unblock(  # type: ignore[misc]
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button[Any],
            ) -> None:
                if interaction.user.id != commandInfo.user.id:  # type: ignore[misc]
                    await interaction.response.send_message(
                        tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.admin.reports.show_reports.not_your_reports",
                        ),
                        ephemeral=True,
                    )
                    return
                await unblock_reporter(commandInfo.guild.id, self.reports[self.page].reporter_id)  # type: ignore[union-attr]
                nonlocal currentReporterIsBlocked
                currentReporterIsBlocked = await checkIfCurrentReporterIsBlocked(reports, self.page)
                await interaction.response.edit_message(view=reportsView(reports, self.page), embed=self.get_embed())

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.show_reports.next.label"),
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
        )
        async def next(  # type: ignore[misc]
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != commandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.not_your_reports",
                    ),
                    ephemeral=True,
                )
                return

            self.page += 1
            if self.page >= len(self.reports):
                self.page = 0
            await interaction.response.edit_message(view=self, embed=self.get_embed())

        def get_embed(self) -> discord.Embed:
            report = self.reports[self.page]
            user_str = str(report.user_id)
            reporter_str = str(report.reporter_id)
            reason = str(report.reason)
            createdAt = str(report.created_at)
            accepted = bool(report.accepted)
            acceptedAt = str(report.accepted_at)
            resolved = bool(report.resolved)
            resolvedAt = str(report.resolved_at)

            locale = str(commandInfo.locale)

            description = tanjunLocalizer.localize(
                locale,
                "commands.admin.reports.show_reports.report.description",
                user=user_str,
                reporter=reporter_str,
                reason=reason,
                createdAt=createdAt,
            )

            if accepted:
                description += "\n" + tanjunLocalizer.localize(
                    locale,
                    "commands.admin.reports.show_reports.report.accepted",
                    acceptedAt=acceptedAt,
                )
            else:
                description += "\n" + tanjunLocalizer.localize(
                    locale, "commands.admin.reports.show_reports.report.not_accepted"
                )

            if resolved:
                description += "\n" + tanjunLocalizer.localize(
                    locale,
                    "commands.admin.reports.show_reports.report.resolved",
                    resolvedAt=resolvedAt,
                )
            else:
                description += "\n" + tanjunLocalizer.localize(
                    locale, "commands.admin.reports.show_reports.report.not_resolved"
                )

            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    locale,
                    "commands.admin.reports.show_reports.report.title",
                    index=self.page + 1,
                    total=len(self.reports),
                ),
                description=description,
            )
            return embed

    view = reportsView(reports)
    await commandInfo.reply(embed=view.get_embed(), view=view)
