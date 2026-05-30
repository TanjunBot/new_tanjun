"""
Wordle service: Centralized game state management, stats tracking, and share generation.

Provides the game logic layer between the command UI and the database/storage layer.
"""

from __future__ import annotations

from models import WordleStatsModel


def _api_to_model(data: dict | None) -> WordleStatsModel | None:
    """Convert API dict result to WordleStatsModel."""
    if data is None:
        return None
    return WordleStatsModel(**data)


async def get_wordle_stats(user_id: str, guild_id: str) -> WordleStatsModel | None:
    """Get Wordle stats for a user in a guild."""
    from api import get_wordle_stats as _get

    data = await _get(user_id, guild_id)
    return _api_to_model(data)


async def upsert_wordle_stats(
    user_id: str,
    guild_id: str,
    won: bool,
    guesses: int,
    hard_mode: bool = False,
) -> WordleStatsModel | None:
    """Update or create Wordle stats after a game ends."""
    from api import upsert_wordle_stats as _upsert

    data = await _upsert(user_id, guild_id, won, guesses, hard_mode)
    return _api_to_model(data)


def validate_hard_mode_guess(guess: str, previous_guesses: list[str], word: str) -> str | None:
    """Validate a guess against hard mode rules, returning an error message or None."""
    if not previous_guesses:
        return None  # First guess is always valid

    last_guess = previous_guesses[-1] if previous_guesses else ""
    if not last_guess:
        return None

    # Evaluate the previous guess to determine which letters were revealed (green/yellow)
    revealed_green = []
    revealed_yellow = []
    word_chars = list(word)

    # First pass: mark greens
    for i, char in enumerate(last_guess):
        if char == word[i]:
            revealed_green.append((i, char))
            word_chars[i] = None  # Mark as used

    # Second pass: mark yellows
    for i, char in enumerate(last_guess):
        if char != word[i] and char in word_chars:
            revealed_yellow.append((i, char))
            word_chars[word_chars.index(char)] = None  # Mark as used

    for i, (guess_char, prev_char, word_char) in enumerate(zip(guess, last_guess, word, strict=True)):
        if prev_char == word_char:
            # Previous guess had this letter in the correct position
            if guess_char != word_char:
                return f"Letter **{word_char.upper()}** must be in position {i + 1} (was correct before)"
        elif prev_char in word and prev_char != word_char:
            # Previous guess had this letter but wrong position
            if prev_char not in guess:
                return f"Letter **{prev_char.upper()}** must be used (was yellow before)"
            # Count revealed instances (green + yellow) of prev_char
            prev_count = sum(1 for pos, ch in revealed_green if ch == prev_char) + sum(
                1 for pos, ch in revealed_yellow if ch == prev_char
            )
            # The letter must appear at least as many times as before
            guess_count = sum(1 for c in guess if c == prev_char)
            if guess_count < prev_count:
                return f"Letter **{prev_char.upper()}** must appear at least {prev_count} time(s)"

    return None


def generate_share_text(guesses: list[str], word: str, won: bool, hard_mode: bool = False) -> str:
    """Generate a shareable Wordle grid using Discord-friendly emoji blocks."""
    lines: list[str] = []
    header = f"Wordle {'🔴 Hard' if hard_mode else ''}"
    if won:
        lines.append(f"{header} {len([g for g in guesses if g != 'NOTHING'])}/6")
    else:
        lines.append(f"{header} X/6")
    lines.append("")

    square_map = {
        "green": "🟩",
        "yellow": "🟨",
        "gray": "⬛",
    }

    for guess in guesses:
        if guess == "NOTHING":
            continue
        if guess == word and won and not hard_mode:
            lines.append("🟩🟩🟩🟩🟩")
            break

        line = ""
        letters_remaining = list(word)
        result = ["gray"] * 5

        # First pass: exact matches
        for j, char in enumerate(guess):
            if char == word[j]:
                result[j] = "green"
                letters_remaining[j] = None

        # Second pass: present but wrong position
        for j, char in enumerate(guess):
            if result[j] == "green":
                continue
            if char in letters_remaining:
                result[j] = "yellow"
                letters_remaining[letters_remaining.index(char)] = None

        line = "".join(square_map[r] for r in result)
        lines.append(line)

    return "\n".join(lines)
