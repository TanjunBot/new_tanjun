from locale_keys import locale
from typing import Any, cast
import discord
import utility
from utility import CommandInfo
from utils.checks import check_bot_permission, check_user_permission, send_check_failure
from utils.embeds import ErrorEmbedCategory, categorized_error_embed

async def removerole(command_info: utility.CommandInfo, user: discord.Member | None=None, role: discord.Role | None=None) -> None:
    result = check_user_permission(command_info, 'manage_roles', use_guild_permissions=True)
    if await send_check_failure(command_info, 'removerole', result):
        return
    result = check_bot_permission(command_info, 'manage_roles')
    if await send_check_failure(command_info, 'removerole', result):
        return

    class RoleManagementView(discord.ui.View):

        def __init__(self, command_info: utility.CommandInfo, action: str='remove') -> None:
            super().__init__(timeout=300)
            self.command_info: utility.CommandInfo = CommandInfo
            self.action: str = action
            self.selected_roles: list[discord.Role] = []
            self.selected_users: list[discord.Member] = []
            self.add_item(discord.ui.RoleSelect(placeholder=locale.commands.admin.removerole.selectRoles(str(command_info.locale)), min_values=1, max_values=25, custom_id='role_select'))
            self.add_item(discord.ui.UserSelect(placeholder=locale.commands.admin.removerole.selectUsers(str(command_info.locale)), min_values=1, max_values=25, custom_id='user_select'))

        @discord.ui.button(label=locale.commands.admin.removerole.confirm.label(str(command_info.locale)), style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if not self.selected_roles or not self.selected_users:
                await interaction.response.send_message(locale.commands.admin.removerole.noSelection(self.command_info.locale), ephemeral=True)
                return
            success_count = 0
            for user in self.selected_users:
                for role in self.selected_roles:
                    if role in user.roles:
                        await user.remove_roles(role)
                        success_count += 1
            await interaction.response.edit_message(content=locale.commands.admin.removerole.multipleSuccess(self.command_info.locale, count=success_count), view=discord.ui.View())
            self.stop()

        @discord.ui.button(label=locale.commands.admin.removerole.cancel.label(str(command_info.locale)), style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.edit_message(content=locale.commands.admin.removerole.cancelled(self.command_info.locale), view=discord.ui.View())
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            data = cast(Any, interaction.data)
            if data and data.get('component_type') == 6:
                assert interaction.guild is not None
                values = data.get('values', [])
                self.selected_roles = [r for r in [interaction.guild.get_role(int(rid)) for rid in values] if r is not None]
                await interaction.response.defer()
            elif data and data.get('component_type') == 5:
                assert interaction.guild is not None
                values = data.get('values', [])
                self.selected_users = [await interaction.guild.fetch_member(int(uid)) for uid in values]
                await interaction.response.defer()
            return True
    if user and role:
        if role not in user.roles:
            embed = utility.tanjunEmbed(title=locale.commands.admin.removerole.doesNotHaveRole.title(str(command_info.locale)), description=locale.commands.admin.removerole.doesNotHaveRole.description(str(command_info.locale)))
            await command_info.reply(embed=embed)
            return
        assert command_info.guild is not None
        if isinstance(command_info.user, discord.Member) and command_info.user.top_role.position <= role.position:
            embed = categorized_error_embed(ErrorEmbedCategory.PERMISSION, locale.commands.admin.removerole.roleTooHigh.title(str(command_info.locale)), locale.commands.admin.removerole.roleTooHigh.description(str(command_info.locale)))
            await command_info.reply(embed=embed)
            return
        if command_info.guild.me.top_role.position <= role.position:
            embed = categorized_error_embed(ErrorEmbedCategory.PERMISSION, locale.commands.admin.removerole.roleTooHighBot.title(str(command_info.locale)), locale.commands.admin.removerole.roleTooHighBot.description(str(command_info.locale)))
            await command_info.reply(embed=embed)
            return
        await user.remove_roles(role)
        embed = utility.tanjunEmbed(title=locale.commands.admin.removerole.success.title(str(command_info.locale)), description=locale.commands.admin.removerole.success.description(command_info.locale, user=user.mention, role=role.mention))
        await command_info.reply(embed=embed)
    else:
        view = RoleManagementView(command_info, action='remove')
        await command_info.reply(locale.commands.admin.removerole.multiplePrompt(str(command_info.locale)), view=view, ephemeral=True)