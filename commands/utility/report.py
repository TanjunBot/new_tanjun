"""Advanced Report System: submit reports with evidence, status transitions,
notifications, and anonymity support."""

from __future__ import annotations

import discord

from api import (
    check_if_reporter_is_blocked,
    get_report_channel,
    report_user,
)
from localizer import tanjunLocalizer
from services.report_service import report_service
from utility import CommandInfo, tanjunEmbed


async def report(
    command_info: CommandInfo,
    reason: str,
    user: discord.Member,
    attachment: discord.Attachment | None = None,
    anonymous: bool = False,
) -> None:
    """Submit a report with optional evidence and anonymity setting."""
    if command_info.guild is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "errors.guildOnly.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "errors.guildOnly.description"),
        )
        await command_info.reply(embed=embed)
        return

    guild = command_info.guild

    # Check if reporter is blocked
    if await check_if_reporter_is_blocked(guild.id, command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.blocked.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.blocked.description"),
        )
        await command_info.reply(embed=embed)
        return

    # Check report channel
    report_channel_info = await get_report_channel(guild.id)
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

    report_channel = guild.get_channel(int(report_channel_info))
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

    if not report_channel.permissions_for(guild.me).send_messages:
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

    # Apply guild anonymity default if user didn't specify
    if not anonymous:
        anonymous = await report_service.get_anonymity_setting(guild.id)

    is_mod = (
        isinstance(command_info.user, discord.Member)
        and command_info.user.guild_permissions.manage_messages
    )

    # Create the report
    report_id = await report_user(
        guild.id,
        user.id,
        command_info.user.id,
        reason,
        is_moderator=is_mod,
    )

    if report_id is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.report.invalid_action.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.utility.report.invalid_action.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    # Upload evidence if provided
    evidence_urls: list[str] = []
    if attachment:
        # Re-use embed endpoint to get a permanent URL
        evidence_embed = discord.Embed(title="Report Evidence")
        evidence_msg = await report_channel.send(embed=evidence_embed, file=await attachment.to_file())
        if evidence_msg.attachments:
            evidence_url = evidence_msg.attachments[0].url
            await report_service.add_evidence(
                guild.id,
                report_id,
                evidence_url,
                filename=attachment.filename,
                uploaded_by=str(command_info.user.id),
            )
            evidence_urls.append(evidence_url)
        await evidence_msg.delete()

    # Build the report channel embed
    reporter_mention = "Anonymous" if anonymous else command_info.user.mention
    embed_desc = tanjunLocalizer.localize(
        command_info.locale,
        "commands.utility.report.new_report.description",
        reason=reason,
        reporter=reporter_mention,
        user=user.mention,
    )

    if evidence_urls:
        embed_desc += f"\n\n📎 **Evidence:** {evidence_urls[0]}"

    if anonymous:
        embed_desc += f"\n\n🔒 **Note:** This report was submitted anonymously."

    # Build action buttons
    view = discord.ui.View()
    guild_locale = str(guild.preferred_locale)
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
            description=embed_desc,
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
    """Handle report button interactions (accept, reject, block, status transitions)."""
    parts = custom_id.split(";")
    report_action = parts[0]
    report_id = parts[1]
    reporter_id = parts[2] if len(parts) > 2 else ""
    note = parts[3] if len(parts) > 3 else None

    if isinstance(interaction.user, discord.User) or not interaction.channel or not interaction.guild:
        return

    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.no_permission.title"),
            description=tanjunLocalizer.localize(str(interaction.locale), "commands.utility.report.no_permission.description"),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    guild = interaction.guild
    locale = str(interaction.locale)
    mod_id = str(interaction.user.id)

    status_map = {
        "report_accept": "investigating",
        "report_reject": "dismissed",
        "report_resolve": "action_taken",
        "report_reopen": "pending",
    }

    if report_action in status_map:
        new_status = status_map[report_action]
        old_status = await report_service.update_status(
            guild.id, report_id, new_status, updated_by=mod_id, note=note
        )
        if old_status is None:
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(locale, "commands.utility.report.invalid_action.title"),
                description=tanjunLocalizer.localize(locale, "commands.utility.report.invalid_action.description"),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        status_labels = {
            "pending": "Pending",
            "investigating": "Investigating",
            "action_taken": "Action Taken",
            "dismissed": "Dismissed",
        }
        label = status_labels.get(new_status, new_status)

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, f"commands.utility.report.report_{report_action.split('_')[1]}_title"),
            description=f"Report status changed to **{label}**.",
        )
        await interaction.response.send_message(embed=embed)

        # Send DM notification to the reporter if not opted out
        if not await report_service.has_opted_out_of_notifications(guild.id, reporter_id):
            try:
                reporter_member = guild.get_member(int(reporter_id))
                if reporter_member:
                    dm_embed = discord.Embed(
                        title=f"Report #{report_id} Status Update",
                        description=f"Your report on **{guild.name}** has been updated to **{label}**.",
                        color=discord.Color.blue(),
                    )
                    if note:
                        dm_embed.add_field(name="Note", value=note, inline=False)
                    await reporter_member.send(embed=dm_embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

    elif report_action == "report_block_reporter":
        await report_service.block_reporter(guild.id, reporter_id)
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
