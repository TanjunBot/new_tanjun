"""
Interactive setup wizards for complex features.
Provides guided, step-by-step configuration using modals and buttons.
"""

from typing import Any, cast

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput, View

import utility
from api import (
    get_log_channel as api_get_log_channel,
    get_log_enable as api_get_log_enable,
    set_log_channel as api_set_log_channel,
    set_log_enable as api_set_log_enable,
    get_level_system_status as api_get_level_system_status,
    set_level_system_status as api_set_level_system_status,
    set_levelup_channel as api_set_levelup_channel,
    set_xp_scaling as api_set_xp_scaling,
    set_text_cooldown as api_set_text_cooldown,
    set_voice_cooldown as api_set_voice_cooldown,
)
from localizer import tanjunLocalizer
from services.booster_service import BoosterService, BoosterType

# ---------------------------------------------------------------------------
# Wizard session state
# ---------------------------------------------------------------------------

_WIZARD_SESSION_TIMEOUT = 600  # 10 minutes


def _require_admin(interaction: discord.Interaction) -> bool:
    """Check if the user has administrator permissions."""
    if (
        isinstance(interaction.user, discord.Member)
        and isinstance(interaction.channel, discord.abc.GuildChannel)
        and not interaction.channel.permissions_for(interaction.user).administrator
    ):
        return False
    return True


async def _not_admin_reply(interaction: discord.Interaction) -> None:
    """Send a permission-denied embed."""
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize("en_US", "commands.admin.embed.missingPermission.title"),
        description=tanjunLocalizer.localize("en_US", "commands.admin.embed.missingPermission.description"),
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


def _loc_or_en(interaction: discord.Interaction) -> str:
    return str(interaction.locale) if interaction.locale else "en_US"


# ---------------------------------------------------------------------------
# Log event keys (matching LOG_OPTIONS order in commands/logs/configure_logs.py)
# ---------------------------------------------------------------------------

LOG_OPTIONS = [
    "automodRuleCreate",
    "automodRuleUpdate",
    "automodRuleDelete",
    "automodAction",
    "guild_channelDelete",
    "guild_channelCreate",
    "guild_channelUpdate",
    "guildUpdate",
    "inviteCreate",
    "inviteDelete",
    "memberJoin",
    "memberLeave",
    "memberUpdate",
    "userUpdate",
    "memberBan",
    "memberUnban",
    "presenceUpdate",
    "messageEdit",
    "messageDelete",
    "reactionAdd",
    "reactionRemove",
    "guildRoleCreate",
    "guildRoleDelete",
    "guildRoleUpdate",
]

# Available XP scaling difficulties
XP_SCALING_OPTIONS = {
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
    "very_hard": "Very Hard",
    "extreme": "Extreme",
}

# ---------------------------------------------------------------------------
# LOG SETUP WIZARD
# ---------------------------------------------------------------------------


