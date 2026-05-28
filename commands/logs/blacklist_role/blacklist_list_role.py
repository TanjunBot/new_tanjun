import discord

import utility
from api import LogBlacklistType, add_log_blacklist, get_log_blacklist, remove_log_blacklist
from localizer import tanjunLocalizer


async def blacklist_list_role(command_info: utility.command_info):
    if not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListRole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListRole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    blacklisted_roles = await get_log_blacklist(command_info.guild.id, LogBlacklistType.ROLE)

    class BlacklistView(discord.ui.View):
        def __init__(self, roles: list, locale: str, guild: discord.Guild):
            super().__init__()
            self.roles = roles
            self.locale = locale
            self.guild = guild
            self.selected_index = 0

        @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
        async def remove_role(self, interaction: discord.Interaction, button: discord.ui.Button):
            role_id = self.roles[self.selected_index]
            await remove_log_blacklist(self.guild.id, role_id, LogBlacklistType.ROLE)
            self.roles = tuple(x for x in self.roles if x != role_id)
            await self.update_view(interaction)

        @discord.ui.button(label="⬆️", custom_id="up")
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index = (self.selected_index - 1) % len(self.roles)
            await self.update_view(interaction)

        @discord.ui.button(label="⬇️", custom_id="down")
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.selected_index = (self.selected_index + 1) % len(self.roles)
            await self.update_view(interaction)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 6:  # RoleSelect
                role_id = interaction.data["values"][0]
                await add_log_blacklist(self.guild.id, role_id, LogBlacklistType.ROLE)
                self.roles += (role_id,)
                await self.update_view(interaction)
            return True

        async def update_view(self, interaction: discord.Interaction):
            if not self.roles or len(self.roles) == 0:
                description = tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListRole.noBlacklistedRoles")
            else:
                if self.selected_index >= len(self.roles):
                    self.selected_index = len(self.roles) - 1
                description = "\n".join(
                    [f"{'➤' if i == self.selected_index else ''} <@&{role}>" for i, role in enumerate(self.roles)]
                )
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(self.locale, "commands.logs.blacklistListRole.title"),
                description=description,
            )
            await interaction.response.edit_message(embed=embed, view=self)

    view = BlacklistView(blacklisted_roles, command_info.locale, command_info.guild)
    view.add_item(
        discord.ui.RoleSelect(
            custom_id="role_select",
            placeholder=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistListRole.addRole.placeholder",
            ),
        )
    )
    if not blacklisted_roles or len(blacklisted_roles) == 0:
        description = tanjunLocalizer.localize(command_info.locale, "commands.logs.blacklistListRole.noBlacklistedRoles")
    else:
        description = "\n".join([f"{'➤' if i == 0 else ''} <@&{role}>" for i, role in enumerate(blacklisted_roles)])
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.logs.blacklistListRole.title"),
        description=description,
    )
    await command_info.reply(embed=embed, view=view)
