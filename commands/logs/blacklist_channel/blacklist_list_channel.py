from api import add_log_blacklist_channel as add_log_blacklist_channel_api, remove_log_blacklist_channel as remove_log_blacklist_channel_api, get_log_blacklist_channel as get_log_blacklist_channels_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_list_channel(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistListChannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistListChannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    blacklisted_channels = await get_log_blacklist_channels_api(commandInfo.guild.id)

    class BlacklistView(discord.ui.View):
        def __init__(self, channels: list, locale: str, guild: discord.Guild):
            super().__init__()
            self.channels = channels
            self.locale = locale
            self.guild = guild
            self.selectedIndex = 0

        @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
        async def remove_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
            channel_id = self.channels[self.selectedIndex][0]
            await remove_log_blacklist_channel_api(self.guild.id, channel_id)
            self.channels = tuple(x for x in self.channels if x[0] != channel_id)
            await self.update_view(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex = (self.selectedIndex - 1) % len(self.channels)
            await self.update_view(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex = (self.selectedIndex + 1) % len(self.channels)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 8:  # ChannelSelect
                channelId = interaction.data["values"][0]
                await add_log_blacklist_channel_api(self.guild.id, channelId)
                self.channels += ((channelId, ), )
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.channels or len(self.channels) == 0:
                description = tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListChannel.noBlacklistedChannels")
            else:
                if self.selectedIndex >= len(self.channels):
                    self.selectedIndex = len(self.channels) - 1
                description = "\n".join([f"{'➤' if i == self.selectedIndex else ''} <#{channel[0]}>" for i, channel in enumerate(self.channels)])
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListChannel.title"),
                description=description
            )
            await interaction.response.edit_message(embed=embed, view=self)

    view = BlacklistView(blacklisted_channels, commandInfo.locale, commandInfo.guild)
    view.add_item(discord.ui.ChannelSelect(custom_id="channel_select", channel_types=[discord.ChannelType.text, discord.ChannelType.voice], placeholder=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListChannel.addChannel.placeholder")))
    if not blacklisted_channels or len(blacklisted_channels) == 0:
        description = tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListChannel.noBlacklistedChannels")
    else:
        description = "\n".join([f"{'➤' if i == 0 else ''} <#{channel[0]}>" for i, channel in enumerate(blacklisted_channels)])
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListChannel.title"),
        description=description
    )
    await commandInfo.reply(embed=embed, view=view)

    
