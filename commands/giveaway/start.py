import discord
from discord import ui
import utility
from utility import commandInfo, relativeTimeStrToDate
from localizer import tanjunLocalizer
from typing import List, Optional
import asyncio


class GiveawayBuilderButton(ui.Button):
    def __init__(self, label, custom_id, style, row=None):
        super().__init__(label=label, custom_id=custom_id, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        await self.view.button_callback(interaction, self)


class CustomNameModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.custom_name.title"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.custom_name.placeholder",
                ),
                default=self.view.giveaway_data["custom_name"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        custom_name = self.children[0].value
        self.view.giveaway_data["custom_name"] = custom_name
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.custom_name.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class SponsorView(ui.View):
    def __init__(self, commandInfo, view):
        super().__init__(timeout=300)
        self.commandInfo = commandInfo
        self.selected_user = []
        self.view = view

        userSelect = discord.ui.UserSelect(
            placeholder=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.sponsor.select.placeholder",
            ),
            min_values=0,
            max_values=1,
            custom_id="user_select",
        )
        userSelect.callback = self.on_user_select
        self.add_item(userSelect)

        confirmBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.confirm"
            ),
            style=discord.ButtonStyle.green,
            custom_id="confirm",
        )
        confirmBtn.callback = self.on_button_press
        self.add_item(confirmBtn)
        cancelBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.cancel"
            ),
            style=discord.ButtonStyle.red,
            custom_id="cancel",
        )
        cancelBtn.callback = self.on_button_press
        self.add_item(cancelBtn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_button_press(self, interaction: discord.Interaction):
        if interaction.data["custom_id"] == "confirm":
            self.view.giveaway_data["sponsor"] = (
                self.selected_user if self.selected_user else None
            )
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.sponsor.updated"
            )
            await self.view.update_embed(interaction.response.edit_message)
        elif interaction.data["custom_id"] == "cancel":
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.sponsor.cancelled"
            )
            await self.view.update_embed(interaction.response.edit_message)

    async def on_user_select(self, interaction: discord.Interaction):
        self.selected_user = interaction.data["values"][0]
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.sponsor.selected",
                user=f"<@{self.selected_user}>",
            ),
        )


class ChangeWinnersModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.change_winners.label"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.change_winners.placeholder",
                ),
                default=self.view.giveaway_data["winners"],
                min_length=1,
                max_length=2,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        winners = int(self.children[0].value)
        self.view.giveaway_data["winners"] = winners
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.winner.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class EndTimeModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.end_time.label"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.end_time.placeholder",
                ),
                default=self.view.giveaway_data["end_time"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        end_time = self.children[0].value
        self.view.giveaway_data["end_time"] = end_time
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.end_time.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class StartTimeModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.start_time.label"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.start_time.placeholder",
                ),
                default=self.view.giveaway_data["start_time"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        start_time = self.children[0].value
        self.view.giveaway_data["start_time"] = start_time
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.start_time.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class RoleRequirementView(ui.View):
    def __init__(self, commandInfo, view):
        super().__init__(timeout=300)
        self.commandInfo = commandInfo
        self.selected_roles = []
        self.view = view
        self.add_item(
            discord.ui.Select(
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.role_requirement.placeholder",
                ),
                min_values=1,
                max_values=25,
                options=[
                    discord.SelectOption(label=role.name, value=role.id, default=False)
                    for role in self.commandInfo.guild.roles
                ],
                custom_id="role_select",
            )
        )
        self.add_item(
            discord.ui.Button(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.confirm"
                ),
                style=discord.ButtonStyle.green,
                custom_id="confirm",
            )
        )
        self.add_item(
            discord.ui.Button(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.cancel"
                ),
                style=discord.ButtonStyle.red,
                custom_id="cancel",
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_button_press(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if button.custom_id == "confirm":
            role_ids = [role.value for role in self.selected_roles]
            self.view.giveaway_data["role_requirement"] = role_ids
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.updated"
            )
            await self.view.update_embed(interaction.response.edit_message)
        elif button.custom_id == "cancel":
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.cancelled"
            )
            await self.view.update_embed(interaction.response.edit_message)


class MessageRequirementModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.new_message_requirement.label",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.new_message_requirement.placeholder",
                ),
                default=self.view.giveaway_data["new_message_requirement"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        new_message_requirement = int(self.children[0].value)
        self.view.giveaway_data["new_message_requirement"] = new_message_requirement
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.new_message_requirement.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class DayRequirementModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.day_requirement.label"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.day_requirement.placeholder",
                ),
                default=self.view.giveaway_data["day_requirement"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        day_requirement = int(self.children[0].value)
        self.view.giveaway_data["day_requirement"] = day_requirement
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.day_requirement.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class RoleRequirementView(ui.View):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        self.roles = self.view.giveaway_data["role_requirement"]
        super().__init__(timeout=600)  # 10 minutes timeout

        roleSelect = ui.RoleSelect(
            placeholder=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.role_requirement.placeholder",
            ),
            min_values=0,
            max_values=25,
            custom_id="role_select",
            default_values=self.roles,
        )
        roleSelect.callback = self.submit
        self.add_item(roleSelect)
        cancelBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.cancel"
            ),
            style=discord.ButtonStyle.red,
            custom_id="cancel",
        )
        cancelBtn.callback = self.cancel
        self.add_item(cancelBtn)
        confirmBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.confirm"
            ),
            style=discord.ButtonStyle.green,
            custom_id="confirm",
        )
        confirmBtn.callback = self.confirm
        self.add_item(confirmBtn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def cancel(self, interaction: discord.Interaction):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.role_requirement.cancelled"
        )
        await self.view.update_embed(interaction.response.edit_message)

    async def confirm(self, interaction: discord.Interaction):
        self.view.giveaway_data["role_requirement"] = self.roles
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.role_requirement.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)

    async def submit(self, interaction: discord.Interaction):
        role_ids = [role for role in interaction.data["values"]]
        if len(role_ids) > 1 and not utility.checkIfhasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.role_requirement.pro"
                ),
                ephemeral=True,
            )
            role_ids = role_ids[:1]
        self.roles = role_ids
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.updated"
            ),
        )


class VoiceRequirementModal(ui.Modal):
    def __init__(self, view, commandInfo, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.voice_requirement.label"
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.voice_requirement.placeholder",
                ),
                default=self.view.giveaway_data["voice_requirement"],
                min_length=1,
                max_length=100,
                required=True,
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        voice_requirement = int(self.children[0].value)
        self.view.giveaway_data["voice_requirement"] = voice_requirement
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.voice_requirement.updated"
        )
        await self.view.update_embed(interaction.response.edit_message)


class AddChannelRequirementValueModal(ui.Modal):
    def __init__(self, view, commandInfo, channel, title, description):
        self.commandInfo = commandInfo
        self.view = view
        self.title = title
        self.channel = channel
        self.description = description
        super().__init__(timeout=600)  # 10 minutes timeout

        self.add_item(
            ui.TextInput(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.add_channel_requirement.v.t",
                ),
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.add_channel_requirement.v.p",
                ),
                min_length=1,
                max_length=10,
                required=True,
            )
        )

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction):
        value = self.children[0].value
        self.view.giveaway_data["channel_requirements"][str(self.channel)] = value
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale,
            "commands.giveaway.builder.add_channel_requirement.value.updated",
        )
        await self.view.update_embed(interaction.response.edit_message)


class AddChannelRequirementView(ui.View):
    def __init__(self, commandInfo, view):
        self.commandInfo = commandInfo
        self.selected_channels = []
        self.view = view
        super().__init__(timeout=600)  # 10 minutes timeout

        channelSelect = discord.ui.ChannelSelect(
            placeholder=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.placeholder",
            ),
            min_values=1,
            max_values=1,
            custom_id="channel_select",
        )
        channelSelect.callback = self.on_channel_select
        self.add_item(channelSelect)
        confirmBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.confirm"
            ),
            style=discord.ButtonStyle.green,
            custom_id="confirm",
        )
        confirmBtn.callback = self.on_button_press
        self.add_item(confirmBtn)
        cancelBtn = discord.ui.Button(
            label=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.cancel"
            ),
            style=discord.ButtonStyle.red,
            custom_id="cancel",
        )
        cancelBtn.callback = self.on_button_press
        self.add_item(cancelBtn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_channel_select(self, interaction: discord.Interaction):
        self.selected_channels = interaction.data["values"]
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.channel.selected",
                channel=f"<#{self.selected_channels[0]}>",
            ),
        )

    async def on_button_press(
        self, interaction: discord.Interaction
    ):
        if interaction.data["custom_id"] == "confirm":
            self.view.giveaway_data["channel_requirements"][
                str(self.selected_channels[0])
            ] = 0
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.value.updated",
            )
            modal = AddChannelRequirementValueModal(
                self.view,
                self.commandInfo,
                self.selected_channels[0],
                tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.add_channel_requirement.v.t",
                ),
                tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.add_channel_requirement.value.description",
                ),
            )
            await interaction.response.send_modal(modal)
        elif interaction.data["custom_id"] == "cancel":
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.cancelled",
            )
            await self.view.update_embed(interaction.response.edit_message)


