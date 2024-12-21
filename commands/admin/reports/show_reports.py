import discord
import utility
from localizer import tanjunLocalizer
from api import (
    get_reports,
    accept_report,
    reject_report,
    resolve_report,
    delete_report,
)


async def show_reports(commandInfo: utility.commandInfo, user: discord.Member = None):
    if not commandInfo.user.guild_permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.reports.show_reports.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.reports.show_reports.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    reports = await get_reports(commandInfo.guild.id, user.id if user else None)

    if not reports:
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
        await commandInfo.reply(embed=embed)
        return

    class reportsView(discord.ui.View):
        def __init__(self, reports: list):
            super().__init__()
            self.reports = reports
            self.page = 0
            self.previous.disabled = len(reports) <= 1
            self.next.disabled = len(reports) <= 1

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.show_reports.previous.label"
            ),
            style=discord.ButtonStyle.secondary,
            emoji="⬅️",
        )
        async def previous(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
        ):
            if interaction.user.id != commandInfo.user.id:
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
            await interaction.response.edit_message(
                view=self, embed=self.get_embed()
            )

        # @discord.ui.button(
        #     label=tanjunLocalizer.localize(
        #         commandInfo.locale, "commands.admin.reports.show_reports.remove.label"
        #     ),
        #     style=discord.ButtonStyle.danger,
        #     emoji="🗑️",
        # )
        # async def remove(
        #     self,
        #     interaction: discord.Interaction,
        #     button: discord.ui.Button,
        # ):
        #     if interaction.user.id != commandInfo.user.id:
        #         await interaction.response.send_message(
        #             tanjunLocalizer.localize(
        #                 commandInfo.locale,
        #                 "commands.admin.reports.show_reports.not_your_reports",
        #             ),
        #             ephemeral=True,
        #         )
        #         return

        #     await delete_report(commandInfo.guild.id, self.reports[self.page][0])
        #     self.reports.pop(self.page)
        #     await interaction.response.edit_message(
        #         view=self, embed=self.get_embed()
        #     )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.show_reports.resolve.label"
            ),
            style=discord.ButtonStyle.success,
            emoji="✅",
        )
        async def resolve(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
        ):
            if interaction.user.id != commandInfo.user.id:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.reports.show_reports.not_your_reports",
                    ),
                    ephemeral=True,
                )
                return

            await resolve_report(commandInfo.guild.id, self.reports[self.page][0])
            self.reports = await get_reports(commandInfo.guild.id, user.id if user else None)
            await interaction.response.edit_message(
                view=self, embed=self.get_embed()
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.show_reports.next.label"
            ),
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
        )
        async def next(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button,
        ):
            if interaction.user.id != commandInfo.user.id:
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
            await interaction.response.edit_message(
                view=self, embed=self.get_embed()
            )

        def get_embed(self = None):
            if self is None:
                self = reportsView(reports)
            report = self.reports[self.page]
            user = report[2]
            reporter = report[3]
            reason = report[4]
            createdAt = report[5]
            accepted = report[6]
            acceptedAt = report[7]
            resolved = report[9]
            resolvedAt = report[10]

            locale = commandInfo.locale

            description = tanjunLocalizer.localize(
                locale,
                "commands.admin.reports.show_reports.report.description",
                user=user,
                reporter=reporter,
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

    def get_embed(self = None):
        if self is None:
            self = reportsView(reports)
        report = self.reports[self.page]
        user = report[2]
        reporter = report[3]
        reason = report[4]
        createdAt = report[5]
        accepted = report[6]
        acceptedAt = report[7]
        resolved = report[9]
        resolvedAt = report[10]

        locale = commandInfo.locale

        description = tanjunLocalizer.localize(
            locale,
            "commands.admin.reports.show_reports.report.description",
            user=user,
            reporter=reporter,
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


    await commandInfo.reply(embed=get_embed(), view=reportsView(reports))
