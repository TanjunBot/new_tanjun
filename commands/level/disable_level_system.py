from typing import Any

import discord  # type: ignore[import-not-found]

from api import (
    delete_level_system_data,
    get_level_system_status,
    set_level_system_status,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def disable_level_system(commandInfo: CommandInfo) -> None:
    class ConfirmDisableView(discord.ui.View):  # type: ignore[misc,no-any-unimported]
        def __init__(self, commandInfo: CommandInfo) -> None:
            super().__init__(timeout=60)
            self.commandInfo = CommandInfo
            self.value = None

        @discord.ui.button(  # type: ignore[untyped-decorator]
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelsystem.confirm"),
            style=discord.ButtonStyle.danger,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            self.value = True  # type: ignore[assignment]
            self.stop()

        @discord.ui.button(  # type: ignore[untyped-decorator]
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelsystem.cancel"),
            style=discord.ButtonStyle.secondary,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            self.value = False  # type: ignore[assignment]
            self.stop()

    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    current_status = await get_level_system_status(str(commandInfo.guild.id))

    if not current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.error.already_disabled.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.error.already_disabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    confirmation_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelsystem.confirmation.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.disablelevelsystem.confirmation.description",
        ),
    )

    view = ConfirmDisableView(commandInfo)
    message = await commandInfo.reply(embed=confirmation_embed, view=view)
    await view.wait()

    if view.value is None:
        await message.delete()
        return
    elif view.value:  # type: ignore[unreachable]
        await delete_level_system_data(str(commandInfo.guild.id))
        await set_level_system_status(str(commandInfo.guild.id), False)

        success_embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelsystem.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.success.description",
            ),
        )
        await message.edit(embed=success_embed, view=None)
    else:
        cancel_embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelsystem.cancel.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.cancel.description",
            ),
        )
        await message.edit(embed=cancel_embed, view=None)
