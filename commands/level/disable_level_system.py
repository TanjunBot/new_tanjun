from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import (
    set_level_system_status,
    get_level_system_status,
    delete_level_system_data,
)
import discord


async def disable_level_system(commandInfo: commandInfo):
    class ConfirmDisableView(discord.ui.View):
        def __init__(self, commandInfo: commandInfo):
            super().__init__(timeout=60)
            self.commandInfo = commandInfo
            self.value = None

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelsystem.confirm"
            ),
            style=discord.ButtonStyle.danger,
        )
        async def confirm(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.value = True
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelsystem.cancel"
            ),
            style=discord.ButtonStyle.secondary,
        )
        async def cancel(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            self.value = False
            self.stop()

    if not commandInfo.user.guild_permissions.administrator:
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
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.disablelevelsystem.confirmation.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.disablelevelsystem.confirmation.description",
        ),
    )

    view = ConfirmDisableView(commandInfo)
    message = await commandInfo.reply(embed=confirmation_embed, view=view)
    await view.wait()

    if view.value is None:
        await message.edit(
            content="Timed out. The level system was not disabled.", view=None
        )
    elif view.value:
        await delete_level_system_data(str(commandInfo.guild.id))
        await set_level_system_status(str(commandInfo.guild.id), False)

        success_embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelsystem.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelsystem.success.description",
            ),
        )
        await message.edit(embed=success_embed, view=None)
    else:
        cancel_embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelsystem.cancel.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelsystem.cancel.description"
            ),
        )
        await message.edit(embed=cancel_embed, view=None)
