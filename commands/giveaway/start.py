from locale_keys import locale
import datetime
import discord
from discord import ui
import utility
from commands.giveaway.utility import generateGiveawayEmbed, sendGiveaway
from services.giveaway_service import GiveawayCreateParams, giveaway_service

class GiveawayBuilderButton(ui.Button):

    def __init__(self, label, custom_id, style, row=None):
        super().__init__(label=label, custom_id=custom_id, style=style, row=row)

    async def callback(self, interaction: discord.Interaction):
        await self.view.button_callback(interaction, self)

class CustomNameModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.custom_name.title(self.command_info.locale), placeholder=locale.commands.giveaway.builder.custom_name.placeholder(self.command_info.locale), default=self.view.giveaway_data['custom_name'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        custom_name = self.children[0].value
        self.view.giveaway_data['custom_name'] = custom_name
        self.view.last_action = locale.commands.giveaway.builder.custom_name.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class SponsorView(ui.View):

    def __init__(self, command_info, view):
        super().__init__(timeout=300)
        self.command_info = command_info
        self.selected_user = []
        self.view = view
        user_select = discord.ui.UserSelect(placeholder=locale.commands.giveaway.builder.sponsor.select.placeholder(self.command_info.locale), min_values=0, max_values=1, custom_id='user_select')
        user_select.callback = self.on_user_select
        self.add_item(user_select)
        confirm_btn = discord.ui.Button(label=locale.commands.giveaway.builder.confirm(self.command_info.locale), style=discord.ButtonStyle.green, custom_id='confirm')
        confirm_btn.callback = self.on_button_press
        self.add_item(confirm_btn)
        cancel_btn = discord.ui.Button(label=locale.commands.giveaway.builder.cancel(self.command_info.locale), style=discord.ButtonStyle.red, custom_id='cancel')
        cancel_btn.callback = self.on_button_press
        self.add_item(cancel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_button_press(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == 'confirm':
            self.view.giveaway_data['sponsor'] = self.selected_user if self.selected_user else None
            self.view.last_action = locale.commands.giveaway.builder.sponsor.updated(self.command_info.locale)
            await self.view.update_embed(interaction.response.edit_message)
        elif interaction.data['custom_id'] == 'cancel':
            self.view.last_action = locale.commands.giveaway.builder.sponsor.cancelled(self.command_info.locale)
            await self.view.update_embed(interaction.response.edit_message)

    async def on_user_select(self, interaction: discord.Interaction):
        self.selected_user = interaction.data['values'][0]
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.sponsor.selected(self.command_info.locale, user=f'<@{self.selected_user}>'))

class ChangeWinnersModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.change_winners.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.change_winners.placeholder(self.command_info.locale), default=self.view.giveaway_data['winners'], min_length=1, max_length=2, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        winners = int(self.children[0].value)
        self.view.giveaway_data['winners'] = winners
        self.view.last_action = locale.commands.giveaway.builder.winner.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class EndTimeModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.end_time.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.end_time.placeholder(self.command_info.locale), default=self.view.giveaway_data['end_time'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        end_time = self.children[0].value
        self.view.giveaway_data['end_time'] = end_time
        self.view.last_action = locale.commands.giveaway.builder.end_time.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class StartTimeModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.start_time.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.start_time.placeholder(self.command_info.locale), default=self.view.giveaway_data['start_time'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        start_time = self.children[0].value
        self.view.giveaway_data['start_time'] = start_time
        self.view.last_action = locale.commands.giveaway.builder.start_time.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class MessageRequirementModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.new_message_requirement.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.new_message_requirement.placeholder(self.command_info.locale), default=self.view.giveaway_data['new_message_requirement'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        new_message_requirement = int(self.children[0].value)
        self.view.giveaway_data['new_message_requirement'] = new_message_requirement
        self.view.last_action = locale.commands.giveaway.builder.new_message_requirement.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class DayRequirementModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.day_requirement.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.day_requirement.placeholder(self.command_info.locale), default=self.view.giveaway_data['day_requirement'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        day_requirement = int(self.children[0].value)
        self.view.giveaway_data['day_requirement'] = day_requirement
        self.view.last_action = locale.commands.giveaway.builder.day_requirement.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class RoleRequirementView(ui.View):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        self.roles = self.view.giveaway_data['role_requirement']
        super().__init__(timeout=600)
        role_select = ui.RoleSelect(placeholder=locale.commands.giveaway.builder.role_requirement.placeholder(self.command_info.locale), min_values=0, max_values=25, custom_id='role_select', default_values=self.roles)
        role_select.callback = self.submit
        self.add_item(role_select)
        cancel_btn = discord.ui.Button(label=locale.commands.giveaway.builder.cancel(self.command_info.locale), style=discord.ButtonStyle.red, custom_id='cancel')
        cancel_btn.callback = self.cancel
        self.add_item(cancel_btn)
        confirm_btn = discord.ui.Button(label=locale.commands.giveaway.builder.confirm(self.command_info.locale), style=discord.ButtonStyle.green, custom_id='confirm')
        confirm_btn.callback = self.confirm
        self.add_item(confirm_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def cancel(self, interaction: discord.Interaction):
        self.view.last_action = locale.commands.giveaway.builder.role_requirement.cancelled(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

    async def confirm(self, interaction: discord.Interaction):
        self.view.giveaway_data['role_requirement'] = self.roles
        self.view.last_action = locale.commands.giveaway.builder.role_requirement.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

    async def submit(self, interaction: discord.Interaction):
        role_ids = [role for role in interaction.data['values']]
        self.roles = role_ids
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.role_requirement.updated(self.command_info.locale))

class VoiceRequirementModal(ui.Modal):

    def __init__(self, view, command_info, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.voice_requirement.label(self.command_info.locale), placeholder=locale.commands.giveaway.builder.voice_requirement.placeholder(self.command_info.locale), default=self.view.giveaway_data['voice_requirement'], min_length=1, max_length=100, required=True))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_submit(self, interaction: discord.Interaction):
        voice_requirement = int(self.children[0].value)
        self.view.giveaway_data['voice_requirement'] = voice_requirement
        self.view.last_action = locale.commands.giveaway.builder.voice_requirement.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class AddChannelRequirementValueModal(ui.Modal):

    def __init__(self, view, command_info, channel, title, description):
        self.command_info = command_info
        self.view = view
        self.title = title
        self.channel = channel
        self.description = description
        super().__init__(timeout=600)
        self.add_item(ui.TextInput(label=locale.commands.giveaway.builder.add_channel_requirement.v.t(self.command_info.locale), placeholder=locale.commands.giveaway.builder.add_channel_requirement.v.p(self.command_info.locale), min_length=1, max_length=10, required=True))

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction):
        value = self.children[0].value
        self.view.giveaway_data['channel_requirements'][str(self.channel)] = value
        self.view.last_action = locale.commands.giveaway.builder.add_channel_requirement.value.updated(self.command_info.locale)
        await self.view.update_embed(interaction.response.edit_message)

class AddChannelRequirementView(ui.View):

    def __init__(self, command_info, view):
        self.command_info = command_info
        self.selected_channels = []
        self.view = view
        super().__init__(timeout=600)
        channel_select = discord.ui.ChannelSelect(placeholder=locale.commands.giveaway.builder.add_channel_requirement.placeholder(self.command_info.locale), min_values=1, max_values=1, custom_id='channel_select')
        channel_select.callback = self.on_channel_select
        self.add_item(channel_select)
        confirm_btn = discord.ui.Button(label=locale.commands.giveaway.builder.confirm(self.command_info.locale), style=discord.ButtonStyle.green, custom_id='confirm')
        confirm_btn.callback = self.on_button_press
        self.add_item(confirm_btn)
        cancel_btn = discord.ui.Button(label=locale.commands.giveaway.builder.cancel(self.command_info.locale), style=discord.ButtonStyle.red, custom_id='cancel')
        cancel_btn.callback = self.on_button_press
        self.add_item(cancel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_channel_select(self, interaction: discord.Interaction):
        self.selected_channels = interaction.data['values']
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.channel.selected(self.command_info.locale, channel=f'<#{self.selected_channels[0]}>'))

    async def on_button_press(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == 'confirm':
            self.view.giveaway_data['channel_requirements'][str(self.selected_channels[0])] = 0
            self.view.last_action = locale.commands.giveaway.builder.add_channel_requirement.value.updated(self.command_info.locale)
            modal = AddChannelRequirementValueModal(self.view, self.command_info, self.selected_channels[0], locale.commands.giveaway.builder.add_channel_requirement.v.t(self.command_info.locale), locale.commands.giveaway.builder.add_channel_requirement.value.description(self.command_info.locale))
            await interaction.response.send_modal(modal)
        elif interaction.data['custom_id'] == 'cancel':
            self.view.last_action = locale.commands.giveaway.builder.add_channel_requirement.cancelled(self.command_info.locale)
            await self.view.update_embed(interaction.response.edit_message)

class RemoveChannelRequirementView(ui.View):

    def __init__(self, command_info, view):
        self.command_info = command_info
        self.selected_channels = []
        self.view = view
        super().__init__(timeout=300)
        select = discord.ui.Select(placeholder=locale.commands.giveaway.builder.remove_channel_requirement.placeholder(self.command_info.locale), min_values=1, max_values=1, options=[discord.SelectOption(label=command_info.guild.get_channel(int(channel)).name, value=channel, default=False) for channel in self.view.giveaway_data['channel_requirements']], custom_id='channel_select')
        select.callback = self.on_channel_select
        self.add_item(select)
        confirm_btn = discord.ui.Button(label=locale.commands.giveaway.builder.confirm(self.command_info.locale), style=discord.ButtonStyle.green, custom_id='confirm')
        confirm_btn.callback = self.on_button_press
        self.add_item(confirm_btn)
        cancel_btn = discord.ui.Button(label=locale.commands.giveaway.builder.cancel(self.command_info.locale), style=discord.ButtonStyle.red, custom_id='cancel')
        cancel_btn.callback = self.on_button_press
        self.add_item(cancel_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.view.last_action = locale.commands.giveaway.builder.modal.timeout(self.command_info.locale)
        await self.view.update_embed()

    async def on_channel_select(self, interaction: discord.Interaction):
        self.selected_channels = interaction.data['values']
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.channel_selected(self.command_info.locale, channel=f'<#{self.selected_channels[0]}>'))

    async def on_button_press(self, interaction: discord.Interaction):
        if interaction.data['custom_id'] == 'confirm':
            channel_id = self.selected_channels[0]
            self.view.giveaway_data['channel_requirements'].pop(str(channel_id))
            self.view.last_action = locale.commands.giveaway.builder.add_channel_requirement.removed(self.command_info.locale)
            await self.view.update_embed(interaction.response.edit_message)
        elif interaction.data['custom_id'] == 'cancel':
            self.view.last_action = locale.commands.giveaway.builder.add_channel_requirement.cancelled(self.command_info.locale)

class GiveawayBuilder(ui.View):

    def __init__(self, command_info, title, target_channel):
        super().__init__(timeout=600)
        self.command_info = command_info
        self.giveaway_data = {'title': title, 'description': '', 'winners': 1, 'with_button': True, 'custom_name': None, 'sponsor': None, 'price': None, 'message': None, 'end_time': '24h', 'start_time': '0s', 'new_message_requirement': None, 'day_requirement': None, 'role_requirement': [], 'voice_requirement': None, 'channel_requirements': {}, 'target_channel': target_channel}
        self.update_buttons()
        self.last_action = None
        self.generator_message = None

    def update_buttons(self):
        self.clear_items()
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.change_description(self.command_info.locale), custom_id='change_description', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.change_winners.label(self.command_info.locale), custom_id='change_winners', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.sponsor.label(self.command_info.locale), custom_id='sponsor', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.price.label(self.command_info.locale), custom_id='price', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.message.label(self.command_info.locale), custom_id='message', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.end_time.label(self.command_info.locale), custom_id='end_time', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.start_time.label(self.command_info.locale), custom_id='start_time', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.new_message_requirement.label(self.command_info.locale), custom_id='new_message_requirement', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.day_requirement.label(self.command_info.locale), custom_id='day_requirement', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.role_requirement.label(self.command_info.locale), custom_id='role_requirement', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.voice_requirement.label(self.command_info.locale), custom_id='voice_requirement', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.add_channel_requirement.label(self.command_info.locale), custom_id='add_channel_requirement', style=discord.ButtonStyle.primary))
        if self.giveaway_data['channel_requirements']:
            self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.remove_channel_requirement.label(self.command_info.locale), custom_id='remove_channel_requirement', style=discord.ButtonStyle.primary))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.preview(self.command_info.locale), custom_id='preview', style=discord.ButtonStyle.secondary, row=3))
        self.add_item(GiveawayBuilderButton(label=locale.commands.giveaway.builder.confirm(self.command_info.locale), custom_id='confirm', style=discord.ButtonStyle.success, row=3))

    async def update_embed(self, editmessage=None):
        self.update_buttons()
        embed = utility.tanjunEmbed(title=self.giveaway_data['title'], description=(f'## `{self.last_action}`\n\n' if self.last_action else '') + self.giveaway_data['description'])
        embed.add_field(name=locale.commands.giveaway.builder.winners(self.command_info.locale), value=self.giveaway_data['winners'])
        embed.add_field(name=locale.commands.giveaway.builder.sponsor.label(self.command_info.locale), value=f"<@{self.giveaway_data['sponsor']}>" if self.giveaway_data['sponsor'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.price.label(self.command_info.locale), value=self.giveaway_data['price'] if self.giveaway_data['price'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.message.label(self.command_info.locale), value=self.giveaway_data['message'] if self.giveaway_data['message'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.end_time.label(self.command_info.locale), value=f"<t:{int(utility.relativeTimeStrToDate(self.giveaway_data['end_time']).timestamp())}:R>" if self.giveaway_data['end_time'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.start_time.label(self.command_info.locale), value=f"<t:{int(utility.relativeTimeStrToDate(self.giveaway_data['start_time']).timestamp())}:R>" if self.giveaway_data['start_time'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.new_message_requirement.label(self.command_info.locale), value=self.giveaway_data['new_message_requirement'] if self.giveaway_data['new_message_requirement'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.day_requirement.label(self.command_info.locale), value=self.giveaway_data['day_requirement'] if self.giveaway_data['day_requirement'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.role_requirement.label(self.command_info.locale), value=' '.join([f'<@&{role}>' for role in self.giveaway_data['role_requirement']]) if self.giveaway_data['role_requirement'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.voice_requirement.label(self.command_info.locale), value=self.giveaway_data['voice_requirement'] if self.giveaway_data['voice_requirement'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        embed.add_field(name=locale.commands.giveaway.builder.add_channel_requirement.label(self.command_info.locale), value='\n'.join([f'{self.command_info.guild.get_channel(int(channel_id)).mention}: {value}' for channel_id, value in self.giveaway_data['channel_requirements'].items()]) if self.giveaway_data['channel_requirements'] else locale.commands.giveaway.builder.none(self.command_info.locale))
        if not editmessage:
            await self.generator_message.edit(embed=embed, view=self, content='')
        else:
            await editmessage(embed=embed, view=self, content='')

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.command_info.user:
            await interaction.response.send_message(locale.commands.giveaway.builder.not_authorized(self.command_info.locale), ephemeral=True)
            return False
        return True

    async def button_callback(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        if button.custom_id == 'change_description':
            await self.change_description(interaction, button)
        elif button.custom_id == 'change_winners':
            await self.change_winners(interaction, button)
        elif button.custom_id == 'toggle_button':
            await self.toggle_button(interaction, button)
        elif button.custom_id == 'custom_name':
            await self.custom_name(interaction, button)
        elif button.custom_id == 'sponsor':
            await self.sponsor(interaction, button)
        elif button.custom_id == 'price':
            await self.price(interaction, button)
        elif button.custom_id == 'message':
            await self.message(interaction, button)
        elif button.custom_id == 'end_time':
            await self.end_time(interaction, button)
        elif button.custom_id == 'start_time':
            await self.start_time(interaction, button)
        elif button.custom_id == 'new_message_requirement':
            await self.new_message_requirement(interaction, button)
        elif button.custom_id == 'day_requirement':
            await self.day_requirement(interaction, button)
        elif button.custom_id == 'role_requirement':
            await self.role_requirement(interaction, button)
        elif button.custom_id == 'voice_requirement':
            await self.voice_requirement(interaction, button)
        elif button.custom_id == 'add_channel_requirement':
            await self.add_channel_requirement(interaction, button)
        elif button.custom_id == 'remove_channel_requirement':
            await self.remove_channel_requirement(interaction, button)
        elif button.custom_id == 'preview':
            await self.preview(interaction, button)
        elif button.custom_id == 'confirm':
            await self.confirm(interaction, button)

    async def change_description(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.enter_description(self.command_info.locale), embed=None, view=discord.ui.View())
        try:
            message = await self.command_info.client.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=300.0)
        except TimeoutError:
            self.last_action = locale.commands.giveaway.builder.description.timeout(self.command_info.locale)
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data['description'] = message.content
            self.last_action = locale.commands.giveaway.builder.description.updated(self.command_info.locale)
            await self.update_embed()

    async def change_winners(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = ChangeWinnersModal(self, self.command_info, locale.commands.giveaway.builder.change_winners.title(self.command_info.locale), locale.commands.giveaway.builder.change_winners.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def toggle_button(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        self.giveaway_data['with_button'] = not self.giveaway_data['with_button']
        self.update_buttons()
        await self.update_embed(interaction.response.edit_message)

    async def custom_name(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = CustomNameModal(self, self.command_info, locale.commands.giveaway.builder.custom_name.title(self.command_info.locale), locale.commands.giveaway.builder.custom_name.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def sponsor(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        view = SponsorView(self.command_info, self)
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.sponsor.select.placeholder(self.command_info.locale), view=view, embed=None)

    async def price(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.enter_price(self.command_info.locale), embed=None, view=discord.ui.View())
        try:
            message = await self.command_info.client.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=300.0)
        except TimeoutError:
            self.last_action = locale.commands.giveaway.builder.price.timeout(self.command_info.locale)
            await self.update_embed()
        else:
            await message.delete()
            self.giveaway_data['price'] = message.content
            self.last_action = locale.commands.giveaway.builder.price.updated(self.command_info.locale)
            await self.update_embed()

    async def message(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.enter_message(self.command_info.locale), embed=None, view=discord.ui.View())
        try:
            message = await self.command_info.client.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=300.0)
        except TimeoutError:
            self.last_action = locale.commands.giveaway.builder.message.timeout(self.command_info.locale)
            await self.update_embed()
        else:
            await message.delete()
            if len(message.content) > 128:
                self.last_action = locale.commands.giveaway.builder.message.too_long(self.command_info.locale)
                await self.update_embed()
                return
            self.giveaway_data['message'] = message.content
            self.last_action = locale.commands.giveaway.builder.message.updated(self.command_info.locale)
            await self.update_embed()

    async def end_time(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = EndTimeModal(self, self.command_info, locale.commands.giveaway.builder.end_time.title(self.command_info.locale), locale.commands.giveaway.builder.end_time.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def start_time(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = StartTimeModal(self, self.command_info, locale.commands.giveaway.builder.start_time.title(self.command_info.locale), locale.commands.giveaway.builder.start_time.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def new_message_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = MessageRequirementModal(self, self.command_info, locale.commands.giveaway.builder.new_message_requirement.title(self.command_info.locale), locale.commands.giveaway.builder.new_message_requirement.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def day_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = DayRequirementModal(self, self.command_info, locale.commands.giveaway.builder.day_requirement.title(self.command_info.locale), locale.commands.giveaway.builder.day_requirement.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def role_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        view = RoleRequirementView(self, self.command_info, locale.commands.giveaway.builder.role_requirement.title(self.command_info.locale), locale.commands.giveaway.builder.role_requirement.description(self.command_info.locale))
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.role_requirement.select(self.command_info.locale), view=view, embed=None)

    async def voice_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        modal = VoiceRequirementModal(self, self.command_info, locale.commands.giveaway.builder.voice_requirement.title(self.command_info.locale), locale.commands.giveaway.builder.voice_requirement.description(self.command_info.locale))
        await interaction.response.send_modal(modal)

    async def add_channel_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        view = AddChannelRequirementView(self.command_info, self)
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.add_channel_requirement.select(self.command_info.locale), embed=None, view=view)

    async def remove_channel_requirement(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        view = RemoveChannelRequirementView(self.command_info, self)
        await interaction.response.edit_message(content=locale.commands.giveaway.builder.remove_channel_requirement.select(self.command_info.locale), embed=None, view=view)

    async def preview(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        self.giveaway_data['id'] = '1234567890'
        embed = await generateGiveawayEmbed(self.giveaway_data, self.command_info.locale)
        await interaction.response.send_message(content=locale.commands.giveaway.builder.preview(self.command_info.locale), embed=embed, view=self)

    async def confirm(self, interaction: discord.Interaction, button: GiveawayBuilderButton):
        title = self.giveaway_data['title']
        description = self.giveaway_data['description']
        winners = self.giveaway_data['winners']
        with_button = self.giveaway_data['with_button']
        custom_name = self.giveaway_data['custom_name']
        sponsor = self.giveaway_data['sponsor']
        price = self.giveaway_data['price']
        message = self.giveaway_data['message']
        end_time = utility.relativeTimeStrToDate(self.giveaway_data['end_time'])
        start_time = utility.relativeTimeStrToDate(self.giveaway_data['start_time'])
        new_message_requirement = self.giveaway_data['new_message_requirement']
        day_requirement = self.giveaway_data['day_requirement']
        role_requirement = self.giveaway_data['role_requirement']
        voice_requirement = self.giveaway_data['voice_requirement']
        channel_requirements = self.giveaway_data['channel_requirements']
        target_channel = self.giveaway_data['target_channel']
        giveaway_id = await giveaway_service.create(GiveawayCreateParams(guild_id=str(self.command_info.guild.id), title=title, description=description, winners=winners, with_button=with_button, custom_name=custom_name, sponsor=sponsor, price=price, message=message, end_time=end_time, start_time=start_time, new_message_requirement=new_message_requirement, day_requirement=day_requirement, role_requirement=role_requirement, voice_requirement=voice_requirement, channel_requirements=channel_requirements, channel_id=str(target_channel.id)))
        self.giveaway_data['id'] = giveaway_id
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.builder.success.title(self.command_info.locale), description=locale.commands.giveaway.builder.success.description(self.command_info.locale))
        await interaction.response.edit_message(content=None, embed=embed, view=ui.View())
        if start_time < datetime.datetime.now():
            await sendGiveaway(giveaway_id, self.command_info.client)

async def start_giveaway(command_info, title, target_channel):
    if not command_info.user.guild_permissions.manage_guild:
        await command_info.reply(locale.commands.giveaway.builder.no_permission(command_info.locale))
        return
    view = GiveawayBuilder(command_info, title, target_channel)
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.builder.loading(command_info.locale), description=locale.commands.giveaway.builder.loading(command_info.locale))
    message = await command_info.reply(embed=embed, view=view)
    view.generator_message = message
    await view.update_embed()