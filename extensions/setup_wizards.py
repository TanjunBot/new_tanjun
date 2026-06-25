"""
Interactive setup wizards for complex features.
Provides guided, step-by-step configuration using selects and buttons.
"""
from locale_keys import locale as l10n
from typing import Any, cast
import discord
from models import LogEnableModel
from utils.discord_channels import bot_can_send_messages, channel_mention, resolve_guild_channel
from utils.embeds import TanjunEmbed
from discord import app_commands
from discord.ext import commands
from discord.ui import View
import utility
from api import get_level_system_status as api_get_level_system_status
from api import get_log_channel as api_get_log_channel
from api import get_log_enable as api_get_log_enable
from api import set_level_system_status as api_set_level_system_status
from api import set_levelup_channel as api_set_levelup_channel
from api import set_log_channel as api_set_log_channel
from api import set_log_enable as api_set_log_enable
from api import set_text_cooldown as api_set_text_cooldown
from api import set_voice_cooldown as api_set_voice_cooldown
from api import set_xp_scaling as api_set_xp_scaling
from services.booster_service import BoosterService, BoosterType
_WIZARD_SESSION_TIMEOUT = 600


def _discord_embed(embed: TanjunEmbed | discord.Embed) -> discord.Embed:
    if isinstance(embed, discord.Embed):
        return embed
    return embed.to_discord_embed()


def _require_admin(interaction: discord.Interaction) -> bool:
    """Check if the user has administrator permissions."""
    return interaction.guild is not None and isinstance(interaction.user, discord.Member) and isinstance(interaction.channel, discord.abc.GuildChannel) and interaction.channel.permissions_for(interaction.user).administrator

async def _not_admin_reply(interaction: discord.Interaction) -> None:
    """Send a permission-denied embed."""
    embed = utility.tanjunEmbed(title=l10n.commands.admin.embed.missingPermission.title('en_US'), description=l10n.commands.admin.embed.missingPermission.description('en_US'))
    await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)

def _loc_or_en(interaction: discord.Interaction) -> str:
    return str(interaction.locale) if interaction.locale else 'en_US'
LOG_OPTIONS = ['automodRuleCreate', 'automodRuleUpdate', 'automodRuleDelete', 'automodAction', 'guild_channelDelete', 'guild_channelCreate', 'guild_channelUpdate', 'guildUpdate', 'inviteCreate', 'inviteDelete', 'memberJoin', 'memberLeave', 'memberUpdate', 'userUpdate', 'memberBan', 'memberUnban', 'presenceUpdate', 'messageEdit', 'messageDelete', 'reactionAdd', 'reactionRemove', 'guildRoleCreate', 'guildRoleDelete', 'guildRoleUpdate']
XP_SCALING_OPTIONS = {'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard', 'very_hard': 'Very Hard', 'extreme': 'Extreme'}

