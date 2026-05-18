from typing import Any

import discord
from discord.ui import View

import utility
from localizer import tanjunLocalizer


async def nuke_channel(commandInfo: utility.CommandInfo, channel: discord.TextChannel | None = None) -> None:
    class ConfirmView(View):
        def __init__(self, commandInfo: utility.CommandInfo) -> None:
            super().__init__(timeout=60)
            self.commandInfo = commandInfo
            self.value = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.commandInfo.user:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.nuke.unauthorizedUser"),  # type: ignore[misc]
                    ephemeral=True,
                )
                return False
            return True

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.confirm"),
            style=discord.ButtonStyle.danger,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.nuke.confirmationPrompt")  # type: ignore[misc]
            )
            self.value = True  # type: ignore[assignment]
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.cancel"),
            style=discord.ButtonStyle.secondary,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.commandInfo.locale, "commands.admin.nuke.cancelledMessage")  # type: ignore[misc]
            )
            self.value = False  # type: ignore[assignment]
            self.stop()

        async def on_timeout(self) -> None:
            if self.message:  # type: ignore[attr-defined]
                await self.message.edit(view=None)  # type: ignore[attr-defined]

    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if channel is None:
        channel = commandInfo.channel  # type: ignore[misc, assignment]

    if not channel.guild.me.guild_permissions.manage_channels:  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nuke.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.confirmationTitle"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.nuke.confirmationDescription",
            channel=channel.mention,  # type: ignore[union-attr]
        ),
    )
    view = ConfirmView(commandInfo)
    await commandInfo.reply(embed=embed, view=view)

    await view.wait()

    if view.value is None:
        await commandInfo.channel.send(tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.timeoutMessage"))  # type: ignore[union-attr]
        return
    elif not view.value:  # type: ignore[unreachable]
        return

    def check(m: discord.Message) -> bool:  # type: ignore[unreachable]
        return m.author == commandInfo.user and m.channel == commandInfo.channel

    try:
        confirmation_message = await commandInfo.client.wait_for("message", check=check, timeout=30.0)
    except TimeoutError:
        await commandInfo.channel.send(tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.timeoutMessage"))
        return

    if (
        confirmation_message.content.lower()
        != tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.confirmationWord").lower()
    ):
        await commandInfo.channel.send(
            tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.incorrectConfirmation")
        )
        return

    try:
        new_channel = await channel.clone(
            reason=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.nukeReason")
        )
        await channel.delete()
        await new_channel.send(
            tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.nuke.nukeSuccessMessage",
                user=commandInfo.user.mention,
            )
        )
    except discord.Forbidden:
        await commandInfo.channel.send(tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.forbiddenError"))
    except discord.HTTPException:
        await commandInfo.channel.send(tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.nuke.httpError"))
