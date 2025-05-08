def allowed_words(locale: str) -> list[str]:
    with open(f"commands/games/wordle_words/{locale}/allowed_words.txt", encoding="utf-8") as file:
        return file.read().splitlines()


def possible_words(locale: str) -> list[str]:
    with open(f"commands/games/wordle_words/{locale}/possible_words.txt", encoding="utf-8") as file:
        return file.read().splitlines()
