from locale_keys import locale
import random
import utility

async def random_number_command(command_info: utility.CommandInfo, min: int, max: int, amount: int=1) -> None:
    try:
        min = int(min)
        max = int(max)
        amount = int(amount)
    except ValueError:
        embed = utility.tanjunEmbed(title=locale.commands.math.randomnumber.error.title(str(command_info.locale)), description=locale.commands.math.randomnumber.error.invalid_input(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if max < min:
        embed = utility.tanjunEmbed(title=locale.commands.math.randomnumber.error.title(str(command_info.locale)), description=locale.commands.math.randomnumber.error.invalid_range(str(command_info.locale)))
    elif amount < 1:
        embed = utility.tanjunEmbed(title=locale.commands.math.randomnumber.error.title(str(command_info.locale)), description=locale.commands.math.randomnumber.error.invalid_amount(str(command_info.locale)))
    else:
        numbers = [random.randint(min, max) for _ in range(amount)]
        numbers_str = ', '.join(map(str, numbers))
        embed = utility.tanjunEmbed(title=locale.commands.math.randomnumber.success.title(str(command_info.locale)), description=locale.commands.math.randomnumber.success.description(command_info.locale, min=min, max=max, amount=amount, numbers=numbers_str))
        embed.set_footer(text=locale.commands.math.randomnumber.not_truly_random(str(command_info.locale)))
    await command_info.reply(embed=embed)