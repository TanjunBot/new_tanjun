# Unused imports:
# from typing import Union
import random
from math import sqrt

import discord

from api import (
    check_if_opted_out,
    clear_counting_mode,
    get_count_mode_goal,
    get_counting_mode_mode,
    get_counting_mode_progress,
    get_last_mode_counter_id,
    set_counting_mode_progress,
)
from localizer import tanjunLocalizer
from utility import tanjunEmbed

modeMap = {
    1: "normal",
    2: "negative",
    3: "reverse",
    4: "prime",
    5: "even",
    6: "odd",
    7: "fibonacci",
    8: "double",
    9: "triple",
    10: "houndreds",
    11: "binary",
    12: "romean",
    13: "square",
    14: "cube",
}

primes = [
    0,
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
    191,
    193,
    197,
    199,
]

fibonacci = [
    -1,
    0,
    1,
    2,
    3,
    5,
    8,
    13,
    21,
    34,
    55,
    89,
    144,
    233,
    377,
    610,
    987,
    1597,
    2584,
    4181,
    6765,
    10946,
    17711,
    28657,
    46368,
    75025,
    121393,
    196418,
    317811,
    514229,
]


def romeal_to_number(romeal):
    romeal_map = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    number = 0
    romeal = romeal.upper()

    letter_index = 0
    while letter_index < len(romeal):
        letter = romeal[letter_index]
        next_letter = romeal[letter_index + 1] if letter_index + 1 < len(romeal) else None
        next_next_letter = romeal[letter_index + 2] if letter_index + 2 < len(romeal) else None
        next_next_next_letter = romeal[letter_index + 3] if letter_index + 3 < len(romeal) else None

        letter_value = romeal_map.get(letter, 0)
        next_letter_value = romeal_map.get(next_letter, 0) if next_letter else 0

        if (
            (letter == next_letter)
            and (next_letter == next_next_letter)
            and (next_next_letter == next_next_next_letter)
            and next_next_next_letter
        ):
            return float("nan")  # Invalid romeal number

        if letter_value < next_letter_value:
            number -= letter_value
        else:
            number += letter_value

        letter_index += 1

    return number


def number_to_romeal(number):
    if number == 0:
        return "0"

    if not (0 < number < 4000):
        return "Invalid input: Number must be between 1 and 3999."

    numeral_map = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    roman_numeral = []

    for value, numeral in numeral_map:
        while number >= value:
            roman_numeral.append(numeral)
            number -= value

    return "".join(roman_numeral)


def get_correct_next_number(mode: int, number: int):
    if mode == 1:
        return number + 1
    if mode == 2:
        return number - 1
    if mode == 3:
        return number - 1
    if mode == 4:
        return primes[primes.index(number) + 1]
    if mode == 5:
        return number + 2
    if mode == 6:
        return number + 2
    if mode == 7:
        if number == -1:
            return 0
        if number == 0:
            return 1
        if number == -15:  # First 1 was stored as -15
            return 1  # Return 1 again for the second 1
        idx = fibonacci.index(number)
        return int(fibonacci[idx + 1])
    if mode == 8:
        return number * 2
    if mode == 9:
        return number * 3
    if mode == 10:
        return number + 100
    if mode == 11:
        return int(str(bin(int(bin(number)[2:], 2) + 1))[2:])
    if mode == 12:
        return number_to_romeal(number + 1) if number != 0 else "I"
    if mode == 13:
        if number == 0:
            return 1
        next_num = int(sqrt(number)) + 1
        return next_num * next_num
    if mode == 14:
        if number == 0:
            return 1
        next_num = int(number ** (1 / 3)) + 1
        return next_num**3


def get_goal(mode: int):
    if mode == 1:
        # nosec: B311
        return random.randint(20, 100)
    if mode == 2:
        # nosec: B311
        return random.randint(-100, -20)
    if mode == 3:
        # nosec: B311
        return random.randint(5, 80)
    if mode == 4:
        # nosec: B311
        return primes[random.randint(5, len(primes) - 1)]
    if mode == 5:
        # nosec: B311
        number = random.randint(20, 100)
        return number if number % 2 == 0 else number + 1
    if mode == 6:
        # nosec: B311
        number = random.randint(20, 100)
        return number if number % 2 != 0 else number + 1
    if mode == 7:
        # nosec: B311
        return fibonacci[random.randint(5, len(fibonacci) - 1)]
    if mode == 8:
        # nosec: B311
        return 2 ** random.randint(5, 20)
    if mode == 9:
        # nosec: B311
        return 3 ** random.randint(5, 10)
    if mode == 10:
        # nosec: B311
        return random.randint(20, 100) * 100
    if mode == 11:
        # nosec: B311
        return int(str(bin(random.randint(20, 100)))[2:])
    if mode == 12:
        # nosec: B311
        return number_to_romeal(random.randint(20, 100))
    if mode == 13:
        return random.randint(20, 100) ** 2
    if mode == 14:
        return random.randint(20, 100) ** 3


