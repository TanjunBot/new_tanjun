from locale_keys import locale
import re
from typing import Any, cast
import discord
from discord.ui import Modal, Select, TextInput, View
import utility

async def create_embed(command_info: utility.CommandInfo, channel: discord.TextChannel, title: str) -> None:

    class EmbedCreatorView(View):

        def __init__(self, command_info: utility.CommandInfo, target_channel: discord.TextChannel) -> None:
            super().__init__(timeout=1800)
            self.command_info: utility.CommandInfo = command_info
            self.embed: discord.Embed = discord.Embed(title=title, color=16777215)
            self.preview_message: discord.Message | None = None
            self.target_channel: discord.TextChannel = target_channel
            self.field_count: int = 0
            self.max_fields: int = 25
            self.message: discord.Message | None = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_info.user:
                await interaction.response.send_message(locale.commands.admin.embed.unauthorizedUser(str(self.command_info.locale)), ephemeral=True)
                return False
            return True

        @discord.ui.button(label=locale.commands.admin.embed.buttons.setDescription(str(command_info.locale)), style=discord.ButtonStyle.primary)
        async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_message(content=locale.commands.admin.embed.setDescription.message(self.command_info.locale), ephemeral=True, view=discord.ui.View())
            try:
                message = await self.command_info.client.wait_for('message', check=lambda m: m.author == interaction.user and m.channel == interaction.channel, timeout=300.0)
            except TimeoutError:
                await interaction.followup.send_message(locale.commands.admin.embed.setDescription.timeout(self.command_info.locale), ephemeral=True)
            else:
                await message.delete()
                self.embed.description = str(message.content)
                await interaction.edit_original_response(content=locale.commands.admin.embed.descriptionUpdated(str(self.command_info.locale)))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.addField(str(command_info.locale)), style=discord.ButtonStyle.primary)
        async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if self.field_count >= self.max_fields:
                await interaction.response.send_message(locale.commands.admin.embed.maxFieldsReached(self.command_info.locale), ephemeral=True)
            else:
                await interaction.response.send_modal(FieldModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.setFooter(str(command_info.locale)), style=discord.ButtonStyle.primary)
        async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(FooterModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.setColor(str(command_info.locale)), style=discord.ButtonStyle.primary)
        async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ColorModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.setImage(str(command_info.locale)), style=discord.ButtonStyle.secondary)
        async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ImageModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.setThumbnail(str(command_info.locale)), style=discord.ButtonStyle.secondary)
        async def set_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_modal(ThumbnailModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.editField(str(command_info.locale)), style=discord.ButtonStyle.secondary)
        async def edit_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if self.field_count == 0:
                await interaction.response.send_message(locale.commands.admin.embed.noFieldsToEdit(self.command_info.locale), ephemeral=True)
            else:
                await interaction.response.send_modal(EditFieldModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.removeField(str(command_info.locale)), style=discord.ButtonStyle.danger)
        async def remove_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if self.field_count == 0:
                await interaction.response.send_message(locale.commands.admin.embed.noFieldsToRemove(self.command_info.locale), ephemeral=True)
            else:
                await interaction.response.send_modal(RemoveFieldModal(self))

        @discord.ui.button(label=locale.commands.admin.embed.buttons.preview(str(command_info.locale)), style=discord.ButtonStyle.secondary)
        async def preview(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            if self.preview_message:
                await self.preview_message.delete()
            channel = cast(discord.abc.Messageable, interaction.channel)
            self.preview_message = await channel.send(embed=self.embed)
            await interaction.response.send_message(locale.commands.admin.embed.previewSent(str(self.command_info.locale)), ephemeral=True)

        @discord.ui.button(label=locale.commands.admin.embed.buttons.send(str(command_info.locale)), style=discord.ButtonStyle.green)
        async def send(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await self.target_channel.send(embed=self.embed)
            await interaction.response.send_message(locale.commands.admin.embed.embedSent(self.command_info.locale, channel=self.target_channel.mention), ephemeral=True)
            self.stop()

        async def on_timeout(self) -> None:
            for item in self.children:
                if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                    item.disabled = True
            if self.message:
                await self.message.edit(view=self)

    class FieldModal(Modal):

        def __init__(self, view: 'EmbedCreatorView') -> None:
            super().__init__(title=locale.commands.admin.embed.modals.fieldModal.title(view.command_info.locale))
            self.view: EmbedCreatorView = view
            self.name: TextInput = TextInput(label=locale.commands.admin.embed.modals.fieldModal.nameLabel(str(view.command_info.locale)), style=discord.TextStyle.short, required=True, max_length=256, min_length=1)
            self.value = TextInput(label=locale.commands.admin.embed.modals.fieldModal.valueLabel(view.command_info.locale), style=discord.TextStyle.long, required=True, max_length=1024, min_length=1)
            self.inline = TextInput(label=locale.commands.admin.embed.modals.fieldModal.inlineLabel(view.command_info.locale), style=discord.TextStyle.short, required=True, max_length=1, min_length=1, placeholder='y/n')
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            inline = self.inline.value.lower() == 'true' or self.inline.value.lower() == 'y'
            self.view.embed.add_field(name=self.name.value, value=self.value.value, inline=inline)
            self.view.field_count += 1
            await interaction.response.send_message(locale.commands.admin.embed.fieldAdded(self.view.command_info.locale), ephemeral=True)

    class FooterModal(Modal):

        def __init__(self, view: 'EmbedCreatorView') -> None:
            super().__init__(title=locale.commands.admin.embed.modals.footerModal.title(view.command_info.locale))
            self.view = view
            self.text = TextInput(label=locale.commands.admin.embed.modals.footerModal.label(view.command_info.locale), style=discord.TextStyle.short, default=view.embed.footer.text, required=True, max_length=2048, min_length=1)
            self.icon_url = TextInput(label=locale.commands.admin.embed.modals.footerModal.iconLabel(view.command_info.locale), style=discord.TextStyle.short, default=view.embed.footer.icon_url, required=False, max_length=2048)
            self.add_item(self.text)
            self.add_item(self.icon_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_footer(text=self.text.value, icon_url=self.icon_url.value if self.icon_url.value else None)
            await interaction.response.send_message(locale.commands.admin.embed.footerUpdated(self.view.command_info.locale), ephemeral=True)

    class ColorModal(Modal):

        def __init__(self, view) -> None:
            super().__init__(title=locale.commands.admin.embed.modals.colorModal.title(view.command_info.locale))
            self.view = view
            self.color = TextInput(label=locale.commands.admin.embed.modals.colorModal.label(view.command_info.locale), style=discord.TextStyle.short, default=str(view.embed.color) if view.embed.color else '#FFFFFF', required=True, max_length=7, min_length=7)
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            color_regex: str = '^#(?:[0-9a-fA-F]{3}){1,2}$'
            if re.match(color_regex, str(self.color.value)):
                color: int = int(str(self.color.value).replace('#', ''), 16)
                self.view.embed.color = color
                await interaction.response.send_message(locale.commands.admin.embed.colorUpdated(str(self.view.command_info.locale)), ephemeral=True)
            else:
                await interaction.response.send_message(locale.commands.admin.embed.invalidColorCode(str(self.view.command_info.locale)), ephemeral=True)

    class ImageModal(Modal):

        def __init__(self, view) -> None:
            super().__init__(title=locale.commands.admin.embed.modals.imageModal.title(view.command_info.locale))
            self.view = view
            self.image_url = TextInput(label=locale.commands.admin.embed.modals.imageModal.label(view.command_info.locale), style=discord.TextStyle.short, default=view.embed.image.url, required=True, max_length=2048)
            self.add_item(self.image_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_image(url=self.image_url.value)
            await interaction.response.send_message(locale.commands.admin.embed.imageUpdated(self.view.command_info.locale), ephemeral=True)

    class ThumbnailModal(Modal):

        def __init__(self, view) -> None:
            super().__init__(title=locale.commands.admin.embed.modals.thumbnailModal.title(view.command_info.locale))
            self.view = view
            self.thumbnail_url = TextInput(label=locale.commands.admin.embed.modals.thumbnailModal.label(view.command_info.locale), style=discord.TextStyle.short, default=view.embed.thumbnail.url, required=True, max_length=2048)
            self.add_item(self.thumbnail_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_thumbnail(url=self.thumbnail_url.value)
            await interaction.response.send_message(locale.commands.admin.embed.thumbnailUpdated(self.view.command_info.locale), ephemeral=True)

    class EditFieldModal(Modal):

        def __init__(self, view: 'EmbedCreatorView') -> None:
            super().__init__(title=locale.commands.admin.embed.modals.editFieldModal.title(view.command_info.locale))
            self.view = view
            self.field_index = Select[Any](placeholder=locale.commands.admin.embed.modals.editFieldModal.selectField(view.command_info.locale), options=[discord.SelectOption(label=locale.commands.admin.embed.modals.editFieldModal.fieldLabel(view.command_info.locale, index=i + 1), value=str(i)) for i in range(len(view.embed.fields))])
            self.name = TextInput(label=locale.commands.admin.embed.modals.fieldModal.nameLabel(view.command_info.locale), style=discord.TextStyle.short, required=True, max_length=256, min_length=1)
            self.value = TextInput(label=locale.commands.admin.embed.modals.fieldModal.valueLabel(view.command_info.locale), style=discord.TextStyle.long, required=True, max_length=1024, min_length=1)
            self.inline = TextInput(label=locale.commands.admin.embed.modals.fieldModal.inlineLabel(view.command_info.locale), style=discord.TextStyle.short, required=True, max_length=1, min_length=1, placeholder='y/n')
            self.add_item(self.field_index)
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            index = int(self.field_index.values[0])
            inline = self.inline.value.lower() == 'y'
            self.view.embed.set_field_at(index, name=self.name.value, value=self.value.value, inline=inline)
            await interaction.response.send_message(locale.commands.admin.embed.fieldEdited(self.view.command_info.locale), ephemeral=True)

    class RemoveFieldModal(Modal):

        def __init__(self, view: 'EmbedCreatorView') -> None:
            super().__init__(title=locale.commands.admin.embed.modals.removeFieldModal.title(view.command_info.locale))
            self.view = view
            self.field_index = Select[Any](placeholder=locale.commands.admin.embed.modals.removeFieldModal.selectField(view.command_info.locale), options=[discord.SelectOption(label=locale.commands.admin.embed.modals.removeFieldModal.fieldLabel(view.command_info.locale, number=i + 1), value=str(i)) for i in range(len(view.embed.fields))])
            self.add_item(self.field_index)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            index = int(self.field_index.values[0])
            self.view.embed.remove_field(index)
            self.view.field_count -= 1
            await interaction.response.send_message(locale.commands.admin.embed.fieldRemoved(self.view.command_info.locale), ephemeral=True)
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_messages):
        embed = utility.tanjunEmbed(title=locale.commands.admin.embed.missingPermission.title(command_info.locale), description=locale.commands.admin.embed.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    view = EmbedCreatorView(command_info, channel)
    embed = utility.tanjunEmbed(title=locale.commands.admin.embed.creatorTitle(str(command_info.locale)), description=locale.commands.admin.embed.creatorDescription(command_info.locale, channel=channel.mention))
    view.message = await command_info.reply(embed=embed, view=view)