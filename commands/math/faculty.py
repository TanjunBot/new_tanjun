import math

import utility
from localizer import tanjunLocalizer


async def faculty_command(command_info: utility.CommandInfo, number: int) -> None:
    try:
        number = int(number)
    except ValueError:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.invalid_input"),
        )
        await command_info.reply(embed=embed)
        return
    if number < 0:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.invalid_number"),
        )
    elif number > 100:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.error.invalid_number2"),
        )
    elif number == 0:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.math.faculty.success.description",
                number=number,
                result=1,
            ),
        )

        embed.set_footer(
            text=tanjunLocalizer.localize(str(command_info.locale), "commands.math.randomnumber.not_truly_random")
        )
    else:
        result = math.factorial(number)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.math.faculty.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.math.faculty.success.description",
                number=number,
                result=result,
            ),
        )
    await command_info.reply(embed=embed)