class LogChannelSelectView(View):
    """Step 1: Select a log channel."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild

    @discord.ui.channel_select(
        placeholder="Select a text channel for logging...",
        channel_types=[discord.ChannelType.text],
    )
    async def on_channel_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect[Any],  # type: ignore[misc]
    ) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if not select.values:
            return

        channel = cast(discord.TextChannel, select.values[0])

        # Check bot permissions
        assert interaction.client is not None and interaction.client.user is not None
        self_member = self.guild.get_member(interaction.client.user.id)
        if self_member is None or not channel.permissions_for(self_member).send_messages:
            embed = utility.tanjunEmbed(
                title="Missing Permission",
                description="I don't have permission to send messages in that channel.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Save the channel
        await api_set_log_channel(str(self.guild.id), str(channel.id))

        embed = utility.tanjunEmbed(
            title="✅ Log Channel Set",
            description=f"Log channel has been set to {channel.mention}.\n\nNow let's configure which events to log.",
        )
        event_view = LogEventConfigView(self.locale, self.guild)
        await interaction.response.edit_message(embed=embed, view=event_view)


class LogEventConfigView(View):
    """Step 2: Configure which log events to track."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self._log_enabled = None
        self._current_page = 0
        self._items_per_page = 7

    async def _load(self) -> None:
        if self._log_enabled is None:
            self._log_enabled = await api_get_log_enable(str(self.guild.id))

    def _page_keys(self) -> list[str]:
        start = self._current_page * self._items_per_page
        return LOG_OPTIONS[start : start + self._items_per_page]

    async def _render_embed(self) -> discord.Embed:
        await self._load()
        assert self._log_enabled is not None
        lines: list[str] = []
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            enabled = self._log_enabled.get_option(idx)
            icon = "✅" if enabled else "❌"
            lines.append(f"{icon} {key}")
        total_pages = (len(LOG_OPTIONS) + self._items_per_page - 1) // self._items_per_page
        return utility.tanjunEmbed(
            title="Log Event Configuration",
            description=(
                "\n".join(lines)
                + f"\n\nPage {self._current_page + 1}/{total_pages}"
            ),
        )

    @discord.ui.button(label="✅ Enable page", style=discord.ButtonStyle.success)
    async def enable_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._load()
        assert self._log_enabled is not None
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            if not self._log_enabled.get_option(idx):
                await api_set_log_enable(str(self.guild.id), **{key: True})
                self._log_enabled.set_option(idx, True)
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Disable page", style=discord.ButtonStyle.danger)
    async def disable_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._load()
        assert self._log_enabled is not None
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            if self._log_enabled.get_option(idx):
                await api_set_log_enable(str(self.guild.id), **{key: False})
                self._log_enabled.set_option(idx, False)
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        if self._current_page > 0:
            self._current_page -= 1
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        total_pages = (len(LOG_OPTIONS) + self._items_per_page - 1) // self._items_per_page
        if self._current_page < total_pages - 1:
            self._current_page += 1
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="✅ Finish Log Setup", style=discord.ButtonStyle.green, row=2)
    async def finish(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        embed = utility.tanjunEmbed(
            title="✅ Log Setup Complete",
            description="Logging has been configured successfully! Events will be tracked in the selected channel.",
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()


# ---------------------------------------------------------------------------
# LEVEL SYSTEM SETUP WIZARD
# ---------------------------------------------------------------------------


class LevelSetupView(View):
    """Step 1: Choose XP scaling difficulty."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild

    @discord.ui.button(label="🟢 Easy", style=discord.ButtonStyle.success, row=0)
    async def easy(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._set_scaling(interaction, "easy")

    @discord.ui.button(label="🟡 Medium", style=discord.ButtonStyle.primary, row=0)
    async def medium(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._set_scaling(interaction, "medium")

    @discord.ui.button(label="🟠 Hard", style=discord.ButtonStyle.secondary, row=1)
    async def hard(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._set_scaling(interaction, "hard")

    @discord.ui.button(label="🔴 Very Hard", style=discord.ButtonStyle.danger, row=1)
    async def very_hard(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._set_scaling(interaction, "very_hard")

    @discord.ui.button(label="💀 Extreme", style=discord.ButtonStyle.danger, row=1)
    async def extreme(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._set_scaling(interaction, "extreme")

    async def _set_scaling(self, interaction: discord.Interaction, scaling: str) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return

        await api_set_xp_scaling(str(self.guild.id), scaling)

        embed = utility.tanjunEmbed(
            title="XP Scaling Set",
            description=f"XP difficulty set to **{scaling}**. Now let's configure cooldowns.",
        )
        view = LevelCooldownView(self.locale, self.guild)
        await interaction.response.edit_message(embed=embed, view=view)


class LevelCooldownView(View):
    """Step 2: Configure cooldowns."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild

    @discord.ui.button(label="⚡ Fast (30s)", style=discord.ButtonStyle.success)
    async def fast(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._apply_cooldowns(interaction, 30, 60)

    @discord.ui.button(label="⏳ Normal (60s)", style=discord.ButtonStyle.primary)
    async def normal(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._apply_cooldowns(interaction, 60, 120)

    @discord.ui.button(label="🐢 Slow (120s)", style=discord.ButtonStyle.secondary)
    async def slow(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        await self._apply_cooldowns(interaction, 120, 300)

    async def _apply_cooldowns(self, interaction: discord.Interaction, text_cd: int, voice_cd: int) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return

        await api_set_text_cooldown(str(self.guild.id), text_cd)
        await api_set_voice_cooldown(str(self.guild.id), voice_cd)

        embed = utility.tanjunEmbed(
            title="Cooldowns Configured",
            description=(
                f"Text XP cooldown: **{text_cd}s**\n"
                f"Voice XP cooldown: **{voice_cd}s**\n\n"
                "Now let's set a level-up announcement channel (optional)."
            ),
        )
        view = LevelChannelView(self.locale, self.guild)
        await interaction.response.edit_message(embed=embed, view=view)


class LevelChannelView(View):
    """Step 3 (optional): Set level-up announcement channel."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild

    @discord.ui.channel_select(
        placeholder="Select a channel for level-up announcements...",
        channel_types=[discord.ChannelType.text],
    )
    async def on_channel_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.ChannelSelect[Any],  # type: ignore[misc]
    ) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if select.values:
            channel = cast(discord.TextChannel, select.values[0])
            await api_set_levelup_channel(str(self.guild.id), str(channel.id))
            msg = f"Level-up announcements will be sent to {channel.mention}."
        else:
            msg = "No level-up channel set."
        embed = utility.tanjunEmbed(
            title="Channel Set",
            description=msg + "\n\nLevel system setup is complete! 🎉",
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.secondary)
    async def skip(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        embed = utility.tanjunEmbed(
            title="✅ Level Setup Complete",
            description="The leveling system is now active! Members earn XP by chatting.\n\nTip: Use `/level add-level-role` to reward roles at specific levels.",
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()


# ---------------------------------------------------------------------------
# GIVEAWAY SETUP WIZARD
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# BOOSTER SETUP WIZARD
# ---------------------------------------------------------------------------


class BoosterSetupView(View):
    """Booster configuration wizard."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self._steps_done: set[str] = set()

    async def _refresh(self, interaction: discord.Interaction) -> None:
        desc_parts: list[str] = []
        booster_service = BoosterService()

        channel_id = await booster_service.get(BoosterType.CHANNEL, str(self.guild.id))
        role_id = await booster_service.get(BoosterType.ROLE, str(self.guild.id))
        if "channel" in self._steps_done:
            desc_parts.append("✅ Booster channel configured")
        else:
            desc_parts.append("⬜ Not configured yet — press **Set Booster Channel**")
        if "role" in self._steps_done:
            desc_parts.append("✅ Booster role configured")
        else:
            desc_parts.append("⬜ Not configured yet — press **Set Booster Role**")

        embed = utility.tanjunEmbed(
            title="Booster Setup",
            description="\n".join(desc_parts),
        )
        if channel_id:
            embed.add_field(name="Current Channel", value=f"<#{channel_id}>", inline=True)
        if role_id:
            embed.add_field(name="Current Role", value=f"<@&{role_id}>", inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🎤 Set Booster Channel", style=discord.ButtonStyle.primary)
    async def set_channel(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await interaction.response.send_modal(BoosterChannelModal(self.locale, self.guild, self))

    @discord.ui.button(label="🎭 Set Booster Role", style=discord.ButtonStyle.primary)
    async def set_role(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await interaction.response.send_modal(BoosterRoleModal(self.locale, self.guild, self))

    @discord.ui.button(label="✅ Finish Booster Setup", style=discord.ButtonStyle.green)
    async def finish(
        self, interaction: discord.Interaction, _button: discord.ui.Button[Any]  # type: ignore[misc]
    ) -> None:
        embed = utility.tanjunEmbed(
            title="✅ Booster Setup Complete",
            description="Boosters can now claim their perks!",
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()


class BoosterChannelModal(Modal):
    def __init__(self, locale: str, guild: discord.Guild, parent_view: BoosterSetupView) -> None:
        super().__init__(title="Set Booster Channel")
        self.locale = locale
        self.guild = guild
        self.parent = parent_view

        self.add_item(
            TextInput(
                label="Voice Channel ID",
                placeholder="Paste the voice channel ID",
                required=True,
                max_length=20,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        try:
            channel_id = int(str(self.children[0].value))
        except ValueError:
            embed = utility.tanjunEmbed(title="Invalid ID", description="Please provide a valid channel ID.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel = self.guild.get_channel(channel_id)
        if channel is None:
            embed = utility.tanjunEmbed(title="Channel Not Found", description="Could not find that channel in this server.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        booster_service = BoosterService()
        await booster_service.add(BoosterType.CHANNEL, str(self.guild.id), str(channel_id))
        self.parent._steps_done.add("channel")

        embed = utility.tanjunEmbed(
            title="Booster Channel Set",
            description=f"Boosters can now claim <#{channel_id}> as their private channel.",
        )
        await interaction.response.edit_message(embed=embed, view=self.parent)


class BoosterRoleModal(Modal):
    def __init__(self, locale: str, guild: discord.Guild, parent_view: BoosterSetupView) -> None:
        super().__init__(title="Set Booster Role")
        self.locale = locale
        self.guild = guild
        self.parent = parent_view

        self.add_item(
            TextInput(
                label="Role ID",
                placeholder="Paste the role ID",
                required=True,
                max_length=20,
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        try:
            role_id = int(str(self.children[0].value))
        except ValueError:
            embed = utility.tanjunEmbed(title="Invalid ID", description="Please provide a valid role ID.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        role = self.guild.get_role(role_id)
        if role is None:
            embed = utility.tanjunEmbed(title="Role Not Found", description="Could not find that role in this server.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        booster_service = BoosterService()
        await booster_service.add(BoosterType.ROLE, str(self.guild.id), str(role_id))
        self.parent._steps_done.add("role")

        embed = utility.tanjunEmbed(
            title="Booster Role Set",
            description=f"Users with {role.mention} can claim booster perks.",
        )
        await interaction.response.edit_message(embed=embed, view=self.parent)


# ---------------------------------------------------------------------------
# COG & COMMAND REGISTRATION
# ---------------------------------------------------------------------------


class SetupWizardsCog(commands.Cog):
    """Cog that provides /setup commands for guided configuration."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._setup_commands = SetupWizardCommands()
        self.bot.tree.add_command(self._setup_commands)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self._setup_commands.name)

    @app_commands.command(
        name=app_commands.locale_str("setup_logs_name"),
        description=app_commands.locale_str("setup_logs_description"),
    )
    async def setup_logs(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to configure logging."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None

        existing = await api_get_log_channel(str(interaction.guild.id))
        if existing:
            embed = utility.tanjunEmbed(
                title="Logging Already Configured",
                description=f"A log channel is already set (<#{existing}>). Use `/logs set-log-channel` to change it.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = utility.tanjunEmbed(
            title="📋 Log Setup Wizard",
            description="Welcome! Let's get logging configured.\n\n**Step 1:** Select a text channel where log messages will be sent.",
        )
        view = LogChannelSelectView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name=app_commands.locale_str("setup_level_name"),
        description=app_commands.locale_str("setup_level_description"),
    )
    async def setup_level(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to configure the leveling system."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None

        active = bool(await api_get_level_system_status(str(interaction.guild.id)))
        if active:
            embed = utility.tanjunEmbed(
                title="Level System Already Active",
                description="The level system is already enabled. Use `/level` commands to adjust settings.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = utility.tanjunEmbed(
            title="📊 Level Setup Wizard",
            description=(
                "Let's set up the leveling system!\n\n"
                "**Step 1:** Choose how quickly XP requirements increase.\n"
                "• **Easy** — fast leveling\n"
                "• **Medium** — balanced\n"
                "• **Hard** — slower\n"
                "• **Very Hard** — challenging\n"
                "• **Extreme** — grindy"
            ),
        )
        # Enable the level system first
        await api_set_level_system_status(str(interaction.guild.id), True)
        view = LevelSetupView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name=app_commands.locale_str("setup_giveaway_name"),
        description=app_commands.locale_str("setup_giveaway_description"),
    )
    async def setup_giveaway(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to create a giveaway."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None

        # Launch the existing giveaway builder directly — it provides a full interactive UI
        from commands.giveaway.start import start_giveaway
        from utility import CommandInfo

        cmd_info = CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=None,
            locale=_loc_or_en(interaction),
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )
        await start_giveaway(
            command_info=cmd_info,
            title="New Giveaway",
            target_channel=cast(discord.TextChannel, interaction.channel),
        )

        embed = utility.tanjunEmbed(
            title="🎉 Giveaway Wizard Opened",
            description="The giveaway builder has opened. Use the buttons above to configure your giveaway!",
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name=app_commands.locale_str("setup_booster_name"),
        description=app_commands.locale_str("setup_booster_description"),
    )
    async def setup_booster(self, interaction: discord.Interaction) -> None:
        """Interactive guide for booster perks configuration."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None

        embed = utility.tanjunEmbed(
            title="🎵 Booster Setup Wizard",
            description=(
                "Configure perks for server boosters.\n\n"
                "• **Booster Channel** — boosters get a private voice channel\n"
                "• **Booster Role** — assign a role that grants booster perks"
            ),
        )
        view = BoosterSetupView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=embed, view=view)


class SetupWizardCommands(discord.app_commands.Group):
    """Group for setup wizard commands."""

    def __init__(self) -> None:
        super().__init__(
            name=app_commands.locale_str("setup_name"),
            description=app_commands.locale_str("setup_description"),
        )


# ---------------------------------------------------------------------------
# Cog setup
# ---------------------------------------------------------------------------


async def setup(bot: commands.Bot) -> None:
    """Register the SetupWizards cog."""
    await bot.add_cog(SetupWizardsCog(bot))
