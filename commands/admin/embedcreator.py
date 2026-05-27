import re
from typing import Any, cast

import discord
from discord.ui import Modal, Select, TextInput, View

import utility
from localizer import tanjunLocalizer


async def create_embed(command_info: utility.CommandInfo, channel: discord.TextChannel, title: str) -> None:
    class EmbedCreatorView(View):
        def __init__(self, command_info: utility.CommandInfo, target_channel: discord.TextChannel) -> None:
            super().__init__(timeout=1800)  # 30 minutes timeout
            self.command_info: utility.CommandInfo = command_info  # type: ignore[assignment]
            self.embed: discord.Embed = discord.Embed(title=title, color=0xFFFFFF)
            self.preview_message: discord.Message | None = None
            self.target_channel: discord.TextChannel = target_channel
            self.field_count: int = 0
            self.max_fields: int = 25
            self.message: discord.Message | None = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_info.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(self.command_info.locale), "commands.admin.embed.unauthorizedUser"),
                    ephemeral=True,
                )
                return False
            return True

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.setDescription"),
            style=discord.ButtonStyle.primary,
        )
        async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(  # type: ignore[call-overload]
                content=tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.admin.embed.setDescription.message",
                ),
                ephemeral=True,
                view=discord.ui.View(),
            )
            try:
                message = await self.command_info.client.wait_for(
                    "message",
                    check=lambda m: m.author == interaction.user and m.channel == interaction.channel,
                    timeout=300.0,
                )
            except TimeoutError:
                await interaction.followup.send_message(  # type: ignore[attr-defined]
                    tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.admin.embed.setDescription.timeout",
                    ),
                    ephemeral=True,
                )
            else:
                await message.delete()
                self.embed.description = str(message.content)
                await interaction.edit_original_response(
                    content=tanjunLocalizer.localize(
                        str(self.command_info.locale),
                        "commands.admin.embed.descriptionUpdated",
                    )
                )

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.addField"),
            style=discord.ButtonStyle.primary,
        )
        async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if self.field_count >= self.max_fields:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(self.command_info.locale, "commands.admin.embed.maxFieldsReached"),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(FieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.setFooter"),
            style=discord.ButtonStyle.primary,
        )
        async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_modal(FooterModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.setColor"),
            style=discord.ButtonStyle.primary,
        )
        async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_modal(ColorModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.setImage"),
            style=discord.ButtonStyle.secondary,
        )
        async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_modal(ImageModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.setThumbnail"),
            style=discord.ButtonStyle.secondary,
        )
        async def set_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_modal(ThumbnailModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.editField"),
            style=discord.ButtonStyle.secondary,
        )
        async def edit_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if self.field_count == 0:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(self.command_info.locale, "commands.admin.embed.noFieldsToEdit"),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(EditFieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.removeField"),
            style=discord.ButtonStyle.danger,
        )
        async def remove_field(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if self.field_count == 0:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(self.command_info.locale, "commands.admin.embed.noFieldsToRemove"),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_modal(RemoveFieldModal(self))

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.preview"),
            style=discord.ButtonStyle.secondary,
        )
        async def preview(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            if self.preview_message:
                await self.preview_message.delete()

            channel = cast(discord.abc.Messageable, interaction.channel)
            self.preview_message = await channel.send(embed=self.embed)
            await interaction.response.send_message(
                tanjunLocalizer.localize(str(self.command_info.locale), "commands.admin.embed.previewSent"),
                ephemeral=True,
            )

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.buttons.send"),
            style=discord.ButtonStyle.green,
        )
        async def send(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await self.target_channel.send(embed=self.embed)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.command_info.locale,
                    "commands.admin.embed.embedSent",
                    channel=self.target_channel.mention,
                ),
                ephemeral=True,
            )
            self.stop()

        async def on_timeout(self) -> None:
            for item in self.children:
                if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                    item.disabled = True
            if self.message:
                await self.message.edit(view=self)

    class FieldModal(Modal):
        def __init__(self, view: "EmbedCreatorView") -> None:
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.title",
                )
            )
            self.view: EmbedCreatorView = view
            self.name: TextInput = TextInput(  # type: ignore[type-arg]
                label=tanjunLocalizer.localize(
                    str(view.command_info.locale),
                    "commands.admin.embed.modals.fieldModal.nameLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1,
            )
            self.value = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.valueLabel",
                ),
                style=discord.TextStyle.long,
                required=True,
                max_length=1024,
                min_length=1,
            )
            self.inline = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.inlineLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=1,
                min_length=1,
                placeholder="y/n",
            )
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            inline = self.inline.value.lower() == "true" or self.inline.value.lower() == "y"
            self.view.embed.add_field(name=self.name.value, value=self.value.value, inline=inline)
            self.view.field_count += 1
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.view.command_info.locale, "commands.admin.embed.fieldAdded"),
                ephemeral=True,
            )

    class FooterModal(Modal):
        def __init__(self, view: "EmbedCreatorView") -> None:
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.footerModal.title",
                )
            )
            self.view = view
            self.text = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.footerModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.footer.text,
                required=True,
                max_length=2048,
                min_length=1,
            )
            self.icon_url = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.footerModal.iconLabel",
                ),
                style=discord.TextStyle.short,
                default=view.embed.footer.icon_url,
                required=False,
                max_length=2048,
            )
            self.add_item(self.text)
            self.add_item(self.icon_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_footer(
                text=self.text.value,
                icon_url=self.icon_url.value if self.icon_url.value else None,
            )
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.view.command_info.locale, "commands.admin.embed.footerUpdated"),
                ephemeral=True,
            )

    class ColorModal(Modal):
        def __init__(self, view) -> None:  # type: ignore[no-untyped-def]
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.colorModal.title",
                )
            )
            self.view = view
            self.color = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.colorModal.label",
                ),
                style=discord.TextStyle.short,
                default=str(view.embed.color) if view.embed.color else "#FFFFFF",
                required=True,
                max_length=7,
                min_length=7,
            )
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            color_regex: str = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
            if re.match(color_regex, str(self.color.value)):
                color: int = int(str(self.color.value).replace("#", ""), 16)
                self.view.embed.color = color
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(self.view.command_info.locale),
                        "commands.admin.embed.colorUpdated",
                    ),
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        str(self.view.command_info.locale),
                        "commands.admin.embed.invalidColorCode",
                    ),
                    ephemeral=True,
                )

    class ImageModal(Modal):
        def __init__(self, view) -> None:  # type: ignore[no-untyped-def]
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.imageModal.title",
                )
            )
            self.view = view
            self.image_url = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.imageModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.image.url,
                required=True,
                max_length=2048,
            )
            self.add_item(self.image_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_image(url=self.image_url.value)
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.view.command_info.locale, "commands.admin.embed.imageUpdated"),
                ephemeral=True,
            )

    class ThumbnailModal(Modal):
        def __init__(self, view) -> None:  # type: ignore[no-untyped-def]
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.thumbnailModal.title",
                )
            )
            self.view = view
            self.thumbnail_url = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.thumbnailModal.label",
                ),
                style=discord.TextStyle.short,
                default=view.embed.thumbnail.url,
                required=True,
                max_length=2048,
            )
            self.add_item(self.thumbnail_url)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            self.view.embed.set_thumbnail(url=self.thumbnail_url.value)
            await interaction.response.send_message(
                tanjunLocalizer.localize(
                    self.view.command_info.locale,
                    "commands.admin.embed.thumbnailUpdated",
                ),
                ephemeral=True,
            )

    class EditFieldModal(Modal):
        def __init__(self, view: "EmbedCreatorView") -> None:
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.editFieldModal.title",
                )
            )
            self.view = view
            self.field_index = Select[Any](
                placeholder=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.editFieldModal.selectField",
                ),
                options=[
                    discord.SelectOption(
                        label=tanjunLocalizer.localize(
                            view.command_info.locale,
                            "commands.admin.embed.modals.editFieldModal.fieldLabel",
                            index=i + 1,
                        ),
                        value=str(i),
                    )
                    for i in range(len(view.embed.fields))
                ],
            )
            self.name = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.nameLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1,
            )
            self.value = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.valueLabel",
                ),
                style=discord.TextStyle.long,
                required=True,
                max_length=1024,
                min_length=1,
            )
            self.inline = TextInput(  # type: ignore[var-annotated]
                label=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.fieldModal.inlineLabel",
                ),
                style=discord.TextStyle.short,
                required=True,
                max_length=1,
                min_length=1,
                placeholder="y/n",
            )
            self.add_item(self.field_index)
            self.add_item(self.name)
            self.add_item(self.value)
            self.add_item(self.inline)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            index = int(self.field_index.values[0])
            inline = self.inline.value.lower() == "y"
            self.view.embed.set_field_at(index, name=self.name.value, value=self.value.value, inline=inline)
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.view.command_info.locale, "commands.admin.embed.fieldEdited"),
                ephemeral=True,
            )

    class RemoveFieldModal(Modal):
        def __init__(self, view: "EmbedCreatorView") -> None:
            super().__init__(
                title=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.removeFieldModal.title",
                )
            )
            self.view = view
            self.field_index = Select[Any](
                placeholder=tanjunLocalizer.localize(
                    view.command_info.locale,
                    "commands.admin.embed.modals.removeFieldModal.selectField",
                ),
                options=[discord.SelectOption(label=f"Field {i + 1}", value=str(i)) for i in range(len(view.embed.fields))],
            )
            self.add_item(self.field_index)

        async def on_submit(self, interaction: discord.Interaction) -> None:
            index = int(self.field_index.values[0])
            self.view.embed.remove_field(index)
            self.view.field_count -= 1
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.view.command_info.locale, "commands.admin.embed.fieldRemoved"),
                ephemeral=True,
            )

    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_messages
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                locale=command_info.locale,
                key="commands.admin.embed.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.embed.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    view = EmbedCreatorView(command_info, channel)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.embed.creatorTitle"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.embed.creatorDescription",
            channel=channel.mention,
        ),
    )
    view.message = await command_info.reply(embed=embed, view=view)
