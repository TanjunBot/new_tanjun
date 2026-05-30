from __future__ import annotations

import discord

import utility
from api import LogBlacklistType, add_log_blacklist, get_log_blacklist, remove_log_blacklist
from commands.logs.blacklist_channel.blacklist_utils import get_channel_blacklist_type
from localizer import tanjunLocalizer


async def blacklist_list_channel(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    blacklisted_channels = await get_log_blacklist(command_info.guild.id, LogBlacklistType.CHANNEL)
    blacklisted_voice = await get_log_blacklist(command_info.guild.id, LogBlacklistType.VOICE_CHANNEL)
    blacklisted_categories = await get_log_blacklist(command_info.guild.id, LogBlacklistType.CATEGORY)

    # Store entries with their type for proper removal
    all_entries: list[tuple[str, LogBlacklistType]] = []
    for cid in blacklisted_channels:
        all_entries.append((cid, LogBlacklistType.CHANNEL))
    for cid in blacklisted_voice:
        all_entries.append((cid, LogBlacklistType.VOICE_CHANNEL))
    for cid in blacklisted_categories:
        all_entries.append((cid, LogBlacklistType.CATEGORY))

    class BlacklistView(discord.ui.View):
        def __init__(self, entries: list[tuple[str, LogBlacklistType]], locale: str, guild: discord.Guild):
            super().__init__()
            self.entries = entries
            self.locale = locale
            self.guild = guild
            self.selectedIndex = 0
            self._update_button_states()

        def _update_button_states(self) -> None:
            """Disable navigation and remove buttons when no entries exist."""
            disabled = len(self.entries) == 0
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id in ("remove", "up", "down"):
                    item.disabled = disabled

        @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger, custom_id="remove")
        async def remove_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.entries:
                return
            entity_id, bl_type = self.entries[self.selectedIndex]
            await remove_log_blacklist(self.guild.id, entity_id, bl_type)
            self.entries = [e for e in self.entries if e[0] != entity_id]
            self.selectedIndex = max(0, min(self.selectedIndex, len(self.entries) - 1))
            self._update_button_states()
            await self.update_view(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.entries:
                return
            self.selectedIndex = (self.selectedIndex - 1) % len(self.entries)
            await self.update_view(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.entries:
                return
            self.selectedIndex = (self.selectedIndex + 1) % len(self.entries)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 8:  # ChannelSelect
                channel_id = interaction.data["values"][0]
                channel = self.guild.get_channel(int(channel_id))
                bl_type = get_channel_blacklist_type(channel)
                await add_log_blacklist(self.guild.id, channel_id, bl_type)
                self.entries.append((channel_id, bl_type))
                self._update_button_states()
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.entries:
                description = tanjunLocalizer.localize(
                    self.locale,
                    "commands.logs.blacklistListChannel.noBlacklistedChannels",
                )
            else:
                if self.selectedIndex >= len(self.entries):
                    self.selectedIndex = len(self.entries) - 1
                lines = []
                for i, (entity_id, bl_type) in enumerate(self.entries):
                    prefix = "➤" if i == self.selectedIndex else ""
                    type_tag = ""
                    if bl_type == LogBlacklistType.CATEGORY:
                        type_tag = " [Category]"
                    elif bl_type == LogBlacklistType.VOICE_CHANNEL:
                        type_tag = " [Voice]"
                    else:
                        type_tag = " [Text]"
                    lines.append(f"{prefix} <#{entity_id}>{type_tag}")
                description = "\n".join(lines)
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListChannel.title"),
                description=description,
            )
            await interaction.response.edit_message(embed=embed, view=self)

    view = BlacklistView(all_entries, command_info.locale, command_info.guild)
    view.add_item(
        discord.ui.ChannelSelect(
            custom_id="channel_select",
            channel_types=[
                discord.ChannelType.text,
                discord.ChannelType.voice,
                discord.ChannelType.category,
            ],
            placeholder=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListChannel.addChannel.placeholder",
            ),
        )
    )
    if not all_entries:
        description = tanjunLocalizer.localize(
            command_info.locale,
            "commands.logs.blacklistListChannel.noBlacklistedChannels",
        )
    else:
        lines = []
        for i, (entity_id, bl_type) in enumerate(all_entries):
            prefix = "➤" if i == 0 else ""
            type_tag = ""
            if bl_type == LogBlacklistType.CATEGORY:
                type_tag = " [Category]"
            elif bl_type == LogBlacklistType.VOICE_CHANNEL:
                type_tag = " [Voice]"
            else:
                type_tag = " [Text]"
            lines.append(f"{prefix} <#{entity_id}>{type_tag}")
        description = "\n".join(lines)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.logs.blacklistListChannel.title"),
        description=description,
    )
    await command_info.reply(embed=embed, view=view)
