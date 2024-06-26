import math
import utility
from localizer import tanjunLocalizer


async def faculty_command(commandInfo: utility.commandInfo, number: int):
    try:
        number = int(number)
    except ValueError:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.error.invalid_input"
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    if number < 0:
         embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.faculty.error.invalid_number"
            )
         )
    elif number > 100:
         embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.faculty.error.invalid_number2"
            )
         )
    elif number == 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.faculty.success.description",
                number=number,
                result=1
            ),
        )

        embed.set_footer(text=tanjunLocalizer.localize(
            commandInfo.locale, "commands.math.randomnumber.not_truly_random"
        ))
    else:
        result = math.factorial(number)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.faculty.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.faculty.success.description",
                number=number,
                result=result
            ),
        )
    await commandInfo.reply(embed=embed)
