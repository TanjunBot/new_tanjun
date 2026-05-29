import random
from math import sqrt

import discord

from api import check_if_opted_out
from localizer import tanjunLocalizer
from models import CountingMode
from services.counting_repository import CountingMode as _CountingDBMode
from services.counting_repository import CountingRepository
from utility import DiscordSafe, EmbedColor, tanjunEmbed

repo = CountingRepository
MODE = _CountingDBMode.MODES

# ── Mode definitions ─────────────────────────────────────────

modeMap = {
    CountingMode.NORMAL: "normal",
    CountingMode.NEGATIVE: "negative",
    CountingMode.REVERSE: "reverse",
    CountingMode.PRIME: "prime",
    CountingMode.EVEN: "even",
    CountingMode.ODD: "odd",
    CountingMode.FIBONACCI: "fibonacci",
    CountingMode.DOUBLE: "double",
    CountingMode.TRIPLE: "triple",
    CountingMode.HUNDREDS: "houndreds",
    CountingMode.BINARY: "binary",
    CountingMode.ROMEAN: "romean",
    CountingMode.SQUARE: "square",
    CountingMode.CUBE: "cube",
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


def get_correct_next_number(mode: CountingMode, number: int | str):
    if mode == CountingMode.NORMAL:
        return number + 1
    if mode == CountingMode.NEGATIVE:
        return number - 1
    if mode == CountingMode.REVERSE:
        return number - 1
    if mode == CountingMode.PRIME:
        return primes[primes.index(number) + 1]
    if mode == CountingMode.EVEN:
        return number + 2
    if mode == CountingMode.ODD:
        return number + 2
    if mode == CountingMode.FIBONACCI:
        if number == -1:
            return 0
        if number == 0:
            return 1
        if number == -15:  # First 1 was stored as -15
            return 1  # Return 1 again for the second 1
        idx = fibonacci.index(number)
        return int(fibonacci[idx + 1])
    if mode == CountingMode.DOUBLE:
        return number * 2
    if mode == CountingMode.TRIPLE:
        return number * 3
    if mode == CountingMode.HUNDREDS:
        return number + 100
    if mode == CountingMode.BINARY:
        return number + 1
    if mode == CountingMode.ROMEAN:
        return number_to_romeal(number + 1) if number != 0 else "I"
    if mode == CountingMode.SQUARE:
        if number == 0:
            return 1
        next_num = int(sqrt(number)) + 1
        return next_num * next_num
    if mode == CountingMode.CUBE:
        if number == 0:
            return 1
        next_num = int(number ** (1 / 3)) + 1
        return next_num**3


def get_goal(mode: CountingMode):
    if mode == CountingMode.NORMAL:
        # nosec: B311
        return random.randint(20, 100)
    if mode == CountingMode.NEGATIVE:
        # nosec: B311
        return random.randint(-100, -20)
    if mode == CountingMode.REVERSE:
        # nosec: B311
        return random.randint(5, 80)
    if mode == CountingMode.PRIME:
        # nosec: B311
        return primes[random.randint(5, len(primes) - 1)]
    if mode == CountingMode.EVEN:
        # nosec: B311
        number = random.randint(20, 100)
        return number if number % 2 == 0 else number + 1
    if mode == CountingMode.ODD:
        # nosec: B311
        number = random.randint(20, 100)
        return number if number % 2 != 0 else number + 1
    if mode == CountingMode.FIBONACCI:
        # nosec: B311
        return fibonacci[random.randint(5, len(fibonacci) - 1)]
    if mode == CountingMode.DOUBLE:
        # nosec: B311
        return 2 ** random.randint(5, 20)
    if mode == CountingMode.TRIPLE:
        # nosec: B311
        return 3 ** random.randint(5, 10)
    if mode == CountingMode.HUNDREDS:
        # nosec: B311
        return random.randint(20, 100) * 100
    if mode == CountingMode.BINARY:
        # nosec: B311
        return random.randint(20, 100)
    if mode == CountingMode.ROMEAN:
        # nosec: B311
        return number_to_romeal(random.randint(20, 100))
    if mode == CountingMode.SQUARE:
        return random.randint(20, 100) ** 2
    if mode == CountingMode.CUBE:
        return random.randint(20, 100) ** 3


def get_first_number(mode: CountingMode) -> int | None:
    if mode == CountingMode.NORMAL:
        return 0
    if mode == CountingMode.NEGATIVE:
        return 0
    if mode == CountingMode.REVERSE:
        return 101
    if mode == CountingMode.PRIME:
        return 0
    if mode == CountingMode.EVEN:
        return 0
    if mode == CountingMode.ODD:
        return -1
    if mode == CountingMode.FIBONACCI:
        return -1
    if mode == CountingMode.DOUBLE:
        return 1
    if mode == CountingMode.TRIPLE:
        return 1
    if mode == CountingMode.HUNDREDS:
        return 0
    if mode == CountingMode.BINARY:
        return 0
    if mode == CountingMode.ROMEAN:
        return 0
    if mode == CountingMode.SQUARE:
        return 0
    if mode == CountingMode.CUBE:
        return 0


async def counting(message: discord.Message, config: dict | None = None) -> None:
    """Counting modes handler. Accepts optional pre-fetched config to skip DB queries.

    The config dict should have keys: 'progress', 'mode', 'goal', 'last_counter_id', 'guild_id'.
    """
    if config is not None:
        progress = config.get("progress")
        mode_raw = config.get("mode")
        goal = config.get("goal")
        last_counter_id = config.get("last_counter_id")
    else:
        progress = await repo.get_progress(MODE, message.channel.id)
        mode_raw = await repo.get_mode(message.channel.id)
        goal = None  # Fetched later if needed
        last_counter_id = None

    # Normalize mode to CountingMode enum
    if isinstance(mode_raw, int):
        mode = CountingMode(mode_raw)
    else:
        mode = mode_raw

    locale = message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en_US"

    if not progress and progress != 0:
        return

    if mode == CountingMode.ROMEAN:
        progress = number_to_romeal(progress)

    # Binary mode stores progress as integer; no conversion needed

    if await check_if_opted_out(message.author.id):
        await DiscordSafe.send_dm(message.author, tanjunLocalizer.localize(locale, "minigames.counting.opted_out"))
        await DiscordSafe.delete(message)
        return

    content = message.content

    if mode == CountingMode.ROMEAN:
        correct_number = get_correct_next_number(mode, romeal_to_number(progress))
    else:
        correct_number = get_correct_next_number(mode, progress)

    if not content:
        await DiscordSafe.add_reaction(message, "💀")
        # nosec: B311
        new_mode = random.choice(list(modeMap))
        goal = get_goal(new_mode)
        embed = tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correct_number,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[new_mode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[new_mode]}.description",
                ),
                goal=goal,
            ),
        )
        await repo.clear(MODE, message.channel.id)
        if new_mode == CountingMode.ROMEAN:
            goal = romeal_to_number(goal)
        starter = get_first_number(new_mode)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            guild_id=message.guild.id,
            mode=new_mode,
            goal=goal,
            counter_id="nobody",
        )
        await DiscordSafe.reply(message, embed=embed)
        return

    try:
        number = (
            int(content, 2)
            if mode == CountingMode.BINARY
            else (int(content) if mode != CountingMode.ROMEAN else content)
        )
    except ValueError:
        await DiscordSafe.add_reaction(message, "💀")
        # nosec: B311
        new_mode = random.choice(list(modeMap))
        goal = get_goal(new_mode)
        embed = tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correct_number,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[new_mode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[new_mode]}.description",
                ),
                goal=goal,
            ),
        )
        await repo.clear(MODE, message.channel.id)
        if new_mode == CountingMode.ROMEAN:
            goal = romeal_to_number(goal)
        starter = get_first_number(new_mode)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            guild_id=message.guild.id,
            mode=new_mode,
            goal=goal,
            counter_id="nobody",
        )
        await DiscordSafe.reply(message, embed=embed)
        return

    if number != correct_number:
        await DiscordSafe.add_reaction(message, "💀")
        # nosec: B311
        new_mode = random.choice(list(modeMap))
        goal = get_goal(new_mode)
        embed = tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed.description",
                number=correct_number,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[new_mode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[new_mode]}.description",
                ),
                goal=goal,
            ),
        )
        await repo.clear(MODE, message.channel.id)
        if new_mode == CountingMode.ROMEAN:
            goal = romeal_to_number(goal)
        starter = get_first_number(new_mode)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            guild_id=message.guild.id,
            mode=new_mode,
            goal=goal,
            counter_id="nobody",
        )
        await DiscordSafe.reply(message, embed=embed)
        return

    if config is None:
        last_counter_id = await repo.get_last_counter_id(MODE, message.channel.id)

    if last_counter_id == str(message.author.id):
        await DiscordSafe.add_reaction(message, "💀")
        # nosec: B311
        new_mode = random.choice(list(modeMap))
        goal = get_goal(new_mode)
        embed = tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.failed_double.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.failed_double.description",
                number=correct_number,
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[new_mode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[new_mode]}.description",
                ),
                goal=goal,
            ),
        )
        await repo.clear(MODE, message.channel.id)
        if new_mode == CountingMode.ROMEAN:
            goal = romeal_to_number(goal)
        starter = get_first_number(new_mode)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            guild_id=message.guild.id,
            mode=new_mode,
            goal=goal,
            counter_id="nobody",
        )
        await DiscordSafe.reply(message, embed=embed)
        return

    if config is None or goal is None:
        goal = await repo.get_goal(message.channel.id)

    if mode == CountingMode.ROMEAN:
        number = romeal_to_number(number)

    if number == goal:
        await DiscordSafe.add_reaction(message, "🎉")
        # nosec: B311
        new_mode = random.choice(list(modeMap))
        new_goal = get_goal(new_mode)
        if new_mode == CountingMode.ROMEAN:
            new_goal = romeal_to_number(new_goal)
        embed = tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(locale, "minigames.counting.modes.won.title"),
            description=tanjunLocalizer.localize(
                locale,
                "minigames.counting.modes.won.description",
                mode_name=tanjunLocalizer.localize(locale, f"minigames.counting.modes.modes.{modeMap[new_mode]}.name"),
                mode_description=tanjunLocalizer.localize(
                    locale,
                    f"minigames.counting.modes.modes.{modeMap[new_mode]}.description",
                ),
                goal=goal,
                new_goal=new_goal,
            ),
        )
        await repo.clear(MODE, message.channel.id)
        starter = get_first_number(new_mode)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=starter,
            guild_id=message.guild.id,
            mode=new_mode,
            goal=new_goal,
            counter_id="nobody",
        )
        await DiscordSafe.reply(message, embed=embed)
        return

    if mode == CountingMode.ROMEAN:
        correct_number = romeal_to_number(correct_number)

    await repo.set_mode_progress(
        channel_id=message.channel.id,
        progress=(-15 if (mode == CountingMode.FIBONACCI and number == 1 and progress == 0) else correct_number),
        guild_id=message.guild.id,
        mode=mode,
        goal=goal,
        counter_id=message.author.id,
    )
    # nosec: B311
    if random.randint(1, 100) == 1:
        correct_number = get_correct_next_number(mode, correct_number)
        # Display next number in the correct format for the mode
        display_number = (
            bin(correct_number)[2:] if mode == CountingMode.BINARY else (
                number_to_romeal(correct_number) if mode == CountingMode.ROMEAN else str(correct_number)
            )
        )
        await DiscordSafe.send(message.channel, content=display_number)
        await repo.set_mode_progress(
            channel_id=message.channel.id,
            progress=(romeal_to_number(correct_number) if mode == CountingMode.ROMEAN else correct_number),
            guild_id=message.guild.id,
            mode=mode,
            goal=goal,
            counter_id="me",
        )
