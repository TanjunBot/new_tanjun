import os
import random

flags = []

for file in os.listdir("commands/games/country_flags"):
    if file.endswith(".png"):
        flags.append(file)


def random_flag() -> str:
    return random.choice(flags)


def get_flag_img(flag_name: str) -> str:
    return f"commands/games/country_flags/{flag_name}"
