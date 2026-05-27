import utility
from localizer import tanjunLocalizer


async def calc(command_info: utility.CommandInfo, expression: str) -> None:
    nsp = utility.NumericStringParser()

    try:
        result = nsp.eval(expression)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.calc.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.math.calc.success.description",
                expression=expression,
                result=result,
            ),
        )
    except Exception as e:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.calc.error.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.math.calc.error.description", error=str(e)
            ),
        )

    await command_info.reply(embed=embed)
