from typing import Any

import discord

import utility
from localizer import tanjunLocalizer
from services.trigger_message_service import trigger_message_service


async def configure_trigger_messages(  # type: ignore[no-untyped-def]
    command_info: utility.CommandInfo,
):
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    trigger_messages = await trigger_message_service.get_all(command_info.guild.id)

    if trigger_messages is None or len(trigger_messages) == 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.noTriggerMessages.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.noTriggerMessages.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    channels = await trigger_message_service.get_trigger_channels(command_info.guild.id, trigger_messages[0].id)
    page = 0
    selected_channel = 0

    async def generate_embed():  # type: ignore[no-untyped-def]
        nonlocal page, trigger_messages, channels, selected_channel
        if page < 0 or page >= len(trigger_messages):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.trigger.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.trigger.noTriggerMessages.description",
                ),
            )
            return embed

        trigger_message = trigger_messages[page]
        description = tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.trigger_messages.configure.trigger.description",
            trigger=trigger_message.trigger,
            response=trigger_message.response,
        )

        if trigger_message.case_sensitive:
            description += "\n\n" + tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.trigger.case_sensitive",
            )
        else:
            description += "\n\n" + tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.trigger.caseInsensitive",
            )

        if channels is not None and len(channels) > 0:
            description += "\n\n" + tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.trigger.channels",
            )
            for index, channel in enumerate(channels):
                if index == selected_channel:
                    description += f"\n🠲 {index + 1}. <#{channel.channel_id}>"
                else:
                    description += f"\n{index + 1}. <#{channel.channel_id}>"
        else:
            description += "\n\n" + tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.trigger.noChannels",
            )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.trigger.title",
                trigger=trigger_message.trigger,
            ),
            description=description,
        )
        return embed

    class TriggerMessageModal(discord.ui.Modal):
        def __init__(self, command_info: utility.CommandInfo) -> None:
            super().__init__(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.modal.title",
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.trigger.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.trigger.placeholder",
                    ),
                    required=True,
                    max_length=100,
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.response.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.response.placeholder",
                    ),
                    required=True,
                    max_length=1000,
                )
            )

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.case_sensitive.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.trigger_messages.configure.modal.case_sensitive.placeholder",
                    ),
                    default="n",
                    required=True,
                    max_length=1,
                )
            )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            trigger = self.children[0].value.strip()  # type: ignore[attr-defined]
            response = self.children[1].value.strip()  # type: ignore[attr-defined]
            case_sensitive = self.children[2].value == "y"  # type: ignore[attr-defined]
            await trigger_message_service.create(command_info.guild.id, trigger, response, case_sensitive)  # type: ignore[union-attr]
            nonlocal trigger_messages
            trigger_messages = await trigger_message_service.get_all(command_info.guild.id)  # type: ignore[union-attr]
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[0].id,
            )
            embed = await generate_embed()  # type: ignore[no-untyped-call]
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageChannelView(discord.ui.View):
        def __init__(self, command_info: utility.CommandInfo, trigger_id: int) -> None:
            super().__init__()

            channel_select = discord.ui.ChannelSelect(  # type: ignore[var-annotated]
                placeholder=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.placeholder",
                ),
                min_values=1,
                max_values=1,
                custom_id="channel_select",
            )
            channel_select.callback = self.on_channel_select  # type: ignore[method-assign]
            self.add_item(channel_select)

        async def on_channel_select(self, interaction: discord.Interaction) -> None:
            from typing import Any, cast

            data = cast(Any, interaction.data)
            nonlocal channels
            await trigger_message_service.add_channel(
                command_info.guild.id,  # type: ignore[union-attr]
                data["values"][0] if data is not None else "",
                trigger_messages[page].id,
            )
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[page].id,
            )
            embed = await generate_embed()  # type: ignore[no-untyped-call]
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    class TriggerMessageView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__()

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.previous.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="⬅️",
            disabled=len(trigger_messages) <= 1,  # type: ignore[arg-type]
        )
        async def trigger(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal page
            page -= 1
            if page < 0:
                page = len(trigger_messages) - 1  # type: ignore[arg-type]
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[page].id,
            )
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.remove.label",
            ),
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
        )
        async def remove(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal trigger_messages
            await trigger_message_service.delete(
                command_info.guild.id,
                trigger_messages[page].id,
            )
            trigger_messages = await trigger_message_service.get_all(command_info.guild.id)  # type: ignore[union-attr]
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[0].id,
            )
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.new.label",
            ),
            style=discord.ButtonStyle.primary,
            emoji="➕",
        )
        async def new(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            modal = TriggerMessageModal(command_info)
            await interaction.response.send_modal(modal)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.next.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
            disabled=len(trigger_messages) <= 1,  # type: ignore[arg-type]
        )
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal page
            page += 1
            if page >= len(trigger_messages):  # type: ignore[arg-type]
                page = 0
            nonlocal channels
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[page].id,
            )
            nonlocal selected_channel
            selected_channel = 0
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.trigger_messages.configure.up.label"),
            style=discord.ButtonStyle.secondary,
            emoji="⬆️",
            row=1,
            disabled=len(channels) <= 1,  # type: ignore[arg-type]
        )
        async def up(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal selected_channel
            selected_channel -= 1
            if selected_channel < 0:
                selected_channel = len(channels) - 1  # type: ignore[arg-type]
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.add_channel.label",
            ),
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=1,
        )
        async def add_channel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            view = TriggerMessageChannelView(command_info, trigger_messages[page].id)
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.title",
                    trigger=trigger_messages[page].trigger,
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.trigger_messages.configure.trigger.addChannel.description",
                ),
            )
            await interaction.response.edit_message(embed=embed, view=view)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.remove_channel.label",
            ),
            style=discord.ButtonStyle.danger,
            emoji="🚫",
            row=1,
            disabled=len(channels) <= 1,  # type: ignore[arg-type]
        )
        async def remove_channel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal channels
            await trigger_message_service.remove_channel(
                command_info.guild.id,  # type: ignore[union-attr]
                channels[selected_channel].channel_id,
                trigger_messages[page].id,
            )
            channels = await trigger_message_service.get_trigger_channels(
                command_info.guild.id,
                trigger_messages[page].id,
            )
            await self.update_message(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.trigger_messages.configure.down.label",
            ),
            style=discord.ButtonStyle.secondary,
            emoji="⬇️",
            row=1,
            disabled=len(channels) <= 1,  # type: ignore[arg-type]
        )
        async def down(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            nonlocal selected_channel
            selected_channel += 1
            if selected_channel >= len(channels):  # type: ignore[arg-type]
                selected_channel = 0
            await self.update_message(interaction)

        async def update_message(self, interaction: discord.Interaction) -> None:
            embed = await generate_embed()  # type: ignore[no-untyped-call]
            view = TriggerMessageView()
            await interaction.response.edit_message(embed=embed, view=view)

    view = TriggerMessageView()
    embed = await generate_embed()  # type: ignore[no-untyped-call]
    await command_info.reply(embed=embed, view=view)
