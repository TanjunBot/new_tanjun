def words(locale: str):
    with open(f"commands/games/hangman_words/{locale}/allowed_words.txt", encoding="utf-8") as file:
        return file.read().splitlines()
