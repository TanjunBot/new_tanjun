from locale_keys import locale
from services.math import MathService
math_service = MathService()

async def calc(command_info: 'utility.CommandInfo', expression: str) -> None:
    import utility
    result = math_service.evaluate(expression)
    if result.error:
        embed = utility.tanjunEmbed(title=locale.commands.math.calc.error.title(str(command_info.locale)), description=locale.commands.math.calc.error.description(str(command_info.locale), error=result.error))
    else:
        embed = utility.tanjunEmbed(title=locale.commands.math.calc.success.title(str(command_info.locale)), description=locale.commands.math.calc.success.description(str(command_info.locale), expression=expression, result=result.result))
    await command_info.reply(embed=embed)