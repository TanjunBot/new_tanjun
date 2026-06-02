from locale_keys import locale
import utility
from services.ai_service import AiService

async def delete_custom_situation(command_info: utility.CommandInfo) -> None:
    situation = await AiService.get_user_situation(command_info.user.id)
    if situation is None:
        embed = utility.tanjunEmbed(title=locale.commands.ai.deletecustom.notfound.title(str(command_info.locale)), description=locale.commands.ai.deletecustom.notfound.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    await AiService.delete_situation(situation.user_id)
    embed = utility.tanjunEmbed(title=locale.commands.ai.deletecustom.success.title(str(command_info.locale)), description=locale.commands.ai.deletecustom.success.description(command_info.locale, name=situation.name))
    await command_info.reply(embed=embed)