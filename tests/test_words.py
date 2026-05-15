"""Tests for hangman_words/words.py and wordle_words/words.py — comprehensive."""

import os

import pytest

from tests.mock_config import patch_config_module

patch_config_module()


class TestHangmanWordsExistence:
    def test_english_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        result = words("en")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_german_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("de")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("German word file not available")

    def test_french_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("fr")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("French word file not available")

    def test_spanish_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("es")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("Spanish word file not available")

    def test_dutch_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("nl")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("Dutch word file not available")

    def test_polish_words_exist(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("pl")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("Polish word file not available")


class TestHangmanWordsQuality:
    def test_english_words_are_strings(self) -> None:
        from commands.games.hangman_words.words import words

        result = words("en")
        for word in result[:10]:
            assert isinstance(word, str)

    def test_english_words_are_lowercase(self) -> None:
        """All hangman words should be lowercase for case-insensitive comparison."""
        from commands.games.hangman_words.words import words

        result = words("en")
        for word in result[:100]:
            assert word == word.lower(), f"Word not lowercase: {word}"

    def test_english_words_are_unique(self) -> None:
        """Check that word list doesn't have duplicates."""
        from commands.games.hangman_words.words import words

        result = words("en")
        assert len(result) == len(set(result)), "Duplicate words found in hangman word list"

    def test_english_words_have_reasonable_length(self) -> None:
        """Words should be at least 2 characters."""
        from commands.games.hangman_words.words import words

        result = words("en")
        for word in result[:100]:
            assert len(word) >= 2, f"Word too short: {word}"

    def test_english_words_no_empty_strings(self) -> None:
        from commands.games.hangman_words.words import words

        result = words("en")
        for word in result:
            assert len(word) > 0, "Empty string in word list"

    def test_english_words_no_whitespace(self) -> None:
        from commands.games.hangman_words.words import words

        result = words("en")
        for word in result[:100]:
            assert word == word.strip(), f"Word has whitespace: '{word}'"

    def test_german_words_quality(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("de")
            for word in result[:50]:
                assert isinstance(word, str)
                assert len(word) > 0
        except FileNotFoundError:
            pytest.skip("German word file not available")

    def test_french_words_quality(self) -> None:
        from commands.games.hangman_words.words import words

        try:
            result = words("fr")
            for word in result[:50]:
                assert isinstance(word, str)
                assert len(word) > 0
        except FileNotFoundError:
            pytest.skip("French word file not available")


class TestHangmanWordsNonexistentLocale:
    def test_nonexistent_locale_raises(self) -> None:
        from commands.games.hangman_words.words import words

        with pytest.raises(FileNotFoundError):
            words("xx_ZZ_nonexistent")

    def test_random_string_raises(self) -> None:
        from commands.games.hangman_words.words import words

        with pytest.raises(FileNotFoundError):
            words("not_a_locale")

    def test_empty_string_raises(self) -> None:
        from commands.games.hangman_words.words import words

        with pytest.raises(FileNotFoundError):
            words("")


class TestHangmanWordsAllLocales:
    """Test that all locale directories have valid word files."""

    @pytest.fixture
    def locale_dirs(self):
        base = "commands/games/hangman_words"
        if not os.path.isdir(base):
            return []
        return [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith("_")]

    def test_each_locale_has_words_file(self, locale_dirs) -> None:
        for locale in locale_dirs:
            filepath = os.path.join("commands/games/hangman_words", locale, "allowed_words.txt")
            assert os.path.isfile(filepath), f"Missing word file for locale: {locale}"

    def test_each_locale_loads_successfully(self, locale_dirs) -> None:
        from commands.games.hangman_words.words import words

        for locale in locale_dirs:
            result = words(locale)
            assert isinstance(result, list)
            assert len(result) > 0, f"Locale {locale} has empty word list"

    def test_each_locale_words_are_strings(self, locale_dirs) -> None:
        from commands.games.hangman_words.words import words

        for locale in locale_dirs:
            result = words(locale)
            for word in result[:10]:
                assert isinstance(word, str), f"Non-string word in {locale}: {word}"


class TestWordleAllowedWords:
    def test_english_allowed_words_exist(self) -> None:
        from commands.games.wordle_words.words import allowed_words

        result = allowed_words("en")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_german_allowed_words_exist(self) -> None:
        from commands.games.wordle_words.words import allowed_words

        try:
            result = allowed_words("de")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("German word file not available")

    def test_english_allowed_words_are_strings(self) -> None:
        from commands.games.wordle_words.words import allowed_words

        result = allowed_words("en")
        for word in result[:10]:
            assert isinstance(word, str)

    def test_english_allowed_words_are_unique(self) -> None:
        from commands.games.wordle_words.words import allowed_words

        result = allowed_words("en")
        assert len(result) == len(set(result)), "Duplicate words in allowed list"

    def test_nonexistent_locale_raises(self) -> None:
        from commands.games.wordle_words.words import allowed_words

        with pytest.raises(FileNotFoundError):
            allowed_words("xx_ZZ_nonexistent")


class TestWordlePossibleWords:
    def test_english_possible_words_exist(self) -> None:
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_english_possible_words_are_strings(self) -> None:
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        for word in result[:10]:
            assert isinstance(word, str)

    def test_possible_words_subset_of_allowed(self) -> None:
        """Possible (answer) words should be a subset of allowed words."""
        from commands.games.wordle_words.words import allowed_words, possible_words

        allowed = set(allowed_words("en"))
        possible = possible_words("en")
        for word in possible[:50]:
            assert word in allowed, f"Possible word not in allowed list: {word}"

    def test_english_possible_words_are_five_letters(self) -> None:
        """Wordle words should be 5 letters."""
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        for word in result[:50]:
            assert len(word) == 5, f"Word not 5 letters: {word}"

    def test_english_possible_words_are_lowercase(self) -> None:
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        for word in result[:50]:
            assert word == word.lower(), f"Word not lowercase: {word}"

    def test_english_possible_words_no_empty(self) -> None:
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        for word in result:
            assert len(word) > 0, "Empty string in possible words"

    def test_possible_words_are_unique(self) -> None:
        from commands.games.wordle_words.words import possible_words

        result = possible_words("en")
        assert len(result) == len(set(result)), "Duplicate words in possible list"


class TestWordleMultiLocale:
    def test_german_possible_words(self) -> None:
        from commands.games.wordle_words.words import possible_words

        try:
            result = possible_words("de")
            assert isinstance(result, list)
            assert len(result) > 0
            for word in result[:10]:
                assert isinstance(word, str)
        except FileNotFoundError:
            pytest.skip("German word file not available")

    def test_french_possible_words(self) -> None:
        from commands.games.wordle_words.words import possible_words

        try:
            result = possible_words("fr")
            assert isinstance(result, list)
            assert len(result) > 0
            for word in result[:10]:
                assert isinstance(word, str)
        except FileNotFoundError:
            pytest.skip("French word file not available")

    def test_spanish_possible_words(self) -> None:
        from commands.games.wordle_words.words import possible_words

        try:
            result = possible_words("es")
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            pytest.skip("Spanish word file not available")


class TestWordleAllLocales:
    """Test that all wordle locale directories have both required files."""

    @pytest.fixture
    def locale_dirs(self):
        base = "commands/games/wordle_words"
        if not os.path.isdir(base):
            return []
        return [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and not d.startswith("_")]

    def test_each_locale_has_allowed_words(self, locale_dirs) -> None:
        for locale in locale_dirs:
            filepath = os.path.join("commands/games/wordle_words", locale, "allowed_words.txt")
            assert os.path.isfile(filepath), f"Missing allowed_words.txt for locale: {locale}"

    def test_each_locale_has_possible_words(self, locale_dirs) -> None:
        for locale in locale_dirs:
            filepath = os.path.join("commands/games/wordle_words", locale, "possible_words.txt")
            assert os.path.isfile(filepath), f"Missing possible_words.txt for locale: {locale}"

    def test_each_locale_possible_subset_of_allowed(self, locale_dirs) -> None:
        from commands.games.wordle_words.words import allowed_words, possible_words

        for locale in locale_dirs:
            try:
                allowed = set(allowed_words(locale))
                possible = possible_words(locale)
                for word in possible[:20]:
                    assert word in allowed, f"Locale {locale}: possible word '{word}' not in allowed list"
            except FileNotFoundError:
                pass  # Skip if file not found
