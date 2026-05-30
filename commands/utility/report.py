import discord

from api import (
    accept_report,
    block_reporter,
    check_if_reporter_is_blocked,
    get_report_channel,
    reject_report,
    report_user,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def report(command_info: CommandInfo, reason: str, user: discord.Member) -> None:
    if command_info.guild is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "errors.guildOnly.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "errors.guildOnly.description"),
        )
        await command_info.reply(embed=embed)
        return

    if await check_if_reporter_is_blocked(command_info.guild.id, command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.blocked.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.blocked.description"),
        )
        await command_info.reply(embed=embed)
        return

    report_channel_info = await get_report_channel(command_info.guild.id)
    if not report_channel_info:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.no_report_channel.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.report.no_report_channel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    report_channel = command_info.guild.get_channel(int(report_channel_info))
    if not report_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.report.report_channel_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.report.report_channel_not_found.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(report_channel, (discord.ForumChannel, discord.CategoryChannel)):
        return

    if not report_channel.permissions_for(command_info.guild.me).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.no_permission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.utility.report.no_permission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not reason:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.no_reason.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.no_reason.description"),
        )
        await command_info.reply(embed=embed)
        return

    if len(reason) < 12:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.reason_too_short.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.report.reason_too_short.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    report_id = await report_user(
        command_info.guild.id,
        user.id,
        command_info.user.id,
        reason,
        command_info.user.guild_permissions.manage_messages if isinstance(command_info.user, discord.Member) else False,
    )

    view = discord.ui.View()
    guild_locale = str(command_info.guild.preferred_locale)
    accept_locale = tanjunLocalizer.localize(guild_locale, "commands.utility.report.accept.label")
    view.add_item(
        discord.ui.Button(
            label=accept_locale,
            style=discord.ButtonStyle.success,
            custom_id=f"report_accept;{report_id};{command_info.user.id}",
        )
    )
    reject_locale = tanjunLocalizer.localize(guild_locale, "commands.utility.report.reject.label")
    view.add_item(
        discord.ui.Button(
            label=reject_locale,
            style=discord.ButtonStyle.danger,
            custom_id=f"report_reject;{report_id};{command_info.user.id}",
        )
    )
    block_reporter_locale = tanjunLocalizer.localize(guild_locale, "commands.utility.report.block_reporter.label")
    view.add_item(
        discord.ui.Button(
            label=block_reporter_locale,
            style=discord.ButtonStyle.danger,
            custom_id=f"report_block_reporter;{report_id};{command_info.user.id}",
        )
    )

    await report_channel.send(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.new_report.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.report.new_report.description",
                reason=reason,
                reporter=command_info.user.mention,
                user=user.mention,
            ),
        ),
        view=view,
    )

    await command_info.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.report_sent.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.report_sent.description"),
        )
    )


async def report_btn_click(interaction: discord.Interaction, custom_id: str) -> None:
    report_action = custom_id.split(";")[0]
    reporter_id = custom_id.split(";")[2]
    report_id = custom_id.split(";")[1]
    if isinstance(interaction.user, discord.User) or not interaction.channel or not interaction.guild:
        return
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.no_permission.title"),
            description=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.no_permission.description"),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if report_action == "report_accept":
        await accept_report(interaction.guild.id, report_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.report_accepted.title"),
            description=tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.utility.report.report_accepted.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    elif report_action == "report_reject":
        await reject_report(interaction.guild.id, report_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.report_rejected.title"),
            description=tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.utility.report.report_rejected.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    elif report_action == "report_block_reporter":
        await block_reporter(interaction.guild.id, reporter_id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.reporter_blocked.title"),
            description=tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.utility.report.reporter_blocked.description",
            ),
        )
        await interaction.response.send_message(embed=embed)

    else:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.invalid_action.title"),
            description=tanjunLocalizer.localize(
                str(interaction.locale), "commands.utility.report.invalid_action.description"
            ),
        )
        await interaction.response.send_message(embed=embed)
