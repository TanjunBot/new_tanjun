from typing import Any, cast

import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo
from utils.checks import check_bot_permission, check_user_permission, send_check_failure
from utils.embeds import ErrorEmbedCategory, categorized_error_embed


async def removerole(
    command_info: utility.CommandInfo,
    user: discord.Member | None = None,
    role: discord.Role | None = None,
) -> None:
    # User permission check
    result = check_user_permission(command_info, "manage_roles", use_guild_permissions=True)
    if await send_check_failure(command_info, "removerole", result):
        return

    # Bot permission check
    result = check_bot_permission(command_info, "manage_roles")
    if await send_check_failure(command_info, "removerole", result):
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
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.confirm.label"),
            style=discord.ButtonStyle.green,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if not self.selected_roles or not self.selected_users:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.admin.removerole.noSelection",
                    ),
                    ephemeral=True,
                )
                return

            success_count = 0
            for user in self.selected_users:
                for role in self.selected_roles:
                    if role in user.roles:
                        await user.remove_roles(role)
                        success_count += 1

            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.admin.removerole.multipleSuccess",
                    count=success_count,
                ),
                view=discord.ui.View(),
            )
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.cancel.label"),
            style=discord.ButtonStyle.red,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.admin.removerole.cancelled",
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
        if role not in user.roles:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.doesNotHaveRole.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.removerole.doesNotHaveRole.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

        # Hierarchy checks
        assert command_info.guild is not None
        if isinstance(command_info.user, discord.Member) and command_info.user.top_role.position <= role.position:
            embed = categorized_error_embed(
                ErrorEmbedCategory.PERMISSION,
                tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.roleTooHigh.title"),
                tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.roleTooHigh.description"),
            )
            await command_info.reply(embed=embed)
            return

        if command_info.guild.me.top_role.position <= role.position:
            embed = categorized_error_embed(
                ErrorEmbedCategory.PERMISSION,
                tanjunLocalizer.localize(str(command_info.locale), "commands.admin.removerole.roleTooHighBot.title"),
                tanjunLocalizer.localize(
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
                command_info.locale,
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
