from locale_keys import locale
import discord
from api import delete_level_system_data, get_level_system_status, set_level_system_status
from utility import ErrorEmbedCategory, categorized_error_embed, categorized_success_embed, command_info, tanjunEmbed

async def disable_level_system(command_info: command_info):

    class ConfirmDisableView(discord.ui.View):

        def __init__(self, command_info: command_info):
            super().__init__(timeout=60)
            self.command_info = command_info
            self.value = None

        @discord.ui.button(label=locale.commands.level.disablelevelsystem.confirm(command_info.locale), style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            self.stop()

        @discord.ui.button(label=locale.commands.level.disablelevelsystem.cancel(command_info.locale), style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = False
            self.stop()
    if not command_info.user.guild_permissions.administrator:
        embed = categorized_error_embed(ErrorEmbedCategory.PERMISSION, title=locale.commands.level.disablelevelsystem.error.no_permission.title(command_info.locale), description=locale.commands.level.disablelevelsystem.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    current_status = await get_level_system_status(str(command_info.guild.id))
    if not current_status:
        embed = categorized_error_embed(ErrorEmbedCategory.NOT_FOUND, title=locale.commands.level.disablelevelsystem.error.already_disabled.title(command_info.locale), description=locale.commands.level.disablelevelsystem.error.already_disabled.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    confirmation_embed = tanjunEmbed(title=locale.commands.level.disablelevelsystem.confirmation.title(command_info.locale), description=locale.commands.level.disablelevelsystem.confirmation.description(command_info.locale))
    view = ConfirmDisableView(command_info)
    message = await command_info.reply(embed=confirmation_embed, view=view)
    await view.wait()
    if view.value is None:
        await message.delete()
        return
    elif view.value:
        await delete_level_system_data(str(command_info.guild.id))
        await set_level_system_status(str(command_info.guild.id), False)
        embed = categorized_success_embed(title=locale.commands.level.disablelevelsystem.success.title(command_info.locale), description=locale.commands.level.disablelevelsystem.success.description(command_info.locale))
        await message.edit(embed=embed, view=None)
    else:
        cancel_embed = tanjunEmbed(title=locale.commands.level.disablelevelsystem.cancel.title(command_info.locale), description=locale.commands.level.disablelevelsystem.cancel.description(command_info.locale))
        await message.edit(embed=cancel_embed, view=None)