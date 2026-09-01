from locale_keys import locale
import math
import utility

async def faculty_command(command_info: utility.CommandInfo, number: int) -> None:
    try:
        number = int(number)
    except ValueError:
        embed = utility.tanjunEmbed(title=locale.commands.math.faculty.error.title(str(command_info.locale)), description=locale.commands.math.faculty.error.invalid_input(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if number < 0:
        embed = utility.tanjunEmbed(title=locale.commands.math.faculty.error.title(str(command_info.locale)), description=locale.commands.math.faculty.error.invalid_number(str(command_info.locale)))
    elif number > 100:
        embed = utility.tanjunEmbed(title=locale.commands.math.faculty.error.title(str(command_info.locale)), description=locale.commands.math.faculty.error.invalid_number2(str(command_info.locale)))
    elif number == 0:
        embed = utility.tanjunEmbed(title=locale.commands.math.faculty.success.title(str(command_info.locale)), description=locale.commands.math.faculty.success.description(command_info.locale, number=number, result=1))
        embed.set_footer(text=locale.commands.math.randomnumber.not_truly_random(str(command_info.locale)))
    else:
        result = math.factorial(number)
        embed = utility.tanjunEmbed(title=locale.commands.math.faculty.success.title(str(command_info.locale)), description=locale.commands.math.faculty.success.description(command_info.locale, number=number, result=result))
    await command_info.reply(embed=embed)