class RemoveChannelRequirementView(ui.View):
    def __init__(self, commandInfo, view):
        self.commandInfo = commandInfo
        self.selected_channels = []
        self.view = view
        super().__init__(timeout=300)

        select = discord.ui.Select(
                placeholder=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.giveaway.builder.remove_channel_requirement.placeholder",
                ),
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(
                        label=commandInfo.guild.get_channel(int(channel)).name, value=channel, default=False
                    )
                    for channel in self.view.giveaway_data["channel_requirements"]
                ],
                custom_id="channel_select",
            )
        select.callback = self.on_channel_select
        self.add_item(select)
        confirmBtn = discord.ui.Button(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.confirm"
                ),
                style=discord.ButtonStyle.green,
                custom_id="confirm",
            )
        confirmBtn.callback = self.on_button_press
        self.add_item(confirmBtn)
        cancelBtn = discord.ui.Button(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.cancel"
                ),
                style=discord.ButtonStyle.red,
                custom_id="cancel",
            )
        cancelBtn.callback = self.on_button_press
        self.add_item(cancelBtn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = tanjunLocalizer.localize(
            self.commandInfo.locale, "commands.giveaway.builder.modal.timeout"
        )
        await self.view.update_embed()

    async def on_channel_select(self, interaction: discord.Interaction):
        self.selected_channels = interaction.data["values"]
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.channel_selected",
                channel=f"<#{self.selected_channels[0]}>",
            ),
        )

    async def on_button_press(
        self, interaction: discord.Interaction
    ):
        if interaction.data["custom_id"] == "confirm":
            channel_id = self.selected_channels[0]
            self.view.giveaway_data["channel_requirements"].pop(str(channel_id))
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.add_channel_requirement.removed"
            )
            await self.view.update_embed(interaction.response.edit_message)
        elif interaction.data["custom_id"] == "cancel":
            self.view.last_action = tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.cancelled",
            )


