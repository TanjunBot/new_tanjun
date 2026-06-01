import utility
from localizer import tanjunLocalizer
from services.ai_service import AiService, TokenOverview


async def show_tokens(command_info: utility.CommandInfo) -> None:
    overview = await AiService.get_token_overview(command_info.user.id)

    if overview is None:
        await AiService.initialize_user(command_info.user.id)
        overview = await AiService.get_token_overview(command_info.user.id)

    if overview is None:
        overview = TokenOverview(free_token=500, plus_token=0, paid_token=0, used_token=0)

    total = overview.free_token + overview.plus_token + overview.paid_token

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.tokens.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.ai.tokens.success.description",
            total=total,
            free=overview.free_token,
            plus=overview.plus_token,
            paid=overview.paid_token,
            used=overview.used_token,
        ),
    )
    await command_info.reply(embed=embed)
