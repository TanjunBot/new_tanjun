import math

import discord
from discord.ui import Button, Modal, Select, TextInput, View

from api import add_level_role, get_all_level_roles, remove_level_role
from localizer import tanjunLocalizer
from utility import command_info, tanjunEmbed


async def show_level_roles_command(command_info: command_info):
    if not command_info.user.guild_permissions.manage_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.showlevelroles.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.showlevelroles.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    level_roles = await get_all_level_roles(str(command_info.guild.id))

    class LevelRolesView(View):
        def __init__(self, command_info, level_roles):
            super().__init__(timeout=300)
            self.command_info = command_info
            self.level_roles = level_roles
            self.current_page = 0
            self.update_options()

        def update_options(self):
            self.clear_items()
            options = [
                discord.SelectOption(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.data",
                        level=group.level,
                    ),
                    value=f"{group.level}|{','.join(group.role_ids)}",
                )
                for group in self.level_roles
            ]

            start = self.current_page * 25
            end = start + 25

            select = Select(
                placeholder=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.select_placeholder",
                ),
                options=options[start:end],
            )
            select.callback = self.on_select
            self.add_item(select)

            if self.current_page > 0:
                prev_button = Button(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.previous_button",
                    ),
                    style=discord.ButtonStyle.gray,
                )
                prev_button.callback = self.previous_page
                self.add_item(prev_button)

            if end < len(options):
                next_button = Button(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.next_button",
                    ),
                    style=discord.ButtonStyle.gray,
                )
                next_button.callback = self.next_page
                self.add_item(next_button)

            add_button = Button(
                label=tanjunLocalizer.localize(self.command_info.locale, "commands.level.showlevelroles.add_button"),
                style=discord.ButtonStyle.green,
            )
            add_button.callback = self.add_role
            self.add_item(add_button)

            remove_button = Button(
                label=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_button",
                ),
                style=discord.ButtonStyle.red,
            )
            remove_button.callback = self.remove_role
            self.add_item(remove_button)

        async def on_select(self, interaction: discord.Interaction):
            level, roles = interaction.data["values"][0].split("|")
            level = int(level)
            roles = roles.split(",")

            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.selected_level.title",
                    level=level,
                ),
                description=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.selected_level.description",
                    roles=", ".join([f"<@&{role}>" for role in roles]),
                ),
            )

            await interaction.response.edit_message(embed=embed, view=self)

        async def previous_page(self, interaction: discord.Interaction):
            self.current_page = max(0, self.current_page - 1)
            self.update_options()
            await interaction.response.edit_message(view=self)

        async def next_page(self, interaction: discord.Interaction):
            max_pages = math.ceil(len(self.level_roles) / 25)
            self.current_page = min(max_pages - 1, self.current_page + 1)
            self.update_options()
            await interaction.response.edit_message(view=self)

        # this is currently really buggy and does not work. Too much work to fix. May be removed in the future or fixed.
        async def add_role(self, interaction: discord.Interaction):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.add_role_prompt",
                ),
                view=AddRoleView(self.command_info),
                ephemeral=True,
            )

        async def remove_role(self, interaction: discord.Interaction):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_role_prompt",
                ),
                view=RemoveRoleView(self.command_info, self.level_roles),
                ephemeral=True,
            )

    class AddRoleView(View):
        def __init__(self, command_info):
            super().__init__()
            self.command_info = command_info
            self.add_item(
                discord.ui.RoleSelect(
                    placeholder=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.role_select_placeholder",
                    ),
                    min_values=1,
                    max_values=1,
                    custom_id="role_select",
                )
            )
            self.add_item(
                Button(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.cancel_button",
                    ),
                    style=discord.ButtonStyle.red,
                    custom_id="cancel_button",
                )
            )

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.data["component_type"] == 3:  # RoleSelect
                self.selected_role = interaction.data["values"][0]
                await interaction.response.send_modal(AddRoleLevelModal(self.command_info, self.selected_role))
            elif interaction.data["custom_id"] == "cancel_button":
                await interaction.response.edit_message(
                    content=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.add_role_cancelled",
                    ),
                    view=None,
                )
            return True

    class AddRoleLevelModal(Modal):
        def __init__(self, command_info, role_id):
            super().__init__(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.level.showlevelroles.add_role_modal.title",
                )
            )
            self.command_info = command_info
            self.role_id = role_id
            self.level = TextInput(
                label=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.level.showlevelroles.add_role_modal.level_label",
                ),
                placeholder=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.level.showlevelroles.add_role_modal.level_placeholder",
                ),
                min_length=1,
                max_length=3,
            )
            self.add_item(self.level)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                level = int(self.level.value)
                if level < 1:
                    pass
                    # raise ValueError
            except ValueError:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.add_role_modal.invalid_level",
                    ),
                    ephemeral=True,
                )
                return

            await add_level_role(str(interaction.guild.id), self.role_id, level)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.add_role_modal.success",
                    role=f"<@&{self.role_id}>",
                    level=level,
                ),
                ephemeral=True,
            )

    class RemoveRoleView(View):
        def __init__(self, command_info, level_roles):
            super().__init__()
            self.command_info = command_info
            self.level_roles = level_roles
            self.current_page = 0
            self.update_options()

        def update_options(self):
            self.clear_items()
            options = []
            for group in self.level_roles:
                for role_id in group.role_ids:
                    options.append(
                        discord.SelectOption(
                            label=tanjunLocalizer.localize(
                                self.command_info.locale,
                                "commands.level.showlevelroles.remove_role_data",
                                level=group.level,
                                role=f"{role_id}",
                            ),
                            value=f"{level}|{role_id}",
                        )
                    )

            start = self.current_page * 25
            end = start + 25

            select = Select(
                placeholder=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_role_select_placeholder",
                ),
                options=options[start:end],
                max_values=min(len(options[start:end]), 25),
            )
            select.callback = self.on_select
            self.add_item(select)

            if self.current_page > 0:
                prev_button = Button(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.previous_button",
                    ),
                    style=discord.ButtonStyle.gray,
                )
                prev_button.callback = self.previous_page
                self.add_item(prev_button)

            if end < len(options):
                next_button = Button(
                    label=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.level.showlevelroles.next_button",
                    ),
                    style=discord.ButtonStyle.gray,
                )
                next_button.callback = self.next_page
                self.add_item(next_button)

        async def on_select(self, interaction: discord.Interaction):
            self.selected_roles = interaction.data["values"]
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_role_confirm",
                    count=len(self.selected_roles),
                ),
                view=RemoveRoleConfirmView(self.command_info, self.selected_roles),
                ephemeral=True,
            )

        async def previous_page(self, interaction: discord.Interaction):
            self.current_page = max(0, self.current_page - 1)
            self.update_options()
            await interaction.response.edit_message(view=self)

        async def next_page(self, interaction: discord.Interaction):
            max_pages = math.ceil(sum(len(group.role_ids) for group in self.level_roles) / 25)
            self.current_page = min(max_pages - 1, self.current_page + 1)
            self.update_options()
            await interaction.response.edit_message(view=self)

    class RemoveRoleConfirmView(View):
        def __init__(self, command_info, selected_roles):
            super().__init__()
            self.command_info = command_info
            self.selected_roles = selected_roles

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.showlevelroles.remove_role_confirm.confirm_button",
            ),
            style=discord.ButtonStyle.red,
        )
        async def confirm(self, interaction: discord.Interaction, button: Button):
            for role_data in self.selected_roles:
                level, role_id = role_data.split("|")
                await remove_level_role(str(interaction.guild.id), role_id, int(level))

            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_role_success",
                    count=len(self.selected_roles),
                ),
                view=None,
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.showlevelroles.remove_role_confirm.cancel_button",
            ),
            style=discord.ButtonStyle.gray,
        )
        async def cancel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.level.showlevelroles.remove_role_cancelled",
                ),
                view=None,
            )

    if not level_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(command_info.locale, "commands.level.showlevelroles.no_roles.title"),
            description=tanjunLocalizer.localize(command_info.locale, "commands.level.showlevelroles.no_roles.description"),
        )
        await command_info.reply(embed=embed)
        return

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.level.showlevelroles.title"),
        description=tanjunLocalizer.localize(command_info.locale, "commands.level.showlevelroles.description"),
    )

    for group in level_roles:
        embed.add_field(
            name=tanjunLocalizer.localize(command_info.locale, "commands.level.showlevelroles.level", level=group.level),
            value=", ".join([f"<@&{role}>" for role in group.role_ids]),
            inline=False,
        )

    # This is currently really buggy and does not work. Too much work to fix. May be removed in the future or fixed.
    # view = LevelRolesView(command_info, level_roles)
    view = discord.ui.View()
    await command_info.reply(embed=embed, view=view)
