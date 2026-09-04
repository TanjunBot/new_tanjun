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

        # Determine voice channel: specified parameter or the user's current voice channel
        target_voice_channel: Optional[discord.VoiceChannel | discord.StageChannel] = voice_channel
        if target_voice_channel is None and isinstance(interaction.user, discord.Member):
            if interaction.user.voice and interaction.user.voice.channel:
                vc = interaction.user.voice.channel
                if isinstance(vc, (discord.VoiceChannel, discord.StageChannel)):
                    target_voice_channel = vc

        # Base URL from config or fallback
        base_url = config.activity_public_url.rstrip("/") if config.activity_public_url else f"http://localhost:{config.activity_server_port}"
        web_game_url = f"{base_url}/activity?session={session.session_id}"

        # Create standard Discord Activity Voice Channel Invite
        invite_url: Optional[str] = None
        invite_error: Optional[str] = None
        if target_voice_channel is not None and interaction.guild is not None:
            try:
                invite = await target_voice_channel.create_invite(
                    max_age=3600,
                    max_uses=0,
                    target_type=discord.InviteTarget.embedded_application,
                    target_application_id=int(config.applicationId),
                    reason=f"Discord Activity {game.name} gestartet von {interaction.user}"
                )
                invite_url = invite.url
            except discord.Forbidden:
                invite_error = "Fehlende Berechtigung 'Einladung erstellen' im Sprachkanal."
            except Exception as e:
                logger.warning("Could not create Discord embedded_application invite: %s", e)
                invite_error = str(e)

        title = f"🎮 Discord Activity: {game.name}"
        description = (
            f"**{interaction.user.mention}** hat ein Multiplayer-Spiel gestartet!\n\n"
            f"🔹 **Spiel:** {game.name}\n"
            f"🔹 **Sitzungs-ID:** `{session.session_id}`\n"
            f"🔹 **Multiplayer:** 2 Spieler (oder 1 vs. Tanjun Bot)\n"
        )

        if target_voice_channel is not None:
            description += f"🔹 **Sprachkanal:** {target_voice_channel.mention}\n\n"
        else:
            description += f"🔹 **Tipp:** Tritt einem Sprachkanal bei, um die Activity direkt in Discord zu spielen!\n\n"

        if invite_url:
            description += f"🚀 **[Klicke hier, um im Sprachkanal zu starten!]({invite_url})**\n"
        elif invite_error:
            description += f"⚠️ *Sprachkanal-Start nicht möglich: {invite_error}*\n"

        description += f"🌐 **[Alternativ im Browser / Web öffnen]({web_game_url})**"

        embed = utility.tanjunEmbed(
            title=title,
            description=description
        )

        view = discord.ui.View()
        if invite_url:
            view.add_item(discord.ui.Button(label="In Discord starten (Voice)", url=invite_url, style=discord.ButtonStyle.link, emoji="🚀"))
        view.add_item(discord.ui.Button(label="Im Browser öffnen", url=web_game_url, style=discord.ButtonStyle.link, emoji="🌐"))

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
