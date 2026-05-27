from typing import Any, cast

import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def removerole(
    command_info: utility.CommandInfo,
    user: discord.Member | None = None,
    role: discord.Role | None = None,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and command_info.user.guild_permissions
        and not command_info.user.guild_permissions.manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.removerole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")

    if command_info.guild.me.guild_permissions.manage_roles is False:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.removerole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.removerole.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    class RoleManagementView(discord.ui.View):
        def __init__(self, command_info: utility.CommandInfo, action: str = "remove") -> None:
            super().__init__(timeout=300)
            self.command_info: utility.CommandInfo = CommandInfo  # type: ignore[assignment]
            self.action: str = action
            self.selected_roles: list[discord.Role] = []
            self.selected_users: list[discord.Member] = []
            self.add_item(
                discord.ui.RoleSelect(
                    placeholder=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.selectRoles"),
                    min_values=1,
                    max_values=25,
                    custom_id="role_select",
                )
            )
            self.add_item(
                discord.ui.UserSelect(
                    placeholder=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.selectUsers"),
                    min_values=1,
                    max_values=25,
                    custom_id="user_select",
                )
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.confirm"),
            style=discord.ButtonStyle.green,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not self.selected_roles or not self.selected_users:
                await interaction.response.send_message(
                    content=tanjunLocalizer.localize(
                        self.command_info.locale,
                        f"commands.admin.{self.action}role.noSelection",
                    ),
                    ephemeral=True,
                )
                return

            success_count = 0
            for user in self.selected_users:
                for role in self.selected_roles:
                    if self.action == "remove":
                        if role in user.roles:
                            await user.remove_roles(role)
                            success_count += 1
                    else:
                        if role not in user.roles:
                            await user.add_roles(role)
                            success_count += 1

            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    str(self.command_info.locale),
                    f"commands.admin.{self.action}role.multipleSuccess",
                    count=success_count,
                ),
                view=discord.ui.View(),
            )
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.cancel"),
            style=discord.ButtonStyle.red,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.edit_message(  # type: ignore[misc]
                tanjunLocalizer.localize(
                    str(self.command_info.locale),
                    f"commands.admin.{self.action}role.cancelled",
                ),
                view=discord.ui.View(),
            )
            self.stop()

        async def on_error(
            self,
            interaction: discord.Interaction,
            error: Exception,
            item: discord.ui.Item,  # type: ignore[type-arg]
        ) -> None:
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.command_info.locale, "commands.admin.removerole.error"),
                ephemeral=True,
            )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            data = cast(dict[str, object], interaction.data)
            if data.get("component_type") == 6:  # RoleSelect
                if interaction.guild is None:
                    raise ValueError("Guild is missing")
                values = cast(list[str], data.get("values", []))
                self.selected_roles = [r for r in [interaction.guild.get_role(int(rid)) for rid in values] if r is not None]
                await interaction.response.defer()
            elif data.get("component_type") == 5:  # UserSelect
                if interaction.guild is None:
                    raise ValueError("Guild is missing")
                values = cast(list[str], data.get("values", []))
                self.selected_users = [await interaction.guild.fetch_member(int(uid)) for uid in values]
                await interaction.response.defer()
            return True

    if user is not None and role is not None:
        # Single user, single role
        if role not in user.roles:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.removerole.doesNotHaveRole.title",
                ),
                description=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.removerole.doesNotHaveRole.description",
                ),
            )
            await command_info.reply(embed=embed)

            return

        if isinstance(command_info.user, discord.Member) and command_info.user.top_role.position <= role.position:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.roleTooHigh.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.removerole.roleTooHigh.description",
                ),
            )
            await command_info.reply(embed=embed)

            return

        if command_info.guild.me.top_role.position <= role.position:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.roleTooHighBot.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.removerole.roleTooHighBot.description",
                ),
            )
            await command_info.reply(embed=embed)

            return

        await user.remove_roles(role)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.removerole.success.description",
                user=user.mention,
                role=role.mention,
            ),
        )
        await command_info.reply(embed=embed)
    else:
        # Multiple users or roles
        view = RoleManagementView(command_info, action="remove")
        await command_info.reply(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.multiplePrompt"),
            view=view,
            ephemeral=True,
        )
