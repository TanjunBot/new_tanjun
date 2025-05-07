import discord

import utility
from api import (
    add_trigger_message,
    add_trigger_message_channel,
    get_trigger_message_channels,
    get_trigger_messages,
    remove_trigger_message,
    remove_trigger_message_channel,
)
from localizer import tanjunLocalizer


async def configure_trigger_messages(
    commandInfo: utility.commandInfo,
):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    trigger_messages = await get_trigger_messages(commandInfo.guild.id)

    if not trigger_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.noTriggerMessages.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.noTriggerMessages.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[0][0])
    page = 0
    selected_channel = 0

    async def generate_embed():
        if page < 0 or page >= len(trigger_messages):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.trigger.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.trigger.noTriggerMessages.description",
                ),
            )
            return embed

        trigger_message = trigger_messages[page]
        description = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.trigger_messages.configure.trigger.description",
            trigger=trigger_message[2],
            response=trigger_message[3],
        )

        if trigger_message[4]:
            description += "\n\n" + tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.trigger.caseSensitive",
            )
        else:
            description += "\n\n" + tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.trigger.caseInsensitive",
            )

        if channels:
            description += "\n\n" + tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.trigger.channels",
            )
            for index, channel in enumerate(channels):
                if index == selected_channel:
                    description += f"\n🠲 {index + 1}. <#{channel[1]}>"
                else:
                    description += f"\n{index + 1}. <#{channel[1]}>"
        else:
            description += "\n\n" + tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.trigger.noChannels",
            )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.trigger.title",
                trigger=trigger_message[2],
            ),
            description=description,
        )
        return embed

    class TriggerMessageModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.modal.title",
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.trigger.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.trigger.placeholder",
                    ),
                    required=True,
                    max_length=100,
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.response.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.response.placeholder",
                    ),
                    required=True,
                    max_length=1000,
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.caseSensitive.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.admin.trigger_messages.configure.modal.caseSensitive.placeholder",
                    ),
                    default="n",
                    required=True,
                    max_length=1,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            trigger = self.children[0].value.strip()
            response = self.children[1].value.strip()
            caseSensitive = self.children[2].value == "y"
            await add_trigger_message(commandInfo.guild.id, trigger, response, caseSensitive)
            nonlocal trigger_messages
            trigger_messages = await get_trigger_messages(commandInfo.guild.id)
            nonlocal channels
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[0][0])
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageChannelView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo, trigger_id: int):
            super().__init__()

            channelSelect = discord.ui.ChannelSelect(
                placeholder=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.placeholder",
                ),
                min_values=1,
                max_values=1,
                custom_id="channel_select",
            )
            channelSelect.callback = self.on_channel_select
            self.add_item(channelSelect)

        async def on_channel_select(self, interaction: discord.Interaction):
            nonlocal channels
            await add_trigger_message_channel(
                commandInfo.guild.id,
                interaction.data["values"][0],
                trigger_messages[page][0],
            )
            nonlocal channels
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[page][0])
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageView(discord.ui.View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.previous.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="⬅️",
            disabled=len(trigger_messages) <= 1,
        )
        async def trigger(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal page
            page -= 1
            if page < 0:
                page = len(trigger_messages) - 1
            nonlocal channels
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[page][0])
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.remove.label",
            ),
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
        )
        async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal trigger_messages
            await remove_trigger_message(commandInfo.guild.id, trigger_messages[page][0])
            trigger_messages = await get_trigger_messages(commandInfo.guild.id)
            nonlocal channels
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[0][0])
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.new.label",
            ),
            style=discord.ButtonStyle.primary,
            emoji="➕",
        )
        async def new(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = TriggerMessageModal(commandInfo)
            await interaction.response.send_modal(modal)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.next.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
            disabled=len(trigger_messages) <= 1,
        )
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal page
            page += 1
            if page >= len(trigger_messages):
                page = 0
            nonlocal channels
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[page][0])
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.trigger_messages.configure.up.label"),
            style=discord.ButtonStyle.secondary,
            emoji="⬆️",
            row=1,
            disabled=len(channels) <= 1,
        )
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal selected_channel
            selected_channel -= 1
            if selected_channel < 0:
                selected_channel = len(channels) - 1
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.add_channel.label",
            ),
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=1,
        )
        async def add_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
            view = TriggerMessageChannelView(commandInfo, trigger_messages[page][0])
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.title",
                    trigger=trigger_messages[page][2],
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.description",
                ),
            )
            await interaction.response.edit_message(embed=embed, view=view)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.remove_channel.label",
            ),
            style=discord.ButtonStyle.danger,
            emoji="🚫",
            row=1,
            disabled=len(channels) <= 1,
        )
        async def remove_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal channels
            await remove_trigger_message_channel(
                commandInfo.guild.id,
                channels[selected_channel][1],
                trigger_messages[page][0],
            )
            channels = await get_trigger_message_channels(commandInfo.guild.id, trigger_messages[page][0])
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.configure.down.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="⬇️",
            row=1,
            disabled=len(channels) <= 1,
        )
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
            nonlocal selected_channel
            selected_channel += 1
            if selected_channel >= len(channels):
                selected_channel = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction):
            embed = await generate_embed()
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    view = TriggerMessageView()
    embed = await generate_embed()
    await commandInfo.reply(embed=embed, view=view)
