from localizer import tanjunLocalizer
from services.math import MathService

math_service = MathService()


async def calc(command_info: "utility.CommandInfo", expression: str) -> None:  # noqa: F821 — forward ref
    import utility  # noqa: PLC0415 — inline import to avoid circular deps

    result = math_service.evaluate(expression)

    if result.error:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.calc.error.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.math.calc.error.description", error=result.error
            ),
        )
    else:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.calc.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.math.calc.success.description",
                expression=expression,
                result=result.result,
            ),
        )

    await command_info.reply(embed=embed)
