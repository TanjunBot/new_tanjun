from api import get_log_role_blacklist as get_log_blacklist_roles_api, remove_log_role_blacklist as remove_log_blacklist_role_api, add_log_role_blacklist as add_log_blacklist_role_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_list_role(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistListRole.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistListRole.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    blacklisted_roles = await get_log_blacklist_roles_api(commandInfo.guild.id)

    class BlacklistView(discord.ui.View):
        def __init__(self, roles: list, locale: str, guild: discord.Guild):
            super().__init__()
            self.roles = roles
            self.locale = locale
            self.guild = guild
            self.selectedIndex = 0

        @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
        async def remove_role(self, interaction: discord.Interaction, button: discord.ui.Button):
            role_id = self.roles[self.selectedIndex][0]
            await remove_log_blacklist_role_api(self.guild.id, role_id)
            self.roles = tuple(x for x in self.roles if x[0] != role_id)
            await self.update_view(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex = (self.selectedIndex - 1) % len(self.roles)
            await self.update_view(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selectedIndex = (self.selectedIndex + 1) % len(self.roles)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 6:  # RoleSelect
                roleId = interaction.data["values"][0]
                await add_log_blacklist_role_api(self.guild.id, roleId)
                self.roles += ((roleId, ), )
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.roles or len(self.roles) == 0:
                description = tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListRole.noBlacklistedRoles")
            else:
                if self.selectedIndex >= len(self.roles):
                    self.selectedIndex = len(self.roles) - 1
                description = "\n".join([f"{'➤' if i == self.selectedIndex else ''} <@&{role[0]}>" for i, role in enumerate(self.roles)])
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListRole.title"),
                description=description
            )
            await interaction.response.edit_message(embed=embed, view=self)

    view = BlacklistView(blacklisted_roles, commandInfo.locale, commandInfo.guild)
    view.add_item(discord.ui.RoleSelect(custom_id="role_select", placeholder=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListRole.addRole.placeholder")))
    if not blacklisted_roles or len(blacklisted_roles) == 0:
        description = tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListRole.noBlacklistedRoles")
    else:
        description = "\n".join([f"{'➤' if i == 0 else ''} <@&{role[0]}>" for i, role in enumerate(blacklisted_roles)])
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistListRole.title"),
        description=description
    )
    await commandInfo.reply(embed=embed, view=view) 