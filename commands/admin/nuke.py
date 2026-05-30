from typing import Any

import discord
from discord.ui import View

import utility
from localizer import tanjunLocalizer
from utility import EmbedColor


async def nuke_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None = None) -> None:
    class ConfirmView(View):
        def __init__(self, command_info: utility.CommandInfo) -> None:
            super().__init__(timeout=60)
            self.command_info = command_info
            self.value = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.command_info.user:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(self.command_info.locale, "commands.admin.nuke.unauthorizedUser"),  # type: ignore[misc]
                    ephemeral=True,
                )
                return False
            return True

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.confirm"),
            style=discord.ButtonStyle.danger,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.command_info.locale, "commands.admin.nuke.confirmationPrompt")  # type: ignore[misc]
            )
            self.value = True  # type: ignore[assignment]
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.cancel"),
            style=discord.ButtonStyle.secondary,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc]
            await interaction.response.send_message(
                tanjunLocalizer.localize(self.command_info.locale, "commands.admin.nuke.cancelledMessage")  # type: ignore[misc]
            )
            self.value = False  # type: ignore[assignment]
            self.stop()

        async def on_timeout(self) -> None:
            if self.message:  # type: ignore[attr-defined]
                await self.message.edit(view=None)  # type: ignore[attr-defined]

    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.nuke.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if channel is None:
        channel = command_info.channel  # type: ignore[misc, assignment]

    if not channel.guild.me.guild_permissions.manage_channels:  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.nuke.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    embed = utility.tanjunEmbed(
        colour=EmbedColor.WARNING,
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.confirmationTitle"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.nuke.confirmationDescription",
            channel=channel.mention,  # type: ignore[union-attr]
        ),
    )
    view = ConfirmView(command_info)
    await command_info.reply(embed=embed, view=view)

    await view.wait()

    if view.value is None:
        await command_info.channel.send(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.timeoutMessage")
        )  # type: ignore[union-attr]
        return
    elif not view.value:  # type: ignore[unreachable]
        return

    def check(m: discord.Message) -> bool:  # type: ignore[unreachable]
        return m.author == command_info.user and m.channel == command_info.channel

    try:
        confirmation_message = await command_info.client.wait_for("message", check=check, timeout=30.0)
    except TimeoutError:
        await command_info.channel.send(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.timeoutMessage")
        )
        return

    if (
        confirmation_message.content.lower()
        != tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.confirmationWord").lower()
    ):
        await command_info.channel.send(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.incorrectConfirmation")
        )
        return

    try:
        new_channel = await channel.clone(
            reason=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.nukeReason")
        )
        await channel.delete()
        await new_channel.send(
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.nuke.nukeSuccessMessage",
                user=command_info.user.mention,
            )
        )
    except discord.Forbidden:
        await command_info.channel.send(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.forbiddenError")
        )
    except discord.HTTPException:
        await command_info.channel.send(tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.httpError"))
    except discord.NotFound:
        await command_info.channel.send(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.nuke.notfoundError")
        )