class LogChannelSelectView(View):
    """Step 1: Select a log channel."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder='Select a text channel for logging...', channel_types=[discord.ChannelType.text])
    async def on_channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if not select.values:
            return
        selected = select.values[0]
        channel = await resolve_guild_channel(self.guild, selected)
        assert interaction.client is not None and interaction.client.user is not None
        self_member = self.guild.get_member(interaction.client.user.id)
        if self_member is None or channel is None or not bot_can_send_messages(channel, self_member):
            embed = utility.tanjunEmbed(title='Missing Permission', description="I don't have permission to send messages in that channel.")
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        await api_set_log_channel(str(self.guild.id), str(channel.id))
        event_view = LogEventConfigView(self.locale, self.guild)
        prefix = f"Log channel set to {channel_mention(selected, channel)}."
        config_embed = await event_view.render_for_message(prefix=prefix)
        await interaction.response.edit_message(embed=config_embed, view=event_view)

class LogEventConfigView(View):
    """Step 2: Configure which log events to track."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self._log_enabled: LogEnableModel | None = None
        self._current_page = 0
        self._items_per_page = 7

    async def _load(self) -> None:
        if self._log_enabled is None:
            self._log_enabled = await api_get_log_enable(str(self.guild.id))

    def _page_keys(self) -> list[str]:
        start = self._current_page * self._items_per_page
        return LOG_OPTIONS[start:start + self._items_per_page]

    async def _render_embed(self) -> TanjunEmbed:
        await self._load()
        assert self._log_enabled is not None
        lines: list[str] = []
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            enabled = self._log_enabled.get_option(idx)
            icon = '✅' if enabled else '❌'
            lines.append(f'{icon} {key}')
        total_pages = (len(LOG_OPTIONS) + self._items_per_page - 1) // self._items_per_page
        return utility.tanjunEmbed(title='Log Event Configuration', description='\n'.join(lines) + f'\n\nPage {self._current_page + 1}/{total_pages}')

    async def render_for_message(self, *, prefix: str | None = None) -> discord.Embed:
        embed = _discord_embed(await self._render_embed())
        if prefix:
            embed.description = f'{prefix}\n\n{embed.description or ""}'
        return embed

    @discord.ui.button(label='✅ Enable page', style=discord.ButtonStyle.success)
    async def enable_page(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await self._load()
        assert self._log_enabled is not None
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            if not self._log_enabled.get_option(idx):
                await api_set_log_enable(str(self.guild.id), **{key: True})
                self._log_enabled.set_option(idx, True)
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)

    @discord.ui.button(label='❌ Disable page', style=discord.ButtonStyle.danger)
    async def disable_page(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await self._load()
        assert self._log_enabled is not None
        for key in self._page_keys():
            idx = LOG_OPTIONS.index(key)
            if self._log_enabled.get_option(idx):
                await api_set_log_enable(str(self.guild.id), **{key: False})
                self._log_enabled.set_option(idx, False)
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)

    @discord.ui.button(label='◀', style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if self._current_page > 0:
            self._current_page -= 1
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        total_pages = (len(LOG_OPTIONS) + self._items_per_page - 1) // self._items_per_page
        if self._current_page < total_pages - 1:
            self._current_page += 1
        embed = await self._render_embed()
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)

    @discord.ui.button(label='✅ Finish Log Setup', style=discord.ButtonStyle.green, row=2)
    async def finish(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        embed = utility.tanjunEmbed(title='✅ Log Setup Complete', description='Logging has been configured successfully! Events will be tracked in the selected channel.')
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)
        self.stop()

