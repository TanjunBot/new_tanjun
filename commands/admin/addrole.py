from typing import Any, cast

import discord

import utility
from localizer import tanjunLocalizer


async def addrole(
    command_info: utility.CommandInfo,
    user: discord.Member | None = None,
    role: discord.Role | None = None,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.addrole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.addrole.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    class RoleManagementView(discord.ui.View):
        def __init__(
            self,
            command_info: utility.CommandInfo,
            action: str = "add",
            user: discord.Member | None = None,
            role: discord.Role | None = None,
        ) -> None:
            super().__init__(timeout=300)
            self.command_info = command_info
            self.action = action
            self.selected_roles: list[discord.Role] = [role] if role else []
            self.selected_users: list[discord.Member] = [user] if user else []

            default_roles = (
                [discord.SelectDefaultValue(id=role.id, type=discord.SelectDefaultValueType.role)] if role else None
            )
            default_users = (
                [discord.SelectDefaultValue(id=user.id, type=discord.SelectDefaultValueType.user)] if user else None
            )

            self.add_item(
                discord.ui.RoleSelect(
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.addrole.roleSelect.placeholder",
                    ),
                    default_values=default_roles,  # type: ignore[arg-type]
                    min_values=1,
                    max_values=25,
                    custom_id="role_select",
                )
            )
            self.add_item(
                discord.ui.UserSelect(
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.addrole.userSelect.placeholder",
                    ),
                    default_values=default_users,  # type: ignore[arg-type]
                    min_values=1,
                    max_values=25,
                    custom_id="user_select",
                )
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.confirm.label"),
            style=discord.ButtonStyle.green,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not self.selected_roles or not self.selected_users:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
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
                    self.command_info.locale,  # type: ignore[misc]
                    f"commands.admin.{self.action}role.multipleSuccess",
                    count=success_count,
                    action=tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
                        "commands.admin.add_role.multipleSuccess.action",
                    )
                    if self.action == "add"
                    else tanjunLocalizer.localize(
                        self.command_info.locale,  # type: ignore[misc]
                        "commands.admin.remove_role.multipleSuccess.action",
                    ),
                ),
                view=discord.ui.View(),
            )
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.cancel.label"),
            style=discord.ButtonStyle.red,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.command_info.locale,  # type: ignore[misc]
                    f"commands.admin.{self.action}role.cancelled",
                ),
                view=discord.ui.View(),
            )
            self.stop()

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            data = cast(Any, interaction.data)
            if data and data.get("component_type") == 6:  # RoleSelect
                assert interaction.guild is not None
                values = data.get("values", [])
                self.selected_roles = [r for r in [interaction.guild.get_role(int(rid)) for rid in values] if r is not None]
                await interaction.response.defer()
            elif data and data.get("component_type") == 5:  # UserSelect
                assert interaction.guild is not None
                values = data.get("values", [])
                self.selected_users = [await interaction.guild.fetch_member(int(uid)) for uid in values]
                await interaction.response.defer()
            return True

    if user and role:
        # Single user, single role
        if role in user.roles:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.alreadyHasRole.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.addrole.alreadyHasRole.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

        if isinstance(command_info.user, discord.Member) and command_info.user.top_role <= role:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.roleTooHigh.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale), "commands.admin.addrole.roleTooHigh.description"
                ),
            )
            await command_info.reply(embed=embed)
            return

        if command_info.guild.me.top_role <= role:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.roleTooHighBot.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.addrole.roleTooHighBot.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

        await user.add_roles(role)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.addrole.success.description",
                user=user.mention,
                role=role.mention,
            ),
        )
        await command_info.reply(embed=embed)
    else:
        # Multiple users or roles
        view = RoleManagementView(command_info, action="add", user=user, role=role)
        await command_info.reply(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.addrole.multiplePrompt"),
            view=view,
            ephemeral=True,
        )
