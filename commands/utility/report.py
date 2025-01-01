from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
import discord
from api import (
    check_if_reporter_is_blocked,
    get_report_channel,
    report_user,
    accept_report,
    reject_report,
    block_reporter,
)


async def report(commandInfo: commandInfo, reason: str, user: discord.Member):
    if await check_if_reporter_is_blocked(commandInfo.guild.id, commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.blocked.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.blocked.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    report_channel = await get_report_channel(commandInfo.guild.id)
    if not report_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.no_report_channel.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.report.no_report_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    report_channel = commandInfo.guild.get_channel(int(report_channel[0]))
    if not report_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.report.report_channel_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.report.report_channel_not_found.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not report_channel.permissions_for(commandInfo.guild.me).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.no_permission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not reason:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.no_reason.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.no_reason.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if len(reason) < 12:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.reason_too_short.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.report.reason_too_short.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    report_id = await report_user(
        commandInfo.guild.id,
        user.id,
        commandInfo.user.id,
        reason,
        commandInfo.user.guild_permissions.manage_messages,
    )

    view = discord.ui.View()
    guild_locale = (
        commandInfo.guild.preferred_locale
        if commandInfo.guild.preferred_locale
        else "en_US"
    )
    accept_locale = tanjunLocalizer.localize(
        guild_locale, "commands.utility.report.accept.label"
    )
    view.add_item(
        discord.ui.Button(
            label=accept_locale,
            style=discord.ButtonStyle.success,
            custom_id=f"report_accept;{report_id};{commandInfo.user.id}",
        )
    )
    reject_locale = tanjunLocalizer.localize(
        guild_locale, "commands.utility.report.reject.label"
    )
    view.add_item(
        discord.ui.Button(
            label=reject_locale,
            style=discord.ButtonStyle.danger,
            custom_id=f"report_reject;{report_id};{commandInfo.user.id}",
        )
    )
    block_reporter_locale = tanjunLocalizer.localize(
        guild_locale, "commands.utility.report.block_reporter.label"
    )
    view.add_item(
        discord.ui.Button(
            label=block_reporter_locale,
            style=discord.ButtonStyle.danger,
            custom_id=f"report_block_reporter;{report_id};{commandInfo.user.id}",
        )
    )

    await report_channel.send(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.new_report.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.report.new_report.description",
                reason=reason,
                reporter=commandInfo.user.mention,
                user=user.mention,
            ),
        ),
        view=view,
    )

    await commandInfo.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.report_sent.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.report.report_sent.description"
            ),
        )
    )


async def report_btn_click(interaction: discord.Interaction, custom_id: str):
    report_action = custom_id.split(";")[0]
    reporter_id = custom_id.split(";")[2]
    report_id = custom_id.split(";")[1]
    if not interaction.user.guild_permissions.manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.no_permission.description"
            ),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if report_action == "report_accept":
        await accept_report(interaction.guild.id, report_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.report_accepted.title"
            ),
            description=tanjunLocalizer.localize(
                interaction.locale,
                "commands.utility.report.report_accepted.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    elif report_action == "report_reject":
        await reject_report(interaction.guild.id, report_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.report_rejected.title"
            ),
            description=tanjunLocalizer.localize(
                interaction.locale,
                "commands.utility.report.report_rejected.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    elif report_action == "report_block_reporter":
        await block_reporter(interaction.guild.id, reporter_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.reporter_blocked.title"
            ),
            description=tanjunLocalizer.localize(
                interaction.locale,
                "commands.utility.report.reporter_blocked.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.invalid_action.title"
            ),
            description=tanjunLocalizer.localize(
                interaction.locale, "commands.utility.report.invalid_action.description"
            ),
        )
        await interaction.response.send_message(embed=embed)
