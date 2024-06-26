# import discord
import utility
from localizer import tanjunLocalizer


async def calc(commandInfo: utility.commandInfo, expression: str):
    nsp = utility.NumericStringParser()

    try:
        result = nsp.eval(expression)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.calc.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.calc.success.description",
                expression=expression,
                result=result
            ),
        )
    except Exception as e:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.calc.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.calc.error.description",
                error=str(e)
            ),
        )

    await commandInfo.reply(embed=embed)
