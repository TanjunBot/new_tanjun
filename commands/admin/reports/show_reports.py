from locale_keys import locale
from typing import Any
import discord
import utility
from api import block_reporter, check_if_reporter_is_blocked, delete_report, get_reports, unblock_reporter
from models import ReportModel

async def show_reports(command_info: utility.CommandInfo, user: discord.Member | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_guild):
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.show_reports.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.reports.show_reports.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    reports = await get_reports(command_info.guild.id, user.id if user else None)
    if not reports:
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.show_reports.noReports.title(str(command_info.locale)), description=locale.commands.admin.reports.show_reports.noReports.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return

    async def checkIfCurrentReporterIsBlocked(reports: list[ReportModel], page: int) -> bool:
        assert command_info.guild is not None
        return bool(await check_if_reporter_is_blocked(command_info.guild.id, str(reports[page].reporter_id)))
    current_reporter_is_blocked = await checkIfCurrentReporterIsBlocked(reports, 0)

    class ReportsView(discord.ui.View):

        def __init__(self, reports: list[ReportModel], page: int=0) -> None:
            super().__init__()
            self.reports = reports
            self.page = page
            self.update_buttons()

        def update_buttons(self) -> None:
            self.previous.disabled = len(self.reports) <= 1
            self.next.disabled = len(self.reports) <= 1

        @discord.ui.button(label=locale.commands.admin.reports.show_reports.previous.label(str(command_info.locale)), style=discord.ButtonStyle.secondary, emoji='⬅️')
        async def previous(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.admin.reports.show_reports.not_your_reports(command_info.locale), ephemeral=True)
                return
            self.page -= 1
            if self.page < 0:
                self.page = len(self.reports) - 1
            await interaction.response.edit_message(view=self, embed=self.get_embed())

        @discord.ui.button(label=locale.commands.admin.reports.show_reports.remove.label(str(command_info.locale)), style=discord.ButtonStyle.danger, emoji='🗑️')
        async def remove(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.admin.reports.show_reports.not_your_reports(command_info.locale), ephemeral=True)
                return
            await delete_report(command_info.guild.id, self.reports[self.page].id)
            self.reports.pop(self.page)
            if len(self.reports) == 0:
                embed = utility.tanjunEmbed(title=locale.commands.admin.reports.show_reports.noReports.title(command_info.locale), description=locale.commands.admin.reports.show_reports.noReports.description(command_info.locale))
                await interaction.response.edit_message(embed=embed, view=None)
                return
            if self.page >= len(self.reports):
                self.page = len(self.reports) - 1
            await interaction.response.edit_message(view=self, embed=self.get_embed())
        if not current_reporter_is_blocked:

            @discord.ui.button(label=locale.commands.admin.reports.show_reports.block.label(command_info.locale), style=discord.ButtonStyle.danger, emoji='🚫')
            async def block(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
                if interaction.user.id != command_info.user.id:
                    await interaction.response.send_message(locale.commands.admin.reports.show_reports.not_your_reports(command_info.locale), ephemeral=True)
                    return
                await block_reporter(command_info.guild.id, self.reports[self.page].reporter_id)
                await interaction.response.edit_message(view=ReportsView(reports, self.page), embed=self.get_embed())
        else:

            @discord.ui.button(label=locale.commands.admin.reports.show_reports.unblock.label(command_info.locale), style=discord.ButtonStyle.success, emoji='🔓')
            async def unblock(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
                if interaction.user.id != command_info.user.id:
                    await interaction.response.send_message(locale.commands.admin.reports.show_reports.not_your_reports(command_info.locale), ephemeral=True)
                    return
                await unblock_reporter(command_info.guild.id, self.reports[self.page].reporter_id)
                nonlocal current_reporter_is_blocked
                current_reporter_is_blocked = await checkIfCurrentReporterIsBlocked(reports, self.page)
                await interaction.response.edit_message(view=ReportsView(reports, self.page), embed=self.get_embed())

        @discord.ui.button(label=locale.commands.admin.reports.show_reports.next.label(str(command_info.locale)), style=discord.ButtonStyle.secondary, emoji='➡️')
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.admin.reports.show_reports.not_your_reports(command_info.locale), ephemeral=True)
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
            created_at = str(report.created_at)
            status = str(report.status)
            accepted = bool(report.accepted)
            accepted_at = str(report.accepted_at)
            resolved = bool(report.resolved)
            resolved_at = str(report.resolved_at)
            locale = str(command_info.locale)
            description = locale.commands.admin.reports.show_reports.report.description(locale, user=user_str, reporter=reporter_str, reason=reason, created_at=created_at)
            description += '\n' + locale.commands.admin.reports.show_reports.report.status(locale, status=status)
            if accepted:
                description += '\n' + locale.commands.admin.reports.show_reports.report.accepted(locale, accepted_at=accepted_at)
            else:
                description += '\n' + locale.commands.admin.reports.show_reports.report.not_accepted(locale)
            if resolved:
                description += '\n' + locale.commands.admin.reports.show_reports.report.resolved(locale, resolved_at=resolved_at)
            else:
                description += '\n' + locale.commands.admin.reports.show_reports.report.not_resolved(locale)
            embed = utility.tanjunEmbed(title=locale.commands.admin.reports.show_reports.report.title(locale, index=self.page + 1, total=len(self.reports)), description=description)
            return embed
    view = ReportsView(reports)
    await command_info.reply(embed=view.get_embed(), view=view)