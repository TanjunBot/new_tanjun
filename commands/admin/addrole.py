import discord

import utility
from localizer import tanjunLocalizer


async def addrole(
    commandInfo: utility.commandInfo,
    user: discord.Member = None,
    role: discord.Role = None,
):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    class RoleManagementView(discord.ui.View):
        def __init__(self, commandInfo, action="add", users=None, roles=None):
            super().__init__(timeout=300)
            self.commandInfo = commandInfo
            self.action = action
            self.selected_roles = [discord.SelectDefaultValue(id=role.id, type=discord.SelectDefaultValueType.role)]
            self.selected_users = [discord.SelectDefaultValue(id=user.id, type=discord.SelectDefaultValueType.user)]
            self.add_item(
                discord.ui.RoleSelect(
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.addrole.roleSelect.placeholder",
                    ),
                    default_values=self.selected_roles,
                    min_values=1,
                    max_values=25,
                    custom_id="role_select",
                )
            )
            self.add_item(
                discord.ui.UserSelect(
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.addrole.userSelect.placeholder",
                    ),
                    default_values=self.selected_users,
                    min_values=1,
                    max_values=25,
                    custom_id="user_select",
                )
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.confirm.label"),
            style=discord.ButtonStyle.green,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            if not self.selected_roles or not self.selected_users:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        f"commands.admin.{self.action}role.noSelection",
                    ),
                    ephemeral=True,
                )
                return

            success_count = 0
            for user in self.selected_users:
                for role in self.selected_roles:
                    if self.action == "add":
                        if role not in user.roles:
                            await user.add_roles(role)
                            success_count += 1
                    else:
                        if role in user.roles:
                            await user.remove_roles(role)
                            success_count += 1

            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    f"commands.admin.{self.action}role.multipleSuccess",
                    count=success_count,
                    action=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.add_role.multipleSuccess.action",
                    )
                    if self.action == "add"
                    else tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.remove_role.multipleSuccess.action",
                    ),
                ),
                view=discord.ui.View(),
            )
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.cancel.label"),
            style=discord.ButtonStyle.red,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    f"commands.admin.{self.action}role.cancelled",
                ),
                view=discord.ui.View(),
            )
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 6:  # RoleSelect
                self.selected_roles = [interaction.guild.get_role(int(r)) for r in interaction.data["values"]]
                await interaction.response.defer()
            elif interaction.data["component_type"] == 5:  # UserSelect
                self.selected_users = [await interaction.guild.fetch_member(int(u)) for u in interaction.data["values"]]
                await interaction.response.defer()
            return True

    if user and role:
        # Single user, single role
        if role in user.roles:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.alreadyHasRole.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.addrole.alreadyHasRole.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        if commandInfo.user.top_role <= role:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.roleTooHigh.title"),
                description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.roleTooHigh.description"),
            )
            await commandInfo.reply(embed=embed)
            return

        if commandInfo.guild.me.top_role <= role:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.roleTooHighBot.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.addrole.roleTooHighBot.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        await user.add_roles(role)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.addrole.success.description",
                user=user.mention,
                role=role.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
    else:
        # Multiple users or roles
        view = RoleManagementView(commandInfo, action="add", users=user, roles=role)
        await commandInfo.reply(
            tanjunLocalizer.localize(commandInfo.locale, "commands.admin.addrole.multiplePrompt"),
            view=view,
            ephemeral=True,
        )
