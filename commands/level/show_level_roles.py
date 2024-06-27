from utility import commandInfo, tanjunEmbed, checkIfHasPro
from localizer import tanjunLocalizer
from api import get_all_level_roles, add_level_role, remove_level_role
import discord
from discord.ui import View, Button, Select, Modal, TextInput
import math

class LevelRolesView(View):
    def __init__(self, commandInfo, level_roles):
        super().__init__(timeout=300)
        self.commandInfo = commandInfo
        self.level_roles = level_roles
        self.current_page = 0
        self.update_options()

    def update_options(self):
        self.clear_items()
        options = [
            discord.SelectOption(label=f"Level {level}", value=f"{level}|{','.join(roles)}")
            for level, roles in self.level_roles.items()
        ]
        
        start = self.current_page * 25
        end = start + 25
        
        select = Select(
            placeholder=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.select_placeholder"
            ),
            options=options[start:end]
        )
        select.callback = self.on_select
        self.add_item(select)
        
        if self.current_page > 0:
            prev_button = Button(label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.previous_button"
            ), style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if end < len(options):
            next_button = Button(label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.next_button"
            ), style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        add_button = Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.add_button"
            ),
            style=discord.ButtonStyle.green
        )
        add_button.callback = self.add_role
        self.add_item(add_button)
        
        remove_button = Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_button"
            ),
            style=discord.ButtonStyle.red
        )
        remove_button.callback = self.remove_role
        self.add_item(remove_button)

    async def on_select(self, interaction: discord.Interaction):
        level, roles = interaction.data["values"][0].split("|")
        level = int(level)
        roles = roles.split(",")
        
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.selected_level.title",
                level=level
            ),
            description=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.selected_level.description",
                roles=", ".join([f"<@&{role}>" for role in roles])
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
                self.commandInfo.locale, "commands.level.showlevelroles.add_role_prompt"
            ),
            view=AddRoleView(self.commandInfo),
            ephemeral=True
        )

    async def remove_role(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_role_prompt"
            ),
            view=RemoveRoleView(self.commandInfo, self.level_roles),
            ephemeral=True
        )

class AddRoleView(View):
    def __init__(self, commandInfo):
        super().__init__()
        self.commandInfo = commandInfo
        self.add_item(
            discord.ui.RoleSelect(
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.level.showlevelroles.role_select_placeholder"
                ),
                min_values=1,
                max_values=1,
                custom_id="role_select",
            )
        )
        self.add_item(Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.cancel_button"
            ),
            style=discord.ButtonStyle.red,
            custom_id="cancel_button"
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["component_type"] == 3:  # RoleSelect
            self.selected_role = interaction.data["values"][0]
            await interaction.response.send_modal(AddRoleLevelModal(self.commandInfo, self.selected_role))
        elif interaction.data["custom_id"] == "cancel_button":
            await interaction.response.edit_message(
                content=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.level.showlevelroles.add_role_cancelled"
                ),
                view=None
            )
        return True

class AddRoleLevelModal(Modal):
    def __init__(self, commandInfo, role_id):
        super().__init__(title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.showlevelroles.add_role_modal.title"
        ))
        self.commandInfo = commandInfo
        self.role_id = role_id
        self.level = TextInput(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.add_role_modal.level_label"
            ),
            placeholder=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.add_role_modal.level_placeholder"
            ),
            min_length=1,
            max_length=3
        )
        self.add_item(self.level)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            level = int(self.level.value)
            if level < 1:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.level.showlevelroles.add_role_modal.invalid_level"
                ),
                ephemeral=True
            )
            return

        add_level_role(str(interaction.guild.id), self.role_id, level)
        await interaction.response.send_message(
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.add_role_modal.success",
                role=f"<@&{self.role_id}>",
                level=level
            ),
            ephemeral=True
        )

class RemoveRoleView(View):
    def __init__(self, commandInfo, level_roles):
        super().__init__()
        self.commandInfo = commandInfo
        self.level_roles = level_roles
        self.current_page = 0
        self.update_options()

    def update_options(self):
        self.clear_items()
        options = []
        for level, roles in self.level_roles.items():
            for role_id in roles:
                options.append(discord.SelectOption(
                    label=f"Level {level} - Role {role_id}",
                    value=f"{level}|{role_id}"
                ))
        
        start = self.current_page * 25
        end = start + 25
        
        select = Select(
            placeholder=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_role_select_placeholder"
            ),
            options=options[start:end],
            max_values=min(len(options[start:end]), 25)
        )
        select.callback = self.on_select
        self.add_item(select)
        
        if self.current_page > 0:
            prev_button = Button(label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.previous_button"
            ), style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        if end < len(options):
            next_button = Button(label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.next_button"
            ), style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)

    async def on_select(self, interaction: discord.Interaction):
        self.selected_roles = interaction.data["values"]
        await interaction.response.send_message(
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_role_confirm",
                count=len(self.selected_roles)
            ),
            view=RemoveRoleConfirmView(self.commandInfo, self.selected_roles),
            ephemeral=True
        )

    async def previous_page(self, interaction: discord.Interaction):
        self.current_page = max(0, self.current_page - 1)
        self.update_options()
        await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        max_pages = math.ceil(sum(len(roles) for roles in self.level_roles.values()) / 25)
        self.current_page = min(max_pages - 1, self.current_page + 1)
        self.update_options()
        await interaction.response.edit_message(view=self)

class RemoveRoleConfirmView(View):
    def __init__(self, commandInfo, selected_roles):
        super().__init__()
        self.commandInfo = commandInfo
        self.selected_roles = selected_roles

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        for role_data in self.selected_roles:
            level, role_id = role_data.split("|")
            remove_level_role(str(interaction.guild.id), role_id, int(level))
        
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_role_success",
                count=len(self.selected_roles)
            ),
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.level.showlevelroles.remove_role_cancelled"
            ),
            view=None
        )

async def show_level_roles_command(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.showlevelroles.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.showlevelroles.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.error.no_pro.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.showlevelroles.error.no_pro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    level_roles = get_all_level_roles(str(commandInfo.guild.id))

    if not level_roles:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.no_roles.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.no_roles.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.showlevelroles.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.showlevelroles.description"
        ),
    )

    for level, roles in level_roles.items():
        embed.add_field(
            name=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.showlevelroles.level", level=level
            ),
            value=", ".join([f"<@&{role}>" for role in roles]),
            inline=False,
        )

    # This is currently really buggy and does not work. Too much work to fix. May be removed in the future or fixed.
    # view = LevelRolesView(commandInfo, level_roles)
    view = discord.ui.View()
    await commandInfo.reply(embed=embed, view=view)
