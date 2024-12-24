import discord
import utility
from localizer import tanjunLocalizer
from api import add_trigger_message as add_trigger_message_api, get_trigger_messages_by_channel as get_trigger_messages_by_channel_api

async def add_trigger_message(commandInfo: utility.commandInfo, trigger: str, response: str, caseSensitive: bool = False):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.trigger_messages.add.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.trigger_messages.add.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_trigger_message_api(commandInfo.guild.id, trigger, response, caseSensitive)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.trigger_messages.add.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.trigger_messages.add.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)

