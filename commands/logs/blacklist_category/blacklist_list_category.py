from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, add_log_blacklist, get_log_blacklist, remove_log_blacklist
COMPONENT_TYPE_CHANNEL_SELECT = 8

async def blacklist_list_category(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListCategory.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistListCategory.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    blacklisted_categories = await get_log_blacklist(command_info.guild.id, LogBlacklistType.CATEGORY)

    class BlacklistView(discord.ui.View):

        def __init__(self, categories: list, locale: str, guild: discord.Guild):
            super().__init__()
            self.categories = categories
            self.locale = locale
            self.guild = guild
            self.selectedIndex = 0

        @discord.ui.button(label='Remove', style=discord.ButtonStyle.danger)
        async def remove_category(self, interaction: discord.Interaction, button: discord.ui.Button):
            category_id = self.categories[self.selectedIndex]
            await remove_log_blacklist(self.guild.id, category_id, LogBlacklistType.CATEGORY)
            self.categories = [x for x in self.categories if x != category_id]
            await self.update_view(interaction)

        @discord.ui.button(label='⬆️', custom_id='up')
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.categories:
                return
            self.selectedIndex = (self.selectedIndex - 1) % len(self.categories)
            await self.update_view(interaction)

        @discord.ui.button(label='⬇️', custom_id='down')
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.categories:
                return
            self.selectedIndex = (self.selectedIndex + 1) % len(self.categories)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data['component_type'] == COMPONENT_TYPE_CHANNEL_SELECT:
                channel_id = interaction.data['values'][0]
                await add_log_blacklist(self.guild.id, channel_id, LogBlacklistType.CATEGORY)
                self.categories.append(channel_id)
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.categories or len(self.categories) == 0:
                description = locale.commands.logs.blacklistListCategory.noBlacklistedCategories(self.locale)
            else:
                if self.selectedIndex >= len(self.categories):
                    self.selectedIndex = len(self.categories) - 1
                description = '\n'.join([f"{('➤' if i == self.selectedIndex else '')} <#{category}>" for i, category in enumerate(self.categories)])
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListCategory.title(self.locale), description=description)
            await interaction.response.edit_message(embed=embed, view=self)
    view = BlacklistView(blacklisted_categories, command_info.locale, command_info.guild)
    view.add_item(discord.ui.ChannelSelect(custom_id='channel_select', channel_types=[discord.ChannelType.category], placeholder=locale.commands.logs.blacklistListCategory.addCategory.placeholder(command_info.locale)))
    if not blacklisted_categories or len(blacklisted_categories) == 0:
        description = locale.commands.logs.blacklistListCategory.noBlacklistedCategories(command_info.locale)
    else:
        description = '\n'.join([f"{('➤' if i == 0 else '')} <#{category}>" for i, category in enumerate(blacklisted_categories)])
    embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListCategory.title(command_info.locale), description=description)
    await command_info.reply(embed=embed, view=view)