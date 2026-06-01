"""Advanced Report System: submit reports with evidence, status transitions,
notifications, and anonymity support."""
from __future__ import annotations

from locale_keys import locale
import discord
from api import check_if_reporter_is_blocked, get_report_channel, report_user
from services.report_service import report_service
from utility import CommandInfo, tanjunEmbed

async def report(command_info: CommandInfo, reason: str, user: discord.Member, attachment: discord.Attachment | None=None, anonymous: bool=False) -> None:
    """Submit a report with optional evidence and anonymity setting."""
    if command_info.guild is None:
        embed = tanjunEmbed(title=locale.errors.guildOnly.title(str(command_info.locale)), description=locale.errors.guildOnly.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    guild = command_info.guild
    if await check_if_reporter_is_blocked(guild.id, command_info.user.id):
        embed = tanjunEmbed(title=locale.commands.utility.report.blocked.title(str(command_info.locale)), description=locale.commands.utility.report.blocked.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    report_channel_info = await get_report_channel(guild.id)
    if not report_channel_info:
        embed = tanjunEmbed(title=locale.commands.utility.report.no_report_channel.title(str(command_info.locale)), description=locale.commands.utility.report.no_report_channel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    report_channel = guild.get_channel(int(report_channel_info))
    if not report_channel:
        embed = tanjunEmbed(title=locale.commands.utility.report.report_channel_not_found.title(command_info.locale), description=locale.commands.utility.report.report_channel_not_found.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(report_channel, (discord.ForumChannel, discord.CategoryChannel)):
        return
    if not report_channel.permissions_for(guild.me).send_messages:
        embed = tanjunEmbed(title=locale.commands.utility.report.no_permission.title(str(command_info.locale)), description=locale.commands.utility.report.no_permission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if not reason:
        embed = tanjunEmbed(title=locale.commands.utility.report.no_reason.title(str(command_info.locale)), description=locale.commands.utility.report.no_reason.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if len(reason) < 12:
        embed = tanjunEmbed(title=locale.commands.utility.report.reason_too_short.title(str(command_info.locale)), description=locale.commands.utility.report.reason_too_short.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not anonymous:
        anonymous = await report_service.get_anonymity_setting(guild.id)
    is_mod = isinstance(command_info.user, discord.Member) and command_info.user.guild_permissions.manage_messages
    report_id = await report_user(guild.id, user.id, command_info.user.id, reason, is_moderator=is_mod)
    if report_id is None:
        embed = tanjunEmbed(title=locale.commands.utility.report.invalid_action.title(str(command_info.locale)), description=locale.commands.utility.report.invalid_action.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    evidence_urls: list[str] = []
    if attachment:
        evidence_embed = discord.Embed(title='Report Evidence')
        evidence_msg = await report_channel.send(embed=evidence_embed, file=await attachment.to_file())
        if evidence_msg.attachments:
            evidence_url = evidence_msg.attachments[0].url
            await report_service.add_evidence(guild.id, report_id, evidence_url, filename=attachment.filename, uploaded_by=str(command_info.user.id))
            evidence_urls.append(evidence_url)
        await evidence_msg.delete()
    reporter_mention = 'Anonymous' if anonymous else command_info.user.mention
    embed_desc = locale.commands.utility.report.new_report.description(command_info.locale, reason=reason, reporter=reporter_mention, user=user.mention)
    if evidence_urls:
        embed_desc += f'\n\n📎 **Evidence:** {evidence_urls[0]}'
    if anonymous:
        embed_desc += '\n\n🔒 **Note:** This report was submitted anonymously.'
    view = discord.ui.View()
    guild_locale = str(guild.preferred_locale)
    accept_locale = locale.commands.utility.report.accept.label(guild_locale)
    view.add_item(discord.ui.Button(label=accept_locale, style=discord.ButtonStyle.success, custom_id=f'report_accept;{report_id};{command_info.user.id}'))
    reject_locale = locale.commands.utility.report.reject.label(guild_locale)
    view.add_item(discord.ui.Button(label=reject_locale, style=discord.ButtonStyle.danger, custom_id=f'report_reject;{report_id};{command_info.user.id}'))
    block_reporter_locale = locale.commands.utility.report.block_reporter.label(guild_locale)
    view.add_item(discord.ui.Button(label=block_reporter_locale, style=discord.ButtonStyle.danger, custom_id=f'report_block_reporter;{report_id};{command_info.user.id}'))
    await report_channel.send(embed=tanjunEmbed(title=locale.commands.utility.report.new_report.title(str(command_info.locale)), description=embed_desc), view=view)
    await command_info.reply(embed=tanjunEmbed(title=locale.commands.utility.report.report_sent.title(str(command_info.locale)), description=locale.commands.utility.report.report_sent.description(str(command_info.locale))))

async def report_btn_click(interaction: discord.Interaction, custom_id: str) -> None:
    """Handle report button interactions (accept, reject, block, status transitions)."""
    parts = custom_id.split(';')
    report_action = parts[0]
    report_id = parts[1]
    reporter_id = parts[2] if len(parts) > 2 else ''
    note = parts[3] if len(parts) > 3 else None
    if isinstance(interaction.user, discord.User) or not interaction.channel or (not interaction.guild):
        return
    if not interaction.channel.permissions_for(interaction.user).manage_messages:
        embed = tanjunEmbed(title=locale.commands.utility.report.no_permission.title(str(interaction.locale)), description=locale.commands.utility.report.no_permission.description(str(interaction.locale)))
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    guild = interaction.guild
    loc = str(interaction.locale)
    mod_id = str(interaction.user.id)
    status_map = {'report_accept': 'investigating', 'report_reject': 'dismissed', 'report_resolve': 'action_taken', 'report_reopen': 'pending'}
    if report_action in status_map:
        new_status = status_map[report_action]
        old_status = await report_service.update_status(guild.id, report_id, new_status, updated_by=mod_id, note=note)
        if old_status is None:
            embed = tanjunEmbed(title=locale.commands.utility.report.invalid_action.title(loc), description=locale.commands.utility.report.invalid_action.description(loc))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        status_labels = {'pending': 'Pending', 'investigating': 'Investigating', 'action_taken': 'Action Taken', 'dismissed': 'Dismissed'}
        label = status_labels.get(new_status, new_status)
        action = report_action.split('_')[1]
        if action == 'accept':
            title = locale.commands.utility.reports.report_accepted.title(loc)
            description = locale.commands.utility.reports.report_accepted.description(loc)
        elif action == 'reject':
            title = locale.commands.utility.reports.report_rejected.title(loc)
            description = locale.commands.utility.reports.report_rejected.description(loc)
        else:
            title = locale.commands.utility.report.invalid_action.title(loc)
            description = f'Report status changed to **{label}**.'
        embed = tanjunEmbed(title=title, description=description)
        await interaction.response.send_message(embed=embed)
        if not await report_service.has_opted_out_of_notifications(guild.id, reporter_id):
            try:
                reporter_member = guild.get_member(int(reporter_id))
                if reporter_member:
                    dm_embed = discord.Embed(title=f'Report #{report_id} Status Update', description=f'Your report on **{guild.name}** has been updated to **{label}**.', color=discord.Color.blue())
                    if note:
                        dm_embed.add_field(name='Note', value=note, inline=False)
                    await reporter_member.send(embed=dm_embed)
            except (discord.Forbidden, discord.HTTPException):
                pass
    elif report_action == 'report_block_reporter':
        await report_service.block_reporter(guild.id, reporter_id)
        embed = tanjunEmbed(title=locale.commands.utility.report.reporter_blocked.title(str(interaction.locale)), description=locale.commands.utility.report.reporter_blocked.description(str(interaction.locale)))
        await interaction.response.send_message(embed=embed)
    else:
        embed = tanjunEmbed(title=locale.commands.utility.report.invalid_action.title(str(interaction.locale)), description=locale.commands.utility.report.invalid_action.description(str(interaction.locale)))
        await interaction.response.send_message(embed=embed)
