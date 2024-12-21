import discord
import utility
from localizer import tanjunLocalizer
from api import close_ticket, get_ticket_by_id, get_ticket_messages_by_id
import datetime


async def close_ticket(interaction: discord.Interaction):
    if not interaction.data["custom_id"].startswith("ticket_close;"):
        return

    await interaction.response.defer()

    ticket_id, ticket_channel_id = (
        interaction.data["custom_id"].split(";")[1],
        interaction.data["custom_id"].split(";")[2],
    )

    ticket_message = await get_ticket_messages_by_id(ticket_id)
    if not ticket_message:
        await interaction.followup.send(
            tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.error.ticketNotFound1",
            )
        )
        return

    ticket = await get_ticket_by_id(interaction.guild.id, ticket_id, ticket_channel_id)

    print("ticket", ticket)
    print("interaction.guild.id", interaction.guild.id)
    print("ticket_id", ticket_id)
    if not ticket:
        await interaction.followup.send(
            tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.error.ticketNotFound2",
            )
        )
        return

    ticket_channel = interaction.channel

    print("ticket_channel", ticket_channel)
    print("ticket_channel.id", ticket_channel.id)

    if not ticket_channel.id == int(ticket[6]):
        await interaction.followup.send(
            tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.error.ticketNotFound3",
            )
        )
        return

    ticket_opener = ticket[1]
    ticket_opener_user = await interaction.guild.fetch_member(ticket_opener)

    ticket_open_time = ticket[2]

    print("ticket_message", ticket_message)

    summary_channel_id = int(ticket_message[7]) if ticket_message[7] else None
    print("summary_channel_id", summary_channel_id)
    summary_channel = interaction.guild.get_channel(summary_channel_id)

    print("summary_channel", summary_channel)

    if not summary_channel:
        await interaction.channel.edit(archived=True, locked=True)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.success.ticketClosed",
            ),
            description=tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.success.ticketClosedDescription",
            ),
        )
        await interaction.channel.send(embed=embed)
    else:
        html_content = await generate_summary_html(
            interaction.channel, ticket_opener_user, ticket_open_time
        )

        url = await utility.upload_to_tanjun_logs(html_content)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.success.ticketClosed",
            ),
            description=tanjunLocalizer.localize(
                interaction.locale,
                "commands.admin.close_ticket.success.ticketClosedDescription",
            ),
        )

        view = discord.ui.View()
        btn1 = discord.ui.Button(label=tanjunLocalizer.localize(interaction.locale, "commands.admin.close_ticket.success.viewOnlineSummary"), url=url)
        view.add_item(btn1)
        btn2 = discord.ui.Button(label=tanjunLocalizer.localize(interaction.locale, "commands.admin.close_ticket.success.viewThread"), url=f"https://discord.com/channels/{interaction.guild.id}/{ticket_channel.id}")
        view.add_item(btn2)

        await summary_channel.send(
            content=tanjunLocalizer.localize(interaction.locale, "commands.admin.close_ticket.success.ticketClosed", user=interaction.user.mention),
            embed=embed,
            view=view
        )

        await interaction.channel.edit(archived=True, locked=True)
        
        await interaction.channel.send(
            content=tanjunLocalizer.localize(interaction.locale, "commands.admin.close_ticket.success.ticketClosed", user=interaction.user.mention),
        )