def get_first_number(mode: int):
    if mode == 1:
        return 0
    if mode == 2:
        return 0
    if mode == 3:
        return 101
    if mode == 4:
        return 0
    if mode == 5:
        return 0
    if mode == 6:
        return -1
    if mode == 7:
        return -1
    if mode == 8:
        return 1
    if mode == 9:
        return 1
    if mode == 10:
        return 0
    if mode == 11:
        return 0
    if mode == 12:
        return 0
    if mode == 13:
        return 0
    if mode == 14:
        return 0


async def counting(message: discord.Message):
    if message.author.bot:
        return

    progress = await get_counting_mode_progress(message.channel.id)

    mode = await get_counting_mode_mode(message.channel.id)

    locale = message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en_US"

    if not progress and progress != 0:
        return

    if mode == 12:
        progress = number_to_romeal(progress)

    if mode == 11:
        progress = int(str(progress), 2)

    if await check_if_opted_out(message.author.id):
        try:
            await message.author.send(tanjunLocalizer.localize(locale, "minigames.counting.opted_out"))
        except discord.Forbidden:
            pass
        await message.delete()
        return

    content = message.content

    if mode == 12:
        correctNumber = get_correct_next_number(mode, romeal_to_number(progress))
    else:
        correctNumber = get_correct_next_number(mode, progress)

    if not content:
        await message.add_reaction("💀")
        # nosec: B311
        newMode = random.randint(1, len(modeMap))
        goal = get_goal(newMode)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correctNumber,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[newMode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[newMode]}.description",
                ),
                goal=goal,
            ),
        )
        await clear_counting_mode(message.channel.id)
        if mode == 12:
            goal = romeal_to_number(goal)
        starter = get_first_number(newMode)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            mode=newMode,
            goal=goal,
            counter_id="nobody",
            guild_id=message.guild.id,
        )
        await message.reply(embed=embed)
        return

    try:
        number = int(content) if mode != 12 else content
    except ValueError:
        await message.add_reaction("💀")
        # nosec: B311
        newMode = random.randint(1, len(modeMap))
        goal = get_goal(newMode)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correctNumber,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[newMode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[newMode]}.description",
                ),
                goal=goal,
            ),
        )
        await clear_counting_mode(message.channel.id)
        if mode == 12:
            goal = romeal_to_number(goal)
        starter = get_first_number(newMode)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            mode=newMode,
            goal=goal,
            counter_id="nobody",
            guild_id=message.guild.id,
        )
        await message.reply(embed=embed)
        return

    if number != correctNumber:
        await message.add_reaction("💀")
        # nosec: B311
        newMode = random.randint(1, len(modeMap))
        goal = get_goal(newMode)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correctNumber,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[newMode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[newMode]}.description",
                ),
                goal=goal,
            ),
        )
        await clear_counting_mode(message.channel.id)
        if newMode == 12:
            goal = romeal_to_number(goal)
        starter = get_first_number(newMode)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            mode=newMode,
            goal=goal,
            counter_id="nobody",
            guild_id=message.guild.id,
        )
        await message.reply(embed=embed)
        return

    last_counter_id = await get_last_mode_counter_id(message.channel.id)

    if last_counter_id == str(message.author.id):
        await message.add_reaction("💀")
        # nosec: B311
        newMode = random.randint(1, len(modeMap))
        goal = get_goal(newMode)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed_double.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed_double.description",
                number=correctNumber,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[newMode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[newMode]}.description",
                ),
                goal=goal,
            ),
        )
        await clear_counting_mode(message.channel.id)
        if mode == 12:
            goal = romeal_to_number(goal)
        starter = get_first_number(newMode)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            mode=newMode,
            goal=goal,
            counter_id="nobody",
            guild_id=message.guild.id,
        )
        await message.reply(embed=embed)
        return

    goal = await get_count_mode_goal(message.channel.id)

    if mode == 12:
        number = romeal_to_number(number)

    if number == goal:
        await message.add_reaction("🎉")
        # nosec: B311
        newMode = random.randint(1, len(modeMap))
        new_goal = get_goal(newMode)
        if mode == 12:
            new_goal = romeal_to_number(new_goal)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.won.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.won.description",
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[newMode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[newMode]}.description",
                ),
                goal=goal,
                new_goal=new_goal,
            ),
        )
        await clear_counting_mode(message.channel.id)
        if mode == 12:
            new_goal = romeal_to_number(new_goal)
        starter = get_first_number(newMode)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            mode=newMode,
            goal=new_goal,
            counter_id="nobody",
            guild_id=message.guild.id,
        )
        await message.reply(embed=embed)
        return

    if mode == 12:
        correctNumber = romeal_to_number(correctNumber)

    await set_counting_mode_progress(
        channel_id=message.channel.id,
        progress=(-15 if (mode == 7 and number == 1 and progress == 0) else correctNumber),
        mode=mode,
        counter_id=message.author.id,
        guild_id=message.guild.id,
        goal=goal,
    )
    # nosec: B311
    if random.randint(1, 100) == 1:
        correctNumber = get_correct_next_number(mode, correctNumber)
        await message.channel.send(correctNumber)
        await set_counting_mode_progress(
            channel_id=message.channel.id,
            progress=(romeal_to_number(correctNumber) if mode == 12 else correctNumber),
            mode=mode,
            counter_id="me",
            guild_id=message.guild.id,
            goal=goal,
        )
