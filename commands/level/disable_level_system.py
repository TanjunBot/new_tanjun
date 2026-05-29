import discord

from api import (
    delete_level_system_data,
    get_level_system_status,
    set_level_system_status,
)
from localizer import tanjunLocalizer
from utility import ErrorEmbedCategory, command_info, error_embed, success_embed, tanjunEmbed


async def disable_level_system(command_info: command_info):
    class ConfirmDisableView(discord.ui.View):
        def __init__(self, command_info: command_info):
            super().__init__(timeout=60)
            self.command_info = command_info
            self.value = None

        @discord.ui.button(
            label=tanjunLocalizer.localize(command_info.locale, "commands.level.disablelevelsystem.confirm"),
            style=discord.ButtonStyle.danger,
        )
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            self.stop()

        @discord.ui.button(
            label=tanjunLocalizer.localize(command_info.locale, "commands.level.disablelevelsystem.cancel"),
            style=discord.ButtonStyle.secondary,
        )
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = False
            self.stop()

    if not command_info.user.guild_permissions.administrator:
        embed = error_embed(
            ErrorEmbedCategory.PERMISSION,
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    current_status = await get_level_system_status(str(command_info.guild.id))

    if not current_status:
        embed = error_embed(
            ErrorEmbedCategory.NOT_FOUND,
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.error.already_disabled.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.error.already_disabled.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    confirmation_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, "commands.level.disablelevelsystem.confirmation.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.level.disablelevelsystem.confirmation.description",
        ),
    )

    view = ConfirmDisableView(command_info)
    message = await command_info.reply(embed=confirmation_embed, view=view)
    await view.wait()

    if view.value is None:
        await message.delete()
        return
    elif view.value:
        await delete_level_system_data(str(command_info.guild.id))
        await set_level_system_status(str(command_info.guild.id), False)

        embed = success_embed(
            title=tanjunLocalizer.localize(command_info.locale, "commands.level.disablelevelsystem.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.success.description",
            ),
        )
        await message.edit(embed=embed, view=None)
    else:
        cancel_embed = tanjunEmbed(
            title=tanjunLocalizer.localize(command_info.locale, "commands.level.disablelevelsystem.cancel.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.disablelevelsystem.cancel.description",
            ),
        )
        await message.edit(embed=cancel_embed, view=None)
