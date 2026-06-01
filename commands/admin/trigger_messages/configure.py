from locale_keys import locale
from typing import Any
import discord
import utility
from services.trigger_message_service import trigger_message_service

async def configure_trigger_messages(command_info: utility.CommandInfo):
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.configure.missingPermission.title(command_info.locale), description=locale.commands.admin.trigger_messages.configure.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    trigger_messages = await trigger_message_service.get_all(command_info.guild.id)
    if trigger_messages is None or len(trigger_messages) == 0:
        embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.configure.noTriggerMessages.title(command_info.locale), description=locale.commands.admin.trigger_messages.configure.noTriggerMessages.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[0].id)
    page = 0
    selected_channel = 0

    async def generate_embed():
        nonlocal page, trigger_messages, channels, selected_channel
        if page < 0 or page >= len(trigger_messages):
            embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.configure.trigger.title(command_info.locale), description=locale.commands.admin.trigger_messages.configure.trigger.noTriggerMessages.description(command_info.locale))
            return embed
        trigger_message = trigger_messages[page]
        description = locale.commands.admin.trigger_messages.configure.trigger.description(command_info.locale, trigger=trigger_message.trigger, response=trigger_message.response)
        if trigger_message.case_sensitive:
            description += '\n\n' + locale.commands.admin.trigger_messages.configure.trigger.case_sensitive(command_info.locale)
        else:
            description += '\n\n' + locale.commands.admin.trigger_messages.configure.trigger.caseInsensitive(command_info.locale)
        if channels is not None and len(channels) > 0:
            description += '\n\n' + locale.commands.admin.trigger_messages.configure.trigger.channels(command_info.locale)
            for index, channel in enumerate(channels):
                if index == selected_channel:
                    description += f'\n🠲 {index + 1}. <#{channel.channel_id}>'
                else:
                    description += f'\n{index + 1}. <#{channel.channel_id}>'
        else:
            description += '\n\n' + locale.commands.admin.trigger_messages.configure.trigger.noChannels(command_info.locale)
        embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.configure.trigger.title(command_info.locale, trigger=trigger_message.trigger), description=description)
        return embed

    class TriggerMessageModal(discord.ui.Modal):

        def __init__(self, command_info: utility.CommandInfo) -> None:
            super().__init__(title=locale.commands.admin.trigger_messages.configure.modal.title(command_info.locale))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.trigger_messages.configure.modal.trigger.label(command_info.locale), placeholder=locale.commands.admin.trigger_messages.configure.modal.trigger.placeholder(command_info.locale), required=True, max_length=100))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.trigger_messages.configure.modal.response.label(command_info.locale), placeholder=locale.commands.admin.trigger_messages.configure.modal.response.placeholder(command_info.locale), required=True, max_length=1000))
            self.add_item(discord.ui.TextInput(label=locale.commands.admin.trigger_messages.configure.modal.case_sensitive.label(command_info.locale), placeholder=locale.commands.admin.trigger_messages.configure.modal.case_sensitive.placeholder(command_info.locale), default='n', required=True, max_length=1))

        async def on_submit(self, interaction: discord.Interaction) -> None:
            trigger = self.children[0].value.strip()
            response = self.children[1].value.strip()
            case_sensitive = self.children[2].value == 'y'
            await trigger_message_service.create(command_info.guild.id, trigger, response, case_sensitive)
            nonlocal trigger_messages
            trigger_messages = await trigger_message_service.get_all(command_info.guild.id)
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[0].id)
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageChannelView(discord.ui.View):

        def __init__(self, command_info: utility.CommandInfo, trigger_id: int) -> None:
            super().__init__()
            channel_select = discord.ui.ChannelSelect(placeholder=locale.commands.admin.trigger_messages.configure.trigger.addChannel.placeholder(command_info.locale), min_values=1, max_values=1, custom_id='channel_select')
            channel_select.callback = self.on_channel_select
            self.add_item(channel_select)

        async def on_channel_select(self, interaction: discord.Interaction) -> None:
            from typing import Any, cast
            data = cast(Any, interaction.data)
            nonlocal channels
            await trigger_message_service.add_channel(command_info.guild.id, data['values'][0] if data is not None else '', trigger_messages[page].id)
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[page].id)
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageView(discord.ui.View):

        def __init__(self) -> None:
            super().__init__()

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.previous.label(command_info.locale), style=discord.ButtonStyle.secondary, emoji='⬅️', disabled=len(trigger_messages) <= 1)
        async def trigger(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal page
            page -= 1
            if page < 0:
                page = len(trigger_messages) - 1
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[page].id)
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.remove.label(command_info.locale), style=discord.ButtonStyle.danger, emoji='🗑️')
        async def remove(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal trigger_messages
            await trigger_message_service.delete(command_info.guild.id, trigger_messages[page].id)
            trigger_messages = await trigger_message_service.get_all(command_info.guild.id)
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[0].id)
            await self.update_message(interaction)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.new.label(command_info.locale), style=discord.ButtonStyle.primary, emoji='➕')
        async def new(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            modal = TriggerMessageModal(command_info)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.next.label(command_info.locale), style=discord.ButtonStyle.secondary, emoji='➡️', disabled=len(trigger_messages) <= 1)
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal page
            page += 1
            if page >= len(trigger_messages):
                page = 0
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[page].id)
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.up.label(str(command_info.locale)), style=discord.ButtonStyle.secondary, emoji='⬆️', row=1, disabled=len(channels) <= 1)
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal selected_channel
            selected_channel -= 1
            if selected_channel < 0:
                selected_channel = len(channels) - 1
            await self.update_message(interaction)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.add_channel.label(command_info.locale), style=discord.ButtonStyle.success, emoji='➕', row=1)
        async def add_channel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            view = TriggerMessageChannelView(command_info, trigger_messages[page].id)
            embed = utility.tanjunEmbed(title=locale.commands.admin.trigger_messages.configure.trigger.addChannel.title(command_info.locale, trigger=trigger_messages[page].trigger), description=locale.commands.admin.trigger_messages.configure.trigger.addChannel.description(command_info.locale))
            await interaction.response.edit_message(embed=embed, view=view)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.remove_channel.label(command_info.locale), style=discord.ButtonStyle.danger, emoji='🚫', row=1, disabled=len(channels) <= 1)
        async def remove_channel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal channels
            await trigger_message_service.remove_channel(command_info.guild.id, channels[selected_channel].channel_id, trigger_messages[page].id)
            channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[page].id)
            await self.update_message(interaction)

        @discord.ui.button(label=locale.commands.admin.trigger_messages.configure.down.label(command_info.locale), style=discord.ButtonStyle.secondary, emoji='⬇️', row=1, disabled=len(channels) <= 1)
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            nonlocal selected_channel
            selected_channel += 1
            if selected_channel >= len(channels):
                selected_channel = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction) -> None:
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)
    view = TriggerMessageView()
    embed = await generate_embed()
    await command_info.reply(embed=embed, view=view)