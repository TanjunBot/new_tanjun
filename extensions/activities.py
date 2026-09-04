"""Discord Activity extension for Tanjun Bot.

Manages the Activity web server lifecycle and provides Discord slash commands
to launch multiplayer activity games in voice or text channels.
"""

from __future__ import annotations

import logging
from typing import Optional, cast

import discord
from discord import app_commands
from discord.ext import commands

from activities.base import Player
from activities.manager import session_manager
from activities.server import ActivityServer
import config
import utility

logger = logging.getLogger(__name__)


class ActivityCommands(app_commands.Group):
    """Slash commands for Discord Activities."""

    @app_commands.command(
        name="launch",
        description="Starte eine Discord Activity / Multiplayer-Spiel"
    )
    @app_commands.describe(
        game="Das gewünschte Spiel",
        voice_channel="Optional: Sprachkanal für die Activity"
    )
    @app_commands.choices(
        game=[
            app_commands.Choice(name="Tic-Tac-Toe (Multiplayer & Bot)", value="tictactoe")
        ]
    )
    async def launch_activity(
        self,
        interaction: discord.Interaction,
        game: app_commands.Choice[str],
        voice_channel: Optional[discord.VoiceChannel] = None
    ) -> None:
        await interaction.response.defer()

        host = Player(
            user_id=str(interaction.user.id),
            username=interaction.user.name,
            display_name=interaction.user.display_name,
            avatar_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
            is_host=True
        )

        session = session_manager.create_session(game_type=game.value, host=host)

        # Base URL from config or fallback
        base_url = config.activity_public_url.rstrip("/") if config.activity_public_url else f"http://localhost:{config.activity_server_port}"
        web_game_url = f"{base_url}/activity?session={session.session_id}"

        # If voice channel provided, try to create standard Discord Activity Invite
        invite_url: Optional[str] = None
        if voice_channel is not None and interaction.guild is not None:
            try:
                # Target type 2 is Embedded Application
                invite = await voice_channel.create_invite(
                    max_age=3600,
                    max_uses=0,
                    target_type=discord.InviteTarget.embedded_application,
                    target_application_id=int(config.applicationId),
                    reason=f"Discord Activity {game.name} gestartet von {interaction.user}"
                )
                invite_url = invite.url
            except Exception as e:
                logger.debug("Could not create Discord embedded_application invite: %s", e)

        title = f"🎮 Discord Activity: {game.name}"
        description = (
            f"**{interaction.user.mention}** hat eine neue Spielrunde gestartet!\n\n"
            f"🔹 **Spiel:** {game.name}\n"
            f"🔹 **Sitzungs-ID:** `{session.session_id}`\n"
            f"🔹 **Multiplayer:** 2 Spieler (oder 1 vs. Tanjun Bot)\n\n"
        )

        if invite_url:
            description += f"👉 **[Im Sprachkanal beitreten]({invite_url})**\n"

        description += f"🌐 **[Im Browser / Activity Web öffnen]({web_game_url})**"

        embed = utility.tanjunEmbed(
            title=title,
            description=description
        )

        view = discord.ui.View()
        if invite_url:
            view.add_item(discord.ui.Button(label="In Discord Sprachkanal starten", url=invite_url, style=discord.ButtonStyle.link, emoji="🎮"))
        view.add_item(discord.ui.Button(label="Spiel öffnen (Web App)", url=web_game_url, style=discord.ButtonStyle.link, emoji="🌐"))

        await interaction.followup.send(embed=embed, view=view)


class ActivitiesCog(commands.Cog):
    """Cog managing the Discord Activities web server and commands."""

    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.activity_server: ActivityServer = ActivityServer(
            host=config.activity_server_host,
            port=config.activity_server_port
        )

    async def cog_load(self) -> None:
        await self.activity_server.start()

    async def cog_unload(self) -> None:
        await self.activity_server.stop()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        activity_group = ActivityCommands(name="activity", description="Spiele und Discord Activities")
        if self.bot.tree:
            self.bot.tree.add_command(activity_group)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ActivitiesCog(bot))
