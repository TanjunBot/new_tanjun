from locale_keys import locale
from typing import Any
import discord
from discord.ui import View
import utility
from utility import EmbedColor

async def nuke_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None=None) -> None:

    class ConfirmView(View):

        def __init__(self, command_info: utility.CommandInfo) -> None:
            super().__init__(timeout=60)
            self.command_info = command_info
            self.value = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_info.user:
                await interaction.response.send_message(locale.commands.admin.nuke.unauthorizedUser(self.command_info.locale), ephemeral=True)
                return False
            return True

        @discord.ui.button(label=locale.commands.admin.nuke.confirm(str(command_info.locale)), style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_message(locale.commands.admin.nuke.confirmationPrompt(self.command_info.locale))
            self.value = True
            self.stop()

        @discord.ui.button(label=locale.commands.admin.nuke.cancel(str(command_info.locale)), style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:
            await interaction.response.send_message(locale.commands.admin.nuke.cancelledMessage(self.command_info.locale))
            self.value = False
            self.stop()

        async def on_timeout(self) -> None:
            if self.message:
                await self.message.edit(view=None)
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.nuke.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.nuke.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if channel is None:
        channel = command_info.channel
    if not channel.guild.me.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.nuke.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.nuke.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    embed = utility.tanjunEmbed(colour=EmbedColor.WARNING, title=locale.commands.admin.nuke.confirmationTitle(str(command_info.locale)), description=locale.commands.admin.nuke.confirmationDescription(command_info.locale, channel=channel.mention))
    view = ConfirmView(command_info)
    await command_info.reply(embed=embed, view=view)
    await view.wait()
    if view.value is None:
        await command_info.channel.send(locale.commands.admin.nuke.timeoutMessage(str(command_info.locale)))
        return
    elif not view.value:
        return

    def check(m: discord.Message) -> bool:
        return m.author == command_info.user and m.channel == command_info.channel
    try:
        confirmation_message = await command_info.client.wait_for('message', check=check, timeout=30.0)
    except TimeoutError:
        await command_info.channel.send(locale.commands.admin.nuke.timeoutMessage(str(command_info.locale)))
        return
    if confirmation_message.content.lower() != locale.commands.admin.nuke.confirmationWord(str(command_info.locale)).lower():
        await command_info.channel.send(locale.commands.admin.nuke.incorrectConfirmation(str(command_info.locale)))
        return
    try:
        new_channel = await channel.clone(reason=locale.commands.admin.nuke.nukeReason(str(command_info.locale)))
        await channel.delete()
        await new_channel.send(locale.commands.admin.nuke.nukeSuccessMessage(command_info.locale, user=command_info.user.mention))
    except discord.Forbidden:
        await command_info.channel.send(locale.commands.admin.nuke.forbiddenError(str(command_info.locale)))
    except discord.HTTPException:
        await command_info.channel.send(locale.commands.admin.nuke.httpError(str(command_info.locale)))
    except discord.NotFound:
        await command_info.channel.send(locale.commands.admin.nuke.notfound.description(str(command_info.locale)))