async def generate_summary_html(
    channel: discord.abc.GuildChannel,
    ticket_opener_user: discord.Member,
    ticket_open_time: datetime.datetime,
):
    locale = (
        str(channel.guild.preferred_locale) if channel.guild.preferred_locale else "en"
    )
    html = """
<!DOCTYPE html>
<html lang="en">

<head>
   <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """

    html += f"""
    <title>{channel.name} - Ticket Transcript</title>
    """

    html += """
    <link rel="apple-touch-icon" sizes="180x180" href="https://static.tanjun.bot/favicons/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="https://static.tanjun.bot/favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="https://static.tanjun.bot/favicons/favicon-16x16.png">
    <link rel="manifest" href="https://static.tanjun.bot/favicons/site.webmanifest">
    <link href="https://static.tanjun.bot/fonts/Roboto" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px 0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            transition: background 0.5s, color 0.5s;
        }

        .container {
            width: 90%;
            max-width: 800px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .ticket-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 100%;
        }

        .chat-container {
            width: 100%;
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
        }

        .search-bar {
            padding: 15px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .search-bar input {
            width: 80%;
            padding: 10px;
            border-radius: 20px;
            border: none;
            outline: none;
            font-size: 16px;
        }

        .messages {
            overflow-y: auto;
            flex-grow: 1;
        }

        .message {
            display: flex;
            align-items: flex-start;
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.3s, color 0.3s;
        }

        .message:hover {
            background-color: rgba(255, 255, 255, 0.2);
            color: inherit;
        }

        .message:last-child {
            border-bottom: none;
        }

        .profile-picture {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            margin-right: 15px;
            object-fit: cover;
        }

        .message-content {
            max-width: 80%;
        }

        .username {
            font-weight: 700;
            font-size: 16px;
        }

        .name {
            font-size: 14px;
        }

        .text {
            margin-top: 5px;
            font-size: 15px;
            line-height: 1.6;
        }

        .light {
            background: linear-gradient(160deg, #f0f2f5, #e0e0e0, #c0c0c0, #a0a0a0);
            color: #333;
        }

        .dark {
            background: linear-gradient(145deg, #232526, #414345, #2c3e50, #1b1b1b);
            color: #f0f2f5;
        }

        .midnight {
            background: linear-gradient(150deg, #2c3e50, #4ca1af, #1e3c72, #0f2027);
            color: #ecf0f1;
        }

        .pink {
            background: linear-gradient(155deg, #ff6f91, #ff9671, #ff9a9e, #ff6f91);
            color: #fff;
        }

        .red {
            background: linear-gradient(140deg, #e74c3c, #ff6b6b, #ff8c8c, #ff4e50);
            color: #fff;
        }

        .fire {
            background: linear-gradient(165deg, #ff512f, #dd2476, #ff7e5f, #ff512f);
            color: #fff;
        }

        .underwater {
            background: linear-gradient(170deg, #36d1dc, #5b86e5, #00c6ff, #0072ff);
            color: #fff;
        }

        .neonNight {
            background: linear-gradient(175deg, #000000, #434343, #1f1f1f, #0f0f0f);
            color: #39ff14;
        }

        .highContrastDark {
            background: #000;
            color: #fff;
        }

        .highContrastLight {
            background: #fff;
            color: #000;
        }

        @media (max-width: 600px) {
            .chat-container {
                width: 100%;
                max-height: 100vh;
                border-radius: 0;
            }

            .search-bar input {
                width: 90%;
                font-size: 14px;
            }

            .message {
                padding: 10px;
            }

            .profile-picture {
                width: 40px;
                height: 40px;
                margin-right: 10px;
            }

            .username {
                font-size: 14px;
            }

            .name {
                font-size: 12px;
            }

            .text {
                font-size: 13px;
            }
        }

        .search-bar select {
            padding: 10px;
            border-radius: 20px;
            border: 1px solid #ccc;
            background-color: #fff;
            font-size: 16px;
            margin-bottom: 10px;
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        .search-bar select:focus {
            border-color: #007bff;
            box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
        }

        .light .message:hover {
            color: #333;
        }

        .dark .message:hover,
        .midnight .message:hover,
        .red .message:hover,
        .fire .message:hover,
        .neonNight .message:hover {
            color: #fff;
        }

        .highContrastDark .message:hover {
            color: #fff;
        }

        .highContrastLight .message:hover {
            color: #000;
        }

        .embed {
            border-left: 4px solid #7289da;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            position: relative;
        }

        .light .embed {
            background-color: rgba(255, 255, 255, 0.9);
            color: #333;
        }

        .dark .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .midnight .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .pink .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .red .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .fire .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .underwater .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .neonNight .embed {
            background-color: #2f3136;
            color: #fff;
        }

        .highContrastDark .embed {
            background-color: #000;
            color: #fff;
        }

        .highContrastLight .embed {
            background-color: #fff;
            color: #000;
        }

        .embed-thumbnail {
            position: absolute;
            top: 10px;
            right: 10px;
        }

        .embed-thumbnail-image {
            width: 50px;
            height: 50px;
            border-radius: 5px;
        }

        .embed-title {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
        }

        .embed-description {
            font-size: 14px;
            margin-bottom: 10px;
        }

        .embed-fields {
            display: flex;
            flex-wrap: wrap;
        }

        .embed-field {
            flex: 1;
            min-width: 150px;
            margin-right: 10px;
            margin-bottom: 10px;
        }

        .embed-field-name {
            font-weight: bold;
            font-size: 14px;
        }

        .embed-field-value {
            font-size: 14px;
        }

        .embed-image {
            margin-top: 10px;
            text-align: center;
        }

        .embed-large-image {
            max-width: 100%;
            border-radius: 5px;
        }

        .embed-footer {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }

        .embed-footer-icon {
            width: 20px;
            height: 20px;
            margin-right: 5px;
        }

        .embed-footer-text {
            font-size: 12px;
            color: #b9bbbe;
        }

        .emoji {
            max-width: 32px;
            max-height: 32px;
            width: auto;
            height: auto;
            vertical-align: middle;
        }

        .role-mention {
            color: #00b0f4;
            background-color: rgba(0, 176, 244, 0.1);
            padding: 0 2px;
            border-radius: 3px;
            font-weight: 500;
            cursor: pointer;
        }

        .role-mention:hover {
            background-color: rgba(114, 137, 218, 0.2);
            text-decoration: underline;
        }

        .role-popover {
            background: rgba(30, 33, 36, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            min-width: 250px;
            animation: popoverFadeIn 0.2s ease-out;
            color: #fff;
        }

        @keyframes popoverFadeIn {
            from {
                opacity: 0;
                transform: scale(0.95) translateY(-5px);
            }

            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        .role-popover-header {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .role-popover-title {
            font-size: 16px;
            font-weight: 600;
            color: #fff;
            margin: 0;
        }

        .role-popover-section {
            margin: 8px 0;
        }

        .role-popover-label {
            font-size: 12px;
            text-transform: uppercase;
            color: #b9bbbe;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }

        .role-popover-value {
            font-size: 14px;
            color: #fff;
            line-height: 1.4;
        }

        .role-member-list {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }

        .role-member {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 13px;
        }

        .role-permission {
            display: inline-block;
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 12px;
            margin: 2px;
            font-size: 13px;
        }

        .light .role-popover {
            background: rgba(255, 255, 255, 0.95);
            border-color: rgba(0, 0, 0, 0.1);
            color: #2f3136;
        }

        .light .role-popover-title {
            color: #2f3136;
        }

        .light .role-popover-label {
            color: #4f545c;
        }

        .light .role-popover-value {
            color: #2f3136;
        }

        .light .role-member,
        .light .role-permission {
            background: rgba(0, 0, 0, 0.1);
        }

        .neonNight .role-popover {
            background: rgba(0, 0, 0, 0.95);
            border-color: #39ff14;
            box-shadow: 0 0 20px rgba(57, 255, 20, 0.3);
        }

        .neonNight .role-popover-title {
            color: #39ff14;
        }

        .neonNight .role-member,
        .neonNight .role-permission {
            background: rgba(57, 255, 20, 0.1);
            border: 1px solid rgba(57, 255, 20, 0.3);
        }

        .user-mention {
            color: #00b0f4;
            background-color: rgba(0, 176, 244, 0.1);
            padding: 0 2px;
            border-radius: 3px;
            font-weight: 500;
            cursor: pointer;
        }

        .user-mention:hover {
            background-color: rgba(114, 137, 218, 0.2);
        }

        .user-popover {
            background: rgba(30, 33, 36, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            min-width: 250px;
            animation: popoverFadeIn 0.2s ease-out;
            color: #fff;
        }

        .user-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 12px;
        }

        .user-info {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .user-name {
            font-size: 20px;
            font-weight: 600;
        }

        .user-tag {
            color: #b9bbbe;
            font-size: 14px;
        }

        .user-roles {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-top: 8px;
        }

        .user-role {
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
        }

        .channel-mention {
            color: #7289da;
            background-color: rgba(114, 137, 218, 0.1);
            padding: 0 2px;
            border-radius: 3px;
            font-weight: 500;
            cursor: pointer;
        }

        .channel-mention:hover {
            background-color: rgba(114, 137, 218, 0.2);
            text-decoration: underline;
        }

        .user-mention {
            color: #7289da;
            background-color: rgba(114, 137, 218, 0.1);
            padding: 0 2px;
            border-radius: 3px;
            font-weight: 500;
            cursor: pointer;
        }

        .user-mention:hover {
            background-color: rgba(114, 137, 218, 0.2);
            text-decoration: underline;
        }

        .channel-popover {
            background: rgba(30, 33, 36, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            min-width: 280px;
            animation: popoverFadeIn 0.2s ease-out;
            color: #fff;
        }

        .channel-popover-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .channel-icon {
            font-size: 24px;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
        }

        .channel-info {
            flex: 1;
        }

        .channel-popover-title {
            margin: 0;
            font-size: 16px;
            font-weight: 600;
            color: #fff;
        }

        .channel-type {
            font-size: 12px;
            color: #b9bbbe;
            margin-top: 4px;
        }

        .channel-topic {
            margin-bottom: 16px;
        }

        .topic-label {
            font-size: 12px;
            text-transform: uppercase;
            color: #b9bbbe;
            margin-bottom: 4px;
            letter-spacing: 0.5px;
        }

        .topic-content {
            font-size: 14px;
            line-height: 1.4;
            color: #dcddde;
        }

        .channel-stats {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .stat-icon {
            font-size: 16px;
        }

        .stat-value {
            font-size: 14px;
            color: #b9bbbe;
        }

        .channel-actions {
            display: flex;
            gap: 8px;
        }

        .action-button {
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: background-color 0.2s;
        }

        .action-button.primary {
            background-color: #5865f2;
            color: white;
        }

        .action-button.primary:hover {
            background-color: #4752c4;
        }

        .action-button.secondary {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .action-button.secondary:hover {
            background-color: rgba(255, 255, 255, 0.15);
        }

        /* Theme-specific styles */
        .light .channel-popover {
            background: rgba(255, 255, 255, 0.95);
            border-color: rgba(0, 0, 0, 0.1);
            color: #2f3136;
        }

        .light .channel-popover-title {
            color: #2f3136;
        }

        .light .channel-type,
        .light .topic-label,
        .light .stat-value {
            color: #4f545c;
        }

        .light .topic-content {
            color: #2e3338;
        }

        @keyframes popoverFadeIn {
            from {
                opacity: 0;
                transform: scale(0.95) translateY(-5px);
            }

            to {
                opacity: 1;
                transform: scale(1) translateY(0);
            }
        }

        .role-mention,
        .user-mention,
        .channel-mention {
            cursor: pointer;
            padding: 0 4px;
            border-radius: 3px;
            font-weight: 500;
            display: inline-block;
        }

        .user-mention {
            background-color: rgba(88, 101, 242, 0.15);
            color: var(--brand);
        }

        .channel-mention {
            background-color: rgba(35, 165, 89, 0.15);
            color: var(--brand);
        }

        .role-mention:hover,
        .user-mention:hover,
        .channel-mention:hover {
            opacity: 0.8;
        }

        .ticket-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .ticket-title {
            font-size: 2.5em;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(135deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .ticket-info {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1em;
            margin-top: 10px;
        }

        .ticket-info .user-mention {
            background-color: rgba(88, 101, 242, 0.15);
            color: #fff;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 500;
            display: inline-block;
        }
    </style>
</head>

<body class="fire">
    <div class="container">
    """
    html += f"""
        <div class="ticket-header">
            <h1 class="ticket-title" data-ticket-number="{channel.name}"></h1>
            <div class="ticket-info">
                <span class="ticket-created-by"></span> <span class="user-mention" data-user-id="1"
                    onclick="showTitleUserPopover(event, this)">@{ticket_opener_user.name}</span> <span class="ticket-created-at"></span>
                {ticket_open_time}
            </div>
        </div>
        <div class="chat-container">
            <div class="search-bar">
                <select id="languageSelector" onchange="updateLocalization()">
    """

    html += f"""
                <option value="en" {"selected" if locale == "en-US" or locale == "en-GB" else ""} >English</option>
                <option value="bg" {"selected" if locale == "bg" else ""} >Български</option>
                <option value="zh-CN" {"selected" if locale == "zh-CN" else ""} >中文 (简体)</option>
                <option value="zh-TW" {"selected" if locale == "zh-TW" else ""} >中文 (繁體)</option>
                <option value="hr" {"selected" if locale == "hr" else ""} >Hrvatski</option>
                <option value="cs" {"selected" if locale == "cs" else ""} >Čeština</option>
                <option value="id" {"selected" if locale == "id" else ""} >Bahasa Indonesia</option>
                <option value="da" {"selected" if locale == "da" else ""} >Dansk</option>
                <option value="nl" {"selected" if locale == "nl" else ""} >Nederlands</option>
                <option value="fi" {"selected" if locale == "fi" else ""} >Suomi</option>
                <option value="fr" {"selected" if locale == "fr" else ""} >Français</option>
                <option value="de" {"selected" if locale == "de" else ""} >Deutsch</option>
                <option value="el" {"selected" if locale == "el" else ""} >Ελληνικά</option>
                <option value="hi" {"selected" if locale == "hi" else ""} >हिन्दी</option>
                <option value="hu" {"selected" if locale == "hu" else ""} >Magyar</option>
                <option value="it" {"selected" if locale == "it" else ""} >Italiano</option>
                <option value="ja" {"selected" if locale == "ja" else ""} >日本語</option>
                <option value="ko" {"selected" if locale == "ko" else ""} >한국어</option>
                <option value="es-419" {"selected" if locale == "es-419" else ""} >Español (Latinoamérica)</option>
                <option value="lt" {"selected" if locale == "lt" else ""} >Lietuvių</option>
                <option value="no" {"selected" if locale == "no" else ""} >Norsk</option>
                <option value="pl" {"selected" if locale == "pl" else ""} >Polski</option>
                <option value="pt-BR" {"selected" if locale == "pt-BR" else ""} >Português (Brasil)</option>
                <option value="ro" {"selected" if locale == "ro" else ""} >Română</option>
                <option value="ru" {"selected" if locale == "ru" else ""} >Русский</option>
                <option value="es-ES" {"selected" if locale == "es-ES" else ""} >Español (España)</option>
                <option value="sv-SE" {"selected" if locale == "sv-SE" else ""} >Svenska</option>
                <option value="th" {"selected" if locale == "th" else ""} >ไทย</option>
                <option value="tr" {"selected" if locale == "tr" else ""} >Türkçe</option>
                <option value="uk" {"selected" if locale == "uk" else ""} >Українська</option>
                <option value="vi" {"selected" if locale == "vi" else ""} >Tiếng Việt</option>
                </select>
                <select id="themeSelector" onchange="changeTheme()">
                </select>
                <input type="text" id="searchInput" placeholder="" onkeyup="searchMessages()">
            </div>
            <div class="messages">
"""
    mentioned_roles = []
    mentioned_users = []
    mentioned_channels = []
    async for message in channel.history(limit=42069, oldest_first=True):
        if message.content == "" and len(message.embeds) == 0:
            continue
        html += '<div class="message">'
        html += f'<img src="{message.author.display_avatar.url}" alt="Profile Picture" class="profile-picture">'
        html += f'<div class="message-content">'
        html += f'<div class="username">{message.author.name}</div>'
        html += f'<div class="name">{message.author.name}</div>'
        html += f'<div class="text">{message.content}</div>'
        for embed in message.embeds:
            html += f'<div class="embed" style="border-left-color: {embed.color if embed.color else "#ff4500"}">'
            if embed.thumbnail:
                html += f'<div class="embed-thumbnail"><img src="{embed.thumbnail.url}" alt="Thumbnail" class="embed-thumbnail-image"></div>'
            if embed.title:
                html += f'<div class="embed-title">{embed.title}</div>'
            if embed.description:
                html += f'<div class="embed-description">{embed.description}</div>'
            if embed.fields:
                html += '<div class="embed-fields">'
                for field in embed.fields:
                    html += f'<div class="embed-field"><div class="embed-field-name">{field.name}</div><div class="embed-field-value">{field.value}</div></div>'
                html += "</div>"
            if embed.image:
                html += f'<div class="embed-image"><img src="{embed.image.url}" alt="Large Image" class="embed-large-image"></div>'
            if embed.footer:
                if embed.footer.icon_url:
                    html += f'<div class="embed-footer"><img src="{embed.footer.icon_url}" alt="Footer Icon" class="embed-footer-icon"><span class="embed-footer-text">{embed.footer.text}</span></div>'
                else:
                    html += f'<div class="embed-footer"><span class="embed-footer-text">{embed.footer.text}</span></div>'
            html += "</div>"

        html += "</div></div>"

        mentioned_roles.extend(message.role_mentions)
        mentioned_users.extend(message.mentions)
        mentioned_channels.extend(message.channel_mentions)

    html += """
        </div>

        <script>
        """

    roleJsObject = ""

    for role in mentioned_roles:
        members = []
        for member in role.members:
            members.append(str(member.id))
        permissions = []
        for permission, _ in iter(role.permissions):
            permissions.append(permission)
        roleJsObject += f"""
        {{
            id: '{str(role.id)}',
            name: '{role.name}',
            color: '{role.color}',
            members: {members},
            permissions: {permissions}
        }},
        """

    html += f"""
            const roles = [
                {roleJsObject}
            ];
            """

    channelJsObject = ""

    for channel in mentioned_channels:
        channelJsObject += f"""
        {{
            id: '{channel.id}',
            name: '{channel.name}',
            url: '{channel.jump_url}',
            type: '{channel.type}',
            topic: '{channel.topic}',
        }},
        """

    html += f"""
            const channels = [
                {channelJsObject}
            ];
    """

    userJsObject = ""

    for user in mentioned_users:
        roles = []
        for role in user.roles:
            roles.append(str(role.id))
        userJsObject += f"""
        {{
            id: '{str(user.id)}',
            displayname: '{user.display_name}',
            username: '{user.name}',
            avatar: '{user.avatar}',
            status: '{user.status}',
            roles: {roles},
            createdAt: '{user.created_at}',
        }},
        """

    html += f"""
            const users = [
                {userJsObject}
            ];
    """

    html += """
            const translations = {
                en: {
                    themes: {
                        light: "Light",
                        dark: "Dark",
                        midnight: "Midnight",
                        pink: "Pink",
                        red: "Red",
                        fire: "Fire",
                        underwater: "Underwater",
                        neonNight: "Neon Night",
                        highContrastDark: "High Contrast Dark",
                        highContrastLight: "High Contrast Light"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Created by",
                        at: "at"
                    },
                    searchPlaceholder: "Search messages or senders",
                    popover: {
                        members: "Members",
                        permissions: "Permissions"
                    },
                    channelPopover: {
                        viewChannel: "View Channel",
                        topic: "Topic",
                        typeChannel: "Channel"
                    },
                    permissions: {
                        add_reaction: "Add Reaction",
                        administrator: "Administrator",
                        attach_files: "Attach Files",
                        ban_members: "Ban Members",
                        change_nickname: "Change Nickname",
                        connect: "Connect",
                        create_events: "Create Events",
                        create_expressions: "Create Expressions",
                        create_instant_invite: "Create Instant Invite",
                        create_polls: "Create Polls",
                        create_private_threads: "Create Private Threads",
                        create_public_threads: "Create Public Threads",
                        deafen_members: "Deafen Members",
                        embed_links: "Embed Links",
                        external_emojis: "Use External Emojis",
                        external_stickers: "Use External Stickers",
                        kick_members: "Kick Members",
                        manage_channels: "Manage Channels",
                        manage_emojis: "Manage Emojis",
                        manage_stickers: "Manage Stickers",
                        manage_emojis_and_stickers: "Manage Emojis and Stickers",
                        manage_events: "Manage Events",
                        manage_expressions: "Manage Expressions",
                        manage_guild: "Manage Server",
                        manage_messages: "Manage Messages",
                        manage_nicknames: "Manage Nicknames",
                        manage_permissions: "Manage Permissions",
                        manage_roles: "Manage Roles",
                        manage_threads: "Manage Threads",
                        manage_webhooks: "Manage Webhooks",
                        mention_everyone: "Mention Everyone",
                        moderate_members: "Moderate Members",
                        move_members: "Move Members",
                        mute_members: "Mute Members",
                        priority_speaker: "Priority Speaker",
                        read_message_history: "Read Message History",
                        read_messages: "Read Messages",
                        request_to_speak: "Request to Speak",
                        send_messages: "Send Messages",
                        send_messages_in_threads: "Send Messages in Threads",
                        send_polls: "Send Polls",
                        send_tts_messages: "Send TTS Messages",
                        send_voice_messages: "Send Voice Messages",
                        speak: "Speak",
                        stream: "Stream",
                        use_application_commands: "Use Application Commands",
                        use_embedded_activities: "Use Embedded Activities",
                        use_external_apps: "Use External Apps",
                        use_external_emojis: "Use External Emojis",
                        use_external_sounds: "Use External Sounds",
                        use_external_stickers: "Use External Stickers",
                        use_soundboard: "Use Soundboard",
                        use_voice_activation: "Use Voice Activation",
                        view_audit_log: "View Audit Log",
                        view_channel: "View Channel",
                        view_creator_monetization_analytics: "View Creator Monetization Analytics",
                        view_guild_insights: "View Server Insights",
                        userPopover: {
                            memberSince: "Member since"
                        }
                    }
                },
                bg: {
                    themes: {
                        light: "Светъл",
                        dark: "Тъмно",
                        midnight: "Полунощ",
                        pink: "Розов",
                        red: "Червен",
                        fire: "Огън",
                        underwater: "Под вода",
                        neonNight: "Неонова нощ",
                        highContrastDark: "Висок контраст тъмен",
                        highContrastLight: "Висок контраст светъл"
                    },
                    ticket: {
                        title: "Билет {number}",
                        createdBy: "Създаден от",
                        at: "в"
                    },
                    searchPlaceholder: "Търсене на съощения или податели",
                    popover: {
                        members: "Членове",
                        permissions: "Права"
                    },
                    channelPopover: {
                        viewChannel: "Преглед на канал",
                        topic: "Тема",
                        typeChannel: "Канал"
                    },
                    permissions: {
                        add_reaction: "Добавяне на реакция",
                        administrator: "Администратор",
                        attach_files: "Прикачване на файли",
                        ban_members: "Блокиране на потребители",
                        change_nickname: "Промяна на потребителското име",
                        connect: "Свързване",
                        create_events: "Създаване на събития",
                        create_expressions: "Създаване на изрази",
                        create_instant_invite: "Създаване на моментална покана",
                        create_polls: "Създаване на анкети",
                        create_private_threads: "Създаване на приватни теми",
                        create_public_threads: "Създаване на публични теми",
                        deafen_members: "Заглушаване на потребители",
                        embed_links: "Вмъкване на връзки",
                        external_emojis: "Използване на външни емоджи",
                        external_stickers: "Използване на външни стикери",
                        kick_members: "Изключване на потребители",
                        manage_channels: "Управление на канали",
                        manage_emojis: "Управление на емоджита",
                        manage_stickers: "Управление на стикерите",
                        manage_emojis_and_stickers: "Управление на емоджита и стикерите",
                        manage_events: "Управление на събития",
                        manage_expressions: "Управление на изрази",
                        manage_guild: "Управление на сървъра",
                        manage_messages: "Управление на съобщения",
                        manage_nicknames: "Управление на потребителските имена",
                        manage_permissions: "Управление на разрешения",
                        manage_roles: "Управление на роли",
                        manage_threads: "Управление на темите",
                        manage_webhooks: "Управление на уебхук",
                        mention_everyone: "Упоменаване на всички",
                        moderate_members: "Регулиране на потребители",
                        move_members: "Преместване на потребители",
                        mute_members: "Заглушаване на потребители",
                        priority_speaker: "Предварителен говорник",
                        read_message_history: "Четене на историята на съобщения",
                        read_messages: "Четене на съобщения",
                        request_to_speak: "Заявление за участие",
                        send_messages: "Изпращане на съобщения",
                        send_messages_in_threads: "Изпращане на съобщения в темите",
                        send_polls: "Изпращане на анкети",
                        send_tts_messages: "Изпращане на съобщения TTS",
                        send_voice_messages: "Изпращане на съобщения на глас",
                        speak: "Говорене",
                        stream: "Изпращане на стрийм",
                        use_application_commands: "Използване на команди за приложение",
                        use_embedded_activities: "Използване на вградени дейности",
                        use_external_apps: "Използване на външни приложения",
                        use_external_emojis: "Използване на външни емоджи",
                        use_external_sounds: "Използване на външни звуци",
                        use_external_stickers: "Използване на външни стикери",
                        use_soundboard: "Използване на звукова панела",
                        use_voice_activation: "Използване на активация на глас",
                        view_audit_log: "Преглед на журнала за аудит",
                        view_channel: "Преглед на канала",
                        view_creator_monetization_analytics: "Преглед на анализа на монетизацията на създателите",
                        view_guild_insights: "Преглед на анализа на сървъра",
                        userPopover: {
                            memberSince: "Členem od"
                        }
                    }
                },
                "zh-CN": {
                    themes: {
                        light: "浅色",
                        dark: "深色",
                        midnight: "午夜",
                        pink: "粉色",
                        red: "红色",
                        fire: "火焰",
                        underwater: "水下",
                        neonNight: "霓虹夜",
                        highContrastDark: "高对比度深色",
                        highContrastLight: "高对比度浅色"
                    },
                    ticket: {
                        title: "工单 {number}",
                        createdBy: "创建者",
                        at: "时间"
                    },
                    searchPlaceholder: "搜索消息或发送者",
                    popover: {
                        members: "成员",
                        permissions: "权限"
                    },
                    channelPopover: {
                        viewChannel: "查看频道",
                        topic: "主题",
                        typeChannel: "频道"
                    },
                    permissions: {
                        add_reaction: "添加反应",
                        administrator: "管理员",
                        attach_files: "附加文件",
                        ban_members: "禁止成员",
                        change_nickname: "更改昵称",
                        connect: "连接",
                        create_events: "创建事件",
                        create_expressions: "创建表达式",
                        create_instant_invite: "创建即时邀请",
                        create_polls: "创建投票",
                        create_private_threads: "创建私人主题",
                        create_public_threads: "创建公共主题",
                        deafen_members: "禁言成员",
                        embed_links: "插入链接",
                        external_emojis: "使用外部表情符号",
                        external_stickers: "使用外部贴纸",
                        kick_members: "踢出成员",
                        manage_channels: "管理频道",
                        manage_emojis: "管理表情符号",
                        manage_stickers: "管理贴纸",
                        manage_emojis_and_stickers: "管理表情符号和贴纸",
                        manage_events: "管理事件",
                        manage_expressions: "管理表达式",
                        manage_guild: "管理服务器",
                        manage_messages: "管理消息",
                        manage_nicknames: "管理昵称",
                        manage_permissions: "管理权限",
                        manage_roles: "管理角色",
                        manage_threads: "管理主题",
                        manage_webhooks: "管理网络钩子",
                        mention_everyone: "提及所有人",
                        moderate_members: "管理成员",
                        move_members: "移动成员",
                        mute_members: "禁言成员",
                        priority_speaker: "优先发言者",
                        read_message_history: "阅读消息历史",
                        read_messages: "阅读消息",
                        request_to_speak: "请求发言",
                        send_messages: "发送消息",
                        send_messages_in_threads: "发送消息到主题",
                        send_polls: "发送投票",
                        send_tts_messages: "发送消息 TTS",
                        send_voice_messages: "发送语音消息",
                        speak: "发言",
                        stream: "发送流",
                        use_application_commands: "使用应用程序命令",
                        use_embedded_activities: "使用嵌入活动",
                        use_external_apps: "使用外部应用程序",
                        use_external_emojis: "使用外部表情符号",
                        use_external_sounds: "使用外部声音",
                        use_external_stickers: "使用外部贴纸",
                        use_soundboard: "使用声音板",
                        use_voice_activation: "使用语音激活",
                        view_audit_log: "查看审计日志",
                        view_channel: "查看频道",
                        view_creator_monetization_analytics: "查看创作者货币化分析",
                        view_guild_insights: "查看服务器见解",
                        userPopover: {
                            memberSince: "成员加入时间"
                        }
                    }
                },
                "zh-TW": {
                    themes: {
                        light: "淺色",
                        dark: "深色",
                        midnight: "午夜",
                        pink: "粉色",
                        red: "紅色",
                        fire: "火焰",
                        underwater: "水下",
                        neonNight: "霓虹夜",
                        highContrastDark: "高對比度深色",
                        highContrastLight: "高對比度淺色"
                    },
                    ticket: {
                        title: "工單 {number}",
                        createdBy: "創建者",
                        at: "時間"
                    },
                    searchPlaceholder: "搜索消息或發送者",
                    popover: {
                        members: "成員",
                        permissions: "權限"
                    },
                    channelPopover: {
                        viewChannel: "查看頻道",
                        topic: "主題",
                        typeChannel: "頻道"
                    },
                    permissions: {
                        add_reaction: "添加反應",
                        administrator: "管理員",
                        attach_files: "附加文件",
                        ban_members: "禁止成員",
                        change_nickname: "更改暱稱",
                        connect: "連接",
                        create_events: "創建事件",
                        create_expressions: "創建表達式",
                        create_instant_invite: "創建即時邀請",
                        create_polls: "創建投票",
                        create_private_threads: "創建私人主題",
                        create_public_threads: "創建公共主題",
                        deafen_members: "禁言成員",
                        embed_links: "插入連結",
                        external_emojis: "使用外部表情符號",
                        external_stickers: "使用外部貼紙",
                        kick_members: "踢出成員",
                        manage_channels: "管理頻道",
                        manage_emojis: "管理表情符號",
                        manage_stickers: "管理貼紙",
                        manage_emojis_and_stickers: "管理表情符號和貼紙",
                        manage_events: "管理事件",
                        manage_expressions: "管理表達式",
                        manage_guild: "管理伺服器",
                        manage_messages: "管理消息",
                        manage_nicknames: "管理暱稱",
                        manage_permissions: "管理權限",
                        manage_roles: "管理角色",
                        manage_threads: "管理主題",
                        manage_webhooks: "管理網絡鉤子",
                        mention_everyone: "提及所有人",
                        moderate_members: "管理成員",
                        move_members: "移動成員",
                        mute_members: "禁言成員",
                        priority_speaker: "優先發言者",
                        read_message_history: "閱讀消息歷史",
                        read_messages: "閱讀消息",
                        request_to_speak: "請求發言",
                        send_messages: "發送消息",
                        send_messages_in_threads: "發送消息到主題",
                        send_polls: "發送投票",
                        send_tts_messages: "發送消息 TTS",
                        send_voice_messages: "發送語音消息",
                        speak: "發言",
                        stream: "發送流",
                        use_application_commands: "使用應用程序命令",
                        use_embedded_activities: "使用嵌入活動",
                        use_external_apps: "使用外部應用程序",
                        use_external_emojis: "使用外部表情符號",
                        use_external_sounds: "使用外部聲音",
                        use_external_stickers: "使用外部貼紙",
                        use_soundboard: "使用聲音板",
                        use_voice_activation: "使用語音激活",
                        view_audit_log: "查看審計日誌",
                        view_channel: "查看頻道",
                        view_creator_monetization_analytics: "查看創作者貨幣化分析",
                        view_guild_insights: "查看伺服器見解",
                        userPopover: {
                            memberSince: "成員加入時間"
                        }
                    }
                },
                hr: {
                    themes: {
                        light: "Svijetlo",
                        dark: "Tamno",
                        midnight: "Ponoć",
                        pink: "Ružičasto",
                        red: "Crveno",
                        fire: "Vatra",
                        underwater: "Pod vodom",
                        neonNight: "Neonska noć",
                        highContrastDark: "Visoki kontrast tamno",
                        highContrastLight: "Visoki kontrast svijetlo"
                    },
                    ticket: {
                        title: "Ulaznica {number}",
                        createdBy: "Kreirano od",
                        at: "u"
                    },
                    searchPlaceholder: "Pretraži poruke ili pošiljatelje",
                    popover: {
                        members: "Članovi",
                        permissions: "Dozvole"
                    },
                    channelPopover: {
                        viewChannel: "Pogledajte kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Dodaj reakciju",
                        administrator: "Administrator",
                        attach_files: "Dodajte datoteke",
                        ban_members: "Blokirajte korisnike",
                        change_nickname: "Promijenite korisničko ime",
                        connect: "Povežite",
                        create_events: "Stvorite događaje",
                        create_expressions: "Stvorite izraze",
                        create_instant_invite: "Stvorite trenutnu pozivnicu",
                        create_polls: "Stvorite ankete",
                        create_private_threads: "Stvorite privatne teme",
                        create_public_threads: "Stvorite javne teme",
                        deafen_members: "Zamrzite korisnike",
                        embed_links: "Ubaci vezu",
                        external_emojis: "Koristite vanjske emodžije",
                        external_stickers: "Koristite vanjske stikerice",
                        kick_members: "Isključite korisnike",
                        manage_channels: "Upravljajte kanali",
                        manage_emojis: "Upravljajte emodžije",
                        manage_stickers: "Upravljajte stikerice",
                        manage_emojis_and_stickers: "Upravljajte emodžije i stikerice",
                        manage_events: "Upravljajte događaje",
                        manage_expressions: "Upravljajte izraze",
                        manage_guild: "Upravljajte server",
                        manage_messages: "Upravljajte poruke",
                        manage_nicknames: "Upravljajte korisnička imena",
                        manage_permissions: "Upravljajte dozvole",
                        manage_roles: "Upravljajte uloge",
                        manage_threads: "Upravljajte teme",
                        manage_webhooks: "Upravljajte webhookove",
                        mention_everyone: "Mentionirajte sve",
                        moderate_members: "Regulirajte korisnike",
                        move_members: "Premjestite korisnike",
                        mute_members: "Zamrzite korisnike",
                        priority_speaker: "Predavač prioriteta",
                        read_message_history: "Čitajte povijest poruka",
                        read_messages: "Čitajte poruke",
                        request_to_speak: "Zatražite govore",
                        send_messages: "Pošaljite poruke",
                        send_messages_in_threads: "Pošaljite poruke u temama",
                        send_polls: "Pošaljite ankete",
                        send_tts_messages: "Pošaljite poruke TTS",
                        send_voice_messages: "Pošaljite govorne poruke",
                        speak: "Govoriti",
                        stream: "Streamati",
                        use_application_commands: "Koristite naredbe za aplikaciju",
                        use_embedded_activities: "Koristite ugrađene aktivnosti",
                        use_external_apps: "Koristite vanjske aplikacije",
                        use_external_emojis: "Koristite vanjske emodžije",
                        use_external_sounds: "Koristite vanjske zvukove",
                        use_external_stickers: "Koristite vanjske stikerice",
                        use_soundboard: "Koristite zvučnu ploču",
                        use_voice_activation: "Koristite aktivaciju govora",
                        view_audit_log: "Pregledajte dnevnik za audit",
                        view_channel: "Pregledajte kanal",
                        view_creator_monetization_analytics: "Pregledajte analizu monetizacije kreatora",
                        view_guild_insights: "Pregledajte analizu servera",
                        userPopover: {
                            memberSince: "Členem od"
                        }
                    }
                },
                cs: {
                    themes: {
                        light: "Světlý",
                        dark: "Tmavý",
                        midnight: "Půlnoc",
                        pink: "Růžový",
                        red: "Červený",
                        fire: "Oheň",
                        underwater: "Pod vodou",
                        neonNight: "Neonová noc",
                        highContrastDark: "Vysoký kontrast tmavý",
                        highContrastLight: "Vysoký kontrast světlý"
                    },
                    ticket: {
                        title: "Vstupenka {number}",
                        createdBy: "Vytvořeno od",
                        at: "ve"
                    },
                    searchPlaceholder: "Hledat zprávy nebo odesílatele",
                    popover: {
                        members: "Členové",
                        permissions: "Oprávnění"
                    },
                    channelPopover: {
                        viewChannel: "Přejít na kanal",
                        topic: "Téma",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Přidat reakci",
                        administrator: "Administrátor",
                        attach_files: "Přiložit soubory",
                        ban_members: "Blokovat členy",
                        change_nickname: "Změnit přezdívku",
                        connect: "Připojit",
                        create_events: "Vytvořit události",
                        create_expressions: "Vytvořit výrazy",
                        create_instant_invite: "Vytvořit okamžitou pozvánku",
                        create_polls: "Vytvořit ankety",
                        create_private_threads: "Vytvořit soukromé vlákno",
                        create_public_threads: "Vytvořit veřejné vlákno",
                        deafen_members: "Ztlumit členy",
                        embed_links: "Vložit odkazy",
                        external_emojis: "Používat externí emodžije",
                        external_stickers: "Používat externí stikerice",
                        kick_members: "Vyloučit členy",
                        manage_channels: "Spravovat kanály",
                        manage_emojis: "Spravovat emodžije",
                        manage_stickers: "Spravovat stikerice",
                        manage_emojis_and_stickers: "Spravovat emodžije a stikerice",
                        manage_events: "Spravovat události",
                        manage_expressions: "Spravovat výrazy",
                        manage_guild: "Spravovat server",
                        manage_messages: "Spravovat zprávy",
                        manage_nicknames: "Spravovat přezdívky",
                        manage_permissions: "Spravovat oprávn��ní",
                        manage_roles: "Spravovat role",
                        manage_threads: "Spravovat vlákna",
                        manage_webhooks: "Spravovat webhooky",
                        mention_everyone: "Mentionovat všechny",
                        moderate_members: "Moderovat členy",
                        move_members: "Přesouvat členy",
                        mute_members: "Ztlumit členy",
                        priority_speaker: "Prioritní hlasatel",
                        read_message_history: "Číst historii zpráv",
                        read_messages: "Číst zprávy",
                        request_to_speak: "Žádat o hlas",
                        send_messages: "Poslat zprávy",
                        send_messages_in_threads: "Poslat zprávy do vláken",
                        send_polls: "Poslat ankety",
                        send_tts_messages: "Poslat zprávy TTS",
                        send_voice_messages: "Poslat zvukové zprávy",
                        speak: "Mluvit",
                        stream: "Streamovat",
                        use_application_commands: "Používat nástroje pro aplikaci",
                        use_embedded_activities: "Používat vložené aktivity",
                        use_external_apps: "Používat externí aplikace",
                        use_external_emojis: "Používat externí emodžije",
                        use_external_sounds: "Používat externí zvuky",
                        use_external_stickers: "Používat externí stikerice",
                        use_soundboard: "Používat zvukovou desku",
                        use_voice_activation: "Používat aktivaci hlasu",
                        view_audit_log: "Zobrazit protokol pro audit",
                        view_channel: "Zobrazit kanál",
                        view_creator_monetization_analytics: "Zobrazit analýzu monetizace tvůrců",
                        view_guild_insights: "Zobrazit analýzu serveru",
                        userPopover: {
                            memberSince: "Členem od"
                        }
                    }
                },
                id: {
                    themes: {
                        light: "Terang",
                        dark: "Gelap",
                        midnight: "Tengah malam",
                        pink: "Merah muda",
                        red: "Merah",
                        fire: "Api",
                        underwater: "Bawah air",
                        neonNight: "Malam neon",
                        highContrastDark: "Kontras tinggi gelap",
                        highContrastLight: "Kontras tinggi terang"
                    },
                    ticket: {
                        title: "Tiket {number}",
                        createdBy: "Dibuat oleh",
                        at: "pada pukul"
                    },
                    searchPlaceholder: "Cari pesan atau pengirim",
                    popover: {
                        members: "Anggota",
                        permissions: "Izin"
                    },
                    channelPopover: {
                        viewChannel: "Pergi ke kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Menambahkan reaksi",
                        administrator: "Administrator",
                        attach_files: "Menambahkan file",
                        ban_members: "Memblokir anggota",
                        change_nickname: "Mengubah nama pengguna",
                        connect: "Menghubungi",
                        create_events: "Membuat acara",
                        create_expressions: "Membuat ekspresi",
                        create_instant_invite: "Membuat undangan langsung",
                        create_polls: "Membuat survei",
                        create_private_threads: "Membuat thread pribadi",
                        create_public_threads: "Membuat thread publik",
                        deafen_members: "Membisukan anggota",
                        embed_links: "Menggunakan tautan eksternal",
                        external_emojis: "Menggunakan emodji eksternal",
                        external_stickers: "Menggunakan stiker eksternal",
                        kick_members: "Menghapus anggota",
                        manage_channels: "Mengelola saluran",
                        manage_emojis: "Mengelola emodji",
                        manage_stickers: "Mengelola stiker",
                        manage_emojis_and_stickers: "Mengelola emodji dan stiker",
                        manage_events: "Mengelola acara",
                        manage_expressions: "Mengelola ekspresi",
                        manage_guild: "Mengelola server",
                        manage_messages: "Mengelola pesan",
                        manage_nicknames: "Mengelola nama pengguna",
                        manage_permissions: "Mengelola izin",
                        manage_roles: "Mengelola peran",
                        manage_threads: "Mengelola thread",
                        manage_webhooks: "Mengelola webhook",
                        mention_everyone: "Mention semua",
                        moderate_members: "Memoderasi anggota",
                        move_members: "Memindahkan anggota",
                        mute_members: "Membisukan anggota",
                        priority_speaker: "Pembicara prioritas",
                        read_message_history: "Membaca riwayat pesan",
                        read_messages: "Membaca pesan",
                        request_to_speak: "Meminta bicara",
                        send_messages: "Mengirim pesan",
                        send_messages_in_threads: "Mengirim pesan ke thread",
                        send_polls: "Mengirim survei",
                        send_tts_messages: "Mengirim pesan TTS",
                        send_voice_messages: "Mengirim pesan suara",
                        speak: "Berbicara",
                        stream: "Streaming",
                        use_application_commands: "Menggunakan perintah aplikasi",
                        use_embedded_activities: "Menggunakan aktivitas terintegrasi",
                        use_external_apps: "Menggunakan aplikasi eksternal",
                        use_external_emojis: "Menggunakan emodji eksternal",
                        use_external_sounds: "Menggunakan suara eksternal",
                        use_external_stickers: "Menggunakan stiker eksternal",
                        use_soundboard: "Menggunakan papan suara",
                        use_voice_activation: "Menggunakan aktivasi suara",
                        view_audit_log: "Melihat log audit",
                        view_channel: "Melihat saluran",
                        view_creator_monetization_analytics: "Melihat analisis monetisasi pembuat",
                        view_guild_insights: "Melihat analisis server",
                        userPopover: {
                            memberSince: "Miembro desde"
                        }
                    }
                },
                da: {
                    themes: {
                        light: "Lys",
                        dark: "Mørk",
                        midnight: "Midnat",
                        pink: "Lyserød",
                        red: "Rød",
                        fire: "Ild",
                        underwater: "Under vand",
                        neonNight: "Neon nat",
                        highContrastDark: "Høj kontrast mørk",
                        highContrastLight: "Høj kontrast lys"
                    },
                    ticket: {
                        title: "Billet {number}",
                        createdBy: "Oprettet af",
                        at: "klokken"
                    },
                    channelPopover: {
                        viewChannel: "Pergi ke kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    searchPlaceholder: "Søg i beskeder eller afsendere",
                    popover: {
                        members: "Medlemmer",
                        permissions: "Tilladelser"
                    },
                    permissions: {
                        add_reaction: "Tilføje reaktion",
                        administrator: "Administrator",
                        attach_files: "Biføje filer",
                        ban_members: "Blokér medlemmer",
                        change_nickname: "Skift brugernavn",
                        connect: "Opret forbindelse",
                        create_events: "Opret begivenheder",
                        create_expressions: "Opret udtryk",
                        create_instant_invite: "Opret instantbjudning",
                        create_polls: "Opret undersøgninger",
                        create_private_threads: "Opret private tråde",
                        create_public_threads: "Opret offentlige tråde",
                        deafen_members: "Deafen medlemmer",
                        embed_links: "Inføje links",
                        external_emojis: "Anvende eksterne emojis",
                        external_stickers: "Anvende eksterne stiker",
                        kick_members: "Kicke medlemmer",
                        manage_channels: "Administrer kanaler",
                        manage_emojis: "Administrer emojis",
                        manage_stickers: "Administrer stiker",
                        manage_emojis_and_stickers: "Administrer emojis og stiker",
                        manage_events: "Administrer begivenheder",
                        manage_expressions: "Administrer udtryk",
                        manage_guild: "Administrer server",
                        manage_messages: "Administrer beskeder",
                        manage_nicknames: "Administrer brugernavne",
                        manage_permissions: "Administrer tilladelser",
                        manage_roles: "Administrer roller",
                        manage_threads: "Administrer tråde",
                        manage_webhooks: "Administrer webhooks",
                        mention_everyone: "Mentioner alle",
                        moderate_members: "Moderere medlemmer",
                        move_members: "Flytte medlemmer",
                        mute_members: "Deafen medlemmer",
                        priority_speaker: "Prioritetsværd",
                        read_message_history: "Læse meddelelser fra historik",
                        read_messages: "Læse meddelelser",
                        request_to_speak: "Anmod om at tale",
                        send_messages: "Send beskeder",
                        send_messages_in_threads: "Send beskeder i tråde",
                        send_polls: "Send undersøgninger",
                        send_tts_messages: "Send beskeder TTS",
                        send_voice_messages: "Send talebeskeder",
                        speak: "Tal",
                        stream: "Stream",
                        use_application_commands: "Anvende applikationskommandoer",
                        use_embedded_activities: "Anvende indbæddede aktiviteter",
                        use_external_apps: "Anvende eksterne applikationer",
                        use_external_emojis: "Anvende eksterne emojis",
                        use_external_sounds: "Anvende eksterne lyd",
                        use_external_stickers: "Anvende eksterne stiker",
                        use_soundboard: "Anvende lydtabel",
                        use_voice_activation: "Anvende røstaktivering",
                        view_audit_log: "Vis granskningsloggen",
                        view_channel: "Vis kanalen",
                        view_creator_monetization_analytics: "Vis kreatørernes monetiseringanalys",
                        view_guild_insights: "Vis gildeinsikter",
                        userPopover: {
                            memberSince: "Medlem siden"
                        }
                    }
                },
                nl: {
                    themes: {
                        light: "Licht",
                        dark: "Donker",
                        midnight: "Middernacht",
                        pink: "Roze",
                        red: "Rood",
                        fire: "Vuur",
                        underwater: "Onder water",
                        neonNight: "Neon nacht",
                        highContrastDark: "Hoog contrast donker",
                        highContrastLight: "Hoog contrast licht"
                    },
                    ticket: {
                        title: "Kaartje {number}",
                        createdBy: "Gemaakt door",
                        at: "om"
                    },
                    searchPlaceholder: "Zoek berichten of afzenders",
                    popover: {
                        members: "Leden",
                        permissions: "Rechten"
                    },
                    channelPopover: {
                        viewChannel: "Bekijk kanaal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Reactie toevoegen",
                        administrator: "Administrator",
                        attach_files: "Voeg bestanden toe",
                        ban_members: "Blokkeer leden",
                        change_nickname: "Gebruikersnaam wijzigen",
                        connect: "Verbinding maken",
                        create_events: "Evenementen maken",
                        create_expressions: "Uitdrukkingen maken",
                        create_instant_invite: "Instant-uitnodiging maken",
                        create_polls: "Onderzoeken maken",
                        create_private_threads: "Private threads maken",
                        create_public_threads: "Publieke threads maken",
                        deafen_members: "Geluiden van leden stille",
                        embed_links: "Links invoegen",
                        external_emojis: "Extern gebruik van emojis",
                        external_stickers: "Extern gebruik van stickers",
                        kick_members: "Kick leden",
                        manage_channels: "Kanaalbeheer",
                        manage_emojis: "Emojis beheren",
                        manage_stickers: "Stickers beheren",
                        manage_emojis_and_stickers: "Emojis en stickers beheren",
                        manage_events: "Evenementen beheren",
                        manage_expressions: "Uitdrukkingen beheren",
                        manage_guild: "Serverbeheer",
                        manage_messages: "Beskeder beheren",
                        manage_nicknames: "Brugernamen beheren",
                        manage_permissions: "Beheer rechten",
                        manage_roles: "Rollen beheren",
                        manage_threads: "Threads beheren",
                        manage_webhooks: "Webhooks beheren",
                        mention_everyone: "Mentioneer alle",
                        moderate_members: "Modereer leden",
                        move_members: "Leden verplaatsen",
                        mute_members: "Geluiden van leden stille",
                        priority_speaker: "Prioriteitspreker",
                        read_message_history: "Meddelelser uit historie lezen",
                        read_messages: "Meddelelser lezen",
                        request_to_speak: "Vraag om te spreken",
                        send_messages: "Berichten versturen",
                        send_messages_in_threads: "Berichten versturen in threads",
                        send_polls: "Onderzoeken versturen",
                        send_tts_messages: "Berichten TTS versturen",
                        send_voice_messages: "Berichten op stem geven",
                        speak: "Spreken",
                        stream: "Streamen",
                        use_application_commands: "Gebruik applicatieopdrachten",
                        use_embedded_activities: "Gebruik ingeboude activiteiten",
                        use_external_apps: "Gebruik externe apps",
                        use_external_emojis: "Gebruik externe emojis",
                        use_external_sounds: "Gebruik externe geluiden",
                        use_external_stickers: "Gebruik externe stickers",
                        use_soundboard: "Gebruik geluidsbord",
                        use_voice_activation: "Gebruik stemactivatie",
                        view_audit_log: "Logboek van audit bekijken",
                        view_channel: "Kanaal bekijken",
                        view_creator_monetization_analytics: "Analyse van monetisering van creators bekijken",
                        view_guild_insights: "Inzichten van de server bekijken",
                        userPopover: {
                            memberSince: "Membro desde"
                        }
                    }
                },
                fi: {
                    themes: {
                        light: "Vaalea",
                        dark: "Tumma",
                        midnight: "Keskiyö",
                        pink: "Vaaleanpunainen",
                        red: "Punainen",
                        fire: "Tuli",
                        underwater: "Veden alla",
                        neonNight: "Neon yö",
                        highContrastDark: "Korkea kontrasti tumma",
                        highContrastLight: "Korkea kontrasti vaalea"
                    },
                    ticket: {
                        title: "Lippu {number}",
                        createdBy: "Luotu",
                        at: "klo"
                    },
                    searchPlaceholder: "Etsi viestejä tai lähettäjiä",
                    popover: {
                        members: "Jäsenet",
                        permissions: "Luvat"
                    },
                    channelPopover: {
                        viewChannel: "Näytä kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Lisää reaktio",
                        administrator: "Administrator",
                        attach_files: "Liitä tiedostoja",
                        ban_members: "Baneraa jäseniä",
                        change_nickname: "Vaihda käyttäjänimeä",
                        connect: "Yhteyden muodostaminen",
                        create_events: "Luo tapahtumat",
                        create_expressions: "Luo lausekkeita",
                        create_instant_invite: "Luo heti kutsun",
                        create_polls: "Luo kyselyjä",
                        create_private_threads: "Luo yksityisiä viestiketjuja",
                        create_public_threads: "Luo julkisia viestiketjuja",
                        deafen_members: "Kieltäytyy jäseniä",
                        embed_links: "Käytä ulkoisia linkkejä",
                        external_emojis: "Käytä ulkoisia emodžije",
                        external_stickers: "Käytä ulkoisia stikerke",
                        kick_members: "Poista jäseniä",
                        manage_channels: "Hallitse kanavia",
                        manage_emojis: "Hallitse emodžije",
                        manage_stickers: "Hallitse stikerke",
                        manage_emojis_and_stickers: "Hallitse emodžije ja stikerke",
                        manage_events: "Hallitse tapahtumat",
                        manage_expressions: "Hallitse lausekkeet",
                        manage_guild: "Hallitse serveri",
                        manage_messages: "Hallitse viestit",
                        manage_nicknames: "Hallitse käyttäjänimet",
                        manage_permissions: "Hallitse luvat",
                        manage_roles: "Hallitse roolit",
                        manage_threads: "Hallitse viestiketjut",
                        manage_webhooks: "Hallitse webhookit",
                        mention_everyone: "Mentionaa kaikkia",
                        moderate_members: "Moderoi jäseniä",
                        move_members: "Siirrä jäseniä",
                        mute_members: "Kieltäytyy jäseniä",
                        priority_speaker: "Ensimmäisen jäsenen äänestys",
                        read_message_history: "Lue viestiketjujen historia",
                        read_messages: "Lue viestit",
                        request_to_speak: "Pyydä keskustelemaan",
                        send_messages: "Lähetä viestit",
                        send_messages_in_threads: "Lähetä viestit viestiketjuihin",
                        send_polls: "Lähetä kyselyjä",
                        send_tts_messages: "Lähetä TTS-viestit",
                        send_voice_messages: "Lähetä ääniviestit",
                        speak: "Puhu",
                        stream: "Streamata",
                        use_application_commands: "Käytä sovelluskommandoja",
                        use_embedded_activities: "Käytä sisäkköisiä toimintoja",
                        use_external_apps: "Käytä ulkoisia sovelluksia",
                        use_external_emojis: "Käytä ulkoisia emodžije",
                        use_external_sounds: "Käytä ulkoisia ääniä",
                        use_external_stickers: "Käytä ulkoisia stikerke",
                        use_soundboard: "Käytä äänilauta",
                        use_voice_activation: "Käytä äänilaitteen aktivointia",
                        view_audit_log: "Näytä auditilogi",
                        view_channel: "Näytä kanava",
                        view_creator_monetization_analytics: "Näytä luojaan monetisointianalyysi",
                        view_guild_insights: "Näytä gilden tilastot",
                        userPopover: {
                            memberSince: "Membre depuis"
                        }
                    }
                },
                fr: {
                    themes: {
                        light: "Clair",
                        dark: "Sombre",
                        midnight: "Minuit",
                        pink: "Rose",
                        red: "Rouge",
                        fire: "Feu",
                        underwater: "Sous l'eau",
                        neonNight: "Nuit néon",
                        highContrastDark: "Haut contraste sombre",
                        highContrastLight: "Haut contraste clair"
                    },
                    ticket: {
                        title: "Billet {number}",
                        createdBy: "Créé par",
                        at: "à"
                    },
                    searchPlaceholder: "Rechercher des messages ou des expéditeurs",
                    popover: {
                        members: "Membres",
                        permissions: "Permissions"
                    },
                    channelPopover: {
                        viewChannel: "Voir le canal",
                        topic: "Sujet",
                        typeChannel: "Canal"
                    },
                    permissions: {
                        add_reaction: "Ajouter une réaction",
                        administrator: "Administrateur",
                        attach_files: "Joindre des fichiers",
                        ban_members: "Bannir des membres",
                        change_nickname: "Changer le pseudo",
                        connect: "Se connecter",
                        create_events: "Créer des événements",
                        create_expressions: "Créer des expressions",
                        create_instant_invite: "Créer une invitation",
                        create_polls: "Créer des sondages",
                        create_private_threads: "Créer des fils privés",
                        create_public_threads: "Créer des fils publics",
                        deafen_members: "Rendre sourd des membres",
                        embed_links: "Intégrer des liens",
                        external_emojis: "Utiliser des émojis externes",
                        external_stickers: "Utiliser des autocollants externes",
                        kick_members: "Expulser des membres",
                        manage_channels: "Gérer les salons",
                        manage_emojis: "Gérer les émojis",
                        manage_stickers: "Gérer les autocollants",
                        manage_emojis_and_stickers: "Gérer les émojis et les autocollants",
                        manage_events: "Gérer les événements",
                        manage_expressions: "Gérer les expressions",
                        manage_guild: "Gérer le serveur",
                        manage_messages: "Gérer les messages",
                        manage_nicknames: "Gérer les pseudos",
                        manage_permissions: "Gérer les permissions",
                        manage_roles: "Gérer les rôles",
                        manage_threads: "Gérer les fils",
                        manage_webhooks: "Gérer les webhooks",
                        mention_everyone: "Mentionner everyone",
                        moderate_members: "Modérer les membres",
                        move_members: "Déplacer des membres",
                        mute_members: "Rendre muet des membres",
                        priority_speaker: "Priorité audio",
                        read_message_history: "Voir les anciens messages",
                        read_messages: "Lire les messages",
                        request_to_speak: "Demander à parler",
                        send_messages: "Envoyer des messages",
                        send_messages_in_threads: "Envoyer des messages dans les fils",
                        send_polls: "Envoyer des sondages",
                        send_tts_messages: "Envoyer des messages TTS",
                        send_voice_messages: "Envoyer des messages vocaux",
                        speak: "Parler",
                        stream: "Streamer",
                        use_application_commands: "Utiliser les commandes d'application",
                        use_embedded_activities: "Utiliser les activités intégrées",
                        use_external_apps: "Utiliser des applications externes",
                        use_external_emojis: "Utiliser des émojis externes",
                        use_external_sounds: "Utiliser des sons externes",
                        use_external_stickers: "Utiliser des autocollants externes",
                        use_soundboard: "Utiliser la table de mixage",
                        use_voice_activation: "Utiliser la détection de la voix",
                        view_audit_log: "Voir les logs",
                        view_channel: "Voir les salons",
                        view_creator_monetization_analytics: "Voir les analyses de monétisation",
                        view_guild_insights: "Voir les statistiques du serveur",
                        userPopover: {
                            memberSince: "Membre depuis"
                        }
                    }
                },
                de: {
                    themes: {
                        light: "Hell",
                        dark: "Dunkel",
                        midnight: "Mitternacht",
                        pink: "Rosa",
                        red: "Rot",
                        fire: "Feuer",
                        underwater: "Unterwasser",
                        neonNight: "Neon Nacht",
                        highContrastDark: "Hoher Kontrast Dunkel",
                        highContrastLight: "Hoher Kontrast Hell"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Erstellt von",
                        at: "um"
                    },
                    searchPlaceholder: "Nachrichten oder Absender suchen",
                    popover: {
                        members: "Mitglieder",
                        permissions: "Berechtigungen"
                    },
                    channelPopover: {
                        viewChannel: "Kanal ansehen",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Reaktion hinzufügen",
                        administrator: "Administrator",
                        attach_files: "Dateien angehängt",
                        ban_members: "Mitglieder sperren",
                        change_nickname: "Nickname ändern",
                        connect: "Verbinden",
                        create_events: "Ereignisse erstellen",
                        create_expressions: "Ausdrücke erstellen",
                        create_instant_invite: "Instant-Einladungen erstellen",
                        create_polls: "Umfragen erstellen",
                        create_private_threads: "Private Threads erstellen",
                        create_public_threads: "Öffentliche Threads erstellen",
                        deafen_members: "Mitglieder stumm schalten",
                        embed_links: "Links einfügen",
                        external_emojis: "Externe Emojis verwenden",
                        external_stickers: "Externe Sticker verwenden",
                        kick_members: "Mitglieder kicken",
                        manage_channels: "Kanäle verwalten",
                        manage_emojis: "Emojis verwalten",
                        manage_stickers: "Sticker verwalten",
                        manage_emojis_and_stickers: "Emojis und Sticker verwalten",
                        manage_events: "Ereignisse verwalten",
                        manage_expressions: "Ausdrücke verwalten",
                        manage_guild: "Server verwalten",
                        manage_messages: "Nachrichten verwalten",
                        manage_nicknames: "Nicknamen verwalten",
                        manage_permissions: "Berechtigungen verwalten",
                        manage_roles: "Rollen verwalten",
                        manage_threads: "Threads verwalten",
                        manage_webhooks: "Webhooks verwalten",
                        mention_everyone: "Alle erwähnen",
                        moderate_members: "Mitglieder moderieren",
                        move_members: "Mitglieder verschieben",
                        mute_members: "Mitglieder stumm schalten",
                        priority_speaker: "Prioritätssprecher",
                        read_message_history: "Nachrichtengeschichte lesen",
                        read_messages: "Nachrichten lesen",
                        request_to_speak: "Sprechen beantragen",
                        send_messages: "Nachrichten senden",
                        send_messages_in_threads: "Nachrichten in Threads senden",
                        send_polls: "Umfragen senden",
                        send_tts_messages: "TTS-Nachrichten senden",
                        send_voice_messages: "Sprachnachrichten senden",
                        speak: "Sprechen",
                        stream: "Streamen",
                        use_application_commands: "Anwendungsbefehle verwenden",
                        use_embedded_activities: "Eingebettete Aktivitäten verwenden",
                        use_external_apps: "Externe Apps verwenden",
                        use_external_emojis: "Externe Emojis verwenden",
                        use_external_sounds: "Externe Sounds verwenden",
                        use_external_stickers: "Externe Sticker verwenden",
                        use_soundboard: "Soundboard verwenden",
                        use_voice_activation: "Sprachaktivierung verwenden",
                        view_audit_log: "Audit-Log ansehen",
                        view_channel: "Kanal ansehen",
                        view_creator_monetization_analytics: "Ersteller-Monetisierungs-Analytics ansehen",
                        view_guild_insights: "Server-Einsichten ansehen",
                        userPopover: {
                            memberSince: "Mitglied seit"
                        }
                    }
                },
                el: {
                    themes: {
                        light: "Φωτεινό",
                        dark: "Σκοτεινό",
                        midnight: "Μεσάνυχα",
                        pink: "Ροζ",
                        red: "Κόκκινο",
                        fire: "Φωτιά",
                        underwater: "Υποβρύχιο",
                        neonNight: "Νέον νύχτα",
                        highContrastDark: "Υψηλή αντίθεση σκοτεινό",
                        highContrastLight: "Υψηλή αντίθεση φωτεινό"
                    },
                    searchPlaceholder: "Αναζήτηση μηνυμάτων ή αποστολέων",
                    popover: {
                        members: "Μέλη",
                        permissions: "Δικαιώματα"
                    },
                    ticket: {
                        title: "Τεκμήριο {number}",
                        createdBy: "Δημιουργήθηκε από",
                        at: "στην"
                    },
                    channelPopover: {
                        viewChannel: "Κανάλι προβολή",
                        topic: "Θέμα",
                        typeChannel: "Κανάλι"
                    },
                    permissions: {
                        add_reaction: "Προσθήκη αντίδρασης",
                        administrator: "Διαχειριστής",
                        attach_files: "Επισύναψη αρχείων",
                        ban_members: "Αποκλεισμός μελών",
                        change_nickname: "Αλλαγή ψευδωνύμου",
                        connect: "Σύνδεση",
                        create_events: "Δημιουργία εκδηλώσεων",
                        create_expressions: "Δημιουργία εκφράσεων",
                        create_instant_invite: "Δημιουργία άμεσης πρόσκλησης",
                        create_polls: "Δημιουργία ψηφοφοριών",
                        create_private_threads: "Δημιουργία ιδιωτικών νημάτων",
                        create_public_threads: "Δημιουργία δημόσιων νημάτων",
                        deafen_members: "Σίγαση μελών",
                        embed_links: "Ενσωμάτωση συνδέσμων",
                        external_emojis: "Χρήση εξωτερικών emoji",
                        external_stickers: "Χρήση εξωτερικών αυτοκόλλητων",
                        kick_members: "Αποβολή μελών",
                        manage_channels: "Διαχείριση καναλιών",
                        manage_emojis: "Διαχείριση emoji",
                        manage_stickers: "Διαχείριση αυτοκόλλητων",
                        manage_emojis_and_stickers: "Διαχείριση emoji και αυτοκόλλητων",
                        manage_events: "Διαχείριση εκδηλώσεων",
                        manage_expressions: "Διαχείριση εκφράσεων",
                        manage_guild: "Διαχείριση διακομιστή",
                        manage_messages: "Διαχείριση μηνυμάτων",
                        manage_nicknames: "Διαχείριση ψευδωνύμων",
                        manage_permissions: "Διαχείριση δικαιωμάτων",
                        manage_roles: "Διαχείριση ρόλων",
                        manage_threads: "Διαχείριση νημάτων",
                        manage_webhooks: "Διαχείριση webhooks",
                        mention_everyone: "Αναφορά όλων",
                        moderate_members: "Συντονισμός μελών",
                        move_members: "Μετακίνηση μελών",
                        mute_members: "Σίγαση μελών",
                        priority_speaker: "Ομιλητής προτεραιότητας",
                        read_message_history: "Ανάγνωση ιστορικού μηνυμάτων",
                        read_messages: "Ανάγνωση μηνυμάτων",
                        request_to_speak: "Αίτημα για ομιλία",
                        send_messages: "Αποστολή μηνυμάτων",
                        send_messages_in_threads: "Αποστολή μηνυμάτων σε νήματα",
                        send_polls: "Αποστολή ψηφοφοριών",
                        send_tts_messages: "Αποστολή μηνυμάτων TTS",
                        send_voice_messages: "Αποστολή φωνητικών μηνυμάτων",
                        speak: "Ομιλία",
                        stream: "Μετάδοση",
                        use_application_commands: "Χρήση εντολών εφαρμογής",
                        use_embedded_activities: "Χρήση ενσωματωμένων δραστηριοτήτων",
                        use_external_apps: "Χρήση εξωτερικών εφαρμογών",
                        use_external_emojis: "Χρήση εξωτερικών emoji",
                        use_external_sounds: "Χρήση εξωτερικών ήχων",
                        use_external_stickers: "Χρήση εξωτερικών αυτοκόλλητων",
                        use_soundboard: "Χρήση ηχητικού πίνακα",
                        use_voice_activation: "Χρήση φωνητικής ενεργοποίησης",
                        view_audit_log: "Προβολή αρχείου καταγραφής ελέγχου",
                        view_channel: "Προβολή καναλιού",
                        view_creator_monetization_analytics: "Προβολή αναλυτικών στοιχείων εσόδων δημιουργού",
                        view_guild_insights: "Προβολή στατιστικών διακομιστή",
                        userPopover: {
                            memberSince: "Miembro desde"
                        }
                    }
                },
                hi: {
                    themes: {
                        light: "हल्का",
                        dark: "गहरा",
                        midnight: "मध्यरात्रि",
                        pink: "गुलाबी",
                        red: "लाल",
                        fire: "आग",
                        underwater: "पानी के नीचे",
                        neonNight: "नियॉन रात",
                        highContrastDark: "उच्च कंट्रास्ट गहरा",
                        highContrastLight: "उच्च कंट्रास्ट हल्का"
                    },
                    searchPlaceholder: "संदेश या प्रेषक खोजें",
                    popover: {
                        members: "सदस्य",
                        permissions: "अनुमतियां"
                    },
                    ticket: {
                        title: "टिकेट {number}",
                        createdBy: "बनाया गया",
                        at: "द्वारा"
                    },
                    channelPopover: {
                        viewChannel: "चैनल देखें",
                        topic: "विषय",
                        typeChannel: "चैनल"
                    },
                    permissions: {
                        add_reaction: "प्रतिक्रिया जोड़ें",
                        administrator: "प्रशासक",
                        attach_files: "फ़ाइलें जोड़ें",
                        ban_members: "सदस्यों को प्रतिबंधित करें",
                        change_nickname: "उपनाम बदलें",
                        connect: "कनेक्ट करें",
                        create_events: "कार्यक्रम बनाएं",
                        create_expressions: "अभिव्यक्तियां बनाएं",
                        create_instant_invite: "तत्काल आमंत्रण बनाएं",
                        create_polls: "पोल बनाएं",
                        create_private_threads: "निजी थ्रेड बनाएं",
                        create_public_threads: "स���र्वजनिक थ्रेड बनाएं",
                        deafen_members: "सदस्यों को बधिर करें",
                        embed_links: "लिंक एम्बेड करें",
                        external_emojis: "बाहरी इमोजी का उपयोग करें",
                        external_stickers: "बाहरी स्टिकर का उपयोग करें",
                        kick_members: "सदस्यों को निकालें",
                        manage_channels: "चैनल प्रबंधित करें",
                        manage_emojis: "इमोजी प्रबंधित करें",
                        manage_stickers: "स्टिकर प्रबंधित करें",
                        manage_emojis_and_stickers: "इमोजी और स्टिकर प्रबंधित करें",
                        manage_events: "कार्यक्रम प्रबंधित करें",
                        manage_expressions: "अभिव्यक्तियां प्रबंधित करें",
                        manage_guild: "सर्वर प्रबंधित करें",
                        manage_messages: "संदेश प्रबंधित करें",
                        manage_nicknames: "उपनाम प्रबंधित करें",
                        manage_permissions: "अनुमतियां प्रबंधित करें",
                        manage_roles: "भूमिकाएं प्रबंधित करें",
                        manage_threads: "थ्रेड प्रबंधित करें",
                        manage_webhooks: "वेबहुक प्रबंधित करें",
                        mention_everyone: "सभी को मेंशन करें",
                        moderate_members: "सदस्यों को मॉडरेट करें",
                        move_members: "सदस्यों को स्थानांतरित करें",
                        mute_members: "सदस्यों को म्यूट करें",
                        priority_speaker: "प्राथमिकता वक्ता",
                        read_message_history: "संदेश इतिहास पढ़ें",
                        read_messages: "संदेश पढ़ें",
                        request_to_speak: "बोलने का अनुरोध करें",
                        send_messages: "संदेश भेजें",
                        send_messages_in_threads: "थ्रेड में संदेश भेजें",
                        send_polls: "पोल भेजें",
                        send_tts_messages: "TTS संदेश भेजें",
                        send_voice_messages: "वॉइस संदेश भेजें",
                        speak: "बोलें",
                        stream: "स्ट्रीम करें",
                        use_application_commands: "एप्लिकेशन कमांड का उपयोग करें",
                        use_embedded_activities: "एम्बेडेड गतिविधियों का उपयोग करें",
                        use_external_apps: "बाहरी एप्स का उपयोग करें",
                        use_external_emojis: "बाहरी इमोजी का उपयोग करें",
                        use_external_sounds: "बाहरी ध्वनियों का उपयोग करें",
                        use_external_stickers: "बाहरी स्टिकर का उपयोग करें",
                        use_soundboard: "साउंडबोर्ड का उपयोग करें",
                        use_voice_activation: "वॉइस एक्टिवेशन का उपयोग करें",
                        view_audit_log: "ऑडिट लॉग देखें",
                        view_channel: "चैनल देखें",
                        view_creator_monetization_analytics: "क्रिएटर मौद���रीकरण विश्लेषण देखें",
                        view_guild_insights: "सर्वर इनसाइट्स देखें",
                        userPopover: {
                            memberSince: "Miembro desde"
                        }
                    }
                },
                hu: {
                    themes: {
                        light: "Világos",
                        dark: "Söt",
                        midnight: "Éjfél",
                        pink: "Rózsaszín",
                        red: "Piros",
                        fire: "Tűz",
                        underwater: "Víz alatt",
                        neonNight: "Neon éjszaka",
                        highContrastDark: "Magas kontraszt sötét",
                        highContrastLight: "Magas kontraszt világos"
                    },
                    ticket: {
                        title: "Billet {number}",
                        createdBy: "Créé par",
                        at: "par"
                    },
                    searchPlaceholder: "Üzenetek vagy küldők keresése",
                    popover: {
                        members: "Tagok",
                        permissions: "Jogosultságok"
                    },
                    channelPopover: {
                        viewChannel: "Kanal megtekintése",
                        topic: "Téma",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Reakció hozzáadása",
                        administrator: "Adminisztrátor",
                        attach_files: "Fájlok csatolása",
                        ban_members: "Tagok kitiltása",
                        change_nickname: "Becenév módosítása",
                        connect: "Csatlakozás",
                        create_events: "Események létrehozása",
                        create_expressions: "Kifejezések létrehozása",
                        create_instant_invite: "Azonnali meghívó létrehozása",
                        create_polls: "Szavazások létrehozása",
                        create_private_threads: "Privát szálak létrehozása",
                        create_public_threads: "Nyilvános szálak létrehozása",
                        deafen_members: "Tagok némítása",
                        embed_links: "Linkek beágyazása",
                        external_emojis: "Külső emojik használata",
                        external_stickers: "Külső matricák használata",
                        kick_members: "Tagok kirúgása",
                        manage_channels: "Csatornák kezelése",
                        manage_emojis: "Emojik kezelése",
                        manage_stickers: "Matricák kezelése",
                        manage_emojis_and_stickers: "Emojik és matricák kezelése",
                        manage_events: "Események kezelése",
                        manage_expressions: "Kifejezések kezelése",
                        manage_guild: "Szerver kezelése",
                        manage_messages: "Üzenetek kezelése",
                        manage_nicknames: "Becenevek kezelése",
                        manage_permissions: "Jogosultságok kezelése",
                        manage_roles: "Szerepek kezelése",
                        manage_threads: "Szálak kezelése",
                        manage_webhooks: "Webhookok kezelése",
                        mention_everyone: "Mindenki említése",
                        moderate_members: "Tagok moderálása",
                        move_members: "Tagok mozgatása",
                        mute_members: "Tagok némítása",
                        priority_speaker: "Elsőbbségi beszélő",
                        read_message_history: "Üzenetelőzmények olvasása",
                        read_messages: "Üzenetek olvasása",
                        request_to_speak: "Beszédkérés",
                        send_messages: "Üzenetek küldése",
                        send_messages_in_threads: "Üzenetek küldése szálakban",
                        send_polls: "Szavazások küldése",
                        send_tts_messages: "TTS üzenetek küldése",
                        send_voice_messages: "Hangüzenetek küldése",
                        speak: "Beszéd",
                        stream: "Közvetítés",
                        use_application_commands: "Alkalmazásparancsok használata",
                        use_embedded_activities: "Beágyazott tevékenységek használata",
                        use_external_apps: "Külső alkalmazások használata",
                        use_external_emojis: "Külső emojik használata",
                        use_external_sounds: "Külső hangok használata",
                        use_external_stickers: "Külső matricák használata",
                        use_soundboard: "Hangpanel használata",
                        use_voice_activation: "Hangaktiválás használata",
                        view_audit_log: "Auditnapló megtekintése",
                        view_channel: "Csatorna megtekintése",
                        view_creator_monetization_analytics: "Alkotói monetizálási elemzések megtekintése",
                        view_guild_insights: "Szerver-elemzések megtekintése",
                        userPopover: {
                            memberSince: "Tag ettől"
                        }
                    }
                },
                it: {
                    themes: {
                        light: "Chiaro",
                        dark: "Scuro",
                        midnight: "Mezzanotte",
                        pink: "Rosa",
                        red: "Rosso",
                        fire: "Fuoco",
                        underwater: "Sott'acqua",
                        neonNight: "Notte neon",
                        highContrastDark: "Alto contrasto scuro",
                        highContrastLight: "Alto contrasto chiaro"
                    },
                    ticket: {
                        title: "Billet {number}",
                        createdBy: "Créé par",
                        at: "par"
                    },
                    searchPlaceholder: "Cerca messaggi o mittenti",
                    popover: {
                        members: "Membri",
                        permissions: "Permessi"
                    },
                    channelPopover: {
                        viewChannel: "Visualizza canale",
                        topic: "Tema",
                        typeChannel: "Canale"
                    },
                    permissions: {
                        add_reaction: "Aggiungi reazione",
                        administrator: "Amministratore",
                        attach_files: "Allega file",
                        ban_members: "Bandisci membri",
                        change_nickname: "Cambia nickname",
                        connect: "Connetti",
                        create_events: "Crea eventi",
                        create_expressions: "Crea espressioni",
                        create_instant_invite: "Crea invito istantaneo",
                        create_polls: "Crea sondaggi",
                        create_private_threads: "Crea discussioni private",
                        create_public_threads: "Crea discussioni pubbliche",
                        deafen_members: "Disattiva audio membri",
                        embed_links: "Incorpora link",
                        external_emojis: "Usa emoji esterni",
                        external_stickers: "Usa sticker esterni",
                        kick_members: "Espelli membri",
                        manage_channels: "Gestisci canali",
                        manage_emojis: "Gestisci emoji",
                        manage_stickers: "Gestisci sticker",
                        manage_emojis_and_stickers: "Gestisci emoji e sticker",
                        manage_events: "Gestisci eventi",
                        manage_expressions: "Gestisci espressioni",
                        manage_guild: "Gestisci server",
                        manage_messages: "Gestisci messaggi",
                        manage_nicknames: "Gestisci nickname",
                        manage_permissions: "Gestisci permessi",
                        manage_roles: "Gestisci ruoli",
                        manage_threads: "Gestisci discussioni",
                        manage_webhooks: "Gestisci webhook",
                        mention_everyone: "Menziona tutti",
                        moderate_members: "Modera membri",
                        move_members: "Sposta membri",
                        mute_members: "Silenzia membri",
                        priority_speaker: "Oratore prioritario",
                        read_message_history: "Leggi cronologia messaggi",
                        read_messages: "Leggi messaggi",
                        request_to_speak: "Richiedi di parlare",
                        send_messages: "Invia messaggi",
                        send_messages_in_threads: "Invia messaggi nelle discussioni",
                        send_polls: "Invia sondaggi",
                        send_tts_messages: "Invia messaggi TTS",
                        send_voice_messages: "Invia messaggi vocali",
                        speak: "Parla",
                        stream: "Trasmetti",
                        use_application_commands: "Usa comandi applicazione",
                        use_embedded_activities: "Usa attività incorporate",
                        use_external_apps: "Usa app esterne",
                        use_external_emojis: "Usa emoji esterni",
                        use_external_sounds: "Usa suoni esterni",
                        use_external_stickers: "Usa sticker esterni",
                        use_soundboard: "Usa soundboard",
                        use_voice_activation: "Usa attivazione vocale",
                        view_audit_log: "Visualizza registro audit",
                        view_channel: "Visualizza canale",
                        view_creator_monetization_analytics: "Visualizza analisi monetizzazione creatori",
                        view_guild_insights: "Visualizza statistiche server",
                        userPopover: {
                            memberSince: "Membro dal"
                        }
                    }
                },
                ja: {
                    themes: {
                        light: "ライト",
                        dark: "ダーク",
                        midnight: "ミッドナイト",
                        pink: "ピンク",
                        red: "レッド",
                        fire: "ファイア",
                        underwater: "アンダーウォーター",
                        neonNight: "ネオンナイト",
                        highContrastDark: "ハイコントラストダーク",
                        highContrastLight: "ハイコントラストライト"
                    },
                    searchPlaceholder: "メッセージまたは送信者を検索",
                    popover: {
                        members: "メンバー",
                        permissions: "権限"
                    },
                    ticket: {
                        title: "チケット {number}",
                        createdBy: "作成者",
                        at: ""
                    },
                    channelPopover: {
                        viewChannel: "チャンネルを表示",
                        topic: "トピック",
                        typeChannel: "チャンネル"
                    },
                    permissions: {
                        add_reaction: "��アクションを追加",
                        administrator: "管理者",
                        attach_files: "ファイルを添付",
                        ban_members: "メンバーをBAN",
                        change_nickname: "ニックネームを変更",
                        connect: "接続",
                        create_events: "イベントを作成",
                        create_expressions: "表現を作成",
                        create_instant_invite: "招待を作成",
                        create_polls: "投票を作成",
                        create_private_threads: "プライベートスレッドを作成",
                        create_public_threads: "公開スレッドを作成",
                        deafen_members: "メンバーの音声を無効化",
                        embed_links: "埋め込みリンク",
                        external_emojis: "外部の絵文字を使用",
                        external_stickers: "外部のスタンプを使用",
                        kick_members: "メンバーをキック",
                        manage_channels: "チャンネルを管理",
                        manage_emojis: "絵文字を管理",
                        manage_stickers: "スタンプを管理",
                        manage_emojis_and_stickers: "絵文字とスタンプを管理",
                        manage_events: "イベントを管理",
                        manage_expressions: "表現を管理",
                        manage_guild: "サーバーを管理",
                        manage_messages: "メッセージを管理",
                        manage_nicknames: "ニックネームを管理",
                        manage_permissions: "権限を管理",
                        manage_roles: "ロールを管理",
                        manage_threads: "スレッドを管理",
                        manage_webhooks: "ウェブフックを管理",
                        mention_everyone: "@everyoneメンション",
                        moderate_members: "メンバーをモデレート",
                        move_members: "メンバーを移動",
                        mute_members: "メンバーをミュート",
                        priority_speaker: "優先スピーカー",
                        read_message_history: "メッセージ履歴を表示",
                        read_messages: "メッセージを表示",
                        request_to_speak: "発言をリクエスト",
                        send_messages: "メッセージを送信",
                        send_messages_in_threads: "スレッドでメッセージを送信",
                        send_polls: "投票を送信",
                        send_tts_messages: "TTSメッセージを送信",
                        send_voice_messages: "ボイスメッセージを送信",
                        speak: "発言",
                        stream: "配信",
                        use_application_commands: "アプリケーションコマンドを使用",
                        use_embedded_activities: "埋め込みアクティビティを使用",
                        use_external_apps: "外部アプリを使用",
                        use_external_emojis: "外部の絵文字を使用",
                        use_external_sounds: "外部の音声を使用",
                        use_external_stickers: "外部のスタンプを使用",
                        use_soundboard: "サウンドボードを使用",
                        use_voice_activation: "音声検出を使用",
                        view_audit_log: "監査ログを表示",
                        view_channel: "チャンネルを表示",
                        view_creator_monetization_analytics: "クリエイター収益化分析を表示",
                        view_guild_insights: "サーバーインサ���トを表示",
                        userPopover: {
                            memberSince: "メンバー登録日"
                        }
                    }
                },
                ko: {
                    themes: {
                        light: "라이트",
                        dark: "다크",
                        midnight: "미드나이트",
                        pink: "핑크",
                        red: "레드",
                        fire: "파이어",
                        underwater: "언더워터",
                        neonNight: "네온 나이트",
                        highContrastDark: "고대비 다크",
                        highContrastLight: "고대비 라이트"
                    },
                    searchPlaceholder: "메시지 또는 발신자 검색",
                    popover: {
                        members: "멤버",
                        permissions: "권한"
                    },
                    ticket: {
                        title: "티켓 {number}",
                        createdBy: "만든 사람",
                        at: ""
                    },
                    channelPopover: {
                        viewChannel: "채널 보기",
                        topic: "주제",
                        typeChannel: "채널"
                    },
                    permissions: {
                        add_reaction: "리액션 추가",
                        administrator: "관리자",
                        attach_files: "파일 첨부",
                        ban_members: "멤버 차단",
                        change_nickname: "별명 변경",
                        connect: "연결",
                        create_events: "이벤트 만들기",
                        create_expressions: "표현 만들기",
                        create_instant_invite: "초대 생성",
                        create_polls: "투표 만들기",
                        create_private_threads: "비공개 스레드 만들기",
                        create_public_threads: "공개 스레드 만들기",
                        deafen_members: "멤버 음성 비활성화",
                        embed_links: "링크 첨부",
                        external_emojis: "외부 이모티콘 사용",
                        external_stickers: "외부 스티커 사용",
                        kick_members: "멤버 추방",
                        manage_channels: "채널 관리",
                        manage_emojis: "이모티콘 관리",
                        manage_stickers: "스티커 관리",
                        manage_emojis_and_stickers: "이모티콘 및 스티커 관리",
                        manage_events: "이벤트 관리",
                        manage_expressions: "표현 관리",
                        manage_guild: "서버 관리",
                        manage_messages: "메시지 관리",
                        manage_nicknames: "별명 관리",
                        manage_permissions: "권한 관리",
                        manage_roles: "역할 관리",
                        manage_threads: "스레드 관리",
                        manage_webhooks: "웹후크 관리",
                        mention_everyone: "@everyone 멘션",
                        moderate_members: "멤버 관리",
                        move_members: "멤버 이동",
                        mute_members: "멤버 음소거",
                        priority_speaker: "우선 발언권",
                        read_message_history: "메시지 기록 보기",
                        read_messages: "메시지 보기",
                        request_to_speak: "발언 요청",
                        send_messages: "메시지 보내기",
                        send_messages_in_threads: "스레드에 메시지 보내기",
                        send_polls: "투표 보내기",
                        send_tts_messages: "TTS 메시지 보내기",
                        send_voice_messages: "음성 메시지 보내기",
                        speak: "말하기",
                        stream: "스트리밍",
                        use_application_commands: "애플리케이션 ���령어 사용",
                        use_embedded_activities: "임베드 활동 사���",
                        use_external_apps: "외부 앱 사용",
                        use_external_emojis: "외부 이모티콘 사용",
                        use_external_sounds: "외부 소리 사용",
                        use_external_stickers: "외부 스티커 사용",
                        use_soundboard: "사운드보드 사용",
                        use_voice_activation: "음성 감지 사용",
                        view_audit_log: "감사 로그 보기",
                        view_channel: "채널 보기",
                        view_creator_monetization_analytics: "크리에이터 수익화 분석 보기",
                        view_guild_insights: "서버 인사이트 보기",
                        userPopover: {
                            memberSince: "가입일"
                        }
                    }
                },
                "es-419": {
                    themes: {
                        light: "Claro",
                        dark: "Oscuro",
                        midnight: "Medianoche",
                        pink: "Rosa",
                        red: "Rojo",
                        fire: "Fuego",
                        underwater: "Bajo el agua",
                        neonNight: "Noche de neón",
                        highContrastDark: "Alto contraste oscuro",
                        highContrastLight: "Alto contraste claro"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Creado por",
                        at: "a"
                    },
                    searchPlaceholder: "Buscar mensajes o remitentes",
                    popover: {
                        members: "Miembros",
                        permissions: "Permisos"
                    },
                    channelPopover: {
                        viewChannel: "Ver canal",
                        topic: "Tema",
                        typeChannel: "Canal"
                    },
                    permissions: {
                        add_reaction: "Agregar reacción",
                        administrator: "Administrador",
                        attach_files: "Adjuntar archivos",
                        ban_members: "Banear miembros",
                        change_nickname: "Cambiar apodo",
                        connect: "Conectar",
                        create_events: "Crear eventos",
                        create_expressions: "Crear expresiones",
                        create_instant_invite: "Crear invitación instantánea",
                        create_polls: "Crear encuestas",
                        create_private_threads: "Crear hilos privados",
                        create_public_threads: "Crear hilos públicos",
                        deafen_members: "Ensordecer miembros",
                        embed_links: "Insertar enlaces",
                        external_emojis: "Usar emojis externos",
                        external_stickers: "Usar stickers externos",
                        kick_members: "Expulsar miembros",
                        manage_channels: "Administrar canales",
                        manage_emojis: "Administrar emojis",
                        manage_stickers: "Administrar stickers",
                        manage_emojis_and_stickers: "Administrar emojis y stickers",
                        manage_events: "Administrar eventos",
                        manage_expressions: "Administrar expresiones",
                        manage_guild: "Administrar servidor",
                        manage_messages: "Administrar mensajes",
                        manage_nicknames: "Administrar apodos",
                        manage_permissions: "Administrar permisos",
                        manage_roles: "Administrar roles",
                        manage_threads: "Administrar hilos",
                        manage_webhooks: "Administrar webhooks",
                        mention_everyone: "Mencionar a todos",
                        moderate_members: "Moderar miembros",
                        move_members: "Mover miembros",
                        mute_members: "Silenciar miembros",
                        priority_speaker: "Prioridad de voz",
                        read_message_history: "Leer historial de mensajes",
                        read_messages: "Leer mensajes",
                        request_to_speak: "Solicitar hablar",
                        send_messages: "Enviar mensajes",
                        send_messages_in_threads: "Enviar mensajes en hilos",
                        send_polls: "Enviar encuestas",
                        send_tts_messages: "Enviar mensajes TTS",
                        send_voice_messages: "Enviar mensajes de voz",
                        speak: "Hablar",
                        stream: "Transmitir",
                        use_application_commands: "Usar comandos de aplicación",
                        use_embedded_activities: "Usar actividades integradas",
                        use_external_apps: "Usar aplicaciones externas",
                        use_external_emojis: "Usar emojis externos",
                        use_external_sounds: "Usar sonidos externos",
                        use_external_stickers: "Usar stickers externos",
                        use_soundboard: "Usar tablero de sonidos",
                        use_voice_activation: "Usar activación por voz",
                        view_audit_log: "Ver registro de auditoría",
                        view_channel: "Ver canal",
                        view_creator_monetization_analytics: "Ver análisis de monetización de creadores",
                        view_guild_insights: "Ver estadísticas del servidor",
                        userPopover: {
                            memberSince: "Miembro desde"
                        }
                    }
                },
                lt: {
                    themes: {
                        light: "Šviesus",
                        dark: "Tamsus",
                        midnight: "Vidurnaktis",
                        pink: "Rožinis",
                        red: "Raudonas",
                        fire: "Ugnis",
                        underwater: "Po vandeniu",
                        neonNight: "Neono naktis",
                        highContrastDark: "Didelis kontrastas tamsus",
                        highContrastLight: "Didelis kontrastas šviesus"
                    },
                    searchPlaceholder: "Ieškoti žinučių ar siuntėjų",
                    popover: {
                        members: "Nariai",
                        permissions: "Leidimai"
                    },
                    ticket: {
                        title: "Tiket {number}",
                        createdBy: "Sukurta",
                        at: "pulksten"
                    },
                    channelPopover: {
                        viewChannel: "Peržiūrėti kanalą",
                        topic: "Tema",
                        typeChannel: "Kanalas"
                    },
                    permissions: {
                        add_reaction: "Pridėti reakciją",
                        administrator: "Administratorius",
                        attach_files: "Pridėti failus",
                        ban_members: "Užblokuoti narius",
                        change_nickname: "Keisti slapyvardį",
                        connect: "Prisijungti",
                        create_events: "Kurti įvykius",
                        create_expressions: "Kurti išraiškas",
                        create_instant_invite: "Kurti momentinį pakvietimą",
                        create_polls: "Kurti apklausas",
                        create_private_threads: "Kurti privačius pokalbius",
                        create_public_threads: "Kurti viešus pokalbius",
                        deafen_members: "Nutildyti narius",
                        embed_links: "Įterpti nuorodas",
                        external_emojis: "Naudoti išorinius jaustukus",
                        external_stickers: "Naudoti išorinius lipdukus",
                        kick_members: "Išmesti narius",
                        manage_channels: "Valdyti kanalus",
                        manage_emojis: "Valdyti jaustukus",
                        manage_stickers: "Valdyti lipdukus",
                        manage_emojis_and_stickers: "Valdyti jaustukus ir lipdukus",
                        manage_events: "Valdyti įvykius",
                        manage_expressions: "Valdyti išraiškas",
                        manage_guild: "Valdyti serverį",
                        manage_messages: "Valdyti žinutes",
                        manage_nicknames: "Valdyti slapyvardžius",
                        manage_permissions: "Valdyti leidimus",
                        manage_roles: "Valdyti roles",
                        manage_threads: "Valdyti pokalbius",
                        manage_webhooks: "Valdyti webhook'us",
                        mention_everyone: "Paminėti visus",
                        moderate_members: "Moderuoti narius",
                        move_members: "Perkelti narius",
                        mute_members: "Nutildyti narius",
                        priority_speaker: "Prioritetinis kalbėtojas",
                        read_message_history: "Skaityti žinučių istoriją",
                        read_messages: "Skaityti žinutes",
                        request_to_speak: "Prašyti kalbėti",
                        send_messages: "Siųsti žinutes",
                        send_messages_in_threads: "Siųsti žinutes pokalbiuose",
                        send_polls: "Siųsti apklausas",
                        send_tts_messages: "Siųsti TTS žinutes",
                        send_voice_messages: "Siųsti balso žinutes",
                        speak: "Kalbėti",
                        stream: "Transliuoti",
                        use_application_commands: "Naudoti programos komandas",
                        use_embedded_activities: "Naudoti įterptas veiklas",
                        use_external_apps: "Naudoti išorines programas",
                        use_external_emojis: "Naudoti išorinius jaustukus",
                        use_external_sounds: "Naudoti išorinius garsus",
                        use_external_stickers: "Naudoti išorinius lipdukus",
                        use_soundboard: "Naudoti garso lentą",
                        use_voice_activation: "Naudoti balso aktyvavimą",
                        view_audit_log: "Peržiūrėti audito žurnalą",
                        view_channel: "Peržiūrėti kanalą",
                        view_creator_monetization_analytics: "Peržiūrėti kūrėjų monetizacijos analitiką",
                        view_guild_insights: "Peržiūrėti serverio įžvalgas",
                        userPopover: {
                            memberSince: "Narys nuo"
                        }
                    }
                },
                no: {
                    themes: {
                        light: "Lys",
                        dark: "Mørk",
                        midnight: "Midnatt",
                        pink: "Rosa",
                        red: "Rød",
                        fire: "Ild",
                        underwater: "Under vann",
                        neonNight: "Neon natt",
                        highContrastDark: "Høy kontrast mørk",
                        highContrastLight: "Høy kontrast lys"
                    },
                    ticket: {
                        title: "Ticker {number}",
                        createdBy: "Laget av",
                        at: "kl"
                    },
                    searchPlaceholder: "Søk i meldinger eller avsendere",
                    popover: {
                        members: "Medlemmer",
                        permissions: "Tillatelser"
                    },
                    channelPopover: {
                        viewChannel: "Vis kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Legg til reaksjon",
                        administrator: "Administrator",
                        attach_files: "Legg ved filer",
                        ban_members: "Utesteng medlemmer",
                        change_nickname: "Endre kallenavn",
                        connect: "Koble til",
                        create_events: "Opprett arrangementer",
                        create_expressions: "Opprett uttrykk",
                        create_instant_invite: "Opprett øyeblikkelig invitasjon",
                        create_polls: "Opprett avstemninger",
                        create_private_threads: "Opprett private tråder",
                        create_public_threads: "Opprett offentlige tråder",
                        deafen_members: "Demp medlemmer",
                        embed_links: "Bygg inn lenker",
                        external_emojis: "Bruk eksterne emojier",
                        external_stickers: "Bruk eksterne klistremerker",
                        kick_members: "Spark ut medlemmer",
                        manage_channels: "Administrer kanaler",
                        manage_emojis: "Administrer emojier",
                        manage_stickers: "Administrer klistremerker",
                        manage_emojis_and_stickers: "Administrer emojier og klistremerker",
                        manage_events: "Administrer arrangementer",
                        manage_expressions: "Administrer uttrykk",
                        manage_guild: "Administrer server",
                        manage_messages: "Administrer meldinger",
                        manage_nicknames: "Administrer kallenavn",
                        manage_permissions: "Administrer tillatelser",
                        manage_roles: "Administrer roller",
                        manage_threads: "Administrer tråde",
                        manage_webhooks: "Administrer webhooks",
                        mention_everyone: "Nevn alle",
                        moderate_members: "Moderer medlemmer",
                        move_members: "Flytt medlemmer",
                        mute_members: "Demp medlemmer",
                        priority_speaker: "Prioritert taler",
                        read_message_history: "Les meldingshistorikk",
                        read_messages: "Les meldinger",
                        request_to_speak: "Be om å snakke",
                        send_messages: "Send meldinger",
                        send_messages_in_threads: "Send meldinger i tråder",
                        send_polls: "Send avstemninger",
                        send_tts_messages: "Send TTS-meldinger",
                        send_voice_messages: "Send talemeldinger",
                        speak: "Snakk",
                        stream: "Strøm",
                        use_application_commands: "Bruk applikasjonskommandoer",
                        use_embedded_activities: "Bruk innebygde aktiviteter",
                        use_external_apps: "Bruk eksterne apper",
                        use_external_emojis: "Bruk eksterne emojier",
                        use_external_sounds: "Bruk eksterne lyder",
                        use_external_stickers: "Bruk eksterne klistremerker",
                        use_soundboard: "Bruk lydpanel",
                        use_voice_activation: "Bruk stemmeaktivering",
                        view_audit_log: "Vis revisjonslogg",
                        view_channel: "Vis kanal",
                        view_creator_monetization_analytics: "Vis skapermonetiseringsanalyse",
                        view_guild_insights: "Vis serverinnsikt",
                        userPopover: {
                            memberSince: "Medlem siden"
                        }
                    }
                },
                pl: {
                    themes: {
                        light: "Jasny",
                        dark: "Ciemny",
                        midnight: "Północ",
                        pink: "Różowy",
                        red: "Czerwony",
                        fire: "Ogień",
                        underwater: "Pod wodą",
                        neonNight: "Neonowa noc",
                        highContrastDark: "Wysoki kontrast ciemny",
                        highContrastLight: "Wysoki kontrast jasny"
                    },
                    ticket: {
                        title: "Tiket {number}",
                        createdBy: "Utworzony przez",
                        at: "w"
                    },
                    searchPlaceholder: "Szukaj wiadomości lub nadawców",
                    popover: {
                        members: "Członkowie",
                        permissions: "Uprawnienia"
                    },
                    channelPopover: {
                        viewChannel: "Wyświetl kanał",
                        topic: "Temat",
                        typeChannel: "Kanał"
                    },
                    permissions: {
                        add_reaction: "Dodaj reakcję",
                        administrator: "Administrator",
                        attach_files: "Załącz pliki",
                        ban_members: "Banuj członków",
                        change_nickname: "Zmień pseudonim",
                        connect: "Połącz",
                        create_events: "Twórz wydarzenia",
                        create_expressions: "Twórz wyrażenia",
                        create_instant_invite: "Twórz natychmiastowe zaproszenia",
                        create_polls: "Twórz ankiety",
                        create_private_threads: "Twórz prywatne wątki",
                        create_public_threads: "Twórz publiczne wątki",
                        deafen_members: "Wycisz członków",
                        embed_links: "Osadzaj linki",
                        external_emojis: "Używaj zewnętrznych emoji",
                        external_stickers: "Używaj zewnętrznych naklejek",
                        kick_members: "Wyrzucaj członków",
                        manage_channels: "Zarządzaj kanałami",
                        manage_emojis: "Zarządzaj emoji",
                        manage_stickers: "Zarządzaj naklejkami",
                        manage_emojis_and_stickers: "Zarządzaj emoji i naklejkami",
                        manage_events: "Zarządzaj wydarzeniami",
                        manage_expressions: "Zarządzaj wyrażeniami",
                        manage_guild: "Zarządzaj serwerem",
                        manage_messages: "Zarządzaj wiadomościami",
                        manage_nicknames: "Zarządzaj pseudonimami",
                        manage_permissions: "Zarządzaj uprawnieniami",
                        manage_roles: "Zarządzaj rolami",
                        manage_threads: "Zarządzaj wątkami",
                        manage_webhooks: "Zarządzaj webhookami",
                        mention_everyone: "Oznacz wszystkich",
                        moderate_members: "Moderuj członków",
                        move_members: "Przenoś członków",
                        mute_members: "Wyciszaj członków",
                        priority_speaker: "Mówca priorytetowy",
                        read_message_history: "Czytaj historię wiadomości",
                        read_messages: "Czytaj wiadomości",
                        request_to_speak: "Poproś o głos",
                        send_messages: "Wysyłaj wiadomości",
                        send_messages_in_threads: "Wysyłaj wiadomości w wątkach",
                        send_polls: "Wysyłaj ankiety",
                        send_tts_messages: "Wysyłaj wiadomości TTS",
                        send_voice_messages: "Wysyłaj wiadomości głosowe",
                        speak: "Mów",
                        stream: "Streamuj",
                        use_application_commands: "Używaj komend aplikacji",
                        use_embedded_activities: "Używaj wbudowanych aktywności",
                        use_external_apps: "Używaj zewnętrznych aplikacji",
                        use_external_emojis: "Używaj zewnętrznych emoji",
                        use_external_sounds: "Używaj zewnętrznych dźwięków",
                        use_external_stickers: "Używaj zewnętrznych naklejek",
                        use_soundboard: "Używaj tablicy dźwięków",
                        use_voice_activation: "Używaj aktywacji głosowej",
                        view_audit_log: "Przeglądaj dziennik zdarzeń",
                        view_channel: "Przeglądaj kanał",
                        view_creator_monetization_analytics: "Przeglądaj analizy monetyzacji twórców",
                        view_guild_insights: "Przeglądaj statystyki serwera",
                        userPopover: {
                            memberSince: "Członek od"
                        }
                    }
                },
                "pt-BR": {
                    themes: {
                        light: "Claro",
                        dark: "Escuro",
                        midnight: "Meia-noite",
                        pink: "Rosa",
                        red: "Vermelho",
                        fire: "Fogo",
                        underwater: "Subaquático",
                        neonNight: "Noite neon",
                        highContrastDark: "Alto contraste escuro",
                        highContrastLight: "Alto contraste claro"
                    },
                    searchPlaceholder: "Pesquisar mensagens ou remetentes",
                    popover: {
                        members: "Membros",
                        permissions: "Permissões"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Criado por",
                        at: "em"
                    },
                    channelPopover: {
                        viewChannel: "Visualizar canal",
                        topic: "Tema",
                        typeChannel: "Canal"
                    },
                    permissions: {
                        add_reaction: "Adicionar reação",
                        administrator: "Administrador",
                        attach_files: "Anexar arquivos",
                        ban_members: "Banir membros",
                        change_nickname: "Alterar apelido",
                        connect: "Conectar",
                        create_events: "Criar eventos",
                        create_expressions: "Criar expressões",
                        create_instant_invite: "Criar convite instantâneo",
                        create_polls: "Criar enquetes",
                        create_private_threads: "Criar tópicos privados",
                        create_public_threads: "Criar tópicos públicos",
                        deafen_members: "Ensurdecer membros",
                        embed_links: "Incorporar links",
                        external_emojis: "Usar emojis externos",
                        external_stickers: "Usar figurinhas externas",
                        kick_members: "Expulsar membros",
                        manage_channels: "Gerenciar canais",
                        manage_emojis: "Gerenciar emojis",
                        manage_stickers: "Gerenciar figurinhas",
                        manage_emojis_and_stickers: "Gerenciar emojis e figurinhas",
                        manage_events: "Gerenciar eventos",
                        manage_expressions: "Gerenciar expressões",
                        manage_guild: "Gerenciar servidor",
                        manage_messages: "Gerenciar mensagens",
                        manage_nicknames: "Gerenciar apelidos",
                        manage_permissions: "Gerenciar permissões",
                        manage_roles: "Gerenciar cargos",
                        manage_threads: "Gerenciar tópicos",
                        manage_webhooks: "Gerenciar webhooks",
                        mention_everyone: "Mencionar todos",
                        moderate_members: "Moderar membros",
                        move_members: "Mover membros",
                        mute_members: "Silenciar membros",
                        priority_speaker: "Voz prioritária",
                        read_message_history: "Ler histórico de mensagens",
                        read_messages: "Ler mensagens",
                        request_to_speak: "Pedir para falar",
                        send_messages: "Enviar mensagens",
                        send_messages_in_threads: "Enviar mensagens em tópicos",
                        send_polls: "Enviar enquetes",
                        send_tts_messages: "Enviar mensagens TTS",
                        send_voice_messages: "Enviar mensagens de voz",
                        speak: "Falar",
                        stream: "Transmitir",
                        use_application_commands: "Usar comandos de aplicativo",
                        use_embedded_activities: "Usar atividades incorporadas",
                        use_external_apps: "Usar aplicativos externos",
                        use_external_emojis: "Usar emojis externos",
                        use_external_sounds: "Usar sons externos",
                        use_external_stickers: "Usar figurinhas externas",
                        use_soundboard: "Usar soundboard",
                        use_voice_activation: "Usar ativação por voz",
                        view_audit_log: "Ver registro de auditoria",
                        view_channel: "Ver canal",
                        view_creator_monetization_analytics: "Ver análise de monetização de criadores",
                        view_guild_insights: "Ver insights do servidor",
                        userPopover: {
                            memberSince: "Membro desde"
                        }
                    }
                },
                ro: {
                    themes: {
                        light: "Luminos",
                        dark: "Întunecat",
                        midnight: "Miezul nopții",
                        pink: "Roz",
                        red: "Roșu",
                        fire: "Foc",
                        underwater: "Subacvatic",
                        neonNight: "Noapte neon",
                        highContrastDark: "Contrast înalt întunecat",
                        highContrastLight: "Contrast înalt luminos"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Criado por",
                        at: "em"
                    },
                    searchPlaceholder: "Căutați mesaje sau expeditori",
                    popover: {
                        members: "Membri",
                        permissions: "Permisii"
                    },
                    channelPopover: {
                        viewChannel: "Vizualizați canalul",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Adăugați reacțiune",
                        administrator: "Administrator",
                        attach_files: "Fișiere atașate",
                        ban_members: "Blocați membri",
                        change_nickname: "Schimbați numele de utilizator",
                        connect: "Conectați",
                        create_events: "Creați evenimente",
                        create_expressions: "Creați expresii",
                        create_instant_invite: "Creați invitații instant",
                        create_polls: "Creați chestionare",
                        create_private_threads: "Creați fire private",
                        create_public_threads: "Creați fire publice",
                        deafen_members: "Stopați membri",
                        embed_links: "Inserarea linkurilor",
                        external_emojis: "Utilizați emojis externi",
                        external_stickers: "Utilizați stricker externi",
                        kick_members: "Kickează membri",
                        manage_channels: "Administrați canalele",
                        manage_emojis: "Administrați emojis",
                        manage_stickers: "Administrați stricker",
                        manage_emojis_and_stickers: "Administrați emojis și stricker",
                        manage_events: "Administrați evenimente",
                        manage_expressions: "Administrați expresii",
                        manage_guild: "Administrați serverul",
                        manage_messages: "Administrați mesajele",
                        manage_nicknames: "Administrați numele de utilizator",
                        manage_permissions: "Administrați permisii",
                        manage_roles: "Administrați rolurile",
                        manage_threads: "Administrați firele",
                        manage_webhooks: "Administrați webhooks",
                        mention_everyone: "Mentionați toți",
                        moderate_members: "Moderați membri",
                        move_members: "Mută membri",
                        mute_members: "Stopați membri",
                        priority_speaker: "Vorbitor priorității",
                        read_message_history: "Citește istoricul mesajelor",
                        read_messages: "Citește mesajele",
                        request_to_speak: "Solicitați să vorbă",
                        send_messages: "Trimite mesaje",
                        send_messages_in_threads: "Trimite mesaje în fire",
                        send_polls: "Trimite chestionare",
                        send_tts_messages: "Trimite mesaje TTS",
                        send_voice_messages: "Trimite mesaje vocale",
                        speak: "Vorbește",
                        stream: "Stream",
                        use_application_commands: "Utilizați comenzi de aplicație",
                        use_embedded_activities: "Utilizați activități încorporate",
                        use_external_apps: "Utilizați aplicații externe",
                        use_external_emojis: "Utilizați emojis externe",
                        use_external_sounds: "Utilizați sunetele externe",
                        use_external_stickers: "Utilizați stricker externe",
                        use_soundboard: "Utilizați panoul sonor",
                        use_voice_activation: "Utilizați activarea vocei",
                        view_audit_log: "Vizualizați jurnalul de audit",
                        view_channel: "Vizualizați canalul",
                        view_creator_monetization_analytics: "Vizualizați analizați monetizării creatorilor",
                        view_guild_insights: "Vizualizați înțelegerile serverului",
                        userPopover: {
                            memberSince: "Membru din"
                        }
                    }
                },
                ru: {
                    themes: {
                        light: "Светлый",
                        dark: "Темный",
                        midnight: "Полночь",
                        pink: "Розовый",
                        red: "Красный",
                        fire: "Огонь",
                        underwater: "Под водой",
                        neonNight: "Неоновая ночь",
                        highContrastDark: "Высокий контраст темный",
                        highContrastLight: "Высокий контраст светлый"
                    },
                    ticket: {
                        title: "Тикет {number}",
                        createdBy: "Создан",
                        at: "в"
                    },
                    searchPlaceholder: "Поиск сообщений или отправителей",
                    popover: {
                        members: "Участники",
                        permissions: "Права"
                    },
                    channelPopover: {
                        viewChannel: "Просмотр канала",
                        topic: "Тема",
                        typeChannel: "Канал"
                    },
                    permissions: {
                        add_reaction: "Добавить реакцию",
                        administrator: "Администратор",
                        attach_files: "Прикрепить файлы",
                        ban_members: "Забанить участников",
                        change_nickname: "Изменить никнейм",
                        connect: "Подключиться",
                        create_events: "Создать события",
                        create_expressions: "Создать выражения",
                        create_instant_invite: "Создать мгновенные приглашения",
                        create_polls: "Создать опросы",
                        create_private_threads: "Создать приватные темы",
                        create_public_threads: "Создать публичные темы",
                        deafen_members: "Заглушить участников",
                        embed_links: "Вставить ссылки",
                        external_emojis: "Использовать внешние эмодзи",
                        external_stickers: "Использовать внешние стикеры",
                        kick_members: "Кикнуть участников",
                        manage_channels: "Управлять каналами",
                        manage_emojis: "Управлять эмодзи",
                        manage_stickers: "Управлять стикерами",
                        manage_emojis_and_stickers: "Управлять эмодзи и стикерами",
                        manage_events: "Управлять событиями",
                        manage_expressions: "Управлять выражениями",
                        manage_guild: "Управлять гильдией",
                        manage_messages: "Управлять сообщениями",
                        manage_nicknames: "Управлять никнеймами",
                        manage_permissions: "Управлять правами",
                        manage_roles: "Управлять ролями",
                        manage_threads: "Управлять темами",
                        manage_webhooks: "Управлять вебхуками",
                        mention_everyone: "Упомянуть всех",
                        moderate_members: "Модерировать участников",
                        move_members: "Переместить участников",
                        mute_members: "Заглушить участников",
                        priority_speaker: "Приоритетный участник",
                        read_message_history: "Читать историю сообщений",
                        read_messages: "Читать сообщения",
                        request_to_speak: "Запросить разговор",
                        send_messages: "Отправить сообщения",
                        send_messages_in_threads: "Отправить сообщения в темы",
                        send_polls: "Отправить опросы",
                        send_tts_messages: "Отправить сообщения TTS",
                        send_voice_messages: "Отправить голосовые сообщения",
                        speak: "Говорить",
                        stream: "Стримить",
                        use_application_commands: "Использовать команды приложений",
                        use_embedded_activities: "Использовать встроенные ак��ивность",
                        use_external_apps: "Использовать внешние приложения",
                        use_external_emojis: "Использовать внешние эмодзи",
                        use_external_sounds: "Использовать внешние звуки",
                        use_external_stickers: "Использовать внешние стикеры",
                        use_soundboard: "Использовать звуковую панель",
                        use_voice_activation: "Использовать активацию голоса",
                        view_audit_log: "Просмотреть журнал аудита",
                        view_channel: "Просмотреть канал",
                        view_creator_monetization_analytics: "Просмотреть анализ монетизац��и создателей",
                        view_guild_insights: "Просмотреть анализ гильдии",
                        userPopover: {
                            memberSince: "Участник с"
                        }
                    }
                },
                "es-ES": {
                    themes: {
                        light: "Claro",
                        dark: "Oscuro",
                        midnight: "Medianoche",
                        pink: "Rosa",
                        red: "Rojo",
                        fire: "Fuego",
                        underwater: "Bajo el agua",
                        neonNight: "Noche de neón",
                        highContrastDark: "Alto contraste oscuro",
                        highContrastLight: "Alto contraste claro"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Creado por",
                        at: "en"
                    },
                    searchPlaceholder: "Buscar mensajes o remitentes",
                    popover: {
                        members: "Miembros",
                        permissions: "Permisos"
                    },
                    channelPopover: {
                        viewChannel: "Ver canal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Añadir reacción",
                        administrator: "Administrador",
                        attach_files: "Adjuntar archivos",
                        ban_members: "Banear miembros",
                        change_nickname: "Cambiar apodo",
                        connect: "Conectar",
                        create_events: "Crear eventos",
                        create_expressions: "Crear expresiones",
                        create_instant_invite: "Crear invitaciones instantáneas",
                        create_polls: "Crear encuestas",
                        create_private_threads: "Crear hilos privados",
                        create_public_threads: "Crear hilos públicos",
                        deafen_members: "Silenciar miembros",
                        embed_links: "Insertar enlaces",
                        external_emojis: "Usar emojis externos",
                        external_stickers: "Usar stickers externos",
                        kick_members: "Expulsar miembros",
                        manage_channels: "Administrar canales",
                        manage_emojis: "Administrar emojis",
                        manage_stickers: "Administrar stickers",
                        manage_emojis_and_stickers: "Administrar emojis y stickers",
                        manage_events: "Administrar eventos",
                        manage_expressions: "Administrar expresiones",
                        manage_guild: "Administrar hermandad",
                        manage_messages: "Administrar mensajes",
                        manage_nicknames: "Administrar apodos",
                        manage_permissions: "Administrar permisos",
                        manage_roles: "Administrar roles",
                        manage_threads: "Administrar hilos",
                        manage_webhooks: "Administrar webhooks",
                        mention_everyone: "Mencionar a todos",
                        moderate_members: "Moderar miembros",
                        move_members: "Mover miembros",
                        mute_members: "Silenciar miembros",
                        priority_speaker: "Orador de prioridad",
                        read_message_history: "Leer historial de mensajes",
                        read_messages: "Leer mensajes",
                        request_to_speak: "Solicitar hablar",
                        send_messages: "Enviar mensajes",
                        send_messages_in_threads: "Enviar mensajes en hilos",
                        send_polls: "Enviar encuestas",
                        send_tts_messages: "Enviar mensajes TTS",
                        send_voice_messages: "Enviar mensajes de voz",
                        speak: "Hablar",
                        stream: "Transmitir",
                        use_application_commands: "Usar comandos de aplicación",
                        use_embedded_activities: "Usar actividades incrustadas",
                        use_external_apps: "Usar aplicaciones externas",
                        use_external_emojis: "Usar emojis externos",
                        use_external_sounds: "Usar sonidos externos",
                        use_external_stickers: "Usar stickers externos",
                        use_soundboard: "Usar tablero de sonido",
                        use_voice_activation: "Usar activación de voz",
                        view_audit_log: "Ver registro de auditoría",
                        view_channel: "Ver canal",
                        view_creator_monetization_analytics: "Ver análisis de monetización de creadores",
                        view_guild_insights: "Ver estadísticas de hermandad",
                        userPopover: {
                            memberSince: "Miembro desde"
                        }
                    }
                },
                "sv-SE": {
                    themes: {
                        light: "Ljus",
                        dark: "Mörk",
                        midnight: "Midnatt",
                        pink: "Rosa",
                        red: "Röd",
                        fire: "Eld",
                        underwater: "Under vatten",
                        neonNight: "Neon natt",
                        highContrastDark: "Hög kontrast m��rk",
                        highContrastLight: "Hög kontrast ljus"
                    },
                    searchPlaceholder: "Sök i meddelanden eller avsändare",
                    popover: {
                        members: "Medlemmar",
                        permissions: "Rättigheter"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Skapad av",
                        at: "i"
                    },
                    channelPopover: {
                        viewChannel: "Visa kanal",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Lägg till reaktion",
                        administrator: "Administratör",
                        attach_files: "Bifoga filer",
                        ban_members: "Banna medlemmar",
                        change_nickname: "Ändra användarnamn",
                        connect: "Ansluta",
                        create_events: "Skapa evenemang",
                        create_expressions: "Skapa uttryck",
                        create_instant_invite: "Skapa instantbjudningar",
                        create_polls: "Skapa undersökningar",
                        create_private_threads: "Skapa privata trådar",
                        create_public_threads: "Skapa offentliga trådar",
                        deafen_members: "Döva medlemmar",
                        embed_links: "Infoga länkar",
                        external_emojis: "Använda externa emojis",
                        external_stickers: "Använda externa sticker",
                        kick_members: "Kicka medlemmar",
                        manage_channels: "Hantera kanaler",
                        manage_emojis: "Hantera emojis",
                        manage_stickers: "Hantera sticker",
                        manage_emojis_and_stickers: "Hantera emojis och sticker",
                        manage_events: "Hantera evenemang",
                        manage_expressions: "Hantera uttryck",
                        manage_guild: "Hantera gilde",
                        manage_messages: "Hantera meddelanden",
                        manage_nicknames: "Hantera användarnamn",
                        manage_permissions: "Hantera rättigheter",
                        manage_roles: "Hantera roller",
                        manage_threads: "Hantera trådar",
                        manage_webhooks: "Hantera webhooks",
                        mention_everyone: "Mentionera alla",
                        moderate_members: "Moderera medlemmar",
                        move_members: "Flytta medlemmar",
                        mute_members: "Döva medlemmar",
                        priority_speaker: "Prioritetsvärd",
                        read_message_history: "Läsa meddelandeförhistoria",
                        read_messages: "Läsa meddelanden",
                        request_to_speak: "Begär att tala",
                        send_messages: "Skicka meddelanden",
                        send_messages_in_threads: "Skicka meddelanden i trådar",
                        send_polls: "Skicka undersökningar",
                        send_tts_messages: "Skicka TTS-meddelanden",
                        send_voice_messages: "Skicka talade meddelanden",
                        speak: "Tal",
                        stream: "Strömma",
                        use_application_commands: "Använda applikationskommandon",
                        use_embedded_activities: "Använda inbäddade aktiviteter",
                        use_external_apps: "Använda externa applikationer",
                        use_external_emojis: "Använda externa emojis",
                        use_external_sounds: "Använda externa ljud",
                        use_external_stickers: "Använda externa sticker",
                        use_soundboard: "Använda ljudpanelen",
                        use_voice_activation: "Använda röstaktivering",
                        view_audit_log: "Visa granskningsloggen",
                        view_channel: "Visa kanalen",
                        view_creator_monetization_analytics: "Visa kreatörerns monetiseringanalys",
                        view_guild_insights: "Visa gildeinsikter",
                        userPopover: {
                            memberSince: "Medlem sedan"
                        }
                    }
                },
                th: {
                    themes: {
                        light: "สว่าง",
                        dark: "มืด",
                        midnight: "เที่ยงคืน",
                        pink: "ชมพู",
                        red: "แดง",
                        fire: "ไฟ",
                        underwater: "ใต้น้ำ",
                        neonNight: "นีออนไนท์",
                        highContrastDark: "ความคมชัดสูงมืด",
                        highContrastLight: "ความคมชัดสูงสว่าง"
                    },
                    searchPlaceholder: "ค้นหาข้อความหรือผู้ส่ง",
                    popover: {
                        members: "สมาชิก",
                        permissions: "สิทธิ์"
                    },
                    ticket: {
                        title: "การติดต่อ {number}",
                        createdBy: "สร้างโดย",
                        at: "ใน"
                    },
                    channelPopover: {
                        viewChannel: "ดูช่อง",
                        topic: "หัวข้อ",
                        typeChannel: "ช่อง"
                    },
                    permissions: {
                        add_reaction: "เพิ่มการตอบกลับ",
                        administrator: "ผู้ดูเนินการ",
                        attach_files: "แนบไฟล์",
                        ban_members: "แบนสมาชิก",
                        change_nickname: "เปลี่ยนชื่อผู้ใช้",
                        connect: "เชื่อม",
                        create_events: "สร้างเหตุการณ์",
                        create_expressions: "สร้างนิพจน์",
                        create_instant_invite: "สร้างเชิญตอบทันที",
                        create_polls: "สร้างแบบสำรวจ",
                        create_private_threads: "สร้างเส้นที่เปิดเผยส่วนตัว",
                        create_public_threads: "สร้างเส้นที่เปิดเผยสาธารณะ",
                        deafen_members: "ปิดเสียงสมาชิก",
                        embed_links: "แนบลิงค์",
                        external_emojis: "ใช้งานโอมเจอร์ภายนอก",
                        external_stickers: "ใช้งานสติ๊กเกอร์ภายนอก",
                        kick_members: "ยกเลิกสมาชิก",
                        manage_channels: "จัดการแคนล",
                        manage_emojis: "จัดการโอมเจอร์",
                        manage_stickers: "จัดการสติ๊กเกอร์",
                        manage_emojis_and_stickers: "จัดการโอมเจอร์และสติ๊กเกอร์",
                        manage_events: "จัดการเหตุการณ์",
                        manage_expressions: "จัดการนิพจน์",
                        manage_guild: "จัดการกิลดี",
                        manage_messages: "จัดการข้อความ",
                        manage_nicknames: "จัดการชื่อผู้ใช้",
                        manage_permissions: "จัดการสิทธิ์",
                        manage_roles: "จัดการบทบาท",
                        manage_threads: "จัดการเส้นที่",
                        manage_webhooks: "จัดการเว็บเฮก",
                        mention_everyone: "อ้างถึงทุกคน",
                        moderate_members: "ระงับสมาชิก",
                        move_members: "ย้ายสมาชิก",
                        mute_members: "ปิดเสียงสมาชิก",
                        priority_speaker: "ผู้สร้างเสียงสำคัญ",
                        read_message_history: "อ่านประวัติข้อความ",
                        read_messages: "อ่านข้อความ",
                        request_to_speak: "ขอร้อง",
                        send_messages: "ส่งข้อความ",
                        send_messages_in_threads: "ส่งข้อความในเส้นที่",
                        send_polls: "ส่งแบบสำรวจ",
                        send_tts_messages: "ส่งข้อความ TTS",
                        send_voice_messages: "ส่งข้อความเสียง",
                        speak: "พูด",
                        stream: "ส่งสตรีม",
                        use_application_commands: "ใช้คำสั่งแอปพลิเคชัน",
                        use_embedded_activities: "ใช้กิจกรรมที่นำเข้า",
                        use_external_apps: "ใช้แอปพลิเคชันภายนอก",
                        use_external_emojis: "ใช้โอมเจอร์ภายนอก",
                        use_external_sounds: "ใช้เสียงภายนอก",
                        use_external_stickers: "ใช้สติ๊กเกอร์ภายนอก",
                        use_soundboard: "ใช้แปนเสียง",
                        use_voice_activation: "ใช้การเปิดเสียง",
                        view_audit_log: "ดูบันทึกการตรวจสอบ",
                        view_channel: "ดูแคนล",
                        view_creator_monetization_analytics: "ดูการวิเคราะห์การระยะยันของผู้สร้าง",
                        view_guild_insights: "ดูข้อมูลกิลดี",
                        userPopover: {
                            memberSince: "เป็นสมาชิกตั้งแต่"
                        }
                    }
                },
                tr: {
                    themes: {
                        light: "Açık",
                        dark: "Koyu",
                        midnight: "Gece yarısı",
                        pink: "Pembe",
                        red: "Kırmızı",
                        fire: "Ateş",
                        underwater: "Su altı",
                        neonNight: "Neon gece",
                        highContrastDark: "Yüksek kontrast koyu",
                        highContrastLight: "Yüksek kontrast açık"
                    },
                    searchPlaceholder: "Mesajları veya göndericileri ara",
                    popover: {
                        members: "Üyeler",
                        permissions: "İzinler"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Oprettet af",
                        at: "i"
                    },
                    channelPopover: {
                        viewChannel: "Kanalı görüntüle",
                        topic: "Tema",
                        typeChannel: "Kanal"
                    },
                    permissions: {
                        add_reaction: "Reaksiyon ekle",
                        administrator: "Yönetici",
                        attach_files: "Dosyaları ekle",
                        ban_members: "Üyeleri yasakla",
                        change_nickname: "Kullanıcı adını değiştir",
                        connect: "Bağlan",
                        create_events: "Etkinlik oluştur",
                        create_expressions: "İfade oluştur",
                        create_instant_invite: "Anında davet oluştur",
                        create_polls: "Anket oluştur",
                        create_private_threads: "Özel konuşma işleri oluştur",
                        create_public_threads: "Genel konuşma işleri oluştur",
                        deafen_members: "Üyeleri sessizleştir",
                        embed_links: "Bağlantıları ekle",
                        external_emojis: "Harici emojileri kullan",
                        external_stickers: "Harici stickerleri kullan",
                        kick_members: "Üyeleri at",
                        manage_channels: "Kanalları yönet",
                        manage_emojis: "Emojileri yönet",
                        manage_stickers: "Stickerleri yönet",
                        manage_emojis_and_stickers: "Emojileri ve stickerleri yönet",
                        manage_events: "Etkinlikleri yönet",
                        manage_expressions: "İfadeyi yönet",
                        manage_guild: "Guildi yönet",
                        manage_messages: "Mesajları yönet",
                        manage_nicknames: "Kullanıcı adlarını yönet",
                        manage_permissions: "İzinleri yönet",
                        manage_roles: "Rolleri yönet",
                        manage_threads: "Konuşma işlerini yönet",
                        manage_webhooks: "Webhookları yönet",
                        mention_everyone: "Herkesi önem",
                        moderate_members: "Üyeleri denetle",
                        move_members: "Üyeleri taşı",
                        mute_members: "Üyeleri sessizleştir",
                        priority_speaker: "Öncelikli konuşmacı",
                        read_message_history: "Mesaj geçmişini oku",
                        read_messages: "Mesajları oku",
                        request_to_speak: "Konuşmayı iste",
                        send_messages: "Mesaj gönder",
                        send_messages_in_threads: "Mesajları konuşma işlerine gönder",
                        send_polls: "Anketleri gönder",
                        send_tts_messages: "TTS mesajları gönder",
                        send_voice_messages: "Sesli mesajları gönder",
                        speak: "Konuş",
                        stream: "Akış",
                        use_application_commands: "Uygulama komutlarını kullan",
                        use_embedded_activities: "Kullanıcı etkinliklerini kullan",
                        use_external_apps: "Harici uygulamaları kullan",
                        use_external_emojis: "Harici emojileri kullan",
                        use_external_sounds: "Harici sesleri kullan",
                        use_external_stickers: "Harici stickerleri kullan",
                        use_soundboard: "Ses panosunu kullan",
                        use_voice_activation: "Ses aktivasyonunu kullan",
                        view_audit_log: "Denetim günlüğünü görüntüle",
                        view_channel: "Kanalı görüntüle",
                        view_creator_monetization_analytics: "Oluşturucu monetizasyon analizini görüntüle",
                        view_guild_insights: "Guild analizini görüntüle",
                        userPopover: {
                            memberSince: "Üyelik tarihi"
                        }
                    }
                },
                uk: {
                    themes: {
                        light: "Світлий",
                        dark: "Темний",
                        midnight: "Опівніч",
                        pink: "Рожевий",
                        red: "Червоний",
                        fire: "Вогонь",
                        underwater: "Під водою",
                        neonNight: "Неонова ніч",
                        highContrastDark: "Високий контраст темний",
                        highContrastLight: "Високий контраст світлий"
                    },
                    searchPlaceholder: "Шукати повідомлення або відправників",
                    popover: {
                        members: "Учасники",
                        permissions: "Права"
                    },
                    channelPopover: {
                        viewChannel: "Перегляд каналів",
                        topic: "Тема",
                        typeChannel: "Канал"
                    },
                    ticket: {
                        title: "Тикет {number}",
                        createdBy: "Створений",
                        at: "в"
                    },
                    permissions: {
                        add_reaction: "Додати реакцію",
                        administrator: "Адміністратор",
                        attach_files: "Додати файли",
                        ban_members: "Забанити учасників",
                        change_nickname: "Змінити нікнейм",
                        connect: "Підключитися",
                        create_events: "Створити події",
                        create_expressions: "Створити вирази",
                        create_instant_invite: "Створити миттєву запрошення",
                        create_polls: "Створити опитування",
                        create_private_threads: "Створити приватні теми",
                        create_public_threads: "Створити публічні теми",
                        deafen_members: "Заглушити учасників",
                        embed_links: "Вставити посилання",
                        external_emojis: "Використовувати зовнішні емодзі",
                        external_stickers: "Використовувати зовнішні стикери",
                        kick_members: "Вигнати учасників",
                        manage_channels: "Управляти каналами",
                        manage_emojis: "Управляти емодзі",
                        manage_stickers: "Управляти стикерами",
                        manage_emojis_and_stickers: "Управляти емодзі та стикерами",
                        manage_events: "Управляти подіями",
                        manage_expressions: "Управляти виразами",
                        manage_guild: "Управляти гільдією",
                        manage_messages: "Управляти повідомленнями",
                        manage_nicknames: "Управляти ніками",
                        manage_permissions: "Управляти правами",
                        manage_roles: "Управляти ролями",
                        manage_threads: "Управляти темами",
                        manage_webhooks: "Управляти вебхуками",
                        mention_everyone: "Згадати всіх",
                        moderate_members: "Модерати учасників",
                        move_members: "Перемістити учасників",
                        mute_members: "Заглушити учасників",
                        priority_speaker: "Оповідач пріоритету",
                        read_message_history: "Читати історію повідомлень",
                        read_messages: "Читати повідомлення",
                        request_to_speak: "Запросити говорити",
                        send_messages: "Надіслати повідомлення",
                        send_messages_in_threads: "Надіслати повідомлення в теми",
                        send_polls: "Надіслати опитування",
                        send_tts_messages: "Надіслати TTS повідомлення",
                        send_voice_messages: "Надіслати мовні повідомлення",
                        speak: "Говорити",
                        stream: "Стримувати",
                        use_application_commands: "Використовувати команди додатку",
                        use_embedded_activities: "Використовувати вбудовані активності",
                        use_external_apps: "Використовувати зовнішні додатки",
                        use_external_emojis: "Використовувати зовнішні емодзі",
                        use_external_sounds: "Використовувати зовнішні звуки",
                        use_external_stickers: "Використовувати зовнішні стикери",
                        use_soundboard: "Використовувати звукову панель",
                        use_voice_activation: "Використовувати активацію мови",
                        view_audit_log: "Переглядати журнал аудиту",
                        view_channel: "Переглядати канал",
                        view_creator_monetization_analytics: "Переглядати аналіз монетизації творців",
                        view_guild_insights: "Переглядати аналіз гільдії",
                        userPopover: {
                            memberSince: "Учасник з"
                        }
                    }
                },
                vi: {
                    themes: {
                        light: "Sáng",
                        dark: "Tối",
                        midnight: "Nửa đêm",
                        pink: "Hồng",
                        red: "Đỏ",
                        fire: "Lửa",
                        underwater: "Dưới nước",
                        neonNight: "Đêm neon",
                        highContrastDark: "Tương phản cao tối",
                        highContrastLight: "Tương phản cao sáng"
                    },
                    ticket: {
                        title: "Ticket {number}",
                        createdBy: "Tạo bởi",
                        at: "lúc"
                    },
                    searchPlaceholder: "Tìm kiếm tin nhắn hoặc người gửi",
                    popover: {
                        members: "Thành viên",
                        permissions: "Quyền"
                    },
                    channelPopover: {
                        viewChannel: "Xem kênh",
                        topic: "Chủ đề",
                        typeChannel: "Kênh"
                    },
                    permissions: {
                        add_reaction: "Thêm phản ứng",
                        administrator: "Quản trị viên",
                        attach_files: "Đính kèm tài liệu",
                        ban_members: "Cấm thành viên",
                        change_nickname: "Đổi tên đăng nhập",
                        connect: "Kết nối",
                        create_events: "Tạo sự kiện",
                        create_expressions: "Tạo biểu thức",
                        create_instant_invite: "Tạo lời mời ngay",
                        create_polls: "Tạo khảo sát",
                        create_private_threads: "Tạo chủ đề riêng tư",
                        create_public_threads: "Tạo chủ đề công khai",
                        deafen_members: "Ngừng âm thanh thành viên",
                        embed_links: "Chèn liên kết",
                        external_emojis: "Sử dụng biểu tượng emoji ngoài",
                        external_stickers: "Sử dụng sticker ngoài",
                        kick_members: "Kick thành viên",
                        manage_channels: "Quản lý kênh",
                        manage_emojis: "Quản lý emoji",
                        manage_stickers: "Quản lý sticker",
                        manage_emojis_and_stickers: "Quản lý emoji và sticker",
                        manage_events: "Quản lý sự kiện",
                        manage_expressions: "Quản lý biểu thức",
                        manage_guild: "Quản lý gilde",
                        manage_messages: "Quản lý tin nhắn",
                        manage_nicknames: "Quản lý tên đăng nhập",
                        manage_permissions: "Quản lý quyền",
                        manage_roles: "Quản lý vai trò",
                        manage_threads: "Quản lý chủ đề",
                        manage_webhooks: "Quản lý webhook",
                        mention_everyone: "Nhắc đến tất cả",
                        moderate_members: "Kiểm soát thành viên",
                        move_members: "Di chuyển thành viên",
                        mute_members: "Ngừng âm thanh thành viên",
                        priority_speaker: "Người nói ưu tiên",
                        read_message_history: "Đọc lịch sử tin nhắn",
                        read_messages: "Đọc tin nhắn",
                        request_to_speak: "Yêu cầu nói",
                        send_messages: "Gửi tin nhắn",
                        send_messages_in_threads: "Gửi tin nhắn vào chủ đề",
                        send_polls: "Gửi khảo sát",
                        send_tts_messages: "Gửi tin nhắn TTS",
                        send_voice_messages: "Gửi tin nhắn giọng",
                        speak: "Nói",
                        stream: "Stream",
                        use_application_commands: "Sử dụng lệnh ứng dụng",
                        use_embedded_activities: "Sử dụng hoạt động nhúng",
                        use_external_apps: "Sử dụng ứng dụng bên ngoài",
                        use_external_emojis: "Sử dụng emoji bên ngoài",
                        use_external_sounds: "Sử dụng âm thanh bên ngoài",
                        use_external_stickers: "Sử dụng sticker bên ngoài",
                        use_soundboard: "Sử dụng bảng âm thanh",
                        use_voice_activation: "Sử dụng kích hoạt giọng",
                        view_audit_log: "Xem nhật ký kiểm tra",
                        view_channel: "Xem kênh",
                        view_creator_monetization_analytics: "Xem phân tích phát triển doanh thu tác giả",
                        view_guild_insights: "Xem thống kê gilde",
                        userPopover: {
                            memberSince: "Thành viên từ"
                        }
                    }
                }
            };

            function updateTicketText() {
                const currentLang = document.getElementById('languageSelector').value;
                const ticketNumber = document.querySelector('.ticket-title').getAttribute('data-ticket-number');

                console.log(currentLang);
                console.log(translations[currentLang].ticket);
                console.log(ticketNumber);
                console.log(translations[currentLang].ticket.title.replace('{number}', ticketNumber));

                // Update ticket title
                document.querySelector('.ticket-title').textContent =
                    translations[currentLang].ticket.title.replace('{number}', ticketNumber);

                // Update created by text
                document.querySelector('.ticket-created-by').textContent =
                    translations[currentLang].ticket.createdBy;

                // Update at text
                document.querySelector('.ticket-created-at').textContent =
                    translations[currentLang].ticket.at;
            }

            function updateLocalization() {
                const language = document.getElementById('languageSelector').value;
                const themeSelector = document.getElementById('themeSelector');
                const searchInput = document.getElementById('searchInput');

                themeSelector.innerHTML = '';
                for (const [key, value] of Object.entries(translations[language].themes)) {
                    const option = document.createElement('option');
                    option.value = key;
                    option.textContent = value;
                    if (key === 'fire') option.selected = true;
                    themeSelector.appendChild(option);
                }

                updateTicketText();

                searchInput.placeholder = translations[language].searchPlaceholder;
            }

            document.addEventListener('DOMContentLoaded', () => {
                updateLocalization();
                replaceAllMentions();
            });

            function searchMessages() {
                const input = document.getElementById('searchInput').value.toLowerCase();
                const messages = document.querySelectorAll('.message');

                messages.forEach(message => {
                    const username = message.querySelector('.username').textContent.toLowerCase();
                    const text = message.querySelector('.text').textContent.toLowerCase();
                    const nameElement = message.querySelector('.name');
                    const name = nameElement ? nameElement.textContent.toLowerCase() : '';

                    if (username.includes(input) || text.includes(input) || name.includes(input)) {
                        message.style.display = '';
                    } else {
                        message.style.display = 'none';
                    }
                });
            }

            function changeTheme() {
                const theme = document.getElementById('themeSelector').value;
                document.body.className = theme;
            }
            function replaceAllMentions() {
                const messages = document.querySelectorAll('.message .text');

                messages.forEach((message, index) => {
                    let html = message.innerHTML;
                    // Replace role mentions
                    roles.forEach(role => {
                        const roleMention = `<@&${role.id}>`;
                        const encodedRoleMention = `&lt;@&amp;${role.id}&gt;`;
                        const roleElement = `<span class="role-mention role-${role.id}" data-role-id="${role.id}" style="color: ${role.color}; background-color: ${role.color}1A">@${role.name}</span>`;

                        while (html.includes(roleMention) || html.includes(encodedRoleMention)) {
                            html = html.replace(encodedRoleMention, roleElement)
                                .replace(roleMention, roleElement);
                        }
                    });

                    // Replace user mentions
                    users.forEach(user => {
                        const userMention = `<@${user.id}>`;
                        const encodedUserMention = `&lt;@${user.id}&gt;`;
                        const userElement = `<span class="user-mention" data-user-id="${user.id}">@${user.displayname}</span>`;

                        while (html.includes(userMention) || html.includes(encodedUserMention)) {
                            html = html.replace(encodedUserMention, userElement)
                                .replace(userMention, userElement);
                        }
                    });

                    // Replace channel mentions
                    channels.forEach(channel => {
                        const channelMention = `<#${channel.id}>`;
                        const encodedChannelMention = `&lt;#${channel.id}&gt;`;
                        const channelElement = `<span class="channel-mention ${channel.type}-channel" data-channel-id="${channel.id}"><span class="channel-hash">#</span>${channel.name}</span>`;

                        while (html.includes(channelMention) || html.includes(encodedChannelMention)) {
                            html = html.replace(encodedChannelMention, channelElement)
                                .replace(channelMention, channelElement);
                        }
                    });

                    message.innerHTML = html;
                    message.querySelectorAll('.role-mention').forEach(mention => {
                        mention.addEventListener('click', (event) => {
                            event.stopPropagation();
                            const roleId = mention.getAttribute('data-role-id');
                            const role = roles.find(r => r.id === roleId);
                            if (role) {
                                showRolePopover(role, event);
                            }
                        });
                    });

                    message.querySelectorAll('.user-mention').forEach(mention => {
                        mention.addEventListener('click', (event) => {
                            event.stopPropagation();
                            const userId = mention.getAttribute('data-user-id');
                            const user = users.find(u => u.id === userId);
                            if (user) {
                                showUserPopover(user, event);
                            }
                        });
                    });

                    message.querySelectorAll('.channel-mention').forEach(mention => {
                        mention.addEventListener('click', (event) => {
                            event.stopPropagation();
                            const channelId = mention.getAttribute('data-channel-id');
                            const channel = channels.find(c => c.id === channelId);
                            if (channel) {
                                showChannelPopover(channel, event);
                            }
                        });
                    });
                });
            }

            document.addEventListener('DOMContentLoaded', () => {
                replaceAllMentions();
            });

            const mentionStyles = document.createElement('style');
            mentionStyles.textContent = `
            .role-mention, .user-mention, .channel-mention {
                cursor: pointer;
                padding: 0 4px;
                border-radius: 3px;
                font-weight: 500;
                display: inline-block;
            }
            
            .user-mention {
                background-color: rgba(88, 101, 242, 0.15);
                color: var(--brand);
            }
            
            .channel-mention {
                background-color: rgba(35, 165, 89, 0.15);
                color: var(--brand);
            }
            
            .role-mention:hover, .user-mention:hover, .channel-mention:hover {
                opacity: 0.8;
            }
        `;
            document.head.appendChild(mentionStyles);

            function showRolePopover(role, event) {
                event.preventDefault();
                event.stopPropagation();

                const existingPopovers = document.querySelectorAll('.role-popover, .user-popover, .channel-popover');
                existingPopovers.forEach(p => p.remove());

                const currentLang = document.getElementById('languageSelector').value;
                const t = translations[currentLang] || translations['en'];

                const popover = document.createElement('div');
                popover.className = 'role-popover'; popover.innerHTML = `
                <div class="role-popover-header">
                    <h3 class="role-popover-title">@${role.name}</h3>
                </div>
                
                <div class="role-popover-section">
                    <div class="role-popover-label">${t.popover.members}</div>
                    <div class="role-member-list">
                        ${role.members.map(member => `
                            <span class="role-member">${member}</span>
                        `).join('')}
                    </div>
                </div>
                
                <div class="role-popover-section">
                    <div class="role-popover-label">${t.popover.permissions}</div>
                    <div class="role-popover-value">
                        ${role.permissions.map(permission => `
                            <span class="role-permission">${t.permissions[permission] || permission}</span>
                        `).join('')}
                    </div>
                </div>
            `;

                document.body.appendChild(popover);

                const rect = event.target.getBoundingClientRect();
                popover.style.position = 'fixed';
                popover.style.left = `${rect.left}px`;
                popover.style.top = `${rect.bottom + 8}px`;

                setTimeout(() => {
                    document.addEventListener('click', function closePopover(e) {
                        if (!popover.contains(e.target) && !e.target.matches('.role-mention')) {
                            popover.remove();
                            document.removeEventListener('click', closePopover);
                        }
                    });
                }, 0);
            }

            function showTitleUserPopover(event, element) {
                const userId = element.getAttribute('data-user-id');
                showUserPopover(users.find(user => user.id === userId), event);
            }

            function showUserPopover(user, event) {
                event.preventDefault();
                event.stopPropagation();

                document.querySelectorAll('.role-popover, .user-popover, .channel-popover').forEach(p => p.remove());

                const currentLang = document.getElementById('languageSelector').value;
                const t = translations[currentLang] || translations['en'];

                const userRoles = user.roles
                    .map(roleId => roles.find(r => r.id === roleId))
                    .filter(role => role !== undefined);

                const popover = document.createElement('div');
                popover.className = 'user-popover';
                popover.innerHTML = `
        <div class="user-info">
            <img src="${user.avatar}" alt="${user.displayname}" class="user-avatar">
            <div class="user-header">
                <div class="user-name">${user.displayname}</div>
                <div class="user-tag">${user.username}</div>
            </div>
            ${userRoles.length > 0 ? `
                <div class="user-roles">
                    ${userRoles.map(role => `
                        <span class="user-role" style="color: ${role.color}">
                            ${role.name}
                        </span>
                    `).join('')}
                </div>
            ` : ''}
            <div class="user-joined">
                ${t.permissions.userPopover.memberSince} ${new Date(user.createdAt).toLocaleDateString()}
            </div>
        </div>
    `;

                const rect = event.target.getBoundingClientRect();
                popover.style.position = 'fixed';
                popover.style.left = `${rect.left}px`;
                popover.style.top = `${rect.bottom + 8}px`;

                document.body.appendChild(popover);
                const popoverRect = popover.getBoundingClientRect();
                if (popoverRect.right > window.innerWidth) {
                    popover.style.left = `${window.innerWidth - popoverRect.width - 16}px`;
                }
                if (popoverRect.bottom > window.innerHeight) {
                    popover.style.top = `${rect.top - popoverRect.height - 8}px`;
                }

                // Close popover when clicking outside
                document.addEventListener('click', function closePopover(e) {
                    if (!popover.contains(e.target) && !e.target.classList.contains('user-mention')) {
                        popover.remove();
                        document.removeEventListener('click', closePopover);
                    }
                });
            }
            function showChannelPopover(channel, event) {
                event.stopPropagation();

                const existingPopover = document.querySelector('.channel-popover');
                if (existingPopover) {
                    existingPopover.remove();
                }

                const currentLang = document.getElementById('languageSelector').value;
                const t = translations[currentLang] || translations['en']; // Fallback to English

                const popover = document.createElement('div');
                popover.className = 'channel-popover';

                let typeIcon, typeColor;
                switch (channel.type) {
                    case 'text':
                        typeIcon = '#';
                        typeColor = 'var(--text-muted)';
                        break;
                    case 'announcement':
                        typeIcon = '📢';
                        typeColor = 'var(--info)';
                        break;
                    case 'voice':
                        typeIcon = '🔊';
                        typeColor = 'var(--online)';
                        break;
                    case 'forum':
                        typeIcon = '📋';
                        typeColor = 'var(--brand)';
                        break;
                    default:
                        typeIcon = '#';
                        typeColor = 'var(--text-muted)';
                }

                popover.innerHTML = `
        <div class="channel-popover-header">
            <div class="channel-icon" style="color: ${typeColor}">${typeIcon}</div>
            <div class="channel-info">
                <h3 class="channel-popover-title">${channel.name}</h3>
                <div class="channel-type">${channel.type.charAt(0).toUpperCase() + channel.type.slice(1)} ${t.channelPopover.typeChannel}</div>
            </div>
        </div>
        ${channel.topic ? `
            <div class="channel-topic">
                <div class="topic-label">${t.channelPopover.topic}</div>
                <div class="topic-content">${channel.topic}</div>
            </div>
        ` : ''}
        <div class="channel-actions">
            <button class="action-button primary" onclick="window.location.href='${channel.url}'">${t.channelPopover.viewChannel}</button>
        </div>
    `;
                const rect = event.target.getBoundingClientRect();
                popover.style.position = 'fixed';
                popover.style.left = `${rect.left}px`;
                popover.style.top = `${rect.bottom + 8}px`;

                document.body.appendChild(popover);
                const popoverRect = popover.getBoundingClientRect();
                if (popoverRect.right > window.innerWidth) {
                    popover.style.left = `${window.innerWidth - popoverRect.width - 16}px`;
                }
                if (popoverRect.bottom > window.innerHeight) {
                    popover.style.top = `${rect.top - popoverRect.height - 8}px`;
                }

                document.addEventListener('click', function closePopover(e) {
                    if (!popover.contains(e.target) && !e.target.classList.contains('channel-mention')) {
                        popover.remove();
                        document.removeEventListener('click', closePopover);
                    }
                });
            }
        </script>
</body>

</html>
"""
    return html
