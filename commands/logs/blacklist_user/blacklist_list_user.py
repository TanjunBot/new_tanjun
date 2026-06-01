from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, add_log_blacklist, get_log_blacklist, remove_log_blacklist

async def blacklist_list_user(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListUser.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistListUser.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    blacklisted_users = await get_log_blacklist(command_info.guild.id, LogBlacklistType.USER)

    class BlacklistView(discord.ui.View):

        def __init__(self, users: list, locale: str, guild: discord.Guild):
            super().__init__()
            self.users = users
            self.locale = locale
            self.guild = guild
            self.selected_index = 0

        @discord.ui.button(label='Remove', style=discord.ButtonStyle.danger)
        async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button):
            user_id = self.users[self.selected_index]
            await remove_log_blacklist(self.guild.id, user_id, LogBlacklistType.USER)
            self.users = tuple((x for x in self.users if x != user_id))
            await self.update_view(interaction)

        @discord.ui.button(label='⬆️', custom_id='up')
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index = (self.selected_index - 1) % len(self.users)
            await self.update_view(interaction)

        @discord.ui.button(label='⬇️', custom_id='down')
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index = (self.selected_index + 1) % len(self.users)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data['component_type'] == 5:
                user_id = interaction.data['values'][0]
                await add_log_blacklist(self.guild.id, user_id, LogBlacklistType.USER)
                self.users += (user_id,)
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.users or len(self.users) == 0:
                description = locale.commands.logs.blacklistListUser.noBlacklistedUsers(self.locale)
            else:
                if self.selected_index >= len(self.users):
                    self.selected_index = len(self.users) - 1
                description = '\n'.join([f"{('➤' if i == self.selected_index else '')} <@{user}>" for i, user in enumerate(self.users)])
            embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListUser.title(self.locale), description=description)
            await interaction.response.edit_message(embed=embed, view=self)
    view = BlacklistView(blacklisted_users, command_info.locale, command_info.guild)
    view.add_item(discord.ui.UserSelect(custom_id='user_select', placeholder=locale.commands.logs.blacklistListUser.addUser.placeholder(command_info.locale)))
    if not blacklisted_users or len(blacklisted_users) == 0:
        description = locale.commands.logs.blacklistListUser.noBlacklistedUsers(command_info.locale)
    else:
        description = '\n'.join([f"{('➤' if i == 0 else '')} <@{user}>" for i, user in enumerate(blacklisted_users)])
    embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistListUser.title(command_info.locale), description=description)
    await command_info.reply(embed=embed, view=view)