class LevelSetupView(View):
    """Step 1: Choose XP scaling difficulty."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self.completed = False

    @discord.ui.button(label='🟢 Easy', style=discord.ButtonStyle.success, row=0)
    async def easy(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._set_scaling(interaction, 'easy')

    @discord.ui.button(label='🟡 Medium', style=discord.ButtonStyle.primary, row=0)
    async def medium(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._set_scaling(interaction, 'medium')

    @discord.ui.button(label='🟠 Hard', style=discord.ButtonStyle.secondary, row=1)
    async def hard(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._set_scaling(interaction, 'hard')

    @discord.ui.button(label='🔴 Very Hard', style=discord.ButtonStyle.danger, row=1)
    async def very_hard(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._set_scaling(interaction, 'very_hard')

    @discord.ui.button(label='💀 Extreme', style=discord.ButtonStyle.danger, row=1)
    async def extreme(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._set_scaling(interaction, 'extreme')

    async def _set_scaling(self, interaction: discord.Interaction, scaling: str) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await api_set_xp_scaling(str(self.guild.id), scaling)
        embed = utility.tanjunEmbed(title='XP Scaling Set', description=f"XP difficulty set to **{scaling}**.\n\n**Step 2:** Choose how often members can earn XP again.\n• **Fast** — 30s text, 60s voice\n• **Normal** — 60s text, 120s voice\n• **Slow** — 120s text, 300s voice")
        view = LevelCooldownView(self.locale, self.guild, self)
        await interaction.response.edit_message(embed=_discord_embed(embed), view=view)

class LevelCooldownView(View):
    """Step 2: Configure cooldowns."""

    def __init__(self, locale: str, guild: discord.Guild, setup_view: 'LevelSetupView') -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self.setup_view = setup_view

    @discord.ui.button(label='⚡ Fast (30s)', style=discord.ButtonStyle.success)
    async def fast(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._apply_cooldowns(interaction, 30, 60)

    @discord.ui.button(label='⏳ Normal (60s)', style=discord.ButtonStyle.primary)
    async def normal(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._apply_cooldowns(interaction, 60, 120)

    @discord.ui.button(label='🐢 Slow (120s)', style=discord.ButtonStyle.secondary)
    async def slow(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        await self._apply_cooldowns(interaction, 120, 300)

    async def _apply_cooldowns(self, interaction: discord.Interaction, text_cd: int, voice_cd: int) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        await api_set_text_cooldown(str(self.guild.id), text_cd)
        await api_set_voice_cooldown(str(self.guild.id), voice_cd)
        embed = utility.tanjunEmbed(title='Cooldowns Configured', description=f"Text XP cooldown: **{text_cd}s**\nVoice XP cooldown: **{voice_cd}s**\n\n**Step 3 (optional):** Choose where level-up messages are sent.\n• **Select a channel** — all announcements go to that channel\n• **Skip** — announcements are sent in the channel where each member leveled up")
        view = LevelChannelView(self.locale, self.guild, self.setup_view)
        await interaction.response.edit_message(embed=_discord_embed(embed), view=view)

class LevelChannelView(View):
    """Step 3 (optional): Set level-up announcement channel."""

    def __init__(self, locale: str, guild: discord.Guild, setup_view: 'LevelSetupView') -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self.setup_view = setup_view

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder='Optional: pick a fixed level-up channel...', channel_types=[discord.ChannelType.text])
    async def on_channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if select.values:
            selected = select.values[0]
            channel = await resolve_guild_channel(self.guild, selected)
            assert interaction.client is not None and interaction.client.user is not None
            self_member = self.guild.get_member(interaction.client.user.id)
            if self_member is None or channel is None:
                embed = utility.tanjunEmbed(title='Error', description='Could not verify bot permissions.')
                await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
                return
            perms = channel.permissions_for(self_member)
            if not (perms.view_channel and perms.send_messages):
                embed = utility.tanjunEmbed(title='Missing Permission', description="I don't have permission to send messages in that channel. Please select a different channel.")
                await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
                return
            await api_set_levelup_channel(str(self.guild.id), str(channel.id))
            msg = f'Level-up announcements will be sent to {channel_mention(selected, channel)}.'
        else:
            msg = 'No fixed channel set. Level-up messages will be sent in the channel where each member leveled up.'
        self.setup_view.completed = True
        embed = utility.tanjunEmbed(title='Channel Set', description=msg + '\n\nLevel system setup is complete! 🎉')
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)
        self.stop()

    @discord.ui.button(label='⏭ Skip', style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        self.setup_view.completed = True
        embed = utility.tanjunEmbed(title='✅ Level Setup Complete', description='The leveling system is now active! Members earn XP by chatting.\n\nLevel-up messages will be sent in the channel where each member leveled up. You can set a fixed channel later with `/level setlevelupchannel`.\n\nTip: Use `/level add-level-role` to reward roles at specific levels.')
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)
        self.stop()

class BoosterSetupView(View):
    """Booster configuration wizard."""

    def __init__(self, locale: str, guild: discord.Guild) -> None:
        super().__init__(timeout=_WIZARD_SESSION_TIMEOUT)
        self.locale = locale
        self.guild = guild
        self._steps_done: set[str] = set()

    async def _update_booster_ui(self, interaction: discord.Interaction) -> None:
        desc_parts: list[str] = []
        booster_service = BoosterService()
        channel_id = await booster_service.get(BoosterType.CHANNEL, str(self.guild.id))
        role_id = await booster_service.get(BoosterType.ROLE, str(self.guild.id))
        if 'channel' in self._steps_done:
            desc_parts.append('✅ Booster category configured')
        else:
            desc_parts.append('⬜ Not configured yet — select a **booster category** below')
        if 'role' in self._steps_done:
            desc_parts.append('✅ Booster role configured')
        else:
            desc_parts.append('⬜ Not configured yet — select a **booster role** below')
        embed = utility.tanjunEmbed(title='Booster Setup', description='\n'.join(desc_parts))
        if channel_id:
            category = self.guild.get_channel(int(channel_id))
            if category is not None and getattr(category, 'name', None):
                embed.add_field(name='Current Category', value=category.name, inline=True)
            else:
                embed.add_field(name='Current Category', value=f'`{channel_id}`', inline=True)
        if role_id:
            embed.add_field(name='Current Role', value=f'<@&{role_id}>', inline=True)
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)

    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder='Select a category for booster voice channels...', channel_types=[discord.ChannelType.category])
    async def on_category_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if not select.values:
            return
        selected = select.values[0]
        category = await resolve_guild_channel(self.guild, selected)
        if category is None:
            embed = utility.tanjunEmbed(title='Category Not Found', description='Could not find that category in this server.')
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        if getattr(category, 'type', None) != discord.ChannelType.category:
            embed = utility.tanjunEmbed(title='Invalid Category', description='Please select a channel category.')
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        booster_service = BoosterService()
        await booster_service.add(BoosterType.CHANNEL, str(self.guild.id), str(category.id))
        self._steps_done.add('channel')
        await self._update_booster_ui(interaction)

    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder='Select a role to grant booster perks...')
    async def on_role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        if not select.values:
            return
        selected: discord.Role | discord.Object = select.values[0]
        role: discord.Role | None = selected if isinstance(selected, discord.Role) else self.guild.get_role(selected.id)
        if role is None:
            embed = utility.tanjunEmbed(title='Role Not Found', description='Could not find that role in this server.')
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        booster_service = BoosterService()
        await booster_service.add(BoosterType.ROLE, str(self.guild.id), str(role.id))
        self._steps_done.add('role')
        await self._update_booster_ui(interaction)

    @discord.ui.button(label='✅ Finish Booster Setup', style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, _button: discord.ui.Button[Any]) -> None:
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        embed = utility.tanjunEmbed(title='✅ Booster Setup Complete', description='Boosters can now claim their perks!')
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=_discord_embed(embed), view=self)
        self.stop()

class SetupWizardsCog(commands.Cog):
    """Cog that provides /setup commands for guided configuration."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._setup_commands = SetupWizardCommands(bot)
        self.bot.tree.add_command(self._setup_commands)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self._setup_commands.name)