class GiveawayBuilder(ui.View):
    def __init__(
        self,
        commandInfo,
        title,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        end_time,
        start_time,
        new_message_requirement,
        day_requirement,
        role_requirement,
        voice_requirement,
    ):
        super().__init__(timeout=600)  # 10 minutes timeout
        self.commandInfo = commandInfo
        self.giveaway_data = {
            "title": title,
            "description": "",
            "winners": winners,
            "with_button": with_button,
            "custom_name": custom_name,
            "sponsor": sponsor,
            "price": price,
            "message": message,
            "end_time": end_time,
            "start_time": start_time,
            "new_message_requirement": new_message_requirement,
            "day_requirement": day_requirement,
            "role_requirement": [role_requirement] if role_requirement else [],
            "voice_requirement": voice_requirement,
            "channel_requirements": {},
        }
        self.update_buttons()
        self.last_action = None
        self.generator_message = None

    def update_buttons(self):
        self.clear_items()

        # Add all the buttons
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.change_description"
                ),
                custom_id="change_description",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.change_winners.label"
                ),
                custom_id="change_winners",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.with_button"
                ),
                custom_id="toggle_button",
                style=(
                    discord.ButtonStyle.success
                    if self.giveaway_data["with_button"]
                    else discord.ButtonStyle.danger
                ),
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.custom_name.label"
                ),
                custom_id="custom_name",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.sponsor.label"
                ),
                custom_id="sponsor",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.price.label"
                ),
                custom_id="price",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.message.label"
                ),
                custom_id="message",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.end_time.label"
                ),
                custom_id="end_time",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.start_time.label"
                ),
                custom_id="start_time",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.new_message_requirement.label"
                ),
                custom_id="new_message_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.day_requirement.label"
                ),
                custom_id="day_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.role_requirement.label"
                ),
                custom_id="role_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.voice_requirement.label"
                ),
                custom_id="voice_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.add_channel_requirement.label"
                ),
                custom_id="add_channel_requirement",
                style=discord.ButtonStyle.primary,
            )
        )
        if self.giveaway_data["channel_requirements"]:
            self.add_item(
                GiveawayBuilderButton(
                    label=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.giveaway.builder.remove_channel_requirement.label",
                    ),
                    custom_id="remove_channel_requirement",
                    style=discord.ButtonStyle.primary,
                )
            )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.preview"
                ),
                custom_id="preview",
                style=discord.ButtonStyle.secondary,
                row=3,
            )
        )
        self.add_item(
            GiveawayBuilderButton(
                label=tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.confirm"
                ),
                custom_id="confirm",
                style=discord.ButtonStyle.success,
                row=3
            )
        )

    async def update_embed(self, editmessage=None):
        self.update_buttons()
        embed = discord.Embed(
            title=self.giveaway_data["title"],
            description=(f"## `{self.last_action}`\n\n" if self.last_action else "")
            + self.giveaway_data["description"],
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.winners"
            ),
            value=self.giveaway_data["winners"],
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.with_button"
            ),
            value=(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.true"
                )
                if self.giveaway_data["with_button"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.false"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.custom_name.label"
            ),
            value=(
                self.giveaway_data["custom_name"]
                if self.giveaway_data["custom_name"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.sponsor.label"
            ),
            value=(
                f"<@{self.giveaway_data['sponsor']}>"
                if self.giveaway_data["sponsor"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.price.label"
            ),
            value=(
                self.giveaway_data["price"]
                if self.giveaway_data["price"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.message.label"
            ),
            value=(
                self.giveaway_data["message"]
                if self.giveaway_data["message"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.end_time.label"
            ),
            value=(
                f"<t:{int(relativeTimeStrToDate(self.giveaway_data['end_time']).timestamp())}:R>"
                if self.giveaway_data["end_time"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.start_time.label"
            ),
            value=(
                f"<t:{int(relativeTimeStrToDate(self.giveaway_data['start_time']).timestamp())}:R>"
                if self.giveaway_data["start_time"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.new_message_requirement.label"
            ),
            value=(
                self.giveaway_data["new_message_requirement"]
                if self.giveaway_data["new_message_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.day_requirement.label"
            ),
            value=(
                self.giveaway_data["day_requirement"]
                if self.giveaway_data["day_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.label"
            ),
            value=(
                (
                    " ".join(
                        [
                            f"<@&{role}>"
                            for role in self.giveaway_data["role_requirement"]
                        ]
                    )
                )
                if self.giveaway_data["role_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.voice_requirement.label"
            ),
            value=(
                self.giveaway_data["voice_requirement"]
                if self.giveaway_data["voice_requirement"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        embed.add_field(
            name=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.add_channel_requirement.label"
            ),
            value=(
                "\n".join(
                    [
                        f"{self.commandInfo.guild.get_channel(int(channel_id)).mention}: {value}"
                        for channel_id, value in self.giveaway_data[
                            "channel_requirements"
                        ].items()
                    ]
                )
                if self.giveaway_data["channel_requirements"]
                else tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.none"
                )
            ),
        )
        if not editmessage:
            await self.generator_message.edit(embed=embed, view=self, content="")
        else:
            await editmessage(embed=embed, view=self, content="")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.commandInfo.user:
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.not_authorized"
                ),
                ephemeral=True,
            )
            return False
        return True

    async def button_callback(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        print("Button pressed")
        if button.custom_id == "change_description":
            await self.change_description(interaction, button)
        elif button.custom_id == "change_winners":
            await self.change_winners(interaction, button)
        elif button.custom_id == "toggle_button":
            await self.toggle_button(interaction, button)
        elif button.custom_id == "custom_name":
            await self.custom_name(interaction, button)
        elif button.custom_id == "sponsor":
            await self.sponsor(interaction, button)
        elif button.custom_id == "price":
            await self.price(interaction, button)
        elif button.custom_id == "message":
            await self.message(interaction, button)
        elif button.custom_id == "end_time":
            await self.end_time(interaction, button)
        elif button.custom_id == "start_time":
            await self.start_time(interaction, button)
        elif button.custom_id == "new_message_requirement":
            await self.new_message_requirement(interaction, button)
        elif button.custom_id == "day_requirement":
            await self.day_requirement(interaction, button)
        elif button.custom_id == "role_requirement":
            await self.role_requirement(interaction, button)
        elif button.custom_id == "voice_requirement":
            await self.voice_requirement(interaction, button)
        elif button.custom_id == "add_channel_requirement":
            await self.add_channel_requirement(interaction, button)
        elif button.custom_id == "remove_channel_requirement":
            await self.remove_channel_requirement(interaction, button)
        elif button.custom_id == "preview":
            await self.preview(interaction, button)
        elif button.custom_id == "confirm":
            await self.confirm(interaction, button)

    async def change_description(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_description"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.description.timeout"
                )
            )
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data["description"] = message.content
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.description.updated"
                )
            )
            await self.update_embed()

    async def change_winners(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        modal = ChangeWinnersModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.change_winners.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.change_winners.description"
            ),
        )

        await interaction.response.send_modal(modal)

    async def toggle_button(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        self.giveaway_data["with_button"] = not self.giveaway_data["with_button"]
        self.update_buttons()
        await self.update_embed(interaction.response.edit_message)

    async def custom_name(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = CustomNameModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.custom_name.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.custom_name.description"
            ),
        )
        await interaction.response.send_modal(modal)

    async def sponsor(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        view = SponsorView(self.commandInfo, self)
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.sponsor.select.placeholder"
            ),
            view=view,
            embed=None,
        )

    async def price(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_price"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.price.timeout"
                )
            )
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data["price"] = message.content
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.price.updated"
                )
            )
            await self.update_embed()

    async def message(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.enter_message"
            ),
            embed=None,
            view=discord.ui.View(),
        )
        try:
            message = await self.commandInfo.client.wait_for(
                "message",
                check=lambda m: m.author == interaction.user
                and m.channel == interaction.channel,
                timeout=300.0,
            )
        except asyncio.TimeoutError:
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.message.timeout"
                )
            )
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data["message"] = message.content
            self.last_action = (
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.message.updated"
                )
            )
            await self.update_embed()

    async def end_time(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        modal = EndTimeModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.end_time.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.end_time.description"
            ),
        )
        await interaction.response.send_modal(modal)

    async def start_time(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = StartTimeModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.start_time.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.start_time.description"
            ),
        )
        await interaction.response.send_modal(modal)

    async def new_message_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        modal = MessageRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.new_message_requirement.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.new_message_requirement.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def day_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = DayRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.day_requirement.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.day_requirement.description"
            ),
        )
        await interaction.response.send_modal(modal)

    async def role_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        view = RoleRequirementView(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.description"
            ),
        )
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.role_requirement.select"
            ),
            view=view,
            embed=None,
        )

    async def voice_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        modal = VoiceRequirementModal(
            self,
            self.commandInfo,
            tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.giveaway.builder.voice_requirement.title"
            ),
            tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.voice_requirement.description",
            ),
        )
        await interaction.response.send_modal(modal)

    async def add_channel_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        if not utility.checkIfHasPro(self.commandInfo.guild):
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.giveaway.builder.pro_required"
                ),
                ephemeral=True,
            )
            return
        view = AddChannelRequirementView(self.commandInfo, self)

        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.add_channel_requirement.select",
            ),
            embed=None,
            view=view,
        )

    async def remove_channel_requirement(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ):
        view = RemoveChannelRequirementView(self.commandInfo, self)
        await interaction.response.edit_message(
            content=tanjunLocalizer.localize(
                self.commandInfo.locale,
                "commands.giveaway.builder.remove_channel_requirement.select",
            ),
            embed=None,
            view=view,
        )

    async def preview(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ): ...

    async def confirm(
        self, interaction: discord.Interaction, button: GiveawayBuilderButton
    ): ...


async def start_giveaway(
    commandInfo,
    title,
    winners,
    with_button,
    custom_name,
    sponsor,
    price,
    message,
    end_time,
    start_time,
    new_message_requirement,
    day_requirement,
    role_requirement,
    voice_requirement,
):
    if not commandInfo.user.guild_permissions.manage_guild:
        await commandInfo.reply(
            tanjunLocalizer.localize(
                commandInfo.locale, "giveaway.start.no_permission"
            ),
        )
        return

    # Create the GiveawayBuilder view
    view = GiveawayBuilder(
        commandInfo,
        title,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        end_time,
        start_time,
        new_message_requirement,
        day_requirement,
        role_requirement,
        voice_requirement,
    )

    # Send the initial message with the GiveawayBuilder view
    embed = discord.Embed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.giveaway.builder.loading"),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.giveaway.builder.loading"
        ),
    )
    message = await commandInfo.reply(embed=embed, view=view)
    view.generator_message = message
    await view.update_embed()
