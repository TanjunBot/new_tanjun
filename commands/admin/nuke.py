import discord
from discord.ui import View, Button
import utility
from localizer import tanjunLocalizer
import asyncio

async def nuke_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel = None):
    class ConfirmView(View):
        def __init__(self, commandInfo):
            super().__init__(timeout=60)
            self.commandInfo = commandInfo
            self.value = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.commandInfo.user:
                await interaction.response.send_message(
                    tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.admin.nuke.unauthorizedUser"
                    ),
                    ephemeral=True
                )
                return False
            return True

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.nuke.confirm"), style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.admin.nuke.confirmationPrompt"
            ))
            self.value = True
            self.stop()

        @discord.ui.button(label=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.nuke.cancel"), style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message(tanjunLocalizer.localize(
                self.commandInfo.locale, "commands.admin.nuke.cancelledMessage"
            ))
            self.value = False
            self.stop()

        async def on_timeout(self):
            if self.message:
                await self.message.edit(view=None)
    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.nuke.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nuke.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.guild.me.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.nuke.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nuke.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if channel is None:
        channel = commandInfo.channel

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.confirmationTitle"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.nuke.confirmationDescription",
            channel=channel.mention
        ),
    )
    view = ConfirmView(commandInfo)
    await commandInfo.reply(embed=embed, view=view)

    await view.wait()

    if view.value is None:
        await commandInfo.channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.timeoutMessage"
        ))
        return
    elif not view.value:
        return

    def check(m):
        return m.author == commandInfo.user and m.channel == commandInfo.channel

    try:
        confirmation_message = await commandInfo.client.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await commandInfo.channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.timeoutMessage"
        ))
        return

    if confirmation_message.content.lower() != tanjunLocalizer.localize(commandInfo.locale, "commands.admin.nuke.confirmationWord").lower():
        await commandInfo.channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.incorrectConfirmation"
        ))
        return

    try:
        new_channel = await channel.clone(reason="Channel nuked")
        await channel.delete()
        await new_channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.nukeSuccessMessage",
            user=commandInfo.user.mention
        ))
    except discord.Forbidden:
        await commandInfo.channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.forbiddenError"
        ))
    except discord.HTTPException:
        await commandInfo.channel.send(tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.nuke.httpError"
        ))