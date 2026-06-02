from locale_keys import locale
from typing import Any, cast
import discord
import utility
from utils.checks import check_bot_permission, check_user_permission, send_check_failure
from utils.embeds import ErrorEmbedCategory, categorized_error_embed

async def addrole(command_info: utility.CommandInfo, user: discord.Member | None=None, role: discord.Role | None=None) -> None:
    result = check_user_permission(command_info, 'manage_roles', use_guild_permissions=True)
    if await send_check_failure(command_info, 'addrole', result):
        return
    result = check_bot_permission(command_info, 'manage_roles')
    if await send_check_failure(command_info, 'addrole', result):
        return

    class RoleManagementView(discord.ui.View):

        def __init__(self, command_info: utility.CommandInfo, action: str='add', user: discord.Member | None=None, role: discord.Role | None=None) -> None:
            super().__init__(timeout=300)
            self.command_info = command_info
            self.action = action
            self.selected_roles: list[discord.Role] = [role] if role else []
            self.selected_users: list[discord.Member] = [user] if user else []
            default_roles = [discord.SelectDefaultValue(id=role.id, type=discord.SelectDefaultValueType.role)] if role else None
            default_users = [discord.SelectDefaultValue(id=user.id, type=discord.SelectDefaultValueType.user)] if user else None
            self.add_item(discord.ui.RoleSelect(placeholder=locale.commands.admin.addrole.roleSelect.placeholder(command_info.locale), default_values=default_roles, min_values=1, max_values=25, custom_id='role_select'))
            self.add_item(discord.ui.UserSelect(placeholder=locale.commands.admin.addrole.userSelect.placeholder(command_info.locale), default_values=default_users, min_values=1, max_values=25, custom_id='user_select'))

        @discord.ui.button(label=locale.commands.admin.addrole.confirm.label(str(command_info.locale)), style=discord.ButtonStyle.green)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if not self.selected_roles or not self.selected_users:
                role_cmd = locale.commands.admin.addrole if self.action == 'add' else locale.commands.admin.removerole
                await interaction.response.send_message(role_cmd.noSelection(self.command_info.locale), ephemeral=True)
                return
            success_count = 0
            for user in self.selected_users:
                for role in self.selected_roles:
                    if self.action == 'add':
                        if role not in user.roles:
                            await user.add_roles(role)
                            success_count += 1
                    elif role in user.roles:
                        await user.remove_roles(role)
                        success_count += 1
            role_cmd = locale.commands.admin.addrole if self.action == 'add' else locale.commands.admin.removerole
            action_label = locale.commands.admin.add_role.multipleSuccess.action(self.command_info.locale) if self.action == 'add' else locale.commands.admin.remove_role.multipleSuccess.action(self.command_info.locale)
            await interaction.response.edit_message(content=role_cmd.multipleSuccess(self.command_info.locale, count=success_count, action=action_label), view=discord.ui.View())
            self.stop()

        @discord.ui.button(label=locale.commands.admin.addrole.cancel.label(str(command_info.locale)), style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            role_cmd = locale.commands.admin.addrole if self.action == 'add' else locale.commands.admin.removerole
            await interaction.response.edit_message(content=role_cmd.cancelled(self.command_info.locale), view=discord.ui.View())
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
        if role in user.roles:
            embed = utility.tanjunEmbed(title=locale.commands.admin.addrole.alreadyHasRole.title(str(command_info.locale)), description=locale.commands.admin.addrole.alreadyHasRole.description(command_info.locale))
            await command_info.reply(embed=embed)
            return
        assert command_info.guild is not None
        if isinstance(command_info.user, discord.Member) and command_info.user.top_role <= role:
            embed = categorized_error_embed(ErrorEmbedCategory.PERMISSION, locale.commands.admin.addrole.roleTooHigh.title(str(command_info.locale)), locale.commands.admin.addrole.roleTooHigh.description(str(command_info.locale)))
            await command_info.reply(embed=embed)
            return
        if command_info.guild.me.top_role <= role:
            embed = categorized_error_embed(ErrorEmbedCategory.PERMISSION, locale.commands.admin.addrole.roleTooHighBot.title(str(command_info.locale)), locale.commands.admin.addrole.roleTooHighBot.description(command_info.locale))
            await command_info.reply(embed=embed)
            return
        await user.add_roles(role)
        embed = utility.tanjunEmbed(title=locale.commands.admin.addrole.success.title(str(command_info.locale)), description=locale.commands.admin.addrole.success.description(command_info.locale, user=user.mention, role=role.mention))
        await command_info.reply(embed=embed)
    else:
        view = RoleManagementView(command_info, action='add', user=user, role=role)
        await command_info.reply(locale.commands.admin.addrole.multiplePrompt(str(command_info.locale)), view=view, ephemeral=True)