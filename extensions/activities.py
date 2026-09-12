"""Discord Activity extension for Tanjun Bot.

Manages the Activity web server lifecycle and provides Discord slash commands
to launch multiplayer activity games in voice or text channels.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, cast

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
            app_commands.Choice(name="Tanjun Game Hub (Lobby & alle Spiele)", value="hub"),
            app_commands.Choice(name="Tanjun Voice Cup (Turnier-Modus)", value="tournament"),
            app_commands.Choice(name="Tic-Tac-Toe (3x3)", value="tictactoe"),
            app_commands.Choice(name="Vier Gewinnt (7x6)", value="connect4"),
            app_commands.Choice(name="Schere Stein Papier (Best of 5)", value="rps"),
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
            f"🔹 **Multiplayer:** Bis zu 16 Spieler (Turnier) bzw. 2 Spieler\n"
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

    @app_commands.command(
        name="tournament",
        description="Starte ein Community-Turnier / Event (Mehrkampf) mit Belohnungen"
    )
    @app_commands.describe(
        title="Titel des Turniers (z. B. Tanjun Cup)",
        mode="Format: Mehrkampf (alle Spiele) oder Einzelsportart",
        rounds="Anzahl der Runden (1-10, Standard: 3)",
        voice_channel="Sprachkanal für das Event (Standard: dein aktueller Voice-Kanal)",
        announcement_channel="Kanal für die Siegerehrung (Standard: aktueller Textkanal)",
        reward_role="Optional: Rolle für Platz 1 (erfordert 'Rollen verwalten')",
        reward_xp_1st="XP für Platz 1 (erfordert 'Server verwalten', max. 5000)",
        reward_xp_2nd="XP für Platz 2 (erfordert 'Server verwalten', max. 5000)",
        reward_xp_3rd="XP für Platz 3 (erfordert 'Server verwalten', max. 5000)",
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="Mehrkampf (Alle Spiele: 3x3, 4-Gewinnt, RPS)", value="mehrkampf"),
            app_commands.Choice(name="Nur Vier Gewinnt", value="connect4"),
            app_commands.Choice(name="Nur Tic-Tac-Toe", value="tictactoe"),
            app_commands.Choice(name="Nur Schere Stein Papier", value="rps"),
            app_commands.Choice(name="Zufallsmix je Runde", value="random"),
        ]
    )
    async def create_tournament(
        self,
        interaction: discord.Interaction,
        title: str = "Tanjun Cup",
        mode: str = "mehrkampf",
        rounds: app_commands.Range[int, 1, 10] = 3,
        voice_channel: Optional[discord.VoiceChannel] = None,
        announcement_channel: Optional[discord.TextChannel] = None,
        reward_role: Optional[discord.Role] = None,
        reward_xp_1st: app_commands.Range[int, 0, 5000] = 0,
        reward_xp_2nd: app_commands.Range[int, 0, 5000] = 0,
        reward_xp_3rd: app_commands.Range[int, 0, 5000] = 0,
    ) -> None:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "Dieser Befehl kann nur auf einem Discord-Server verwendet werden.",
                ephemeral=True
            )
            return

        # 1. Permission Check: XP Rewards require manage_guild or administrator
        can_grant_xp = False
        has_xp_rewards = (reward_xp_1st > 0 or reward_xp_2nd > 0 or reward_xp_3rd > 0)
        if has_xp_rewards:
            if not (interaction.user.guild_permissions.manage_guild or interaction.user.guild_permissions.administrator):
                embed = utility.tanjunEmbed(
                    title="⛔ Fehlende Berechtigung für XP-Belohnungen",
                    description=(
                        "Du benötigst die Berechtigung **Server verwalten** (`manage_guild`) "
                        "oder **Administrator**, um Server-XP als Turniergewinn zu vergeben!"
                    )
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            can_grant_xp = True

        # 2. Permission Check: Role Reward requires manage_roles and proper hierarchy
        can_grant_role = False
        if reward_role is not None:
            if not (interaction.user.guild_permissions.manage_roles or interaction.user.guild_permissions.administrator):
                embed = utility.tanjunEmbed(
                    title="⛔ Fehlende Berechtigung für Rollenvergabe",
                    description=(
                        "Du benötigst die Berechtigung **Rollen verwalten** (`manage_roles`), "
                        "um eine Siegerrolle zu konfigurieren!"
                    )
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if not interaction.guild.me.guild_permissions.manage_roles:
                embed = utility.tanjunEmbed(
                    title="⛔ Dem Bot fehlt Berechtigung",
                    description="Dem Bot fehlt die Berechtigung **Rollen verwalten** (`manage_roles`)."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if interaction.guild.me.top_role <= reward_role:
                embed = utility.tanjunEmbed(
                    title="⛔ Rollenhierarchie-Fehler",
                    description=f"Die gewählte Rolle {reward_role.mention} steht über oder auf gleicher Höhe mit der höchsten Rolle des Bots."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if interaction.user.id != interaction.guild.owner_id and interaction.user.top_role <= reward_role:
                embed = utility.tanjunEmbed(
                    title="⛔ Rollenhierarchie-Fehler",
                    description=f"Die gewählte Rolle {reward_role.mention} steht über oder auf gleicher Höhe mit deiner höchsten Rolle."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            can_grant_role = True

        await interaction.response.defer()

        # Clamp numerical limits server-side
        rounds = max(1, min(10, int(rounds)))
        reward_xp_1st = max(0, min(5000, int(reward_xp_1st)))
        reward_xp_2nd = max(0, min(5000, int(reward_xp_2nd)))
        reward_xp_3rd = max(0, min(5000, int(reward_xp_3rd)))

        # Create host participant and session
        host = Player(
            user_id=str(interaction.user.id),
            username=interaction.user.name,
            display_name=interaction.user.display_name,
            avatar_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None,
            is_host=True
        )

        session = session_manager.create_session(game_type="tournament", host=host)
        tourney = session.tournament
        tourney.title = title[:32]
        tourney.total_rounds = rounds

        # Mode setup
        if mode == "mehrkampf":
            tourney.game_selection = "playlist"
            tourney.disciplines = ["tictactoe", "connect4", "rps"]
            mode_label = "🎖️ Mehrkampf (Tic-Tac-Toe → Vier Gewinnt → RPS)"
        elif mode == "random":
            tourney.game_selection = "random"
            mode_label = "🎲 Zufallsmix je Runde"
        else:
            tourney.game_selection = "single"
            tourney.selected_game = mode
            tourney.disciplines = [mode]
            game_names = {"connect4": "Vier Gewinnt", "tictactoe": "Tic-Tac-Toe", "rps": "Schere Stein Papier"}
            mode_label = f"🎮 {game_names.get(mode, mode)}"

        # Rewards setup
        ann_channel = announcement_channel or (interaction.channel if isinstance(interaction.channel, discord.TextChannel) else None)
        from activities.tournament import TournamentRewards
        tourney.rewards = TournamentRewards(
            guild_id=str(interaction.guild.id),
            channel_id=str(ann_channel.id) if ann_channel else None,
            xp_1st=reward_xp_1st,
            xp_2nd=reward_xp_2nd,
            xp_3rd=reward_xp_3rd,
            role_id=str(reward_role.id) if reward_role else None,
            role_name=reward_role.name if reward_role else None,
            can_grant_xp=can_grant_xp,
            can_grant_role=can_grant_role
        )

        # Wire rewards dispatch callback when cup concludes
        bot_ref = interaction.client

        async def _on_finished_cb(t: Any) -> None:
            await _dispatch_tournament_rewards(bot_ref, t)

        tourney.on_finished_callback = _on_finished_cb

        # Resolve voice channel
        target_voice_channel: Optional[discord.VoiceChannel | discord.StageChannel] = voice_channel
        if target_voice_channel is None and isinstance(interaction.user, discord.Member):
            if interaction.user.voice and interaction.user.voice.channel:
                vc = interaction.user.voice.channel
                if isinstance(vc, (discord.VoiceChannel, discord.StageChannel)):
                    target_voice_channel = vc

        base_url = config.activity_public_url.rstrip("/") if config.activity_public_url else f"http://localhost:{config.activity_server_port}"
        web_game_url = f"{base_url}/activity?session={session.session_id}"

        # Create Discord embedded activity invite
        invite_url: Optional[str] = None
        invite_error: Optional[str] = None
        if target_voice_channel is not None and interaction.guild is not None:
            try:
                invite = await target_voice_channel.create_invite(
                    max_age=7200,
                    max_uses=0,
                    target_type=discord.InviteTarget.embedded_application,
                    target_application_id=int(config.applicationId),
                    reason=f"Turnier-Event {title} gestartet von {interaction.user}"
                )
                invite_url = invite.url
            except discord.Forbidden:
                invite_error = "Fehlende Berechtigung 'Einladung erstellen' im Sprachkanal."
            except Exception as e:
                logger.warning("Could not create embedded invite for tournament: %s", e)
                invite_error = str(e)

        # Format Rewards summary for description
        rewards_lines = []
        if can_grant_xp and has_xp_rewards:
            if reward_xp_1st > 0:
                rewards_lines.append(f"🥇 **Platz 1:** +{reward_xp_1st:,} Level-XP")
            if reward_xp_2nd > 0:
                rewards_lines.append(f"🥈 **Platz 2:** +{reward_xp_2nd:,} Level-XP")
            if reward_xp_3rd > 0:
                rewards_lines.append(f"🥉 **Platz 3:** +{reward_xp_3rd:,} Level-XP")
        if can_grant_role and reward_role:
            rewards_lines.append(f"👑 **Sieger-Rolle:** {reward_role.mention}")
        if not rewards_lines:
            rewards_lines.append("🏅 *Ruhm & Ehre (Keine Server-Belohnungen konfiguriert)*")

        rewards_text = "\n".join(rewards_lines)

        description = (
            f"**{interaction.user.mention}** hat ein offizielles Community-Turnier gestartet!\n\n"
            f"🏆 **Turnier:** `{title}`\n"
            f"🎮 **Format:** {mode_label}\n"
            f"🔄 **Runden:** `{rounds}` Runden\n"
            f"🔑 **Sitzungs-ID:** `{session.session_id}`\n\n"
            f"🎁 **Turnier-Belohnungen:**\n{rewards_text}\n\n"
        )

        if target_voice_channel is not None:
            description += f"🎙️ **Sprachkanal:** {target_voice_channel.mention}\n\n"
        else:
            description += f"💡 **Tipp:** Tritt einem Sprachkanal bei, um die Activity direkt in Discord zu starten!\n\n"

        if invite_url:
            description += f"🚀 **[Hier klicken, um dem Turnier im Voice beizutreten!]({invite_url})**\n"
        elif invite_error:
            description += f"⚠️ *Sprachkanal-Start nicht möglich: {invite_error}*\n"

        description += f"🌐 **[Alternativ im Browser / Web mitspielen]({web_game_url})**"

        embed = utility.tanjunEmbed(
            title=f"🏆 Community-Event: {title}",
            description=description
        )

        view = discord.ui.View()
        if invite_url:
            view.add_item(discord.ui.Button(label="In Discord beitreten (Voice)", url=invite_url, style=discord.ButtonStyle.link, emoji="🚀"))
        view.add_item(discord.ui.Button(label="Im Browser öffnen", url=web_game_url, style=discord.ButtonStyle.link, emoji="🌐"))

        await interaction.followup.send(embed=embed, view=view)


async def _dispatch_tournament_rewards(bot: Any, tourney: Any) -> None:
    """Awards configured XP and roles when a tournament finishes, and announces winners."""
    if not tourney or not hasattr(tourney, "rewards") or tourney.rewards.rewards_granted:
        return
    tourney.rewards.rewards_granted = True

    guild_id = tourney.rewards.guild_id
    channel_id = tourney.rewards.channel_id
    if not guild_id:
        return

    guild = bot.get_guild(int(guild_id))
    if not guild:
        return

    podium = tourney.get_podium()
    if not podium:
        return

    p1 = podium[0] if len(podium) > 0 else None
    p2 = podium[1] if len(podium) > 1 else None
    p3 = podium[2] if len(podium) > 2 else None

    # 1. Award XP
    granted_xp_lines = []
    if tourney.rewards.can_grant_xp:
        from api import update_user_xp
        placements = [
            (p1, tourney.rewards.xp_1st, "🥇"),
            (p2, tourney.rewards.xp_2nd, "🥈"),
            (p3, tourney.rewards.xp_3rd, "🥉")
        ]
        for p, xp, medal in placements:
            if p and xp > 0:
                try:
                    await update_user_xp(guild_id, p["user_id"], xp, respect_cooldown=False)
                    granted_xp_lines.append(f"{medal} **{p['display_name']}**: +{xp:,} XP")
                except Exception as exc:
                    logger.error("Failed to grant tournament XP to %s: %s", p["user_id"], exc)

    # 2. Award Role
    granted_role_line = None
    if tourney.rewards.can_grant_role and tourney.rewards.role_id and str(tourney.rewards.role_id).isdigit() and p1 and str(p1["user_id"]).isdigit():
        role = guild.get_role(int(tourney.rewards.role_id))
        if role:
            try:
                member = guild.get_member(int(p1["user_id"]))
                if not member:
                    member = await guild.fetch_member(int(p1["user_id"]))
                if member and role not in member.roles:
                    await member.add_roles(role, reason=f"Turniersieg: {tourney.title}")
                    granted_role_line = f"👑 Rolle {role.mention} an {member.mention} verliehen!"
            except Exception as exc:
                logger.error("Failed to assign tournament reward role to %s: %s", p1["user_id"], exc)

    # 3. Channel Announcement Embed
    if channel_id and str(channel_id).isdigit():
        target_channel = guild.get_channel(int(channel_id))
        if target_channel and isinstance(target_channel, discord.TextChannel):
            p1_mention = f"<@{p1['user_id']}>" if str(p1['user_id']).isdigit() else p1['display_name']
            desc = (
                f"Das Community-Event **{tourney.title}** ist offiziell beendet!\n\n"
                f"🏆 **Die Gewinner:**\n"
                f"🥇 1. Platz: **{p1_mention}** ({p1['score']} Punkte)\n"
            )
            if p2:
                p2_mention = f"<@{p2['user_id']}>" if str(p2['user_id']).isdigit() else p2['display_name']
                desc += f"🥈 2. Platz: **{p2_mention}** ({p2['score']} Punkte)\n"
            if p3:
                p3_mention = f"<@{p3['user_id']}>" if str(p3['user_id']).isdigit() else p3['display_name']
                desc += f"🥉 3. Platz: **{p3_mention}** ({p3['score']} Punkte)\n"

            if granted_xp_lines:
                desc += f"\n✨ **Level-XP vergeben:**\n" + "\n".join(granted_xp_lines) + "\n"
            if granted_role_line:
                desc += f"\n" + granted_role_line + "\n"

            embed = utility.tanjunEmbed(
                title=f"🎉 Siegerehrung: {tourney.title}",
                description=desc
            )
            try:
                await target_channel.send(embed=embed)
            except Exception as exc:
                logger.error("Could not post tournament victory announcement: %s", exc)


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

        # Register the PRIMARY_ENTRY_POINT command (type 4) via Discord REST API.
        # This is required so the Activity can be launched from the Discord Activities shelf.
        # handler=2 (DISCORD_LAUNCH_ACTIVITY) means Discord handles the launch automatically.
        await self._register_entry_point_command()

    async def _register_entry_point_command(self) -> None:
        """Register or update the Activity Entry Point command via Discord REST API."""
        import aiohttp

        application_id = config.applicationId
        bot_token = config.token
        if not application_id or not bot_token:
            logger.warning("[Activities] Cannot register Entry Point command: missing applicationId or botToken in config.")
            return

        url = f"https://discord.com/api/v10/applications/{application_id}/commands"
        payload = {
            "type": 4,           # PRIMARY_ENTRY_POINT
            "name": "launch",    # Shown as button label in Discord Activities shelf
            "description": "Tanjun Activity starten",
            "handler": 2         # DISCORD_LAUNCH_ACTIVITY — Discord handles the launch
        }
        headers = {
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status in (200, 201):
                        logger.info("[Activities] Entry Point command registered successfully (status %s).", resp.status)
                    else:
                        body = await resp.text()
                        logger.warning("[Activities] Entry Point command registration failed (status %s): %s", resp.status, body)
        except Exception as exc:
            logger.error("[Activities] Error registering Entry Point command: %s", exc)


async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(ActivitiesCog(bot))
