import discord
from discord.ui import View, Button, Modal, TextInput
import utility
from localizer import tanjunLocalizer

async def create_embed(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    class EmbedCreatorView(View):
        def __init__(self, commandInfo, target_channel):
            super().__init__(timeout=600)  # 10 minutes timeout
            self.commandInfo = commandInfo
            self.embed = discord.Embed()
            self.preview_message = None
            self.target_channel = target_channel

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.embed.unauthorizedUser"
                    ),
                    ephemeral=True
                )
                return False
            return True

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.setTitle"), style=discord.ButtonStyle.primary)
        async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(TitleModal(self))

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.setDescription"), style=discord.ButtonStyle.primary)
        async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(DescriptionModal(self))

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.addField"), style=discord.ButtonStyle.primary)
        async def add_field(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(FieldModal(self))

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.setFooter"), style=discord.ButtonStyle.primary)
        async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(FooterModal(self))

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.setColor"), style=discord.ButtonStyle.primary)
        async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(ColorModal(self))

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.preview"), style=discord.ButtonStyle.secondary)
        async def preview(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.preview_message:
                await self.preview_message.delete()
            self.preview_message = await interaction.channel.send(embed=self.embed)
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.admin.embed.previewSent"
            ), ephemeral=True)

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.embed.buttons.send"), style=discord.ButtonStyle.green)
        async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.target_channel.send(embed=self.embed)
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.admin.embed.embedSent",
                channel=self.target_channel.mention
            ), ephemeral=True)
            self.stop()

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    class TitleModal(Modal):
        def __init__(self, view):
            super().__init__(title=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.titleModal.title"))
            self.view = view
            self.title = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.titleModal.label"),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1
            )
            self.add_item(self.title)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.title = self.title.value
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.view.commandInfo.locale, "commands.admin.embed.titleUpdated"
            ), ephemeral=True)

    class DescriptionModal(Modal):
        def __init__(self, view):
            super().__init__(title=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.descriptionModal.title"))
            self.view = view
            self.description = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.descriptionModal.label"),
                style=discord.TextStyle.long,
                required=True,
                max_length=2048,
                min_length=1
            )
            self.add_item(self.description)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.description = self.description.value
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.view.commandInfo.locale, "commands.admin.embed.descriptionUpdated"
            ), ephemeral=True)

    class FieldModal(Modal):
        def __init__(self, view):
            super().__init__(title=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.fieldModal.title"))
            self.view = view
            self.name = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.fieldModal.nameLabel"),
                style=discord.TextStyle.short,
                required=True,
                max_length=256,
                min_length=1
            )
            self.value = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.fieldModal.valueLabel"),
                style=discord.TextStyle.long,
                required=True,
                max_length=1024,
                min_length=1
            )
            self.add_item(self.name)
            self.add_item(self.value)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.add_field(name=self.name.value, value=self.value.value, inline=False)
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.view.commandInfo.locale, "commands.admin.embed.fieldAdded"
            ), ephemeral=True)

    class FooterModal(Modal):
        def __init__(self, view):
            super().__init__(title=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.footerModal.title"))
            self.view = view
            self.text = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.footerModal.label"),
                style=discord.TextStyle.short,
                required=True,
                max_length=2048,
                min_length=1
            )
            self.add_item(self.text)

        async def on_submit(self, interaction: discord.Interaction):
            self.view.embed.set_footer(text=self.text.value)
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.view.commandInfo.locale, "commands.admin.embed.footerUpdated"
            ), ephemeral=True)

    class ColorModal(Modal):
        def __init__(self, view):
            super().__init__(title=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.colorModal.title"))
            self.view = view
            self.color = TextInput(
                label=tanjunLocalizer.localize(view.commandInfo.locale, "commands.admin.embed.modals.colorModal.label"),
                style=discord.TextStyle.short,
                required=True,
                max_length=7,
                min_length=7
            )
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                color = int(self.color.value.replace("#", ""), 16)
                self.view.embed.color = color
                await interaction.response.send_message(tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.colorUpdated"
                ), ephemeral=True)
            except ValueError:
                await interaction.response.send_message(tanjunLocalizer.localize(
                    self.view.commandInfo.locale, "commands.admin.embed.invalidColorCode"
                ), ephemeral=True)

    if not commandInfo.user.guild_permissions.manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                locale = commandInfo.locale, key = "commands.admin.embed.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.embed.missingPermission.description"
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
            channel=channel.mention
        ),
    )
    view.message = await commandInfo.reply(embed=embed, view=view)
