import random
import utility
from localizer import tanjunLocalizer


async def random_number_command(
    commandInfo: utility.commandInfo, min: int, max: int, amount: int = 1
):
    try:
        min = int(min)
        max = int(max)
        amount = int(amount)
    except ValueError:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.invalid_input"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if max < min:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.invalid_range"
            ),
        )
    elif amount < 1:
        # noqa: E501
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.error.invalid_amount"
            ),
        )
    else:
        # nosec: B311
        numbers = [random.randint(min, max) for _ in range(amount)]
        numbers_str = ", ".join(map(str, numbers))

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.math.randomnumber.success.description",
                min=min,
                max=max,
                amount=amount,
                numbers=numbers_str,
            ),
        )

        embed.set_footer(
            text=tanjunLocalizer.localize(
                commandInfo.locale, "commands.math.randomnumber.not_truly_random"
            )
        )

    await commandInfo.reply(embed=embed)
