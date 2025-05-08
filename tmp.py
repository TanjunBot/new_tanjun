from typing import TypeAlias

def allowed_words(locale: str) -> list[str]:
    with open(f"commands/games/wordle_words/{locale}/allowed_words.txt", encoding="utf-8") as file:
        return file.read().splitlines()

print(allowed_words("de"))