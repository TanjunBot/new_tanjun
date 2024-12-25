import discord
from discord.ui import View, Modal, TextInput, Select
import utility
from localizer import tanjunLocalizer
import re
import asyncio


async def create_embed(
    commandInfo: utility.commandInfo, channel: discord.TextChannel, title: str
):
    class EmbedCreatorView(View):
        def __init__(self, commandInfo, target_channel):
            super().__init__(timeout=1800)  # 30 minutes timeout
            self.commandInfo = commandInfo
            self.embed = discord.Embed(title=title, color=0xFFFFFF)
            self.preview_message = None
            self.target_channel = target_channel
            self.field_count = 0
            self.max_fields = 25

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.embed.unauthorizedUser"
                    ),
                    ephemeral=True,
                )
                return False
            return True

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.setDescription"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def set_description(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_message(
                content=tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.embed.setDescription.message",
                ),
                embed=None,
                ephemeral=True,
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
                await interaction.followup.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.embed.setDescription.timeout",
                    ),
                    ephemeral=True,
                )
            else:
                await message.delete()
                self.embed.description = message.content
                await interaction.edit_original_response(
                    content=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.admin.embed.descriptionUpdated",
                    )
                )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.addField"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def add_field(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.field_count >= self.max_fields:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.embed.maxFieldsReached"
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(FieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.setFooter"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def set_footer(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(FooterModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.setColor"
            ),
            style=discord.ButtonStyle.primary,
        )
        async def set_color(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ColorModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.setImage"
            ),
            style=discord.ButtonStyle.secondary,
        )
        async def set_image(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ImageModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.setThumbnail"
            ),
            style=discord.ButtonStyle.secondary,
        )
        async def set_thumbnail(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.send_modal(ThumbnailModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.editField"
            ),
            style=discord.ButtonStyle.secondary,
        )
        async def edit_field(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.field_count == 0:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.embed.noFieldsToEdit"
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(EditFieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.removeField"
            ),
            style=discord.ButtonStyle.danger,
        )
        async def remove_field(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.field_count == 0:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.embed.noFieldsToRemove"
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(RemoveFieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.preview"
            ),
            style=discord.ButtonStyle.secondary,
        )
        async def preview(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.preview_message:
                await self.preview_message.delete()
            self.preview_message = await interaction.channel.send(embed=self.embed)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale, "commands.admin.embed.previewSent"
                ),
                ephemeral=True,
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.buttons.send"
            ),
            style=discord.ButtonStyle.green,
        )
        async def send(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await self.target_channel.send(embed=self.embed)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.commandInfo.locale,
                    "commands.admin.embed.embedSent",
                    channel=self.target_channel.mention,
                ),
                ephemeral=True,
            )
            self.stop()

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    class FieldModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.title",
                )
            )
            self.view = view
            self.name = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.nameLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1,
            )
            self.value = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.valueLabel",
                ),
                style=discord.TextStyle.long,
                required=True,
                max_length=1024,
                min_length=1,
            )
            self.inline = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.inlineLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=5,
                min_length=2,
                placeholder="true/false",
            )
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction):
            inline = self.inline.value.lower() == "true"
            self.view.embed.add_field(
                name=self.name.value, value=self.value.value, inline=inline
            )
            self.view.field_count += 1
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.fieldAdded"
                ),
                ephemeral=True,
            )

    class FooterModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.footerModal.title",
                )
            )
            self.view = view
            self.text = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.footerModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.footer.text,
                required=True,
                max_length=2048,
                min_length=1,
            )
            self.icon_url = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.footerModal.iconLabel",
                ),
                style=discord.TextStyle.short,
                default=view.embed.footer.icon_url,
                required=False,
                max_length=2048,
            )
            self.add_item(self.text)
            self.add_item(self.icon_url)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.set_footer(
                text=self.text.value,
                icon_url=self.icon_url.value if self.icon_url.value else None,
            )
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.footerUpdated"
                ),
                ephemeral=True,
            )

    class ColorModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.colorModal.title",
                )
            )
            self.view = view
            self.color = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.colorModal.label",
                ),
                style=discord.TextStyle.short,
                default=str(view.embed.color) if view.embed.color else "#FFFFFF",
                required=True,
                max_length=7,
                min_length=7,
            )
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction):
            color_regex = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
            if re.match(color_regex, self.color.value):
                color = int(self.color.value.replace("#", ""), 16)
                self.view.embed.color = color
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.view.commandInfo.locale,
                        "commands.admin.embed.colorUpdated",
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.view.commandInfo.locale,
                        "commands.admin.embed.invalidColorCode",
                    ),
                    ephemeral=True,
                )

    class ImageModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.imageModal.title",
                )
            )
            self.view = view
            self.image_url = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.imageModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.image.url,
                required=True,
                max_length=2048,
            )
            self.add_item(self.image_url)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.set_image(url=self.image_url.value)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.imageUpdated"
                ),
                ephemeral=True,
            )

    class ThumbnailModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.thumbnailModal.title",
                )
            )
            self.view = view
            self.thumbnail_url = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.thumbnailModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.thumbnail.url,
                required=True,
                max_length=2048,
            )
            self.add_item(self.thumbnail_url)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.set_thumbnail(url=self.thumbnail_url.value)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale,
                    "commands.admin.embed.thumbnailUpdated",
                ),
                ephemeral=True,
            )

    class EditFieldModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.editFieldModal.title",
                )
            )
            self.view = view
            self.field_index = Select(
                placeholder=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.editFieldModal.selectField",
                ),
                options=[
                    discord.SelectOption(label=f"Field {i+1}", value=str(i))
                    for i in range(len(view.embed.fields))
                ],
            )
            self.name = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.nameLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1,
            )
            self.value = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.valueLabel",
                ),
                style=discord.TextStyle.long,
                required=True,
                max_length=1024,
                min_length=1,
            )
            self.inline = TextInput(
                label=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.fieldModal.inlineLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=5,
                min_length=2,
                placeholder="true/false",
            )
            self.add_item(self.field_index)
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction):
            index = int(self.field_index.values[0])
            inline = self.inline.value.lower() == "true"
            self.view.embed.set_field_at(
                index, name=self.name.value, value=self.value.value, inline=inline
            )
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.fieldEdited"
                ),
                ephemeral=True,
            )

    class RemoveFieldModal(Modal):
        def __init__(self, view):
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.removeFieldModal.title",
                )
            )
            self.view = view
            self.field_index = Select(
                placeholder=tanjunLocalizer.localize(
                    view.commandInfo.locale,
                    "commands.admin.embed.modals.removeFieldModal.selectField",
                ),
                options=[
                    discord.SelectOption(label=f"Field {i+1}", value=str(i))
                    for i in range(len(view.embed.fields))
                ],
            )
            self.add_item(self.field_index)

        async def on_submit(self, interaction: discord.Interaction):
            index = int(self.field_index.values[0])
            self.view.embed.remove_field(index)
            self.view.field_count -= 1
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.fieldRemoved"
                ),
                ephemeral=True,
            )

    if not commandInfo.user.guild_permissions.manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                locale=commandInfo.locale,
                key="commands.admin.embed.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.embed.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    view = EmbedCreatorView(commandInfo, channel)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.embed.creatorTitle"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.embed.creatorDescription",
            channel=channel.mention,
        ),
    )
    view.message = await commandInfo.reply(embed=embed, view=view)