class SetupWizardCommands(discord.app_commands.Group):
    """Group for setup wizard commands."""

    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(name=l10n.setup.name.discord_key, description=l10n.setup.description.discord_key)
        self.bot = bot

    @app_commands.command(name=l10n.setup.logs.name.discord_key, description=l10n.setup.logs.description.discord_key)
    async def logs(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to configure logging."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None
        existing = await api_get_log_channel(str(interaction.guild.id))
        if existing:
            embed = utility.tanjunEmbed(title='Logging Already Configured', description=f'A log channel is already set (<#{existing}>). Use `/logs set-log-channel` to change it.')
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        embed = utility.tanjunEmbed(title='📋 Log Setup Wizard', description="Welcome! Let's get logging configured.\n\n**Step 1:** Select a text channel where log messages will be sent.")
        view = LogChannelSelectView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=_discord_embed(embed), view=view)

    @app_commands.command(name=l10n.setup.level.name.discord_key, description=l10n.setup.level.description.discord_key)
    async def level(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to configure the leveling system."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None
        active = bool(await api_get_level_system_status(str(interaction.guild.id)))
        if active:
            embed = utility.tanjunEmbed(title='Level System Already Active', description='The level system is already enabled. Use `/level`, `/settings`, `/boosts`, and `/blacklist` commands to adjust settings. Set a custom rank card background with `/level set_background`.')
            await interaction.response.send_message(embed=_discord_embed(embed), ephemeral=True)
            return
        embed = utility.tanjunEmbed(title='📊 Level Setup Wizard', description="Let's set up the leveling system!\n\n**Step 1:** Choose how quickly XP requirements increase.\n• **Easy** — fast leveling\n• **Medium** — balanced\n• **Hard** — slower\n• **Very Hard** — challenging\n• **Extreme** — grindy")
        view = LevelSetupView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=_discord_embed(embed), view=view)
        await view.wait()
        if view.completed:
            await api_set_level_system_status(str(interaction.guild.id), True)

    @app_commands.command(name=l10n.setup.giveaway.name.discord_key, description=l10n.setup.giveaway.description.discord_key)
    async def giveaway(self, interaction: discord.Interaction) -> None:
        """Interactive wizard to create a giveaway."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None
        from commands.giveaway.start import start_giveaway
        from utility import CommandInfo
        cmd_info = CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=None, locale=_loc_or_en(interaction), message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await start_giveaway(  # type: ignore[no-untyped-call]
            command_info=cmd_info,
            title='New Giveaway',
            target_channel=cast(discord.TextChannel, interaction.channel),
        )
        embed = utility.tanjunEmbed(title='🎉 Giveaway Wizard Opened', description='The giveaway builder has opened. Use the buttons above to configure your giveaway!')
        await interaction.response.send_message(embed=_discord_embed(embed))

    @app_commands.command(name=l10n.setup.booster.name.discord_key, description=l10n.setup.booster.description.discord_key)
    async def booster(self, interaction: discord.Interaction) -> None:
        """Interactive guide for booster perks configuration."""
        if not _require_admin(interaction):
            await _not_admin_reply(interaction)
            return
        assert interaction.guild is not None
        embed = utility.tanjunEmbed(title='🎵 Booster Setup Wizard', description='Configure perks for server boosters.\n\n• **Booster category** — boosters create private voice channels in this category\n• **Booster role** — select a role that grants booster perks')
        view = BoosterSetupView(_loc_or_en(interaction), interaction.guild)
        await interaction.response.send_message(embed=_discord_embed(embed), view=view)

async def setup(bot: commands.Bot) -> None:
    """Register the SetupWizards cog."""
    await bot.add_cog(SetupWizardsCog(bot))